import argparse
import glob
import json
import shutil
import subprocess
import os
import sys
import tempfile
import time
from abc import ABC
from datetime import datetime, timedelta
from pathlib import Path

import celery
from celery.exceptions import SoftTimeLimitExceeded
from celery import Celery
from celery import Task
from celery.schedules import crontab
import requests
from sqlalchemy import or_, nulls_last

import fast.manager.engine as engine
import fast.manager.models as mod
import find_for_manager
import rogue_one_runner
import tasks
from fast.manager import package_manager
from fast.manager.package_manager import find_new_packages, renew_task, create_version_task, create_version_pair_task
from fast.manager.registry import fetch_npm_registry, fetch_tarball_url
from find_for_manager import record_ror_with_json, create_diff_json, record_ror_with_json_and_pair
from rogue_one_runner import process_package_pair_given_names, process_package_pair
from extract_samples import extract_file
import sqlalchemy
import sqlalchemy.sql.operators as sql_op

DELAY = 10

base_sample_path = Path("/srv/rogueone/RogueOneSamples/")
SAMPLE_FOLDER = base_sample_path / Path("active_survey/")

SINGLE_VERSION_FOLDER = Path("/srv/rogueone/RogueOneSingleVersionSamples/")
PROCESSING_FOLDER = Path("/srv/rogueone/RogueOneProcessing/")
GENERAL_FOLDER = Path("/srv/rogueone/GeneralProcessingFolder/")
retro_survey_folder = base_sample_path / Path("retro_survey")
DB_PATH = "db2.json"  # Should change this.
ANALYSIS_TIMEOUT = 2 * 60 * 60  # 2 hours

try:
    with open(DB_PATH) as f:
        DB_JSON = json.load(f)
except FileNotFoundError as e:
    sys.stderr.write(f"No db config file found at {DB_PATH}.\n")
    DB_JSON = {}
    # sys.exit(1)
except json.JSONDecodeError as e:
    sys.stderr.write(f"Could not load json db config file at {DB_PATH}.\n")
    DB_JSON = {}
    # sys.exit(1)

if "sample_folder" in DB_JSON:
    SAMPLE_FOLDER = Path(DB_JSON["sample_folder"])
if "single_version_folder" in DB_JSON:
    SINGLE_VERSION_FOLDER = Path(DB_JSON["single_version_folder"])
if "processing_folder" in DB_JSON:
    PROCESSING_FOLDER = Path(DB_JSON["processing_folder"])
if "retro_survey_folder" in DB_JSON:
    retro_survey_folder = Path(DB_JSON["retro_survey_folder"])
if "general_folder" in DB_JSON:
    GENERAL_FOLDER = Path(DB_JSON["general_folder"])
if "local_paths" in DB_JSON:
    LOCAL_PATHS = Path(DB_JSON["local_paths"])

if "redis_url" in DB_JSON:
    redis_link = DB_JSON["redis_url"]
    running_local = False
else:
    redis_link = "redis://localhost:6379"
    running_local = True

app = Celery('tasks', backend=redis_link, broker=redis_link)
app.conf.task_routes = {
    'tasks.find_new_version_pairs_list': {'queue': 'local'},
    'tasks.find_new_version_pairs': {'queue': 'local'}
}

SF_LIST = [
    retro_survey_folder,
    SAMPLE_FOLDER,
]


class DBTask(Task, ABC):
    _session = None

    def after_return(self, *args, **kwargs):
        if self._session is not None:
            self._session.close()

    @property
    def session(self):
        if self._session is None:
            db_uri = None
            try:
                with open(DB_PATH) as f:
                    db = json.load(f)
                    db_uri = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"

            except FileNotFoundError as e:
                sys.stderr.write(f"No db config file found at {DB_PATH}.\n")
                # sys.exit(1)
            except json.JSONDecodeError as e:
                sys.stderr.write(f"Could not load json db config file at {DB_PATH}.\n")
                # sys.exit(1)
            if not db_uri:
                db_uri = "sqlite+pysqlite:///:memory:"
            _, Session = engine.init(db_uri, echo=False)
            self._session = Session()
        return self._session


