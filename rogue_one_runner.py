import argparse
import contextlib
import csv
import glob
import json
import multiprocessing
import os
import subprocess
import sys
from datetime import datetime
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import psutil
from tqdm import tqdm

from common import default_exception
from fast.dataflow import extraction as ex, trust_domains as td
from fast.dataflow.trust_domains import code_locs_from_rel_map
from fast.manager import models
from fast.manager.models import csv_header
from fast.manager.package_changes import build_package_json_changes, build_changed_file_list, extract_name_and_versions
from fast.simurun.graph import Graph as ODGenGraph, MemoryLimitExceededError
from fast.simurun.launcher import main as odgen_main


@contextlib.contextmanager
def wd(path):
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def pr(s):
    tqdm.write(str(s) + " \n")


def noop(s):
    pass


def get_package_name(s):
    s = s.split(os.path.sep)[-2]
    return '-'.join(s.split('-')[0:-1])


def run_package(package_folder: str, timeout=1, printer=pr, scripts=None,
                additional_files=set(), args=None, logging_dir=None) -> ODGenGraph:
    with wd(logging_dir if logging_dir else package_folder):
        params = [['-t', 'data_flow', '-f', '800', '--json', '--module', '--run-all', '--skipprint'],
                  ['-t', 'data_flow', '-f', '800', '--json', '--module', '--run-all', '--call-limit', '1', '-s']]
        if args and args.fast:
            params = params[1]
        else:
            params = params[0]
        if args and args.log_level:
            params.append(f"--log_level={args.log_level}")
        if printer == noop:
            params += ['-S']
        g = odgen_main(argv=[package_folder] + params, additional_files=additional_files, scripts=scripts)
        return g


def process_package(package_dir, printer=pr, args=None, changed_files=None,
                    scripts=None, logging_dir=None):
    if changed_files is None:
        changed_files = set()
    if scripts is None:
        scripts = dict()
    if logging_dir:
        printer(f"Logging dir set to: {logging_dir}")
    else:
        printer(f"Logging to package dir ({package_dir})")
    before_odg = datetime.now()
    try:
        odgen_g = run_package(str(package_dir), printer=printer, additional_files=changed_files,
                              scripts=scripts, args=args, logging_dir=logging_dir)
        before_idg = datetime.now()
        try:
            idg = ex.extract_idg(odgen_g)
            done = datetime.now()
            printer(f"Package analysis finished successfully ({package_dir})")
            return idg, odgen_g, before_idg - before_odg, done - before_idg
        except Exception as e:
            log_prefix = f"{multiprocessing.current_process().ident}: Error in IDG extraction for {package_dir}"
            if default_exception(e, args.raise_all, log_prefix, printer=printer):
                raise e
            return None, odgen_g, before_idg - before_odg, datetime.now() - before_idg
    except MemoryLimitExceededError as e:
        raise e
    except Exception as e:
        log_prefix = f"{multiprocessing.current_process().ident}: Error in ODGen graph generation for {package_dir} "
        if default_exception(e, args.raise_all, log_prefix, printer=printer):
            raise e

    return None, None, datetime.now() - before_odg, 0


def rel_map_keys_to_str(rel_map):
    m = {}
    for k in rel_map:
        m[str(k)] = rel_map[k]
    return m


def process_esprima_info(esprima_info):
    result = {}
    blocks = esprima_info.split("Analyzing")
    # parser_options

    for block in blocks:
        filename = block.split("\n")[0].strip()
        if "ecmaVersion" in block and "Error" in block:
            lines = block.split("\n")
            error = []
            for line in lines:
                if "ecmaVersion" in line and "parser_options" not in result:
                    parser_options = json.loads(line)
                    result["parser_options"] = parser_options
                if "Error" in line:
                    error.append(line)
            result["errors"] = {filename: error}
    return result


def process_package_pair(pair_dir, printer=pr, args=None):
    # try:
    #     os.remove("fast/esprima_logger.log")
    #     print('remove old')
    # except:
    #     pass
    esprima_info = ''
    pair_path = Path(pair_dir)
    pair_name = pair_path.name
    package_name, before_version, after_version = extract_name_and_versions(pair_name)
    before_folder = pair_path / (package_name + '-' + before_version)
    after_folder = pair_path / (package_name + '-' + after_version)
    return process_package_pair_given_names(pair_dir, pair_path, before_folder, after_folder,
                                            package_name, before_version, after_version, printer, args)


