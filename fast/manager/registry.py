import subprocess
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import json

import requests
import sqlalchemy

import fast.manager.models as mod
from fast.manager.package_changes import extract_name_and_versions, create_registry_url


def update_version_downloads(session, pkg, version: str, downloads: int):
    try:
        v = session.query(mod.Version).filter_by(number=version, package=pkg).one_or_none()
        if not v:
            v = mod.Version(
                number=version,
                package=pkg
            )
        v.downloads = downloads
        session.add(v)
    except sqlalchemy.exc.SQLAlchemyError as exception:
        sys.stderr.write(f"SQL Error occurred '{exception}' for package '{pkg.name}'\n")
        return



def fetch_version_downloads(session, package_name, pkg):
    if package_name[0] == '@':
        package_name = package_name[1:]
    percent_enc = quote(package_name, safe='@/')
    url = f"https://api.npmjs.org/versions/{percent_enc}/last-week"
    print(url)
    response = requests.get(url)
    if response.status_code != 200:
        sys.stderr.write(f"{url} returned response code {response.status_code} for package '{package_name}'.\n")
        return
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        sys.stderr.write(f"Caught {e} for package '{package_name}'.\n")
        return
    if "downloads" not in data:
        sys.stderr.write(f"No downloads JSON found for package '{package_name}'?\n")
        return
    for k, v in data["downloads"].items():
        update_version_downloads(session, pkg, k, int(v))
    session.commit()


def update_version_time(session, pkg, version: str, time: str):
    ts = datetime.fromisoformat(time[:-1])
    try:
        v = session.query(mod.Version).filter_by(number=version, package=pkg).one_or_none()
        if not v:
            v = mod.Version(
                number=version,
                package=pkg
            )
        v.uploaded_at = ts
        session.add(v)
    except sqlalchemy.exc.SQLAlchemyError as exception:
        sys.stderr.write(f"SQL Error occurred '{exception}' for package '{pkg.name}'\n")
        return


def fetch_npm_registry_with_path(session, path: Path):
    name = path.name
    try:
        package_name, _, _ = extract_name_and_versions(name)
    except ValueError as e:
        sys.stderr.write(f"Invalid folder name: {name}, aborting.\n")
        return
    fetch_npm_registry(session, package_name)


def fetch_npm_registry(session, package_name, pkg=None, get_downloads=False, n=False):
    if not pkg:
        pkg, _ = mod.get_or_create(session, mod.Package, name=package_name)
    if pkg.description and (pkg.versions and ((not get_downloads and pkg.versions[0].uploaded_at) or pkg.versions[0].downloads is not None)):
        return
    url_name = create_registry_url(package_name)
    url = f"https://registry.npmjs.com/{url_name}"
    response = requests.get(url)
    if response.status_code != 200:
        sys.stderr.write(f"{url} returned response code {response.status_code} for package '{package_name}'.\n")
        sys.stderr.write(f"{response}\n")
        return
    try:
        data = response.json()
        if "versions" not in data:
            sys.stderr.write(f"No versions JSON found for package '{package_name}'?\n")
            return

        versions = data["versions"]
        marking = False
        for k in versions:
            if "-security" in k:
                marking = True
                break

        # if not marking:
        #    # sys.stdout.write(f"Checked '{package_name}' and did not find security flag.\n")
        #    return
        # sys.stdout.write(f"Caught security flag for '{package_name}'.\n")

        if "time" not in data or "description" not in data:
            sys.stderr.write(f"No timestamp/description JSON found for flagged package '{package_name}'?\n")
            return

        pkg.description = data['description'][:1000].replace('\x00', '')
        session.add(pkg)
        for k, v in data['time'].items():
            if k == "created" or k == "modified":
                continue
            update_version_time(session, pkg, k, v)

        if get_downloads:
            fetch_version_downloads(session, package_name, pkg)

        if not n or n % 100 == 0:
            session.commit()
    except requests.exceptions.JSONDecodeError as e:
        sys.stderr.write(f"Caught {e} for package '{package_name}'.\n")
        return

nrl_js_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                            '../esprima-csv/remotels.js'))

def fetch_version_dependencies(package_name: str, version_number: str, package_json_path=''):
    if not Path(package_json_path).exists():
        package_json_path = ''
    nrl_cmd = [
        "node", nrl_js_path, package_name, version_number, package_json_path
    ]
    nrl_p = subprocess.run(nrl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    nrl_json = nrl_p.stdout
    try:
        return json.loads(nrl_json)
    except json.decoder.JSONDecodeError as e:
        try:
            return json.loads(nrl_json.split()[-1])
        except:
            if nrl_json.startswith(b"could not find a satisfactory version for string undefined"):
                sys.stderr.write(f"Package {package_name}@{version_number} not present on registry.\n")
                raise e


def fetch_tarball_url(package_name: str, version_number: str):
    if package_name.startswith("@") and "@" in package_name[1:]:
        package_name = create_registry_url(package_name[1:])
    cmd = ["npm", "view", f"{package_name}@{version_number}", "dist.tarball"]
    p = subprocess.run(cmd, capture_output=True)
    url = p.stdout.strip()
    return url
