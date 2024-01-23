import datetime
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Optional

import fast.manager.models as mod
from extract_samples import check_extract_dir, check_extract_single_version
from fast.manager.package_changes import extract_name_and_versions
import celery
d2h_js_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                            'fast/esprima-csv/diff2json.js'))

LOG_LOCATION = "/srv/rogueone/RogueOneProcessing"
#LOG_LOCATION = "/Users/mlou/Classes/Projects/RogueOne-Data/Logs"


def find_or_create_version(session, package: int, number: str, folder: os.PathLike) -> mod.Version:
    v = session.query(mod.Version).filter_by(package_id=package, number=number).one_or_none()
    if v:
        return v
    return create_version(session, package, number, folder)


def create_version(session, package, number: str, folder: os.PathLike) -> mod.Version:
    json_path = Path(folder) / "package.json"
    if not json_path.exists():
        raise Exception(f"No package.json file in {folder}")
    with open(json_path) as json_fp:
        v = mod.Version(package_id=package, number=number, package_json=json.load(json_fp),
                        disk_location=str(folder))
    session.add(v)
    return v


def find_new_packages(session, folder: Path, func) -> [int]:
    package_paths = [x for x in folder.glob("*") if x.is_dir()]
    new_packages = []
    for path in package_paths:
        created, version_pair_id = func(session, path)
        if created:
            new_packages.append(version_pair_id)
            session.commit()
    return new_packages


def create_version_task(session, version_id, timeout, log_location=LOG_LOCATION) -> (bool, Optional[int]):
    version = session.query(mod.Version).filter_by(id=version_id).one_or_none()
    if not version:
        sys.stderr.write(f"Could not find version with provided id '{version_id}'. Aborting.\n")
        return False, None

    if not Path(log_location).exists():
        Path(log_location).mkdir()
    disk_loc = generate_disk_location(version, log_location)
    task = mod.TaskModel(
        state=mod.State.NotStarted,
        last_state_transition=datetime.datetime.now(),
        version_id=version_id,
        timeout=timeout,
        run_timestamp=datetime.datetime.fromtimestamp(0),  # Check if better way
        disk_location=disk_loc,
        json_result=b'[]',
        num_retries=0
    )
    session.add(task)
    if not task.id:
        session.flush()
    return True, task.id


def create_version_pair_task(session, version_pair_id, timeout) -> (bool, Optional[int]):
    version = session.query(mod.VersionPair).filter_by(id=version_pair_id).one_or_none()
    if not version:
        sys.stderr.write(f"Could not find version pair with provided id '{version_pair_id}'. Aborting.\n")
        return False, None

    task = mod.VersionPairTaskModel(
        state=mod.State.NotStarted,
        last_state_transition=datetime.datetime.now(),
        version_id=version_pair_id,
        timeout=timeout,
        run_timestamp=datetime.datetime.fromtimestamp(0),  # Check if better way
        json_result=b'[]',
        num_retries=0
    )
    session.add(task)
    if not task.id:
        session.flush()
    return True, task.id


def renew_task(session, task: mod.TaskModel, log_location):
    if not Path(log_location).exists():
        Path(log_location).mkdir()
    disk_loc = generate_disk_location(version=task.version, log_location=log_location)
    new_task = mod.TaskModel(
        state=mod.State.NotStarted,
        last_state_transition=datetime.datetime.now(),
        version_id=task.version_id,
        timeout=task.timeout,
        run_timestamp=datetime.datetime.fromtimestamp(0),  # Check if better way
        disk_location=disk_loc,
        json_result=b'[]',
        num_retries=task.num_retries + 1
    )
    session.add(new_task)
    if not new_task.id:
        session.flush()
    return new_task.id


def generate_disk_location(version, log_location) -> str:
    package = version.package.name
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y%j')
    while True:
        random = str(uuid.uuid4())[:8]
        temp = f"{log_location}/{package.replace('/', '@')}_{version.number}_{timestamp}_{random}"
        if not Path(temp).exists():
            Path(temp).mkdir()
            return temp

