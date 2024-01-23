import glob
from tqdm import tqdm
import json
import os
import subprocess
import sys
from typing import Optional

import sqlalchemy
import sqlalchemy.exc

import fast.manager.engine as engine
import fast.manager.models as mod
from fast.manager.package_changes import *
from rogue_one_runner import extract_name_and_versions
import argparse
from datetime import datetime
from pprint import pp

from fast.manager.package_changes import extract_name_and_versions

d2h_js_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                            'fast/esprima-csv/diff2json.js'))


def load_json_file(fn):
    try:
        with open(fn) as f:
            return json.load(f)
    except json.decoder.JSONDecodeError as e:
        with open(fn, encoding='utf-8-sig') as f:
            return json.load(f)


def record_package_version(session, version_folder: str):
    try:
        package_json_data = load_json_file(os.path.join(version_folder, 'package.json'))
    except FileNotFoundError as e:
        sys.stderr.write(f"No package.json file found at {version_folder}.\n")
        return

    author = package_json_data.get('author', '')
    if type(author) == list:
        if len(author) > 0:
            author = author[0]
        else:
            author = ''
    if type(author) == str:
        author_name = author
        author_email = author
        author_url = author
    else:
        author_name = author.get('name', None)
        author_email = author.get('email', None)
        author_url = author.get('url', None)
    pkg, new_pkg = mod.get_or_create(session, mod.Package, name=package_json_data['name'],
                                     # author_name=author_name,
                                     # author_email=author_email,
                                     # author_url=author_url
                                     )
    if new_pkg:
        pkg.author_name = author_name
        pkg.author_email = author_email
        pkg.author_url = author_url
        session.add(pkg)
    v = session.query(mod.Version).filter_by(number=package_json_data['version'], package=pkg).one_or_none()
    if not v:
        v = mod.Version(
            number=package_json_data['version'],
            disk_location=version_folder,
            package=pkg,
            package_json=package_json_data,
        )

        session.add(v)


def loop_with_glob(session, globstr, func):
    sample_folders = glob.glob(globstr)
    sample_folders = [x for x in sample_folders if 'active_survey' not in x and 'synth' not in x]
    if args.package_name:
        sample_folders = [s for s in sample_folders if args.package_name in s]
    with tqdm(total=len(sample_folders)) as pbar:
        for f in sample_folders:
            func(session, f)
            pbar.update()
    session.commit()


def record_package_versions(session, sample_folder: str):
    sample_glob = os.path.join(sample_folder, "*", "**-->*", "*/")
    loop_with_glob(session, sample_glob, record_package_version)


def find_or_create_package(session, name: str) -> mod.Package:
    pkg = session.query(mod.Package).filter_by(name=name).one_or_none()
    if pkg:
        return pkg
    pkg = mod.Package(name=name)
    session.add(pkg)
    return pkg


def find_or_create_version(session, package: int, number: str, folder: os.PathLike) -> mod.Version:
    v = session.query(mod.Version).filter_by(package_id=package, number=number).one_or_none()
    if v:
        return v
    json_path = Path(folder) / "package.json"
    if not json_path.exists():
        sys.stderr.write(f"WARNING: Version folder {folder} has no package.json file.\n")
        raise Exception(f"No package.json file in {folder}")
    with open(json_path) as json_fp:
        v = mod.Version(package_id=package, number=number, package_json=json.load(json_fp),
                        disk_location=str(folder))
    session.add(v)
    return v


def record_package_pair(session, op: str) -> Optional[mod.VersionPair]:
    folder_parts = os.path.split(op[0:-1])
    folder_name = folder_parts[1]
    try:
        package_name, before_v, after_v = extract_name_and_versions(folder_name)
    except:
        sys.stderr.write(f"Could not parse folder name, aborting package {op}.\n")
        return

    # Find or create versions
    # Find or create Pair
    pair: mod.VersionPair = session.query(mod.VersionPair).filter(
        mod.VersionPair.disk_location.in_([op.rstrip(os.path.sep),op,str(Path(op))] )).one_or_none()
    if pair:
        return pair
    if args.no_new_vps:
        raise Exception(f"No versionpair found for {op}!")
    pkg = find_or_create_package(session, package_name)
    try:
        if not pkg:
            # sys.stderr.write(f"No package found with name {package_name}.\n")
            raise Exception(f"No package found with name {package_name}.")
        if not pkg.id:
            session.flush()
        if not pkg.id:
            # sys.stderr.write(f"Null id for pkg with name {package_name}.\n")
            raise Exception(f"Null id for pkg with name {package_name}.")
        before = find_or_create_version(session, package=pkg.id, number=before_v,
                                        folder=(Path(op) / f"{package_name}-{before_v}"))
        after = find_or_create_version(session, package=pkg.id, number=after_v,
                                       folder=(Path(op) / f"{package_name}-{after_v}"))
    except Exception as e:
        sys.stderr.write(f"record_package_pair: Aborting package {op}. Cause: {e}.\n")
        return

    folder_parts, group = os.path.split(folder_parts[0])
    g = group.lower()
    if "benign" in g:
        label = "BEN"
    elif "synth" in g:
        label = "SYNTH"
    elif "survey" in g:
        label = "UNK"
    elif "stab" in g:
        label = "MAL"
    else:
        label = "OTHER"
    diff_json = b"[]"
    pair = mod.VersionPair(
        before=before,
        after=after,
        disk_location=op.rstrip(os.path.sep),
        label=label,
        group=group,
        diff_json=diff_json,
    )

    session.add(pair)
    return pair