def get_default_args():
    ap = argparse.ArgumentParser(description="Runner for mass parallel analysis.")
    ap.add_argument("--sample_folder", action="store", help="A folder containing folders of datasets, each of which has \
    folders of before/after update pairs.  e.g. given Samples/30_backstabber_samples/pack_0.1-->pack_0.2/pack_0.1/ as a\
     sample, the argument should be just Samples, so that the samples are captured by **/*-->**/", required=False)
    ap.add_argument("--timeouts", action="store_true", default=False)
    ap.add_argument("--no_redo", action="store_true", default=False)
    ap.add_argument("--single", action='store', help="A folder containing a single package pair to be analyzed.")
    ap.add_argument("--fast", action="store_true", help="Coarser analysis for post-timeout reanalysis attempt.")
    ap.add_argument("--log_level", action="store", help="More or less verbose logs: DEBUG, INFO, WARN, ERROR, FATAL",
                    default="ERROR")
    ap.add_argument("--raise_all", action="store_true", default=False)
    ap.add_argument("--save_odrg", action="store_true", default=False, help="Save the ODRGs built for the before and\
     after versions of the program.  Saves as GraphML in files <pair_dir>/before.graphml and after.graphml.")
    args = ap.parse_args(args=[])
    return args


@app.task(base=DBTask, bind=True, time_limit=0.2 * 60 * 60, expires=DELAY * 60)
def find_new_version_pairs_list(self, sample_folder_list=SF_LIST):
    for l in sample_folder_list:
        find_new_version_pairs.delay(str(l))


@app.task(base=DBTask, bind=True, time_limit=0.2 * 60 * 60, expires=DELAY * 60)
def find_new_version_pairs(self, sample_folder=SAMPLE_FOLDER):
    sample_folder = Path(sample_folder)
    uids = find_new_packages(self.session, sample_folder, package_manager.find_or_create_version_pair)
    self.session.flush()
    for uid in uids:
        vp = self.session.query(mod.VersionPair).join(mod.VersionPair.before).join(mod.Version.package).filter(
            mod.VersionPair.id == uid).one()
        package = vp.before.package
        if package.has_timeout:
            pass
        else:
            enqueue_analysis_job.delay(uid)
            fetch_package_registry.delay(uid)
            fetch_dependency_lists.delay(uid)


@app.task(base=DBTask, bind=True, soft_time_limit=20 * 60, max_retries=3, autoretry_for=(Exception,),
          retry_backoff=True)
def fetch_dependency_lists(self, version_pair_id):
    v2 = mod.Version.__table__.alias(name='after_version')
    vp: mod.VersionPair = self.session.query(mod.VersionPair).filter(mod.VersionPair.id == version_pair_id). \
        join(mod.Version, mod.VersionPair.before).join(v2, mod.VersionPair.after).one()

    up_res = self.session.execute(
        sqlalchemy.update(mod.VersionPair).where(
            mod.VersionPair.id == vp.id
        ).where(or_(mod.VersionPair.deps_download_state == mod.State.NotStarted,
                    mod.VersionPair.deps_download_state == mod.State.CompletedError)
                ).values(deps_download_state=mod.State.Running).returning(mod.VersionPair))
    if not list(up_res):
        return f"fetch_dependency_lists: Dependency download for vp {vp.id}, " + \
            f"{vp.before.package.name} {vp.before.number}->{vp.after.number} canceled due to state: {vp.deps_download_state}"
    new_deps = []
    failed = False
    err = None
    for v in (vp.before, vp.after):
        try:
            new_deps.extend(v.create_dependencies(self.session))
        except json.decoder.JSONDecodeError as e:
            sys.stderr.write(
                f"fetch_dependency_lists: Failed to parse dependency list JSON for version {v.package.name}@{v.number}.\n")
            err = e
            failed = True
    if failed:
        self.session.execute(
            sqlalchemy.update(mod.VersionPair).where(
                mod.VersionPair.id == vp.id
            ).where(mod.VersionPair.deps_download_state == mod.State.Running
                    ).values(deps_download_state=mod.State.CompletedError).returning(mod.VersionPair))
        self.session.commit()
        raise err

    self.session.commit()

    for dep in new_deps:
        download_single_version.delay(dep.id, analyze=True)
    self.session.execute(
        sqlalchemy.update(mod.VersionPair).where(
            mod.VersionPair.id == vp.id
        ).where(mod.VersionPair.deps_download_state == mod.State.Running
                ).values(deps_download_state=mod.State.CompletedSuccess).returning(mod.VersionPair))
    self.session.commit()


