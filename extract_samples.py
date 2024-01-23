import os
import shutil
import sys
from pathlib import Path

import fast.manager.package_manager
from rogue_one_runner import extract_name_and_versions
import tarfile
import celery
ACTIVE_SURVEY = "/srv/rogueone/RogueOneSamples/active_survey/"
# ACTIVE_SURVEY = "/Users/mlou/Classes/Projects/RogueOne-Data/active_survey"
PATH_TO_SURVEY = Path(ACTIVE_SURVEY)
count = 0


def is_correct_format(dir: Path):
    name = dir.name
    package_name, before_version, after_version = extract_name_and_versions(name)
    before_folder = dir / (package_name + '-' + before_version)
    after_folder = dir / (package_name + '-' + after_version)

    before_zip = dir / (package_name + '@' + before_version + ".tgz")
    after_zip = dir / (package_name + '@' + after_version + ".tgz")
    if not before_zip.exists() or not after_zip.exists():
        return False, "No zip file"

    if before_folder.exists() and after_folder.exists():
        json_file = before_folder / "package.json"
        if not json_file.exists():
            return False, "No package json"
        json_file = after_folder / "package.json"
        if not json_file.exists():
            return False, "No package json"
    else:
        return False, "No extracted folder"

    return True, None

def extract_file(zip_folder, dir, folder, rename=True):
    try:
        file = tarfile.open(zip_folder)
        file.extractall(path=dir)
        file.close()
        if rename:
            os.rename(dir / "package", folder)
    except ValueError as e:
        sys.stderr.write(f"Caught Value Error {e} for package '{dir.name}'\n")
    except tarfile.TarError as e:
        sys.stderr.write(f"Caught Tar Error {e} while extracting tar file for '{dir.name}'.\n")
    except OSError as e:
        sys.stderr.write(
            f"Error when renaming {e.filename} to {folder.name}: {e.strerror}.\n")  # Prints an error if package exists

def extract_dir(dir: Path):
    package_name, before_version, after_version = extract_name_and_versions(dir.name)

    before_folder = dir / (package_name + '-' + before_version)
    after_folder = dir / (package_name + '-' + after_version)
    before_zip = dir / (package_name + '@' + before_version + ".tgz")
    after_zip = dir / (package_name + '@' + after_version + ".tgz")

    extract_file(before_zip, dir, before_folder)
    extract_file(after_zip, dir, after_folder)


def delete_folders(dir: Path):
    for file in dir.glob("*"):
        if file.is_dir():
            # Could be modified
            json = file / "package.json"
            if not json.exists():
                try:
                    # sys.stderr.write(f"Deleting folder {file}.\n")
                    shutil.rmtree(file)
                except OSError as e:
                    sys.stderr.write(f"Error when deleting {e.filename}: {e.strerror}.\n")


def check_extract_dir(dir: Path):
    try:
        success, error = is_correct_format(dir)
        if success:
            return
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        sys.stderr.write(f"Error in format check of folder {dir}: {e}\n")
        return

    name = dir.name

    if error == "No zip file":
        sys.stderr.write(f"Missing one or more zip files. Skipping '{name}' package.\n")
        return

    # Delete all incorrect folders and then recreate and extract files
    try:
        delete_folders(dir)
        extract_dir(dir)
        success, error = is_correct_format(dir)
        if not success:
            sys.stderr.write(f"Could not extract folder contents: {error}\n")
            return
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        sys.stderr.write(f"Error in extraction of folder {dir}: {e}\n")
        return

    sys.stdout.write(f"Successfully unpacked package {name}.\n")
    # global count
    # count += 1


def is_version_in_correct_format(folder: Path):
    name = folder.name
    package_name, version = fast.manager.package_manager.extract_package_and_single_version(name)
    package_folder = folder / "package"

    zip_file = folder / (package_name + '-' + version + ".tgz")
    if not zip_file.exists():
        return False, "No zip file"

    if package_folder.exists():
        json_file = package_folder / "package.json"
        if not json_file.exists():
            return False, "No package json"

    else:
        return False, "No extracted folder"

    return True, None


def extract_zip_file(zip_folder, folder):
    try:
        file = tarfile.open(zip_folder)
        file.extractall(path=folder)
        file.close()
    except ValueError as e:
        sys.stderr.write(f"Caught Value Error {e} for package '{folder.name}'\n")
        raise e
    except tarfile.TarError as e:
        sys.stderr.write(f"Caught Tar Error {e} while extracting tar file for '{folder.name}'.\n")
        raise e


def check_extract_single_version(folder: Path) -> bool:
    """

    Args:
        folder:

    Returns: true if successfully extracted, false if exception occurred

    """

    try:
        success, error = is_version_in_correct_format(folder)
        if success:
            return True
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        sys.stderr.write(f"Error in format check of folder {folder}: {e}\n")
        return False
    name = folder.name

    if error == "No zip file":
        sys.stderr.write(f"Missing one or more zip files. Skipping '{name}' package.\n")
        return False

    try:
        package_name, version = fast.manager.package_manager.extract_package_and_single_version(name)
        zip_folder = folder / (package_name + '-' + version + ".tgz")
        extract_zip_file(zip_folder, folder)
        success, error = is_version_in_correct_format(folder)
        if not success:
            sys.stderr.write(f"Could not extract folder contents: {error}\n")
        return success
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        sys.stderr.write(f"Error in extraction of folder {folder}: {e}\n")
        return False


if __name__ == "__main__":
    dirs = [x for x in PATH_TO_SURVEY.glob("*") if x.is_dir()]
    sys.stdout.write(f"Found {len(dirs)} total packages.\n")
    sys.stdout.flush()
    # Concurrent Implementation?
    [check_extract_dir(d) for d in dirs]
    sys.stdout.write(f"Unpacked {count} packages out of {len(dirs)} total packages.\n")