def create_diff_json(version_pair: mod.VersionPair):
    before = version_pair.before
    after = version_pair.after
    if not before or not after:
        sys.stderr.write(f"Somehow {version_pair.id} does not have a before or an after version.\n")
        version_pair.diff_json = b"[]"
        return
    package_name = version_pair.before.package.name

    try:
        diff_cmd = [
            "diff", "-r", "-u", "--unidirectional-new-file",
            "--exclude=*.log", "--exclude=*.gexf", "--exclude=odgen*.json", "--exclude=fast*.json", "--exclude=*.csv",
            "--exclude=*.tsv", "--exclude=*.ndjson",
            before.disk_location,
            after.disk_location,
            # f"'{before.disk_location}'",
            # f"'{after.disk_location}'",
        ]
        diff_output_processing_command = [
            "node", d2h_js_path,
        ]
        diff_p = subprocess.Popen(diff_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        diff_processor_p = subprocess.Popen(diff_output_processing_command, stdin=diff_p.stdout, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        # diff_string = diff_p.stdout.read()
        # diff_processor_p.stdin.write(diff_string)

        diff_json = diff_processor_p.communicate()[0]
        # diff_json = subprocess.check_output(f"diff -r -u --unidirectional-new-file --exclude='.log' --exclude='*.gexf' --exclude='odgen*.json' --exclude='fast*.json' {before.disk_location} {after.disk_location} | npx diff2html --input=stdin -o stdout -f json", shell=True)
    except Exception as e:
        sys.stderr.write(f"Failed to build diff json for {package_name}, {version_pair.disk_location}\n")
        diff_json = b"[]"
    version_pair.diff_json = diff_json[0:1000000]


def record_package_pairs(session, sample_folder: str):
    sample_glob = os.path.join(sample_folder, "**", "*-->*/")
    loop_with_glob(session, sample_glob, record_package_pair)


def null_if_blank(s):
    if s == '':
        return None
    return s


def record_rogue_one_result(session, op):
    folder = os.path.dirname(op)
    try:
        with open(op) as f:
            pair_data = json.load(f)
    except FileNotFoundError as e:
        sys.stderr.write(f"No Rogue One results found at {folder}.\n")
        return
    except json.decoder.JSONDecodeError as e:
        sys.stderr.write(f"Invalid JSON at {folder}: {e}.\n")
        return
    record_ror_with_json(session, op, pair_data)


def record_ror_with_json(session, op, pair_data) -> bool:
    folder = os.path.dirname(op)
    try:
        pair = session.query(mod.VersionPair).filter_by(disk_location=folder).one()
    except sqlalchemy.exc.NoResultFound:
        sys.stderr.write(f"No VersionPair record for {folder}.\n")
        return False
    return record_ror_with_json_and_pair(session, op, pair_data, pair)


def record_ror_with_json_and_pair(session, op, pair_data, pair) -> bool:

    ts = pair_data['run_timestamp']
    if type(ts) in [int, float]:
        dt = datetime.fromtimestamp(ts)
    else:
        dt = datetime.fromisoformat(ts)
    check = session.query(mod.RogueOneResult).filter_by(
        disk_location=op,
        run_timestamp=dt,
    ).one_or_none()
    if check:
        return False

    result_size = os.stat(op).st_size  # Size in bytes of json result
    if result_size > 300000000:
        pair_data['before_path_list'] = []
        pair_data['after_path_list'] = []
        pair_data['system_extra_info'] = {}
        pair_data['before_node_attrs'] = {}
        pair_data['after_node_attrs'] = {}

    ror = mod.RogueOneResult(
        version_pair=pair,
        disk_location=op,
        json_result=pair_data,
        error=pair_data.get('error'),
        suspicious=null_if_blank(pair_data.get('suspicious', None)),
        analysis_length=pair_data.get('update_processing_time', None),
        run_timestamp=dt,
        before_weakly_connected_components=null_if_blank(pair_data['before'].get('weakly_connected_components', None)),
        after_weakly_connected_components=null_if_blank(pair_data['after'].get('weakly_connected_components', None)),
        sinks_added=pair_data.get('sinks_added', None),
        sinks_removed=pair_data.get('sinks_removed', None),
        sinks_changed=pair_data.get('sinks_changed', None),
    )
    # create_diff_json(pair)
    session.add(ror)
    return True


def update_task_model(task: mod.TaskModel, result):  # Handle possible exceptions?

    if result['error'] == 'OK':
        task.set_state(mod.State.CompletedSuccess)
    else:
        task.set_state(mod.State.CompletedError)

    ts = result['run_timestamp']
    if type(ts) in [int, float]:
        dt = datetime.fromtimestamp(ts)
    else:
        dt = datetime.fromisoformat(ts)
    result_size = os.stat(f"{task.disk_location}/rogue_one_output.json").st_size
    if result_size > 300000000:  # Shouldn't happen..?
        pass
    task.json_result = result
    task.error = result.get("error")
    task.run_timestamp = dt
    task.analysis_length = result.get("running_time", 0)


def update_version_pair_task_model(task: mod.VersionPairTaskModel, disk_location, result):  # Handle possible exceptions?
    if result is None:
        task.set_state(mod.State.CompletedError)
        task.error = 'no_result_data'
        return
    if result['error'] == 'OK':
        task.set_state(mod.State.CompletedSuccess)
    else:
        task.set_state(mod.State.CompletedError)

    result_size = os.stat(f"{disk_location}/rogue_one_output.json").st_size
    if result_size > 300000000:  # Shouldn't happen..?
        pass
    task.json_result = result
    task.error = result.get("error")
    before_result = result.get("before", [])
    after_result = result.get("after", [])
    task.analysis_length = before_result.get("running_time", 0) + after_result.get("running_time", 0)


def time_out_version(task: mod.VersionPairTaskModel, result):
    task.set_state(mod.State.TimedOut)
    task.error = "timed_out"
    if result is not None:
        result['error'] = 'timed_out'
        task.json_result = result



def record_rogue_one_results(session, sample_folder: str):
    sample_glob = os.path.join(sample_folder, "**", "*-->*", "rogue_one_output.json")
    loop_with_glob(session, sample_glob, record_rogue_one_result)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Runner for mass parallel analysis.")
    ap.add_argument("--sample_folder", action="store", help="A folder containing folders of datasets, each of which has \
    folders of before/after update pairs.  e.g. given Samples/30_backstabber_samples/pack_0.1-->pack_0.2/pack_0.1/ as a\
     sample, the argument should be just Samples, so that the samples are captured by **/**/*/", required=False)
    ap.add_argument("--test", action="store_true", help="Force analysis to target the dataflow_tests directory")
    ap.add_argument("--timeouts", action="store_true", default=False)
    ap.add_argument("--redo", action="store_true", default=False)
    ap.add_argument("--reset", action="store_true", default=False)
    ap.add_argument("--db", action="store", default=False, required=False)
    ap.add_argument("--package_name", action="store", required=False)
    ap.add_argument("--no_new_vps", action="store_true", default=False)

    args = ap.parse_args()

    if args.db:
        try:
            with open(args.db) as f:
                db = json.load(f)
        except FileNotFoundError as e:
            sys.stderr.write(f"No db config file found at {args.db}.\n")
            sys.exit(1)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Could not load json db config file at {args.db}.\n")
            sys.exit(1)
        db_uri = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"
        engine, Session = engine.init(db_uri, echo=False)
    else:
        engine, Session = engine.init()
    sess = Session()

    if args.reset:
        sys.stderr.write("Resetting database.\n")
        # sess.execute(sqlalchemy.text("DROP TABLE odgenresult CASCADE"))
        sess.commit()
        for md in [mod.Version, mod.Package, mod.RogueOneResult]:
            md.metadata.drop_all(sess.bind)

        for md in [mod.Version, mod.Package, mod.RogueOneResult]:
            md.metadata.create_all(sess.bind)
        sys.stderr.write("DB is reset.\n")
        sys.exit(0)
    record_package_pairs(sess, args.sample_folder)
    record_rogue_one_results(sess, args.sample_folder)

    print("Counts:")
    mods = [mod.Package, mod.Version, mod.VersionPair, mod.RogueOneResult]
    counts = list(map(lambda x: (x, sess.query(x).count()), mods))

    for c in counts:
        print(f"\t{c[0].__name__}: {c[1]}")
    pass

    #                                             group  package  version