def find_or_create_version_pair(session, folder_path: Path, include_ignored=False) -> (bool, int):
    """

    Args:
        session: session object
        folder_path: path to package being checked

    Returns:
        tuple of (bool, str), where bool indicates whether a new version pair was created
        and int returns the id of the new version pair created, if applicable
    """
    try:
        name, before_version, after_version = extract_name_and_versions(folder_path.name)
    except:
        sys.stderr.write(f"find_or_create_version_pair: Could not parse folder name, aborting package {folder_path.name}.\n")
        return False, -1
    full_path = str(folder_path.resolve())
    skip_path = Path(full_path) / "DONOTANALYZE"
    if skip_path.exists():
        return False, -1
    cleaned_location = full_path.rstrip(os.path.sep)
    pair: mod.VersionPair = session.query(mod.VersionPair).filter_by(disk_location=cleaned_location).one_or_none()
    if pair:
        if pair.ignore:
            return False, -1
        else:
            return False, pair.id
    pkg = session.query(mod.Package).filter_by(name=name).one_or_none()
    create_package = pkg is None
    if create_package:
        pkg = mod.Package(name=name)
        session.add(pkg)
    if not pkg.id:
        session.flush()
    if not pkg.id:
        sys.stderr.write(f"find_or_create_version_pair: Could not add package {name} to database. Aborting.\n")
        session.rollback()
        return False, -1
    check_extract_dir(folder_path)
    try:
        # This requires there to be a package.json in the folder.
        before = find_or_create_version(session, package=pkg.id, number=before_version,
                                        folder=(Path(full_path) / f"{name}-{before_version}"))
        after = find_or_create_version(session, package=pkg.id, number=after_version,
                                       folder=(Path(full_path) / f"{name}-{after_version}"))
        # Should I populate package information?
        if create_package:
            author = before.package_json.get('author', '')
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
            pkg.author_url = author_url
            pkg.author_name = author_name
            pkg.author_email = author_email
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        sys.stderr.write(f"find_or_create_version_pair: Aborting package {folder_path.name}. Cause: {e}.\n")
        skip_path.touch()
        return False, -1

    group = folder_path.parent.name
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

    try:  # Taken from find_for_manager
        diff_cmd = [
            "diff", "-r", "-u", "--unidirectional-new-file",
            "--exclude=*.log", "--exclude=*.gexf", "--exclude=odgen*.json", "--exclude=fast*.json", "--exclude=*.csv",
            "--exclude=*.tsv", "--exclude=*.ndjson",
            before.disk_location,
            after.disk_location
        ]
        diff_output_processing_command = [
            "node", d2h_js_path,
        ]
        diff_p = subprocess.Popen(diff_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        diff_processor_p = subprocess.Popen(diff_output_processing_command, stdin=diff_p.stdout, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        diff_json = diff_processor_p.communicate()[0]
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        sys.stderr.write(f"Failed to build diff json for {name}, {folder_path.name}\n")
        diff_json = b"[]"

    pair = mod.VersionPair(
        before=before,
        after=after,
        disk_location=cleaned_location,
        label=label,
        group=group,
        diff_json=diff_json
    )
    session.add(pair)
    if not pair.id:
        session.flush()
    if not pair.id:
        sys.stderr.write(f"Could not add version pair {name} to database. Aborting.\n")
        session.rollback()
        return False, -1
    return True, pair.id


def find_or_create_single_version(session, folder_path: Path) -> (bool, int):
    """

    Args:
        session: session object
        folder_path: path to package being checked

    Returns:
        tuple of (bool, str), where bool indicates whether a new version pair was created
        and int returns the id of the new version pair created, if applicable
    """
    try:
        name, version = extract_package_and_single_version(folder_path.name)
    except:
        sys.stderr.write(f"find_or_create_single_version: Could not parse folder name, aborting package {folder_path.name}.\n")
        return False, -1
    full_path = str(folder_path.resolve())
    cleaned_location = full_path.rstrip(os.path.sep)
    pkg = session.query(mod.Package).filter_by(name=name).one_or_none()
    create_package = pkg is None
    if create_package:
        pkg = mod.Package(name=name)
        session.add(pkg)
    if not pkg.id:
        session.flush()
    if not pkg.id:
        sys.stderr.write(f"find_or_create_single_version: Could not add package {name} to database. Aborting.\n")
        session.rollback()
        return False, -1

    v = session.query(mod.Version).filter_by(package_id=pkg.id, number=version,
                                             disk_location=str(Path(cleaned_location) / "package")).one_or_none()
    if v:
        return False, v.id

    if not check_extract_single_version(folder_path):
        sys.stderr.write(f"find_or_create_single_version: Could not extract version '{folder_path}'.\n")
    try:
        # This requires there to be a package.json in the folder.
        v = create_version(session, package=pkg.id, number=version, folder=(Path(cleaned_location) / "package"))
        # Should I populate package information?
        if create_package:
            author = v.package_json.get('author', '')
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
            pkg.author_url = author_url
            pkg.author_name = author_name
            pkg.author_email = author_email
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        sys.stderr.write(f"find_or_create_single_version: Aborting package {folder_path.name}. Cause: {e}.\n")
        session.rollback()
        return False, -1

    if not v.id:
        session.flush()
    if not v.id:
        sys.stderr.write(f"find_or_create_single_version: Could not add version {name} to database. Aborting.\n")
        session.rollback()
        return False, -1
    return True, v.id


def extract_package_and_single_version(s: str) -> (str, str):
    return tuple(s.rsplit("@", 1))