def process_package_pair_given_names(pair_dir: str, pair_path: Path, before_folder: Path, after_folder: Path,
                                     package_name: str, before_version: str, after_version: str, printer, args):
    printer(f"Starting analysis on pair_dir: {pair_dir}")
    skip_flag = pair_path / "DONOTANALYZE"
    # remove old esprima_logger files before running analysis
    try:
        for i in [before_folder, after_folder]:
            os.remove(os.path.join(i, "esprima_logger.log"))
            # print('remove old')
    except:
        pass
    if skip_flag.exists():
        return None

    before_start = datetime.now()
    before_done = None
    after_done = None
    esprima_info = None
    post_diff_time = None
    try:
        changed_other_files = build_changed_file_list(before_folder, after_folder)
        before_idg, before_odg, before_odg_time, before_idg_time = process_package(before_folder, printer=printer,
                                                                                   args=args,
                                                                                   changed_files=changed_other_files)
        before_done = datetime.now()
        scripts = build_package_json_changes(before_folder, after_folder)
        after_idg, after_odg, after_odg_time, after_idg_time = process_package(after_folder, printer=printer, args=args,
                                                                               changed_files=changed_other_files,
                                                                               scripts=scripts)
        after_done = datetime.now()

        # read esprima_info from new log file, because the esprima function is too deep
        esprima_info_text = ''
        for i in [before_folder, after_folder]:
            with open(os.path.join(i, "esprima_logger.log")) as f:
                esprima_info_text += f.read()
        esprima_info = process_esprima_info(esprima_info_text)

        before_rel_map = td.td_rel_map(before_idg, odgen_graph=before_odg, consolidate_tds=True)
        after_rel_map = td.td_rel_map(after_idg, scripts=scripts, odgen_graph=after_odg, consolidate_tds=True)
        before_rels = td.rels_as_tuples(before_rel_map)
        after_rels = td.rels_as_tuples(after_rel_map)
        suspicious = td.flagged_single_local_rels_from_tuples(before_rels, after_rels)
        post_diff_time = datetime.now()

        for m in (before_rel_map, after_rel_map):
            for k in m:
                if type(m[k]) == set:
                    m[k] = list(m)

        if before_odg.file_node_nums == {} and after_odg.file_node_nums == {}:
            pr(f"WARNING: No files processed for {package_name}_{before_version}-->{after_version}.  Path may be incorrect.")

        if args and args.save_odrg:
            td.sanitize_and_export(before_idg, pair_path / "before.graphml")
            td.sanitize_and_export(after_idg, pair_path / "after.graphml")
        result = {
            'package_name': package_name,
            'label': get_label(pair_dir),
            'group': pair_path.parent.name,
            'system': 'rogue_one',
            'run_timestamp': str(before_start),
            'sinks_added': 0,
            'sinks_removed': 0,
            'sinks_changed': 0,
            'fast_mode': args.fast if args else False,
            'esprima_info': esprima_info,
            'before': {
                'version': before_version,
                'folder': str(before_folder),
                'running_time': (before_done - before_start).total_seconds(),
                'weakly_connected_components': nx.number_weakly_connected_components(before_idg),
                'error': 'OK',
                'file_node_nums': before_odg.file_node_nums,
                'odg_time': str(before_odg_time),
                'idg_time': str(before_idg_time),
                'graph_size': {
                    'odg': {'nodes': before_odg.graph.number_of_nodes(), 'edges': before_odg.graph.number_of_edges()},
                    'idg': {'nodes': before_idg.number_of_nodes(), 'edges': before_idg.number_of_edges()}
                },

            },
            'after': {
                'version': after_version,
                'folder': str(after_folder),
                'running_time': (after_done - before_done).total_seconds(),
                'weakly_connected_components': nx.number_weakly_connected_components(after_idg),
                'error': 'OK',
                'file_node_nums': after_odg.file_node_nums,
                'odg_time': str(after_odg_time),
                'idg_time': str(after_idg_time),
                'graph_size': {
                    'odg': {'nodes': after_odg.graph.number_of_nodes(), 'edges': after_odg.graph.number_of_edges()},
                    'idg': {'nodes': after_idg.number_of_nodes(), 'edges': after_idg.number_of_edges()}
                },
            },
            'error': 'OK',
            'suspicious': bool(suspicious),
            'system_extra_info': {
                'Min': bool(suspicious),
                'trusted': bool(td.flagged_new_local_rels_from_tuples(before_rels, after_rels)),
                'max': bool(td.flagged_rels_from_tuples(before_rels, after_rels)),
                'flagged_all_local_distinct': list(td.flagged_rels_from_tuples(before_rels, after_rels)),
                'flagged_new_local_distinct': list(td.flagged_new_local_rels_from_tuples(before_rels, after_rels)),
                'new_rels': list(suspicious),
                "before_rels": rel_map_keys_to_str(before_rel_map),
                "after_rels": rel_map_keys_to_str(after_rel_map),
                "before_rel_code_locs": code_locs_from_rel_map(before_odg, before_rel_map),
                "after_rel_code_locs": code_locs_from_rel_map(after_odg, after_rel_map),
                'before_running_time': (before_done - before_start).total_seconds(),
                'after_running_time': (after_done - before_done).total_seconds(),
                'skipped_files': list(after_odg.skipped_files),
                'post_processing_time': str(post_diff_time - after_done),
                'command': str(args),
                'mem_info': mem_info(),

            },
        }
    except Exception as e:
        log_prefix = f'process_package_pair: Error Processing {pair_dir}, {str(e)}\n'
        if default_exception(e, args.raise_all, log_prefix, printer=sys.stderr.write):
            raise e
        result = {
            'package_name': package_name,
            'label': get_label(pair_dir),
            'group': pair_path.parent.name,
            'system': 'rogue_one',
            'run_timestamp': str(before_start),
            'sinks_added': 0,
            'sinks_removed': 0,
            'sinks_changed': 0,
            'fast_mode': args.fast if args else False,
            'esprima_info': esprima_info,
            'before': {
                'version': before_version,
                'folder': str(before_folder),
                'flows': "",
                'running_time': (before_done - before_start).total_seconds() if before_done else 0,
                'weakly_connected_components': "",
                'error': 'error',
            },
            'after': {
                'version': after_version,
                'folder': str(after_folder),
                'flows': "",
                'running_time': (after_done - before_done).total_seconds() if before_done and after_done else 0,
                'weakly_connected_components': "",
                'error': 'error',
            },
            'error': 'Error: '+ str(e),
            'identical_flows': "",
            'new_flows': "",
            'removed_flows': "",
            'suspicious': False,
            'system_extra_info': {
                'before_running_time': (before_done - before_start).total_seconds() if before_done else 0,
                'after_running_time': (after_done - before_done).total_seconds() if before_done and after_done else 0,
                'post_processing_time': str(post_diff_time - after_done) if post_diff_time and after_done else 0,
                'command': str(args),
                'mem_info': mem_info(),
            },
        }
    output_file = pair_path / 'rogue_one_output.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, default=str)

    output_csv = pair_path / 'rogue_one_output.csv'
    row = write_result_obj_to_csv(result, output_csv)
    return result

