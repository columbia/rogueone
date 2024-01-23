import contextlib
import time

import networkx as nx

from glob import glob
import os
import fast.simurun.launcher as launcher
import fast.dataflow.extraction as ex
import find_for_manager
import tasks
from fast.manager.engine import init as init_engine
from fast.manager.models import *
import fast.manager.models as mod
from tempfile import TemporaryDirectory
from fast.manager.package_manager import create_version_task, create_version_pair_task

single_v_folder = os.path.join(os.path.dirname(__file__), 'dataflow_fixtures', "single_version")
single_folders = glob(os.path.join(single_v_folder, '*/'))
dual_v_folder = os.path.join(os.path.dirname(__file__), 'dataflow_fixtures', "dual_version")
dual_v_folders = glob(os.path.join(dual_v_folder, '*/'))

gen_graph_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'fast', 'generate_graph.py')
@contextlib.contextmanager
def remember_cwd():
    curdir= os.getcwd()
    try: yield
    except Exception as e: raise e
    finally: os.chdir(curdir)


def test_analyze_single_version_success():
    with TemporaryDirectory() as tdir:
        _, Session = init_engine(echo=False)
        session = Session()
        p = Package(name='semver')
        v = Version(package=p, number='5.1.0', disk_location=str(Path(single_v_folder) / 'daemon' ))
        session.add(p)
        session.add(v)
        session.flush()
        _, tid = create_version_task(session, v.id, 1, log_location=tdir)
        session.flush()
        session.commit()
        tasks.analyze_single_version.apply(args=[tid, session])
        session.flush()
        tm = session.query(TaskModel).filter(TaskModel.id == tid).one()
        assert tm.state == State.CompletedSuccess
        assert tm.json_result['error'] == 'OK'

        # session.rollback()

def test_download_single_version_analysis_method():
    pv_vals = [
        ("kraken-api", "0.1.7"), ("ng-ui-library","1.0.986"),("ng-ui-library","1.0.987"),
               ("eslint-config-eslint", "5.0.2")]
    for pname, vname in pv_vals:
        with TemporaryDirectory() as tdir:
            _, Session = init_engine(echo=False)
            session = Session()
            p = Package(name=pname)
            v = Version(package=p, number=vname, disk_location=None)
            session.add(p)
            session.add(v)
            session.flush()
            loc = tasks.download_single_version_for_analysis(Path(tdir), v)
            if loc is not None:
                assert loc.exists()
                assert (loc / "package").exists()
                assert (loc / "package" / "package.json").exists()


def test_analyze_version_pair_success():
    with TemporaryDirectory() as tdir:
        _, Session = init_engine(echo=False)
        session = Session()
        name, before, after = find_for_manager.extract_name_and_versions("tlg_1.1.3-->1.1.4")
        p = Package(name=name)
        v = Version(package=p, number=before)
        v2 = Version(package=p, number=after)
        session.add(p)
        session.add(v)
        session.add(v2)
        session.flush()
        vp = VersionPair(before_id=v.id, after_id=v2.id, disk_location=tdir, label="", group="", diff_json=b'[]')
        session.add(vp)
        session.flush()
        _, tid = create_version_pair_task(session, vp.id, 1)
        session.flush()
        session.commit()
        tasks.analyze_version_pair.apply(args=[tid, tdir, session])
        # tasks.analyze_version_pair(tid, tdir, session)
        session.flush()
        tm = session.query(VersionPairTaskModel).filter(VersionPairTaskModel.id == tid).one()
        assert tm.state == State.CompletedSuccess
        assert tm.json_result['error'] == 'OK'
        assert tm.analysis_length != 0
        # print(tm.analysis_length)

# DB_PATH = "db.json"
# def test_async_analyze_version_pair_success():
#     db_uri = None
#     try:
#         with open(DB_PATH) as f:
#             db = json.load(f)
#             db_uri = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"
#
#     except FileNotFoundError as e:
#         sys.stderr.write(f"No db config file found at {DB_PATH}.\n")
#         # sys.exit(1)
#     except json.JSONDecodeError as e:
#         sys.stderr.write(f"Could not load json db config file at {DB_PATH}.\n")
#         # sys.exit(1)
#     if not db_uri:
#         db_uri = "sqlite+pysqlite:///:memory:"
#     _, Session = init_engine(db_uri, echo=False)
#     session = Session()
#     with TemporaryDirectory() as tdir:
#         name, before, after = find_for_manager.extract_name_and_versions("ab_0.1.0-->1.0.0")
#         p = session.query(mod.Package).filter_by(name=name).one_or_none()
#         if not p:
#             p = Package(name=name)
#             session.add(p)
#         v = session.query(mod.Version).filter_by(package=p, number=before).one_or_none()
#         if not v:
#             v = Version(package=p, number=before)
#             session.add(v)
#         v2 = session.query(mod.Version).filter_by(package=p, number=after).one_or_none()
#         if not v2:
#             v2 = Version(package=p, number=after)
#             session.add(v2)
#
#         session.flush()
#         vp = session.query(mod.VersionPair).filter_by(before_id=v.id, after_id=v2.id).one_or_none()
#         if not vp:
#             vp = VersionPair(before_id=v.id, after_id=v2.id, disk_location=tdir, label="", group="RandomBenignSamples", diff_json=b'[]')
#             session.add(vp)
#         session.flush()
#
#         _, tid = create_version_pair_task(session, vp.id, 1)
#         session.flush()
#         session.commit()
#         tasks.analyze_version_pair.delay(tid, tdir)
#         time.sleep(1)
#         session.flush()
#         tm = session.query(VersionPairTaskModel).filter(VersionPairTaskModel.id == tid).one()
#         assert tm.state == State.CompletedSuccess
#         assert tm.json_result['error'] == 'OK'
#         assert tm.analysis_length != 0