@app.task(base=DBTask, bind=True)
def download_single_version(self, version_id, analyze=False):
    v: mod.Version = self.session.query(mod.Version).join(mod.Package).filter(mod.Version.id == version_id).one()
    if v.disk_location and Path(v.disk_location).is_relative_to(SINGLE_VERSION_FOLDER):
        return True
    url = fetch_tarball_url(v.package.name, v.number)
    sample_folder_path = Path(SINGLE_VERSION_FOLDER) / f"{v.package.name.replace('/', '@')}@{v.number}"
    try:
        sample_folder_path.mkdir()
    except FileExistsError:
        pass
    tgz_path = sample_folder_path / 'package.tgs'
    if not tgz_path.exists():
        with requests.get(url) as r:
            with open(tgz_path, 'wb') as f:
                for c in r.iter_content(8192):
                    f.write(c)
    extracted_path = sample_folder_path / 'package'
    if not extracted_path.exists():
        extract_file(tgz_path, sample_folder_path, None, rename=False)
    v.disk_location = str(extracted_path)
    self.session.add(v)
    self.session.commit()
    if analyze:
        if self.session.query(mod.TaskModel).filter(
                mod.TaskModel.version_id == v.id
        ).filter(
            sql_op.or_(sql_op.or_(mod.TaskModel.state == mod.State.CompletedSuccess,
                                  mod.TaskModel.state == mod.State.NotStarted),
                       mod.TaskModel.state == mod.State.Running)
        ).count() == 0:
            success, task_id = create_version_task(self.session, v.id, ANALYSIS_TIMEOUT, PROCESSING_FOLDER)
            self.session.commit()
            analyze_single_version.delay(task_id)
    return True


def download_single_version_for_analysis(pair_folder: Path, v: mod.Version) -> Path:
    sample_folder_path = pair_folder / f"{v.package.name.replace('/', '@')}@{v.number}"
    if sample_folder_path.exists():
        return sample_folder_path
    url = fetch_tarball_url(v.package.name, v.number)
    if len(url) == 0:
        return None
    try:
        sample_folder_path.mkdir(parents=True)
    except FileExistsError:
        pass
    tgz_path = sample_folder_path / 'package.tgs'
    if not tgz_path.exists():
        with requests.get(url) as r:
            if r.status_code == 200:
                with open(tgz_path, 'wb') as f:
                    for c in r.iter_content(8192):
                        f.write(c)
            else:
                return None
    extracted_path = sample_folder_path / 'package'
    if not extracted_path.exists():
        extract_file(tgz_path, sample_folder_path, None, rename=False)
    return sample_folder_path


@app.task(base=DBTask, bind=True, time_limit=0.2 * 60 * 60)
def find_new_single_versions(self, sample_folder=SINGLE_VERSION_FOLDER):
    uids = find_new_packages(self.session, sample_folder, package_manager.find_or_create_single_version)
    self.session.flush()
    for uid in uids:
        success, task_id = create_version_task(self.session, uid, ANALYSIS_TIMEOUT, PROCESSING_FOLDER)
        if success:
            self.session.commit()
            analyze_single_version.delay(task_id)


@app.task(base=DBTask, bind=True)
def update_timed_out_tasks(self):
    tasks = mod.TaskModel.timed_out_tasks(self.session)
    sys.stdout.write(f"Found {len(tasks)} timed out tasks.\n")
    try:
        for task in tasks:
            task.set_state(new_state=mod.State.TimedOut)
            new_task = renew_task(self.session, task, PROCESSING_FOLDER)
            self.session.commit()
            analyze_single_version.delay(new_task)
    except Exception as e:
        sys.stderr.write(f"Caught exception of {type(e).__name__}. {e} while attempting to update timed-out tasks.\n")
        self.session.rollback()
        raise e


