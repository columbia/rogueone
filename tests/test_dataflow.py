import networkx as nx

from glob import glob
import os
import fast.simurun.launcher as launcher
import fast.dataflow.extraction as df
from functools import partial
from helper import *
import pytest

gen_graph_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'fast', 'generate_graph.py')

def single_v_graph(f):
    folder = os.path.join(single_v_folder, f)
    #launcher_cmd = ['python3', gen_graph_path, '-t', 'data_flow', '-f', '800', '--json', '--module', '--run-all']
    #launcher_cmd.append(folder)

    return launcher.unittest_main(folder, vul_type='data_flow', module=True, original_path=folder )



def nodes_with_code(g, code):
    return [n[0] for n in g.nodes(data=True) if type(n[1].get('code')) == str and code in n[1]['code']]
def test_simplest_nodes():
    result, g, result_paths = single_v_graph("simplest")
    assert g is not None
    strings = g.get_nodes_by_type('string')
    sources = [n for n in strings if n[1].get('code') == 'source1' and n[1].get('labels:label') != 'AST']
    source_ids = [n[0] for n in sources]
    assert len(sources)  == 1
    source = source_ids[0]

    sinks = df.callsite_return_objs(g)
    assert len(sinks) == 1

    sources_for_sink = df.sources_for_ret_obj(g, list(sinks)[0])

    assert source in sources_for_sink

def test_simplest_idg():
    result, g, result_paths = single_v_graph("simplest")
    idg = df.extract_idg(g)
    assert idg

    retvals = [n for n in idg.nodes(data=True) if n[1].get('obj_type') == df.ObjTypes.APIRetVal]
    statics = [n for n in idg.nodes(data=True) if n[1].get('obj_type') == df.ObjTypes.Static]
    reqs = [n for n in idg.nodes(data=True) if n[1].get('obj_type') == df.ObjTypes.Require]

    assert len(retvals) == 1
    assert len(statics) == 5
    assert len(reqs) == 1

@pytest.mark.skip(reason="The return object for the funcArray[n].call ... is not found.")
def test_assignment_argument():
    result, g, result_paths = single_v_graph("assignment_argument")
    assert g is not None
    strings = g.get_nodes_by_type('string')
    source_ids = [n for n in nodes_with_code(g.graph, 'link') if g.graph.nodes[n].get('labels:label')=='Object' ]
    assert len(source_ids) > 0
    linksource = source_ids[0]

    method_calls = g.get_nodes_by_type('AST_METHOD_CALL')
    sink_ids = [n[0] for n in method_calls if "document.createElement(" in n[1].get('code', '')  ]
    assert len(sink_ids) == 1
    sources_for_doc = df.source_objs_for_callsite(g, sink_ids[0])
    assert linksource in sources_for_doc


    func_call_node = [n[0] for n in method_calls if 'funcArray[n].call(' in n[1].get('code')][0]
    ret = df.return_obj_for_callsite(g, func_call_node)
    assert len(ret) > 0 # Failing because no return object is found for this method.
    sources_for_func = df.source_objs_for_callsite(g, func_call_node)



@pytest.mark.skip(reason="The local call to the concrete anonymous function on line 2 is being counted as non local.")
def test_assignment_argument_callsites():
    result, g, result_paths = single_v_graph("assignment_argument")
    cs_nodes = df.callsite_nodes(g)

    method_calls = g.get_nodes_by_type('AST_METHOD_CALL')
    document_create_node = [n[0] for n in method_calls if 'document.createElement(' in n[1].get('code')][0]
    func_call_node = [n[0] for n in method_calls if 'funcArray[n].call(' in n[1].get('code')][0]

    assert cs_nodes == {document_create_node, func_call_node}


def test_browser_example_2():
    result, g, result_paths = single_v_graph("browser_example_2")