def mem_info():
    pm = psutil.Process(os.getpid()).memory_info()
    return {
        'rss': pm.rss,
         'vms': pm.vms,
        'shared': pm.shared,
        'text': pm.text,
        'lib': pm.lib,
        'data': pm.data,
        'dirty': pm.dirty
    }
def process_package_version_with_model(task: models.TaskModel, printer=pr, args=None):
    esprima_info = ''
    printer(f"Starting analysis on: {task.disk_location}")
    logging_folder = Path(task.disk_location)
    package_name = task.version.package.name
    target_folder = Path(task.version.disk_location)

    # remove old esprima_logger files before running analysis
    try:
        os.remove(os.path.join(logging_folder, "esprima_logger.log"))
    except:
        pass

    start_time = datetime.now()
    end_time = None
    try:
        idg, odg, odg_time, idg_time = \
            process_package(target_folder, printer=printer, args=args, logging_dir=logging_folder)
        end_time = datetime.now()
        # read esprima_info from new log file, because the esprima function is too deep
        esprima_info_text = ''
        with open(os.path.join(logging_folder, "esprima_logger.log")) as f:
            esprima_info_text += f.read()
        esprima_info = process_esprima_info(esprima_info_text)
        if idg:
            rel_map = td.td_rel_map(idg)
            for k in list(rel_map.keys()):
                if type(rel_map[k]) == set:
                    rel_map[k] = list(rel_map)
                if type(k) != str:
                    rel_map[str(k)] = rel_map[k]
                    del rel_map[k]
            error = 'OK'
        else:
            rel_map = None
            error = 'Failed to create IDG.'
        result = {
            'package_name': package_name,
            'label': get_label(str(target_folder)),
            'group': target_folder.parent.parent.name,
            #  TODO: Confirm whether it needs to be parent of parent
            'system': 'rogue_one',
            'run_timestamp': str(start_time),
            'esprima_info': esprima_info,
            'version': task.version.number,
            'data_folder': str(target_folder),
            'result_folder': str(logging_folder),
            'running_time': (end_time - start_time).total_seconds(),
            'weakly_connected_components': nx.number_weakly_connected_components(idg) if idg else 0,
            'error': error,
            'file_node_nums': odg.file_node_nums if odg else {},
            'odg_time': str(odg_time),
            'idg_time': str(idg_time),
            'graph_size': {
                'odg': {'nodes': odg.graph.number_of_nodes(), 'edges': odg.graph.number_of_edges()},
                'idg': {'nodes': idg.number_of_nodes(), 'edges': idg.number_of_edges()}
            },
            'rels': rel_map,
            'code_locs': code_locs_from_rel_map(odg, rel_map) if idg else {},
        }
    except Exception as e:
        log_prefix = f"process_package_version_with_model: Error Processing {target_folder}, {str(e)}\n"
        if default_exception(e, args.raise_all, log_prefix, printer=sys.stderr.write):
            raise e
        result = {
            'package_name': package_name,
            'label': get_label(str(target_folder)),
            'version': task.version.number,
            'group': target_folder.parent.parent.name,
            #  TODO: Confirm whether it needs to be parent of parent
            'system': 'rogue_one',
            'run_timestamp': str(start_time),
            'esprima_info': esprima_info,
            'data_folder': str(target_folder),
            'result_folder': str(logging_folder),
            'flows': "",
            'running_time': (end_time - start_time).total_seconds() if end_time else 0,
            'weakly_connected_components': "",
            'error': str(e),
        }
        # raise e
    output_file = logging_folder / 'rogue_one_output.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, default=str)

    return result


