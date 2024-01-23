import json
import multiprocessing
import os
import sys
import glob
import typing
import xml.etree.cElementTree as ET
import filecmp

import celery.exceptions
from tqdm import tqdm

sample_folder = sys.argv[1]

data_file_name = "fast_package_results.json"
gexf_name = "relevant_subgraph.gexf"
pkg_folder_base = os.path.join(sample_folder, "**", "**", data_file_name)
package_folders = glob.glob(pkg_folder_base)

def find_changed_files(pkg_json_file: str):
    try:
        with open(pkg_json_file) as f:
            ro_data = json.load(f)
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        return set()

    # Get the list of files which were processed. Maybe from the gexf?
    try:
        past_additional_files = set()
        for key in ['before_', 'after_']:
            output_file = os.path.join(ro_data['package_folder'],
                                              ro_data['package_name'] + '-' + ro_data[key+'version'],
                                              'fast_output.json')
            with open(output_file) as f:
                s = f.readlines()[-1]
                data = json.loads(s)
            past_additional_files.update(data.get('additional_files',[]))
    except celery.exceptions.SoftTimeLimitExceeded as e:
        raise e
    except Exception as e:
        past_additional_files = set()
    fn_dict = {}
    for v in ['before', 'after']:
        v_num = ro_data.get(v + '_version', None)
        if not v_num:
            return set()

        gexf_file = os.path.join(ro_data['package_folder'], ro_data['package_name'] + '-' + v_num, gexf_name)
        if not os.path.exists(gexf_file):
            return set()
        ctx = ET.iterparse(gexf_file, events=['end'])
        ns = "{http://www.gexf.net/1.2draft}"
        fns = set()
        finding_filename_id = True
        try:
            for event, element in ctx:
                if finding_filename_id and element.tag.endswith("attributes") and element.get('class') == 'node':
                    fn_id = element.find("./*[@title='filename']").get('id')
                    finding_filename_id = False
                elif element.tag.endswith('attvalue') and element.get('for') == fn_id:
                    fns.add(element.get('value'))
                elif element.tag.endswith('node'):
                    element.clear()
                elif element.tag.endswith('nodes'):
                    break
        except ET.ParseError:
            return set()
        fn_dict[v] = fns
        # We now have a set of all the filenames processed for a version.
        # Now we need to get the total set of js files.
    before_folder, after_folder = [os.path.join(ro_data['package_folder'],
                                                ro_data['package_name'] + '-' + ro_data[v+'_version'])
                                   for v in ['before', 'after']]
    diff = filecmp.dircmp(before_folder, after_folder)
    _, diff_files, right_only = dircmp_closure(diff)
    # set of js files in diff.right_only + js files in dict.diff_files
    changed_js_files = set()
    changed_js_files = changed_js_files.union([a for a in diff_files if a.endswith('.js')])
    changed_js_files = changed_js_files.union([a for a in right_only if a.endswith('.js')])
    return changed_js_files.difference(fn_dict['after']).difference(fn_dict['before']).union(past_additional_files)

def dircmp_closure(diff):
    result = ([],[],[])
    for d in diff.subdirs.values():
        res = dircmp_closure(d)
        root = os.path.relpath(d.left, diff.left)
        for i in [0,1,2]:
            result[i].extend([os.path.join(root, p) for p in res[i]])
    result[0].extend(diff.left_only)
    result[1].extend(diff.diff_files)
    result[2].extend(diff.right_only)
    return result

def process_package(results_file):
    changed_files = find_changed_files(results_file)
    changed_file_name = os.path.join(os.path.dirname(results_file), "rogue_one_additional_files.txt")
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