def test_all_cases_str_to_api():
    result, g, result_paths = single_v_graph("all_cases")
    objects = [n[0] for n in g.graph.nodes(data=True) if n[1].get('labels:label') == 'Object']
    obj_sg = g.graph.subgraph(objects)

    sA = [n[0] for n in obj_sg.nodes(data=True) if type(n[1].get('code')) == str and 'sourceAstr' in n[1]['code']]
    assert len(sA) == 1
    sA = sA[0]
    sA_api_retVal_obj = list(nx.descendants_at_distance(obj_sg, sA, 1))[0]
    sA_callsite = nodes_with_code(g.graph, 'lib.api1(sourceA)')[0]
    sA_ret_obj_for_cs = df.return_obj_for_callsite(g, sA_callsite)
    #assert len(sA_ret_obj_for_cs) == 1
    #assert list(sA_ret_obj_for_cs)[0] == sA_api_retVal_obj
    assert sA_api_retVal_obj in sA_ret_obj_for_cs
    sA_s_objs = df.source_objs_for_callsite(g, sA_callsite)
    assert sA in sA_s_objs

def test_all_cases_export_param_to_api():
    result, g, result_paths = single_v_graph("all_cases")
    cs = [n for n in nodes_with_code(g.graph, 'lib.api2(sourceB)') if g.graph.nodes[n]['type'] == 'AST_METHOD_CALL'][0]

    sources = df.source_objs_for_callsite(g, cs)

    assert len(sources) > 0
    assert any(map(lambda x: df.obj_type(g, x) == df.ObjTypes.ExportParam, sources))

def test_all_cases_callback_param_to_api():
    result, g, result_paths = single_v_graph("all_cases")
    cs_candidates = [n for n in nodes_with_code(g.graph, 'lib.api4(sourceC)') if g.graph.nodes[n]['type'] == 'AST_METHOD_CALL']
    outer_cs = [n for n in cs_candidates if 'lib.api3(function(sourceC){' in g.graph.nodes[n]['code']][0]
    inner_cs = [n for n in cs_candidates if 'lib.api3(function(sourceC){' not in g.graph.nodes[n]['code']][0]

    outer_sources = df.source_objs_for_callsite(g, outer_cs)
    # One of the parameters of the outer function should be the callback
    assert any(map(lambda x: g.graph.nodes[x].get('type') == 'function', outer_sources))
    inner_sources = df.source_objs_for_callsite(g, inner_cs)
    inner_types = list(map(lambda x: df.obj_type(g, x), inner_sources-outer_sources))
    assert df.ObjTypes.CallbackParam in inner_types



def test_all_cases_returnval_to_api():
    result, g, result_paths = single_v_graph("all_cases")
    # outer_cs = [n for n in nodes_with_code(g.graph, "lib.api5(fs.readFileSync('/etc/shadow'))") if g.graph.nodes[n]['type'] == 'AST_METHOD_CALL'][0]
    # inner_cs = [n for n in nodes_with_code(g.graph, "fs.readFileSync('/etc/shadow')") if g.graph.nodes[n]['type'] == 'AST_METHOD_CALL'
    #             and n != outer_cs][0]
    outer_cs = [n for n in nodes_with_code(g.graph, "lib.api5(lib.midApi('/etc/shadow'))") if g.graph.nodes[n]['type'] == 'AST_METHOD_CALL'][0]
    inner_cs = [n for n in nodes_with_code(g.graph, "lib.midApi('/etc/shadow')") if g.graph.nodes[n]['type'] == 'AST_METHOD_CALL'
                and n != outer_cs][0]

    inner_source_candidates = [n for n in nodes_with_code(g.graph, '/etc/shadow') if g.graph.nodes[n].get('labels:label') == 'Object']
    inner_source_set = set(inner_source_candidates)


    outer_ret_obj = df.return_obj_for_callsite(g, outer_cs)
    assert len(outer_ret_obj) == 1
    outer_sources = df.source_objs_for_callsite(g, outer_cs)
    assert len(outer_sources) > 0
    outer_types = list(map(lambda x: df.obj_type(g, x), outer_sources))
    assert df.ObjTypes.APIRetVal in outer_types


    inner_ret_obj = df.return_obj_for_callsite(g, inner_cs)
    assert len(inner_ret_obj) == 1
    inner_sources = df.source_objs_for_callsite(g, inner_cs)
    # Right now this is returning one source, corresponding to the api function.
    inner_types = list(map(lambda x: df.obj_type(g, x), inner_sources))
    assert df.ObjTypes.Static in inner_types




