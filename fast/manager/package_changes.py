import filecmp
import json
import os
import sys
import typing
from pathlib import Path

test_modules = ['mocha']


def processCmd(cmd):
    global test_modules
    wholeCmd = cmd.replace("\\", "")
    wholeCmd = wholeCmd.replace("\n", " ")
    wholeCmd = wholeCmd.split(" ")
    wholeCmd = [i.strip() for i in wholeCmd]
    wholeCmd = [i for i in wholeCmd if i != ""]

    i = 0
    testFiles = 'test/'
    while i in range(0, len(wholeCmd)):
        for j in test_modules:
            if j in wholeCmd[i]:
                i = i + 1
                break
        if wholeCmd[i].startswith("NODE_ENV"):
            i = i + 1
            continue
        elif wholeCmd[i].startswith('--'):
            i = i + 2
            continue
        if i < len(wholeCmd):
            testFiles = wholeCmd[i]
            break
    return testFiles


def exclude_test(pkgpath):
    global test_modules
    exclude_dir = ''
    jsonfile = os.path.join(pkgpath, "package.json")
    Makefile = os.path.join(pkgpath, "Makefile")

    with open(jsonfile) as f:
        jsonContent = json.load(f)

    testDir = ''
    if 'scripts' in jsonContent:
        for command in jsonContent['scripts']:
            # print("command:", command)
            if command == 'test':
                commandContent = jsonContent['scripts'][command]
                for j in test_modules:
                    if j in commandContent:
                        # print("===test modules used:===")
                        # print(commandContent)
                        testDir = processCmd(commandContent)  # the default dir for mocha
                        # print("===test dir we should ignore:===")
                        # print(testDir)
                        exclude_dir = testDir
                if 'make' in commandContent:
                    # print(commandContent)
                    shellCmd = commandContent.split("make")[1].strip()
                    with open(Makefile) as f:
                        makefile = f.read()
                    if shellCmd + ':' in makefile:
                        # print(shellCmd,"found in makefile")
                        # print(commandContent)
                        os.chdir(pkgpath)
                        os.system(commandContent + ' --just-print > exclude_command.txt')
                        with open("exclude_command.txt") as f:
                            wholeCmd = f.read()
                        # print(wholeCmd)
                        # print("===test modules used:===")
                        # print(wholeCmd)
                        testFiles = processCmd(wholeCmd)
                        # print("===test dir we should ignore:===")
                        # print(testFiles)
                        exclude_dir = testFiles
    return exclude_dir


def get_package_data(f: str) -> dict:
    try:
        p = Path(f)
        fn = p / "package.json"
        with open(fn) as f:
            data = json.load(f)
            return data
    except:
        sys.stderr.write(f"Could not read package json for {f}.\n")
        return {}


def build_package_json_changes(before_folder, after_folder) -> dict[str, str]:
    # Get changes in pre and post install scripts and include them.
    before_data, after_data = [get_package_data(f) for f in (before_folder, after_folder)]
    before_scripts = before_data.get('scripts', {})
    if not (before_scripts and type(before_scripts) == type({})):
        before_scripts = {}
    after_scripts = after_data.get('scripts', {})
    if not (after_scripts and type(after_scripts) == type({})):
        after_scripts = {}
    result = {}
    for script_name in ['preinstall', 'install', 'postinstall']:
        if script_name in after_scripts:
            if script_name not in before_scripts or str(after_scripts[script_name]) != str(before_scripts[script_name]):
                result[script_name] = str(after_scripts[script_name])
    return result


def dircmp_closure(diff):
    result = ([], [], [])
    for d in diff.subdirs.values():
        res = dircmp_closure(d)
        root = os.path.relpath(d.left, diff.left)
        for i in [0, 1, 2]:
            result[i].extend([os.path.join(root, p) for p in res[i]])
    result[0].extend(diff.left_only)
    result[1].extend(diff.diff_files)
    result[2].extend(diff.right_only)
    return result


# Return a list of file names of javascript files relative to the package root which have changed and
# are either accessible in the tree of requires or are frontend files.
def build_changed_file_list(before_folder, after_folder) -> typing.Iterable[str]:
    diff = filecmp.dircmp(before_folder, after_folder)
    _, diff_files, right_only = dircmp_closure(diff)
    # set of js files in diff.right_only + js files in dict.diff_files
    changed_js_files = set()
    changed_js_files = changed_js_files.union([a for a in diff_files if a.endswith('.js') or a.endswith('.mjs')])
    changed_js_files = changed_js_files.union([a for a in right_only if a.endswith('.js') or a.endswith('.mjs')])

    # TODO: Make this work better
    changed_js_files = set([a for a in changed_js_files if 'test/' not in a])
    return changed_js_files


if __name__ == '__main__':
    # pkgpath = "/Users/susie/Documents/projects/columbia/RogueOneSamples_2/RandomBenignSamples2/proxy_1.0.1-->1.0.2/proxy-1.0.2"
    # pkgpath = '/Users/susie/Documents/projects/columbia/RogueOneSamples_2/RandomBenignSamples2/box_0.0.3-->0.0.4/box-0.0.4'
    pkgpath = '/Users/susie/Documents/projects/columbia/RogueOneSamples_2/RandomBenignSamples2/fed_0.1.2-->0.1.3/fed-0.1.3'
    res = exclude_test(pkgpath)
    print(res)


def extract_name_and_versions(s: str) -> tuple[str, str, str]:
    sep = "-->"
    sep_idx = s.index(sep)
    after_version = s[sep_idx + len(sep):]
    name_and_before = s[0:sep_idx]
    before_version = name_and_before[name_and_before.rindex("_") + 1:]
    name = name_and_before[0:name_and_before.rindex("_")]
    return name, before_version, after_version


def create_registry_url(s: str) -> str:
    if "@" not in s:
        return s
    sep_idx = s.index("@")
    if sep_idx == 0:
        s = s[1:]
        if "@" not in s:
            return f"@{s}"
        sep_idx = s.index("@")
    pre = s[:sep_idx]
    post = s[sep_idx + 1:]
    return f"@{pre}/{post}"