@app.task(base=DBTask, bind=True, soft_time_limit=2 * 60 * 60)
def process_package_pair_distributed(self, pair: mod.VersionPair, pair_loc: str, pair_path: Path,
                                     before_loc: Path, after_loc: Path, fast: bool = False, session=None):
    if not session:
        session = self.session

    try:

        args = get_default_args()
        if fast:
            args.fast = True

        # result = process_package_pair(pair_loc, args=args, printer=rogue_one_runner.noop)
        result = process_package_pair_given_names(pair_loc, pair_path, before_loc, after_loc,
                                                  pair.before.package.name, pair.before.number, pair.after.number,
                                                  rogue_one_runner.noop, args)

        if result is None:
            sys.stderr.write(
                f"process_package_pair_distributed: Got no result back from {pair.before.package.name}. Perhaps there is a skip flag?\n")
            return None
        # success = record_ror_with_json_and_pair(session, f"{pair_loc}/rogue_one_output.json", result, pair)
        # if success:
        #     session.commit()
        #     session.flush()
        sys.stdout.write(
            f"process_package_pair_distributed: Finished processing package '{pair.before.package.name}'.\n")
        return result
    except SoftTimeLimitExceeded as e:
        sys.stderr.write(f"Soft time limit exceeded for {pair}.")
        pair.before.package.has_timeout = True
        session.add(pair.before.package)
        session.commit()
        raise e

    except Exception as e:
        sys.stderr.write(
            f"process_package_pair_distributed: Caught exception of {type(e).__name__}. {e} while attempting to analyze version pair with "
            f"id: {pair.id}.\n")
        raise e


@app.task(base=DBTask, bind=True, soft_time_limit=2 * 60 * 60)
def enqueue_analysis_job(self, version_pair_id: int, fast: bool = False):
    pair: mod.VersionPair = self.session.query(mod.VersionPair).filter_by(id=version_pair_id).one_or_none()
    try:
        if pair is None:
            sys.stderr.write(
                f"enqueue_analysis_job: Aborting! Could not find version pair with {version_pair_id} within database.\n")
            return None
        args = get_default_args()
        if fast:
            args.fast = True

        result = process_package_pair(pair.disk_location, args=args, printer=rogue_one_runner.noop)
        if result is None:
            sys.stderr.write(
                f"enqueue_analysis_job: Got no result back from {pair.before.package.name}. Perhaps there is a skip flag?\n")
            return None
        success = record_ror_with_json(self.session, f"{pair.disk_location}/rogue_one_output.json", result)
        if success:
            self.session.commit()
            self.session.flush()
        sys.stdout.write(f"enqueue_analysis_job: Finished processing package '{pair.before.package.name}'.\n")
        return result
    except SoftTimeLimitExceeded as e:
        sys.stderr.write(f"Soft time limit exceeded for {pair}.")
        pair.before.package.has_timeout = True
        self.session.add(pair.before.package)
        self.session.commit()
        raise e

    except Exception as e:
        sys.stderr.write(
            f"enqueue_analysis_job: Caught exception of {type(e).__name__}. {e} while attempting to find version pair with "
            f"id: {version_pair_id}.\n")
        raise e


@app.task(base=DBTask, bind=True, time_limit=60)
def fetch_package_registry(self, version_pair_id: int):
    try:
        pair = self.session.query(mod.VersionPair).join(mod.VersionPair.before).join(mod.Version.package).filter(
            mod.VersionPair.id == version_pair_id).one_or_none()
        if pair is None:
            sys.stderr.write(
                f"fetch_package_registry: Aborting! Could not find version pair with {version_pair_id} within database.\n")
            return
        pkg = pair.before.package
        fetch_npm_registry(self.session, package_name=pkg.name, pkg=pkg)
        self.session.flush()
    except Exception as e:
        sys.stderr.write(f"Caught exception of {type(e).__name__}. {e} while attempting to find version pair with "
                         f"id: {version_pair_id}.\n")
        raise e