def get_label(package_folder: str) -> str:
    if 'synth' in package_folder:
        return 'SYNTH'
    elif 'stabber' in package_folder:
        return 'MAL'
    elif 'active_survey' in package_folder:
        return 'UNK'
    elif 'amalfi_NPM' in package_folder:
        return 'IDONTKNOW'
    else:
        return 'BEN'


def write_result_obj_to_csv(result, csv_fn):
    def extract_csv_data(k):
        for ks in ['before', 'after']:
            if k.startswith(ks):
                to_remove = ks + "_"
                subkey = k[len(to_remove):]
                return str(result[ks][subkey])[0:32000]
        return str(result.get(k, ""))[0:32000]

    row = [extract_csv_data(k) for k in csv_header]

    with open(csv_fn, 'w') as f:
        c = csv.writer(f)
        c.writerow(row)
    return row


def write_error(pair_dir, file, err=None):
    pair_path = Path(pair_dir)
    pair_name = pair_path.name
    package_name, before_version, after_version = extract_name_and_versions(pair_name)
    before_folder = pair_path / (package_name + '-' + before_version)
    after_folder = pair_path / (package_name + '-' + after_version)
    result = {
        'package_name': package_name,
        'label': get_label(pair_dir),
        'group': pair_path.parent.name,
        'system': 'rogue_one',
        'run_timestamp': str(datetime.now()),
        'sinks_added': 0,
        'sinks_removed': 0,
        'sinks_changed': 0,
        'before': {
            'version': before_version,
            'folder': str(before_folder),
            'flows': "",
            'running_time': "",
            'weakly_connected_components': "",
            'error': 'error',
        },
        'after': {
            'version': after_version,
            'folder': str(after_folder),
            'flows': "",
            'running_time': "",
            'weakly_connected_components': "",
            'error': 'error',
        },
        'error': 'error',
        'identical_flows': "",
        'new_flows': "",
        'removed_flows': "",
        'suspicious': False,
        'system_extra_info': str(err) if err else '',
    }
    sys.stderr.write(f'Error Processing {pair_dir}, {str(err)}\n')
    # raise err
    return write_result_obj_to_csv(result, file)


