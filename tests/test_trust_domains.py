import contextlib

import networkx as nx

from glob import glob
import os
import fast.simurun.launcher as launcher
import fast.dataflow.extraction as ex
from functools import partial
import fast.dataflow.trust_domains as td
from pprint import pp

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
def single_v_graph(f):
    folder = os.path.join(single_v_folder, f)
    #launcher_cmd = ['python3', gen_graph_path, '-t', 'data_flow', '-f', '800', '--json', '--module', '--run-all']
    #launcher_cmd.append(folder)

    return launcher.unittest_main(folder, vul_type='data_flow', module=True, original_path=folder )

def single_v_idg(f, additional_files=None):
    if not additional_files:
        additional_files=set()
    folder = os.path.join(single_v_folder, f)
    #launcher_cmd = ['python3', gen_graph_path, '-t', 'data_flow', '-f', '800', '--json', '--module', '--run-all']
    #launcher_cmd.append(folder)

    result, g, result_paths =  launcher.unittest_main(folder, vul_type='data_flow', module=True, original_path=folder,
                                                      additional_files=additional_files)
    return ex.extract_idg(g), g


def test_simplest_canonicalization():
    idg, g = single_v_idg('simplest')

    td_map = td.td_rel_map(idg, odgen_graph=g)
    # local goes to lib
    # lib receives local
    assert (td.l_td + ':source1', 'lib.readdir') in td_map


def test_fs_readdir_example():
    idg, g = single_v_idg('fs_readdir_example')
    td_map = td.aggregated_local_td_rel_map(idg, odgen_graph=g)
    assert (td.l_td, 'fs.readdir') in td_map


def test_all_cases_export_param_to_api():
    idg, g = single_v_idg("all_cases")
    td_map = td.aggregated_local_td_rel_map(idg, odgen_graph=g)
    # lib receives local
    rels = list(td_map.keys())
    assert (td.l_td, 'lib.api1') in rels
    assert (td.c_td, 'lib.api2') in rels
    assert (td.l_td, 'process') not in rels
    #assert 'lib' in td_map['fs']


def test_gulp_util():
    idg, g = single_v_idg("gulp-util_arguments_to_args")
    td_map = td.aggregated_local_td_rel_map(idg, odgen_graph=g)
    rels = set(td_map.keys())
    assert (td.c_td, 'multipipe.apply') in rels

def test_export_dep():
    idg, g = single_v_idg('export_dep')
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert (td.c_td, 'lib1') in td_map.keys()

def test_browser():
    idg, g = single_v_idg('browser_example_2')
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert any([k[0].startswith(td.l_td) and 'document' in k[1] for k in td_map])

# def test_daemon():
#     idg, g = single_v_idg('daemon')
#     final = can.canonicalize(idg)
#     assert len(final) > 0
#     assert any(map(lambda df_tuple:
#                    (can.SourceTypes.Require, 'daemon') in df_tuple[1],
#                    final))
# def test_callsite_separation  ():
#     idg, g = single_v_idg("callsite_separation")
#     final = can.canonicalize(idg)
#
# def test_change_from_outside  ():
#     idg, g = single_v_idg("change_from_outside")
#     final = can.canonicalize(idg)
# def test_common_parent        ():
#     idg, g = single_v_idg("common_parent")
#     final = can.canonicalize(idg)
#
# def test_deep_update          ():
#     idg, g = single_v_idg("deep_update")
#     final = can.canonicalize(idg)
# def test_error_sample         ():
#     idg, g = single_v_idg("error_sample")
#     final = can.canonicalize(idg)
# def test_eslint_loop          ():
#     idg, g = single_v_idg("eslint_loop")
#     final = can.canonicalize(idg)
# def test_if_code_attr         ():
#     idg, g = single_v_idg("if_code_attr")
#     final = can.canonicalize(idg)
# def test_imported_callsite    ():
#     idg, g = single_v_idg("imported_callsite")
#     final = can.canonicalize(idg)
# def test_merchantapi_recursion():
#     idg, g = single_v_idg("merchantapi_recursion")
#     final = can.canonicalize(idg)
def test_mutator_library      ():
    idg, g = single_v_idg("mutator_library")
    td_map = td.td_rel_map(idg, odgen_graph=g)

    assert td_map