def test_all_cases_addition():
    result, g, result_paths = single_v_graph("all_cases")
    cs = [n for n in nodes_with_code(g.graph, "lib.api6(sourceE[0] + sourceE[1])") if g.graph.nodes[n]['type'] == 'AST_METHOD_CALL'][0]
    source = nodes_with_code(g.graph, 'ls uname -r')[-1]
    assert source in df.source_objs_for_callsite(g, cs)


def test_callsite_separation  ():
    result, g, result_paths = single_v_graph("callsite_separation")
    assert g is not None
    strings = g.get_nodes_by_type('string')


    for s in ['source1', 'source2']:
        source_ids = [n[0] for n in strings if n[1].get('code') == s and n[1].get('labels:label') == 'Object']
        assert len(source_ids) > 0

        sinks = g.get_nodes_by_type('AST_METHOD_CALL')
        sink_ids = [n[0] for n in sinks if s in n[1].get('code', '')]
        assert len(sink_ids) > 0

        sources_for_cs = df.source_objs_for_callsite(g, sink_ids[0])
        assert source_ids[0] in sources_for_cs


def test_change_from_outside  ():
    result, g, result_paths = single_v_graph("change_from_outside")
def test_common_parent        ():
    # command = 'lsuname -rdate'
    # cp = require('child_process');
    # cp.spawn(command[0] + command[1]);
    # cp.spawn(command[2] + command[3] + command[4] + command[5] + command[6] + command[7] + command[8] + command[9] + command[10])
    # cp.spawn(command[11] + command[12] + command[13] + command[14])
    result, g, result_paths = single_v_graph("common_parent")
    #print(f"Nodes: {g.graph.number_of_nodes()}")
    #print(f"Edges: {g.graph.number_of_edges()}") # (2343, 3385)
    # (2348, 3396)
    assert g
def test_deep_update          ():
    result, g, result_paths = single_v_graph("deep_update")
def test_error_sample         ():
    result, g, result_paths = single_v_graph("error_sample")
def test_eslint_loop          ():
    result, g, result_paths = single_v_graph("eslint_loop")
def test_fs_readdir_example   ():
    result, g, result_paths = single_v_graph("fs_readdir_example")
def test_if_code_attr         ():
    result, g, result_paths = single_v_graph("if_code_attr")
def test_imported_callsite    ():
    result, g, result_paths = single_v_graph("imported_callsite")
def test_merchantapi_recursion():
    result, g, result_paths = single_v_graph("merchantapi_recursion")
def test_mutator_library      ():
    result, g, result_paths = single_v_graph("mutator_library")
def test_self_changing        ():
    result, g, result_paths = single_v_graph("self_changing")
def test_shell                ():
    result, g, result_paths = single_v_graph("shell")
def test_sink_discrimination  ():
    result, g, result_paths = single_v_graph("sink_discrimination")
def test_sink_whitelisting    ():
    result, g, result_paths = single_v_graph("sink_whitelisting")
def test_unknown_callback     ():
    result, g, result_paths = single_v_graph("unknown_callback")
def test_unknown_constructed  ():
    result, g, result_paths = single_v_graph("unknown_constructed")
def test_unknown_proto        ():
    result, g, result_paths = single_v_graph("unknown_proto")
def test_windowing            ():
    result, g, result_paths = single_v_graph("windowing")
def test_windowing_deob       ():
    result, g, result_paths = single_v_graph("windowing_deob")
def test_windowing_obfuscated ():
    result, g, result_paths = single_v_graph("windowing_obfuscated")