@app.task(base=DBTask, bind=True, soft_time_limit=2 * 60 * 60)
def analyze_version_pair(self, vp_task_id, folder=GENERAL_FOLDER, session=None):
    if not session:
        session = self.session
    tvp: mod.VersionPairTaskModel = None
    result: {} = None
    try:
        res = session.execute(sqlalchemy.update(mod.VersionPairTaskModel)
                              .where(mod.VersionPairTaskModel.id == vp_task_id)
                              .where(mod.VersionPairTaskModel.state == mod.State.NotStarted)
                              .values(state=mod.State.Running, last_state_transition=datetime.now())
                              .returning(mod.VersionPairTaskModel))
        upt = res.fetchall()
        session.commit()
        if len(upt) == 0:
            sys.stderr.write(
                f"analyze_version_pair: Aborting! Could not find inactive VPTask with id: {vp_task_id} within database.\n")
            return
        tvp = session.query(mod.VersionPairTaskModel).filter_by(id=vp_task_id,
                                                                state=mod.State.Running).one_or_none()
        if tvp is None:
            sys.stderr.write(
                f"analyze_version_pair: Aborting! Could not find running VPTask with id: {vp_task_id} within database.\n")
            return
        sys.stdout.write(f"analyze_version_pair: received task: {tvp.id}\n")
        if tvp.is_timed_out():  # TODO: Check on this
            sys.stdout.write("analyze_version_pair: task model timed out, aborting.\n")
            return

        version_pair: mod.VersionPair = tvp.version_pair

        # TODO: Check on how data is stored (disk_location may not be null?)

        before_folder = None
        after_folder = None
        pair_folder = None
        is_core = False

        if version_pair.group in mod.core_groups and LOCAL_PATHS:
            pair_folder = Path(LOCAL_PATHS) / version_pair.group / \
                          f"{version_pair.before.package.name}_{version_pair.before.number}-->" \
                          f"{version_pair.after.number}"
            is_core = True
            if pair_folder.exists():
                before_folder = pair_folder / f"{version_pair.before.package.name}-{version_pair.before.number}"
                after_folder = pair_folder / f"{version_pair.after.package.name}-{version_pair.after.number}"
                if not before_folder.exists() or not after_folder.exists():
                    before_folder = None
                    after_folder = None
            else:
                pair_folder.mkdir(parents=True)
                before_folder = download_single_version_for_analysis(pair_folder=pair_folder,
                                                                     v=version_pair.before)
                after_folder = download_single_version_for_analysis(pair_folder=pair_folder,
                                                                    v=version_pair.after)
                if before_folder:
                    before_folder = before_folder / "package"
                if after_folder:
                    after_folder = after_folder / "package"

        if not before_folder or not after_folder:
            # fp = Path(folder)
            # if not fp.exists():
            #     try:
            #         fp.mkdir(parents=True)
            #     except OSError:
            #         sys.stderr.write("Could not create folder!\n")
            #         pass
            # if fp.exists():
            is_core = False
            fp = Path(folder)
            pair_folder = Path(os.curdir).absolute() / fp.parts[-1]
            if not pair_folder.exists():
                pair_folder.mkdir(parents=True)

            before_folder = download_single_version_for_analysis(pair_folder=pair_folder,
                                                                 v=version_pair.before)
            after_folder = download_single_version_for_analysis(pair_folder=pair_folder,
                                                                v=version_pair.after)
            if before_folder:
                before_folder = before_folder / "package"
            if after_folder:
                after_folder = after_folder / "package"

            # sys.stdout.write(f"Created folders: {pair_folder} \n{before_folder}\n{after_folder}\n")
            # if pair_folder and pair_folder.exists():
            #     sys.stdout.write("Pair Folder exists.\n")
            #     sys.stdout.write(f"{os.listdir(pair_folder)}\n")
            # if before_folder and before_folder.exists():
            #     sys.stdout.write("Before Folder exists.\n")
            #     sys.stdout.write(f"{os.listdir(before_folder)}\n")
            # if after_folder and after_folder.exists():
            #     sys.stdout.write("After Folder exists.\n")
            #     sys.stdout.write(f"{os.listdir(after_folder)}\n")

        # Pre-generated result, in case process hits time-out
        result = {
            'package_name': version_pair.before.package.name,
            'label': "UNK",
            'group': version_pair.group,
            'system': 'rogue_one',
            'run_timestamp': str(datetime.now()),
            'sinks_added': 0,
            'sinks_removed': 0,
            'sinks_changed': 0,
            'fast_mode': tvp.num_retries >= 1,
            'esprima_info': None,
            'before': {
                'version': version_pair.before.number,
                'folder': str(before_folder),
                'flows': "",
                'running_time': 0,
                'weakly_connected_components': "",
                'error': 'error',
            },
            'after': {
                'version': version_pair.after.number,
                'folder': str(after_folder),
                'flows': "",
                'running_time': 0,
                'weakly_connected_components': "",
                'error': 'error',
            },
            'error': 'error',
            'identical_flows': "",
            'new_flows': "",
            'removed_flows': "",
            'suspicious': False,
            'system_extra_info': {},
        }

        if not pair_folder or not before_folder or not after_folder:
            sys.stdout.write(f"analyze_version_pair: Could not find / download package for task: {tvp.id}\n")
            tvp.set_state(mod.State.ExceptionCaught)
            tvp.error = "package_not_found"
            result['error'] = 'package_not_found'
            tvp.json_result = result
            session.commit()
            return

        result = process_package_pair_distributed(pair=version_pair, pair_loc=str(pair_folder),
                                                  pair_path=pair_folder, before_loc=before_folder,
                                                  after_loc=after_folder, fast=tvp.num_retries >= 1, session=session)
        if result is not None:
            result['group'] = version_pair.group
            result['label'] = "UNK"
        find_for_manager.update_version_pair_task_model(tvp, pair_folder, result)
        session.commit()

        if not is_core:
            try:
                shutil.rmtree(pair_folder)
            except OSError as e:
                sys.stderr.write(f"analyze_version_pair: Failed to delete {pair_folder} after processing. Error: {e}\n")

    except SoftTimeLimitExceeded as e:
        if tvp:
            sys.stderr.write(f"Soft time limit exceeded for {tvp}.")
            tvp.num_retries += 1
            if tvp.state != mod.State.Running:
                session.commit()
            # Requeues task if task is running and timed out
            elif tvp.num_retries == 1:
                tvp.set_state(mod.State.NotStarted)
                session.commit()
                analyze_version_pair.delay(vp_task_id, folder)
            else:
                find_for_manager.time_out_version(tvp, result)
                session.commit()
        raise e
    except Exception as e:
        sys.stderr.write(
            f"analyze_version_pair: Caught exception of {type(e).__name__}. {e} while attempting to analyze version with "
            f"id: {vp_task_id}.\n")
        session.rollback()
        if tvp:
            if tvp.state == mod.State.Running:
                tvp.set_state(mod.State.ExceptionCaught)
                tvp.error = str(e)[:256]
                session.commit()
        raise e