def package_pair_wrapper(pair, args=None, timeouts=dict()):
    cmd = ['python', __file__, '--single', pair]
    timeout = 60 * 60

    timeout_p = Path(Path(pair).parent.name) / Path(pair).name
    if timeout_p in timeouts:
        return timeouts[timeout_p]

    output_csv = Path(pair) / 'rogue_one_output.csv'
    output_json = Path(pair) / 'rogue_one_output.json'
    if output_csv.exists() and output_json.exists() and args.no_redo:
        try:
            with open(output_csv) as f:
                c = csv.reader(f)
                row = next(c)
                return row
        except:
            sys.stderr.write(f"Existing output detected for {pair} but failed to read, re-analyzing.\n")
    elif output_csv.exists():
        os.remove(output_csv)

    if args.fast:
        try:
            cmd.append("--fast")
            p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=sys.stderr, cwd=pair, timeout=timeout)
        except Exception as e:
            if default_exception(e, rethrow_unexpected=False):
                raise e
            write_error(pair, output_csv, e)

    try:
        p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=sys.stderr, cwd=pair, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            cmd.append("--fast")
            p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=sys.stderr, cwd=pair, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            write_error(pair, output_csv, e)
            # Need to open the output csv and write a timeout error here
        except Exception as e:
            if default_exception(e, rethrow_unexpected=False):
                raise e
            write_error(pair, output_csv, e)

    try:
        with open(output_csv) as csvfile:
            c = csv.reader(csvfile)
            for row in c:
                return row
    except Exception as e:
        log_prefix = f"{multiprocessing.current_process().ident}: Error, no output CSV for {pair} {e}"
        if default_exception(e, rethrow_unexpected=False, logging_prefix=log_prefix, printer=sys.stderr.write):
            raise e
        return None


def timeout_map(sample_folder):
    timeouts_file = Path(sample_folder) / "timeouts.csv"
    package_pairs = dict()
    try:
        with open(timeouts_file) as f:
            c = csv.reader(f)
            header = next(c)
            timeout_message_col = header.index('system_extra_info')
            group_col = header.index('group')
            pkg_name_col = header.index('package_name')
            b_ver_col = header.index('before_version')
            a_ver_col = header.index('after_version')
            for row in c:
                msg = row[timeout_message_col]
                path = Path(row[group_col]) / Path(f"{row[pkg_name_col]}_{row[b_ver_col]}-->{row[a_ver_col]}")
                package_pairs[path] = row

    except FileNotFoundError as e:
        default_exception(e, rethrow_unexpected=False)
    return package_pairs


if __name__ == '__main__':
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
    args = ap.parse_args()
    if not (args.sample_folder or args.single):
        print("Need either --single with a sample or a sample folder to target")
        sys.exit(1)
    elif args.sample_folder:
        sample_glob = os.path.join(args.sample_folder, "**", "*-->**")
        # ngx-pica - preexisting data dep
        # nginxbeautifier - some kind of bug
        # Try another base object to annotate! Maybe Date or Buffer??
    else:
        process_package_pair(args.single, args=args)
        sys.exit(0)

    if not args.timeouts:
        timeouts = timeout_map(args.sample_folder)
    else:
        timeouts = dict()

    sample_dirs = glob.glob(sample_glob)
    import random

    random.shuffle(sample_dirs)
    # sample_dirs = [sample_dirs[0]]
    sample_dirs = [f for f in sample_dirs if 'BenignSamples' in f or '_samples' in f or 'amalfi_NPM' in f]
    with open("rogue_one_mass_analysis.csv", 'w') as f:
        c = csv.writer(f)
        c.writerow(csv_header)
        f.flush()
        with Pool(int(multiprocessing.cpu_count() * 0.7)) as p:
            with tqdm(total=len(sample_dirs)) as pbar:
                # for a in p.map(partial(package_pair_wrapper, args=args), sample_dirs):
                for a in p.imap_unordered(partial(package_pair_wrapper, args=args, timeouts=timeouts), sample_dirs):
                    pbar.update()
                    if a:
                        c.writerow(a)
                    f.flush()

                p.close()
            p.join()