# def test_self_changing        ():
#     idg, g = single_v_idg("self_changing")
#     final = can.canonicalize(idg)
def test_shell                ():
    idg, g = single_v_idg("shell")
    td_map = td.td_rel_map(idg, odgen_graph=g)

    assert td_map

def test_sigmund                ():
    idg, g = single_v_idg("sigmund@1.0.1")
    td_map = td.td_rel_map(idg, odgen_graph=g)

    # assert td_map

def test_lib_as_func            ():
    idg, g = single_v_idg("lib_as_func")
    td_map = td.td_rel_map(idg, odgen_graph=g)

    assert td_map
def test_lib_as_func_in_export  ():
    idg, g = single_v_idg("lib_as_func_in_export")
    td_map = td.td_rel_map(idg, odgen_graph=g)

    assert td_map

def test_pass_obj  ():
    idg, g = single_v_idg("pass_obj")
    td_map = td.td_rel_map(idg, odgen_graph=g)

    assert td_map

def test_process_check  ():
    idg, g = single_v_idg("process_check")
    td_map = td.td_rel_map(idg, odgen_graph=g)

    assert td_map
def test_is_extglob               ():
    idg, g = single_v_idg("is-extglob@2.1.1/package")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert (td.c_td, td.proc_td) not in td_map

def test_fast_artifact            ():
    idg, g = single_v_idg("fast_artifact_motivating")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map

def test_why_three_edges          ():
    idg, g = single_v_idg("why_three_edges")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map
    assert any([a.startswith(':local:obj:') and b == 'lib.create' for a,b in td_map]) # If these could be somehow removed that would be great.
    assert any([a.startswith(':local:obj:') and b == 'sink' for a,b in td_map])
    assert ('lib', 'sink') in td_map

def test_flows_through_array      ():
    idg, g = single_v_idg("flows_through_array")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map

def test_attack_through_proto     ():
    idg, g = single_v_idg("attack_through_proto")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map

def test_attack_through_obj_proto     ():
    idg, g = single_v_idg("attack_through_obj_proto")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map
def test_callback_param     ():
    idg, g = single_v_idg("callback_param")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map
    assert ('axios', 'fs.writeFileSync') in td_map

def test_consolidate_tds    ():
    idg, g = single_v_idg("callback_param")
    td_map = td.td_rel_map(idg, odgen_graph=g, consolidate_tds=True)
    assert td_map
    assert ('axios', 'fs') in td_map

def test_attack_through_obj_proto_rev():
    idg, g = single_v_idg("attack_through_obj_proto_rev")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map
def test_simple_no_flow     ():
    idg, g = single_v_idg("simple_no_flow")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert not td_map

def test_only_props():
    idg, g = single_v_idg("only_props")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map

def test_remove_ref():
    idg, g = single_v_idg("remove_ref")
    td_map = td.td_rel_map(idg, odgen_graph=g)
    assert td_map

def test_overview_ex_new():
    idg, g = single_v_idg("overview_ex_new")
    td_map = td.td_rel_map(idg, odgen_graph=g, consolidate_tds=True)
    assert td_map
    # This test shows something messed up.  We don't have a way right now to show that the flow from {"key": secret} is
    # effectively sanitized by going through secure-store
def test_dynamic_require():
    idg, g = single_v_idg("dynamic_require")
    td_map = td.td_rel_map(idg, odgen_graph=g, consolidate_tds=True)
    assert td_map
    assert ('lib', td.req_td) in td_map


# def test_sink_discrimination  ():
#     idg, g = single_v_idg("sink_discrimination")
#     final = can.canonicalize(idg)
# def test_sink_whitelisting    ():
#     idg, g = single_v_idg("sink_whitelisting")
#     final = can.canonicalize(idg)
# def test_unknown_callback     ():
#     idg, g = single_v_idg("unknown_callback")
#     final = can.canonicalize(idg)
# def test_unknown_constructed  ():
#     idg, g = single_v_idg("unknown_constructed")
#     final = can.canonicalize(idg)
# def test_unknown_proto        ():
#     idg, g = single_v_idg("unknown_proto")
#     final = can.canonicalize(idg)
# def test_windowing            ():
#     idg, g = single_v_idg("windowing")
#     final = can.canonicalize(idg)
# def test_windowing_deob       ():
#     idg, g = single_v_idg("windowing_deob")
#     final = can.canonicalize(idg)
# def test_windowing_obfuscated ():
#     idg, g = single_v_idg("windowing_obfuscated")
#     final = can.canonicalize(idg)