@app.task(base=DBTask, bind=True, soft_time_limit=20 * 60)
def analyze_single_version(self, task_id: int, session=None):
    if not session:
        session = self.session
    task: mod.TaskModel = None
    try:
        res = session.execute(sqlalchemy.update(mod.TaskModel).where(mod.TaskModel.id == task_id).where(
            mod.TaskModel.state == mod.State.NotStarted).values(
            state=mod.State.Running).returning(mod.TaskModel))
        # Acquires lock on file
        upt = res.fetchall()
        session.commit()
        if len(upt) == 0:
            sys.stderr.write(
                f"analyze_single_version: Aborting! Could not find inactive TaskModel with id: {task_id} within database.\n")
            return
        task = session.query(mod.TaskModel).filter_by(id=task_id, state=mod.State.Running).one_or_none()
        if task is None:
            sys.stderr.write(
                f"analyze_single_version: Aborting! Could not find running TaskModel with id: {task_id} within database.\n")
            return
        sys.stdout.write(f"analyze_single_version: received task: {task.disk_location}\n")
        if task.is_timed_out():
            sys.stdout.write("analyze_single_version: task model timed out, aborting.\n")
            return

        args = get_default_args()
        if task.num_retries >= 1:
            args.fast = True

        result = rogue_one_runner.process_package_version_with_model(task, rogue_one_runner.noop, args)
        find_for_manager.update_task_model(task, result)

        session.commit()

    except SoftTimeLimitExceeded as e:
        if task:
            sys.stderr.write(f"Soft time limit exceeded for {task}.")
            task.num_retries += 1
            if task.state != mod.State.Running:
                session.commit()
            # Requeues task if task is running and timed out
            elif task.num_retries == 1:
                task.set_state(mod.State.NotStarted)
                session.commit()
                analyze_single_version.delay(task_id)
            else:
                task.set_state(mod.State.TimedOut)
                session.commit()

        raise e
    except Exception as e:
        sys.stderr.write(
            f"analyze_single_version: Caught exception of {type(e).__name__}. {e} while attempting to analyze version with "
            f"id: {task_id}.  {task.version.disk_location if task else ''}\n")
        session.rollback()
        if task:
            if task.state == mod.State.Running:
                task.set_state(mod.State.ExceptionCaught)
                task.error = str(e)[:256]
                session.commit()
        raise e


core_groups = ['BenignSamples', 'BenignSamples2', 'RandomBenignSamples', 'RandomBenignSamples2',
               '30_backstabber_samples', 'checkmarks_stabber_samples', 'new_backstabber_samples',
               'amalfi_NPM']


