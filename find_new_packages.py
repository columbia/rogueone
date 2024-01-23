import json
import multiprocessing
import os
import sys
import glob
import xml.etree.cElementTree as ET
import filecmp

from tqdm import tqdm

sample_folder = sys.argv[1]

data_file_name = "fast_package_results.json"
gexf_name = "relevant_subgraph.gexf"
pkg_folder_base = os.path.join(sample_folder, "**", "**", data_file_name)
package_folders = glob.glob(pkg_folder_base)

def find_new_packages(results_file: str):
    try:
        with open(results_file) as f:
            ro_data = json.load(f)
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        return set()

    if 'before_version' not in ro_data or 'after_version' not in ro_data:
        return set()
    bv = ro_data['before_version']
    av = ro_data['after_version']
    package_name = ro_data['package_name']
    package_folder = os.path.dirname(results_file)

    before_folder, after_folder = [os.path.join(package_folder, f"{package_name}-{v}", "package.json") for v in [bv, av]]
    try:
        with open(before_folder) as f:
            before_pack_data = json.load(f)
        with open(after_folder) as f:
            after_pack_data = json.load(f)
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        return set()

    after_deps = set(after_pack_data.get('devDependencies', {}).keys()).union(set(after_pack_data.get('dependencies', {}).keys()))
    before_deps = set(before_pack_data.get('devDependencies', {}).keys()).union(set(before_pack_data.get('dependencies', {}).keys()))

    new_deps = after_deps.difference(before_deps)
    if len(new_deps) > 0:
        print(f"Found new deps for package {package_name}: ", new_deps)
    return new_deps


def process_package(results_file):
    changed_files = find_new_packages(results_file)
    changed_file_name = os.path.join(os.path.dirname(results_file), "rogue_one_new_packages.txt")
    with open(changed_file_name, 'w') as f:
        for l in changed_files:
            f.write(f"{l}\n")

with multiprocessing.Pool(int(multiprocessing.cpu_count() * 0.6)) as p:
    with tqdm(total=len(package_folders)) as pbar:
        for a in p.imap_unordered(process_package, package_folders):
            pbar.update(1)
        p.close()
        p.join()
            #if 'lodash' in folder:
            #    continue