@app.task(base=DBTask, bind=True)
def download_core_data_deps(self, session=None):
    if not session:
        session = self.session

    q = session.query(mod.VersionPair)
    q = q.filter(mod.VersionPair.group.in_(core_groups))
    q = q.filter(mod.VersionPair.deps_download_state != mod.State.CompletedSuccess)

    for vp in q.all():
        fetch_dependency_lists.delay(vp.id)


@app.task(base=DBTask, bind=True)
def refresh_core_data_analysis_tasks(self, session=None, group=None):
    if not session:
        session = self.session
    tids_for_analysis = []
    vptm_for_analysis = []
    q = session.query(mod.VersionPair)
    q = q.filter(mod.VersionPair.group == 'retro_survey')
    q = q.join(mod.VersionPair.after)
    q = q.order_by(nulls_last(mod.Version.uploaded_at.desc()))
    #q = q.filter(mod.VersionPair.deps_download_state == mod.State.CompletedSuccess)
    cutoff = datetime(2023, 12, 18)
    for vp in q.all():
        tvp = vp.most_recent_task_result(self.session, cutoff)
        valid_states = [mod.State.CompletedSuccess, mod.State.Running, mod.State.TimedOut]
        if not tvp or tvp.run_timestamp < cutoff or tvp.is_timed_out() or tvp.state not in valid_states:
            success, tid = create_version_pair_task(session, vp.id, 20 * 60)
            if success:
                vptm_for_analysis.append((tid, vp.disk_location))
    session.commit()
    for tid in tids_for_analysis:
        tasks.analyze_single_version.delay(tid)
    for tid, loc in vptm_for_analysis:
        analyze_version_pair.delay(tid, loc)
    sys.stdout.write(f"refresh_core_analysis: Enqueued {len(vptm_for_analysis)} version pairs for analysis.\n")
    return tids_for_analysis, vptm_for_analysis


@app.task(base=DBTask, bind=True)
def consolidate_version_pairs(self):
    all_core_vps = mod.VersionPair.q_core_vps(self.session).join(mod.VersionPair.rogue_one_results, isouter=True). \
        join(mod.VersionPair.before).order_by(mod.VersionPair.id).all()

    def vp_tuple(vp: mod.VersionPair):
        return (vp.before.package.name, vp.group, vp.before.number, vp.after.number)

    vp_map = {}
    for vp in all_core_vps:
        k = vp_tuple(vp)
        if k not in vp_map:
            vp_map[k] = vp.id
        else:
            for ror in vp.rogue_one_results:
                sys.stderr.write(f"Combining {vp} with {vp_map[k]}.\n")
                ror.version_pair_id = vp_map[k]
                self.session.add(ror)
    self.session.commit()


def test_method():
    db_uri = None
    try:
        with open(DB_PATH) as f:
            db = json.load(f)
            db_uri = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"

    except FileNotFoundError as e:
        sys.stderr.write(f"No db config file found at {DB_PATH}.\n")
        # sys.exit(1)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Could not load json db config file at {DB_PATH}.\n")
        # sys.exit(1)
    if not db_uri:
        db_uri = "sqlite+pysqlite:///:memory:"
    _, Session = engine.init(db_uri, echo=False)
    session = Session()

    create_version_task(session, 1, ANALYSIS_TIMEOUT)
    session.commit()

    analyze_single_version(task_id=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Distributed task queue runner that automatically manages analysis of packages")
    # ap.add_argument("--db", action="store", default=False, required=False)
    ap.add_argument("--sample_folder", action="store", help="A folder containing folders of datasets, each of which has \
    folders of before/after update pairs.  e.g. given Samples/30_backstabber_samples/pack_0.1-->pack_0.2/pack_0.1/ as a\
     sample, the argument should be just Samples, so that the samples are captured by **/**/*/", required=False)
    args = ap.parse_args()
    # if args.sample_folder is not None:
    #     groups = Path(args.sample_folder).glob('*' )
    #     for g in groups:
    #         find_new_version_pairs(sample_folder=g)
    # else:
    #     find_new_version_pairs()
    # find_new_single_versions()
    find_new_version_pairs_list.delay()
    # task_id = create_version_task(self.session, uid, ANALYSIS_TIMEOUT, PROCESSING_FOLDER)
    # analyze_single_version.delay(task_id)
