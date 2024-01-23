import argparse
import json
import math
import os
import sys
import typing
import unicodedata
from pathlib import Path
from typing import Any

import sty
from .graph import Graph
from .logger import *
from .opgen import register_func, handle_node, \
    add_edges_between_funcs, analyze_files, analyze_string, generate_obj_graph, find_where_the_func_is_imported
from .helpers import get_func_name
from .trace_rule import TraceRule
from .utilities import _SpecialValue, NodeHandleResult
from .vul_checking import *
from datetime import datetime
from calmjs.parse import es5
import time
import networkx as nx

def unittest_main(file_path, check_signatures=[], vul_type='os_command',
    args=None, graph=None, original_path=None, module=False, additional_files=None, scripts=None):
    if not additional_files:
        additional_files = set()
    """
    main function for uniitest 
    """
    if graph is None:
        G = Graph()
    else:
        G = graph
    # if graph is not None:
    #     del graph
    # G = Graph()
    G.exit_when_found = True
    G.vul_type = vul_type
    G.check_proto_pollution = (vul_type == 'proto_pollution')
    G.check_ipt = (vul_type == 'int_prop_tampering')
    if args is not None:
        G.single_branch = args.single_branch
        G.function_time_limit = args.function_timeout
        G.check_proto_pollution = G.check_proto_pollution or args.proto_pollution
        G.check_ipt = G.check_ipt or args.int_prop_tampering
        G.no_file_based = args.nfb
        G.two_pass = args.rcf
        G.rough_call_dist = args.rcd
        G.auto_exploit = args.exploit
        G.coarse_only = args.coarse_only
    else:
        G.rough_call_dist = False
        if module:
            G.run_all = True
    G.entry_file_path = original_path
    G.ast_num_threshold = 10000
    if module:
        result = module_mode_analyze(G, file_path, additional_files=G.additional_files, scripts=scripts)
    else:
        result = analyze_files(G, file_path, check_signatures=check_signatures)
    # output location of prototype pollution to a seperate file
    proto_pollution_logger = create_logger('proto_pollution',
            output_type='file', file_name="proto_pollution.log")
    if G.proto_pollution:
        proto_pollution_logger.info('Prototype pollution found in package {}'
            .format(G.entry_file_path))
        for ast_node in G.proto_pollution:
            proto_pollution_logger.info('{} {}\n{}'
                .format(ast_node, G.get_node_file_path(ast_node),
                        G.get_node_line_code(ast_node)))
    # IPT output
    ipt_logger = create_logger('ipt',
            output_type='file', file_name="int_prop_tampering.log")
    if G.ipt_use:
        ipt_logger.info('Internal property tampering found in package {}'
            .format(G.entry_file_path))
        if True:
            ipt_logger.info('Write:')
            for ast_node in G.ipt_write:
                ipt_logger.info('{} {}\n{}'
                    .format(ast_node, G.get_node_file_path(ast_node),
                            G.get_node_line_code(ast_node)))
        ipt_logger.info('Use:')
        for ast_node in G.ipt_use:
            ipt_logger.info('{} {}\n{}'
                .format(ast_node, G.get_node_file_path(ast_node),
                        G.get_node_line_code(ast_node)))
    other_logger = create_logger('data_flow', output_type='file', file_name='data_flow_test.log')
    result_paths = generic_generate_paths(G, other_logger, [])
    return result, G, result_paths

def main(argv=None, additional_files=set(), scripts=None):
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Object graph generator for JavaScript.')
    parser.add_argument('-p', '--print', action='store_true',
                        help='Print logs to console, instead of file.')
    parser.add_argument('-S', '--skipprint', action='store_true',
                        help='Skips printing json to stdout.')
    parser.add_argument('-t', '--vul-type', default='os_command',
                        help="Set the vulnerability type to be checked.")
    parser.add_argument('-P', '--prototype-pollution', '--pp',
                        action='store_true',
                        help="Check prototype pollution.")
    parser.add_argument('-I', '--int-prop-tampering', '--ipt',
                        action='store_true',
                        help="Check internal property tampering.")
    parser.add_argument('-m', '--module', action='store_true',
                        help="Module mode. Regard the input file as a module "
                        "required by some other modules. This implies -a.")
    parser.add_argument('-q', '--exit', action='store_true', default=False,
                        help="Exit the program when vulnerability is found.")
    parser.add_argument('-s', '--single-branch', action='store_true',
                        help="Single branch. Do not create multiple "
                        "possibilities when meet a branching point.")
    parser.add_argument('-a', '--run-all', action='store_true', default=False,
                        help="Run all exported functions in module.exports. "
                        "By default, only main functions will be run.")
    parser.add_argument('-f', '--function-timeout', type=float,
                        help="Time limit when running all exported function, "
                        "in seconds. (Defaults to no limit.)")
    parser.add_argument('-c', '--call-limit', default=None, type=int,
                        help="Set the limit of a call statement. "
                        "(Defaults to 3.)")
    parser.add_argument('-e', '--entry-func')
    parser.add_argument('-F', '--nfb', '--no-file-based', action='store_true')
    parser.add_argument('-C', '--rcf', '--rough-control-flow', action='store_true')
    parser.add_argument('-D', '--rcd', '--rough-call-distance', action='store_true')
    parser.add_argument('-X', '--exploit', '--auto-exploit', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-1', '--coarse-only', action='store_true')
    parser.add_argument('-j', '--json', action='store_true', default=False)
    parser.add_argument('-ast_num_threshold', '--ast_num_threshold', default=100000, type=int,
                        help="Before analyzing, if we detect the number of AST node in a file > ast_num_threshold, we treat the file as a blackbox")
    parser.add_argument('input_file', action='store', nargs='?',
        help="Source code file (or directory) to generate object graph for. "
        "Use '-' to get source code from stdin. Ignore this argument to "
        "analyze ./nodes.csv and ./rels.csv.")
    parser.add_argument("--log_level", action="store", default='FATAL')
    
    args = parser.parse_args(args=argv)
    if args.vul_type == 'prototype_pollution' or args.vul_type == 'pp':
        args.vul_type = 'proto_pollution'
    if args.vul_type == 'ipt':
        args.vul_type = 'int_prop_tampering'
    log_level = args.log_level
    logger = create_logger("main_logger", output_type="file", level=log_level)
    esprima_logger = create_logger("esprima_logger", output_type="file", file_name="esprima_logger.log", level=log_level)
    start_time = time.time()
    G = Graph()

    if args.exploit:
        G.auto_exploit = args.exploit
        args.module = True
    if args.print or args.interactive:
        level = logging.DEBUG if args.print else logging.INFO
        logger = create_logger("main_logger", output_type="console",
            level=level)
        create_logger("graph_logger", output_type="console",
            level=level)
        G.print = True
    G.run_all = args.run_all or args.module
    G.no_file_based = args.nfb
    G.two_pass = args.rcf
    G.rough_call_dist = args.rcd
    G.function_time_limit = args.function_timeout
    G.exit_when_found = args.exit
    G.single_branch = args.single_branch
    G.vul_type = args.vul_type
    G.func_entry_point = args.entry_func
    G.check_proto_pollution = (args.prototype_pollution or 
                               args.vul_type == 'proto_pollution')
    G.check_ipt = (args.int_prop_tampering or 
                               args.vul_type == 'int_prop_tampering')
    if args.call_limit is not None:
        G.call_limit = args.call_limit
    G.interactive = args.interactive
    G.coarse_only = args.coarse_only
    G.ast_num_threshold = args.ast_num_threshold
    G.additional_files = additional_files

    # Analyze and simulate
    logger.info('Analysis starts at ' +
        datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'))
    if args.input_file:
        if args.input_file == '-':
            if args.module:
                raise argparse.ArgumentTypeError(
                    'stdin cannot be used with module mode')
            else:
                # analyze from stdin
                source = sys.stdin.read()
                analyze_string(G, source, generate_graph=True)
        else:
            G.entry_file_path = args.input_file
            if args.module:
                # pretend another file is requiring this module
                module_mode_analyze(G, args.input_file, additional_files=G.additional_files, scripts=scripts)
            else:
                # analyze from JS source code files
                analyze_files(G, args.input_file)
    else:
        if args.module:
            raise argparse.ArgumentTypeError(
                'CSV cannot be used with module mode')
        else:
            # analyze from CSVs
            G.import_from_CSV("./nodes.csv", "./rels.csv")
            generate_obj_graph(G, '0')
    total_num_stat = G.get_total_num_statements()
    output = []
    output.append(("Statements:", f" {len(G.covered_stat)} {total_num_stat}"))
    output.append(("Functions:", f" {len(G.covered_func)} {G.get_total_num_functions()}"))
    # G.relabel_nodes()
    G.export_to_CSV("./opg_nodes.tsv", "./opg_rels.tsv")
    logger.log(ATTENTION, 'Analysis finished at ' +
        datetime.today().strftime('%Y-%m-%d %H:%M:%S') +
        ', Time spent: %.3fs' % (time.time() - start_time))
    output.append(("Time spent: ", f" {'%.3fs' % (time.time() - start_time)}"))
    # Vulnerability checking
    # if G.proto_pollution:
    #     logger.debug(sty.ef.inverse + 'prototype pollution' + sty.rs.all)
    #
    #     for ast_node in G.proto_pollution:
    #         pathes = G._dfs_upper_by_edge_type(ast_node)
    #         logger.debug('{} {}\n{}'
    #             .format(sty.fg.li_cyan + ast_node + sty.rs.all,
    #                 G.get_node_file_path(ast_node),
    #                 G.get_node_line_code(ast_node)))
    #     output.append(("proto pollution: ", f" {print(G.proto_pollution)}"))
    #
    # if G.ipt_use:
    #     logger.debug(sty.ef.inverse + 'internal property tampering' + sty.rs.all)
    #
    #     if G.ipt_write:
    #         logger.debug('Write:')
    #         for ast_node in G.ipt_write:
    #             pathes = G._dfs_upper_by_edge_type(ast_node)
    #             logger.debug('{} {}\n{}'
    #                 .format(sty.fg.li_cyan + ast_node + sty.rs.all,
    #                     G.get_node_file_path(ast_node),
    #                     G.get_node_line_code(ast_node)))
    #         print(G.ipt_write)
    #         logger.debug('')
    #     logger.debug('Use:')
    #     for ast_node in G.ipt_use:
    #         pathes = G._dfs_upper_by_edge_type(ast_node)
    #         logger.debug('{} {}\n{}'
    #             .format(sty.fg.li_cyan + ast_node + sty.rs.all,
    #                 G.get_node_file_path(ast_node),
    #                 G.get_node_line_code(ast_node)))
    #     print(G.ipt_use)
    #
    # if G.vul_type not in ['proto_pollution', 'int_prop_tampering']:
    #     res_pathes = generic_generate_paths(G, logger, output)

    # Add filenames
    for n in G.graph.nodes:
        if G.graph.nodes[n].get('labels:label') == 'AST':
            nfp = G.get_node_file_path(n)
            if nfp == 'stdin':
                G.graph.nodes[n]['filename'] = nfp
            elif nfp:
                G.graph.nodes[n]['filename'] = os.path.relpath(nfp, G.entry_file_path)

        name_edges = G.get_in_edges(n, edge_type='NAME_TO_OBJ')
        names = [str(G.graph.nodes[name_edge[0]]['name']) for name_edge in name_edges]
        if len(names) > 0:
            G.graph.nodes[n]['names'] = ", ".join(set(names))

    success_center = ""
    success_result = ""
    if G.success_detect:
        success_center = 'Detection: successful'
        success_result = (sty.fg.green + sty.ef.b + success_center + sty.rs.all)
    else:
        success_center = 'Detection: failed'
        success_result = (sty.fg.yellow + sty.ef.b + success_center + sty.rs.all)
    if args.json:
        output.append(("Success: ", success_center))
    else:
        print(success_result)
    if G.auto_exploit:
        if G.success_exploit:
            print(sty.fg.green + sty.ef.b + 'Exploit: successful' + sty.rs.all)
        else:
            print(sty.fg.yellow + sty.ef.b + 'Exploit: failed' + sty.rs.all)
    else:
        output.append(("Exploit", "turned off"))
        #print(sty.fg.da_grey + sty.ef.b + 'Exploit: turned off' + sty.rs.all)
    running_time = time.time() - start_time
    logger.debug('Time spent: %.3fs' % running_time)
    output.append(('running_time', running_time))
    if G.exit_when_found and G.finished:
        print(sty.ef.b + 'Analysis stopped after vulnerability is found. Only the first few CF paths are kept.' + sty.rs.all)
    vul_files = list(map(lambda p: os.path.relpath(p, G.entry_file_path), G.vul_files))
    #print(sty.ef.b + f'Vulnerable files: {vul_files}' + sty.rs.all)
    if not args.json:
        print(sty.fg.li_magenta + sty.ef.b +
            f'Number of CF Paths: {G.num_of_cf_paths}' + sty.rs.all)
        print(sty.fg.li_magenta + sty.ef.b +
            f'Number of Preceding CF Paths: {G.num_of_prec_cf_paths}' + sty.rs.all)
        print(sty.fg.li_magenta + sty.ef.b +
            f'Number of Full CF Paths: {G.num_of_full_cf_paths}' + sty.rs.all)
    output.append(("Vulnerable files", vul_files))
    output.append(("Number of CF Paths", G.num_of_cf_paths))
    output.append(("Number of Preceding CF Paths", G.num_of_prec_cf_paths))
    output.append(("Number of Full CF Paths", G.num_of_full_cf_paths))
    cf_edges = G.get_edges_by_types(['FLOWS_TO', 'ENTRY', 'EXIT'])
    real_cf_counter = 0
    for e in cf_edges:
        l0 = G.get_node_attr(e[0]).get('labels:label')
        if l0 is None or l0.startswith('Artificial'):
            continue
        l1 = G.get_node_attr(e[1]).get('labels:label')
        if l1 is None or l1.startswith('Artificial'):
            continue
        real_cf_counter += 1
    call_edges = G.get_edges_by_type('CALLS')
    real_ce_counter = 0
    real_call_edges = []
    for e in call_edges:
        l0 = G.get_node_attr(e[0]).get('labels:label')
        if l0 is None or l0.startswith('Artificial'):
            continue
        l1 = G.get_node_attr(e[1]).get('labels:label')
        if l1 is None or l1.startswith('Artificial'):
            continue
        real_ce_counter += 1
        real_call_edges.append(e)

    # try:
    #     graph_for_export = export_data_flow_subgraph(G, res_pathes)
    #     nx.write_gexf(graph_for_export, os.path.join(os.path.dirname(G.entry_file_path), "relevant_subgraph.gexf"))
    # except Exception as e:
    #     print(e, file=sys.stderr)
    #     print("Failed to write gexf for " + G.entry_file_path, file=sys.stderr)
    #     #raise(e)



    if not args.json:
        print(sty.fg.li_magenta +
                f'Number of CF Edges: ' + sty.rs.all + f'{len(cf_edges)}')
        print(sty.fg.li_magenta +
                f'Number of Real CF Edges: ' + sty.rs.all + f'{real_cf_counter}')
        print(sty.fg.li_magenta +
                f'Number of Call Edges: ' + sty.rs.all + f'{len(call_edges)}')
        print(sty.fg.li_magenta +
                f'Number of Real Call Edges: ' + sty.rs.all + f'{real_ce_counter}')
    output.append((f'Number of CF Edges: ',len(cf_edges)))
    output.append((f'Number of Real CF Edges: ',real_cf_counter))
    output.append((f'Number of Call Edges: ',len(call_edges)))
    output.append((f'Number of Real Call Edges: ',real_ce_counter))
    output.append((f"additional_files", [os.path.relpath(f, G.entry_file_path) for f in G.additional_files]))
    # print(real_call_edges)
    covered_stmt = len(G.covered_stat)
    total_stmt = G.get_total_num_statements()
    # print(sty.fg.li_yellow + f'Code coverage: ' + sty.rs.all + 
    #         f'{covered_stmt / total_stmt * 100:.2f}%'
    #         + f' {covered_stmt}/{total_stmt}'
    #         )
    if not args.json:
        print(sty.fg.li_magenta + f'Number of Dynamically Resolvable Calls: ' +
                                sty.rs.all + f'{len(G.dynamic_calls)}')
        print(sty.fg.li_magenta + f'Number of Statically Resolvable Calls: ' +
                                sty.rs.all + f'{len(G.static_calls)}')
        print(sty.fg.li_magenta + f'Number of Unresolvable Calls: ' +
                                sty.rs.all + f'{len(G.unresolvable_calls)}')
        print(sty.fg.li_magenta + f'Number of Function Calls: ' +
                                sty.rs.all + f'{len(G.total_calls)}')
        print(sty.fg.li_magenta + f'Number of Rerun: ' +
                                sty.rs.all + f'{G.rerun_counter}')
    output.append(('Number of Dynamically Resolvable Calls: ', len(G.dynamic_calls)))
    output.append(('Number of Statically Resolvable Calls: ', len(G.static_calls)))
    output.append(('Number of Unresolvable Calls: ', len(G.unresolvable_calls)))
    output.append(('Number of Function Calls: ', len(G.total_calls)))
    output.append(('Number of Rerun: ', G.rerun_counter))

    class SpecialEncoder(json.JSONEncoder):
        def default(self, o: Any) -> Any:
            if isinstance(o, _SpecialValue):
                return f"_SpecialValue({o.alt})"
            if isinstance(o, set):
                return list(o)
            if isinstance(o, typing.Callable):
                return o.__name__
            if isinstance(o, NodeHandleResult):
                return f"NodeHandleResult {str(o)}"
            else:
                return json.JSONEncoder.default(self, o)
    if not args.skipprint:
        json.dump(dict(output), sys.stdout, cls=SpecialEncoder)
        print()

    return G


def module_mode_analyze(G, input_file, additional_files=set(), scripts=None):
    #ps_script = get_post_install_script_require(G)

    script = "var main_func=require('{}');\n".format(input_file)

    spawn_base = "const __rogue_one_spawn = require('child_process').spawn;\n"
    spawn_flag = False
    spawn_template = "__rogue_one_spawn('{}');\n"
    require_template = "require('{}');\n"
    require_re = re.compile(r"([\w_\-/]+\.js)")
    require_n_re = re.compile(r"node ([\w_\-/]+\.js)")
    G.fully_matched_scripts = set()
    if scripts:
        for k in ['preinstall', 'install', 'postinstall']:
            if k in scripts:
                s = scripts[k]
                res2 = require_re.fullmatch(s)
                res1 = require_n_re.fullmatch(s)
                if res1 or res2:
                    res = res1 if res1 else res2
                    fn = res.group(1)
                    if k.startswith('pre'):
                        script = require_template.format(fn) + script
                    else:
                        script =  script + require_template.format(fn)
                    G.fully_matched_scripts.add(k)
                else:
                    spawn_flag = True
                    #script = spawn_template.format(s) + script
    if spawn_flag:
        #script = spawn_base + script
        pass
    G.additional_files = additional_files
    additional_script = "\n".join(
        [f"{add_func_name} = require('{str((Path(input_file) / l).absolute())}');" for l in
         G.additional_files])
    script = script + "\n" + additional_script
    analyze_string(G, script, generate_graph=True)


def generic_generate_paths(G, logger, output):
    return None
    logger.debug(sty.ef.inverse + G.vul_type + sty.rs.all)
    res_path = traceback(G, G.vul_type)
    logger.debug('ResPath0:')
    logger.debug(res_path[0])
    logger.debug('ResPath1:')
    logger.debug(res_path[1])
    res_pathes = vul_checking(G, res_path[0], G.vul_type)
    # print(res_pathes)
    output.append(("res_pathes", res_pathes))
    node_set = set()
    for p in res_pathes:
        for n in p:
            node_set.add(n)
            attrs = G.get_node_attr(n)
            if 'callees' in attrs:
                node_set.update(attrs['callees'])
    node_attrs = {}
    for n in node_set:
        node_attrs[n] = G.get_node_attr(n)
    output.append(("node_attrs", node_attrs))
    res_path_list = []
    for path in res_pathes:
        res_text_path = get_path_text(G, path, path[0])
        res_path_list.append(res_text_path)
        # "Attack Path: ")
        # print(res_text_path)
    if len(res_pathes) != 0:
        with open('vul_func_names.csv', 'a') as fp:
            logger.log(ATTENTION, f'{G.vul_type} successfully found in '
                                  f'{G.entry_file_path} at main?')
            fp.write(f'{G.vul_type},"{G.entry_file_path}","main","",{len(res_path)}\n')
        G.success_detect = True
    return res_pathes


def export_data_flow_subgraph(G, res_pathes):
    gexf_types = [int, float, bool, list, dict, str]
    # New subgraph construction
    # First, build the set of all relevant callsites
    all_nodes = set()
    callsites = [path[-1] for path in res_pathes]
    # Add all elements of the result path to the set of nodes
    for path in res_pathes:
        all_nodes = all_nodes.union(path)

    # Get all AST_CALL_TO_FUNC_OBJ edges
    for node in list(all_nodes):
        all_nodes = all_nodes.union(
            G.get_child_nodes(node, edge_type='AST_CALL_TO_FUNC_OBJ')
        )

    # Add all nodes of objects that affect nodes in the result path or are names of nodes in the result path.
    size = len(all_nodes)
    new_nodes = all_nodes.copy()
    back_edge_types = ['OBJ_REACHES', 'OBJ_TO_AST', 'NAME_TO_OBJ', 'AST_CALL_TO_FUNC_OBJ', 'OBJ_TO_PROP', 'AST_REQUIRE_TO_OBJ']
    forward_edge_types = [ 'AST_CALL_TO_FUNC_OBJ']

    saved_possible_requires = dict()
    for cs in callsites:
        for u,v,weight, edge_attrs in G.get_out_edges(cs, edge_type='AST_CALL_TO_FUNC_OBJ'):
            if v in saved_possible_requires:
                possible_requires = saved_possible_requires[v]
            else:
                possible_requires = find_where_the_func_is_imported(G, v)
                saved_possible_requires[v] = possible_requires
            if not possible_requires or len(possible_requires[0]) == 0:
                continue
            lib_names, require_nodes = possible_requires
            for idx, require_node_id in enumerate(require_nodes):
                all_nodes.add(require_node_id)
                G.add_edge(u, require_node_id, {'type:TYPE': 'AST_TO_LIB_REQUIRE', 'lib_name': lib_names[idx]})
                G.add_edge(v, require_node_id, {'type:TYPE': 'FUNC_OBJ_TO_LIB_REQUIRE', 'lib_name': lib_names[idx]})


    while True:
        for node in list(new_nodes):
            new_nodes = new_nodes.union(
                G.get_ancestors_in(node,
                                   edge_types=back_edge_types,
                                   step=1)
            )
            for et in forward_edge_types:
                new_nodes = new_nodes.union(
                    G.get_child_nodes(node, edge_type=et)
                )
        all_nodes = all_nodes.union(new_nodes)
        new_nodes = set()

        if size == len(all_nodes):
            break
        else:
            size = len(all_nodes)

    for edge in G.graph.edges(data=True):
        if edge[0] in all_nodes and edge[1] in all_nodes:
            attrs = edge[2]
            if attrs['type:TYPE'] == 'OBJ_REACHES':
                for k in ['obj', 'obj_ast_def']:
                    if k in attrs:
                        all_nodes.add(attrs[k])
            if 'scope' in attrs:
                all_nodes.add(attrs['scope'])

    # Add all AST nodes - we need access to all the code.
    [all_nodes.add(n[0]) for n in G.graph.nodes(data=True) if 'labels:label' in n[1] and n[1]['labels:label'] == 'AST']

    # For each callsite, attempt to find the target
    graph_for_export = G.graph.subgraph(all_nodes).copy()
    for node_id, attrs in graph_for_export.nodes(data=True):
        # Mark the callsites:


        # TODO: Mark static sources
        # TODO: Mark dynamic sources (return value of unknown function?)
        # TODO: Mark sinks
        if node_id in callsites:
            attrs['rogue_one_callsite'] = (node_id in callsites)


        # TODO: If a node has just one name node, and that name node has just one target object... contract them?

        # Get rid of non printable attrs
        for k in list(attrs):
            v = attrs[k]
            if type(v) in [set, tuple]:
                v = list(v)
                attrs[k] = v
            if type(v) == list:
                # The write gexf feature assumes that any list is a gexf dynamic https://gexf.net/dynamics.html
                # This does not work for us.
                # the gexf liststring type is not accessible through networkx as far as I can tell.
                # see readwrite/gexf.py:242

                if len(v) == 0:
                    del attrs[k]
                elif len(v) == 1:
                    attrs[k] = v[0]
                    v = v[0]
                else:
                    v = dict(enumerate(v))
                    attrs[k] = v

            if type(v) not in gexf_types:
                if type(v) == _SpecialValue:
                    attrs[k] = '_SpecialValue: ' + str(v)
                else:
                    del attrs[k]
            elif k in ['callees', 'parent_scope_this', 'pythonfunc', "lineno:int", "endlineno:int", "classname", "doccomment"] or \
                        v is None or v == "":
                del attrs[k]

            #elif type(v) == list:
                #del attrs[k]
            if k in attrs and type(attrs[k]) == float:
                if math.isnan(attrs[k]):
                    attrs[k] = "NaN"
                else:
                    attrs[k] = str(int(attrs[k]))
            if k in attrs and type(attrs[k]) == str:
                attrs[k] = "".join(ch for ch in attrs[k] if unicodedata.category(ch)[0]!="C")
        # Set labels
        if 'code' in attrs and type(attrs['code']) != str:
            attrs['code'] = str(attrs['code'])

        if 'name' in attrs:
            attrs['label'] = attrs['name']
        elif 'code' in attrs:
            attrs['label'] = attrs['code']
        elif 'names' in attrs:
            attrs['label'] = attrs['names']
        elif 'type' in attrs:
            attrs['label'] = attrs['type']

    # Get rid of non-printable attrs
    for source, dest, attrs in graph_for_export.edges(data=True):
        attrs['label'] = attrs.get('type:TYPE', '')

        for k in list(attrs):
            v = attrs[k]
            if type(v) not in gexf_types:
                # print(k, ': ', v, type(v))
                del attrs[k]
            elif type(v) == list and len(v) == 1:
                attrs[k] = v[0]
            elif type(v) == list:
                del attrs[k]


    return graph_for_export

def get_post_install_script_require(G):
    package_json_path = os.path.join(G.entry_file_path, "package.json")
    if not os.path.exists(package_json_path):
        return ""

    with open(package_json_path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return ""
        ps_str = data.get("scripts", {}).get("postinstall", "")
        ps_file_re = re.compile(r"(\w+\.js)")
        m = ps_file_re.search(ps_str)
        if not m:
            return ""
        ps_file_path = os.path.join(G.entry_file_path, m.group())

    return f"require('{ps_file_path}');\n"

add_func_name = "additional_func"
def get_additional_requires_from_file(G):
    additional_requires_path = os.path.join(G.entry_file_path, "..", "rogue_one_additional_files.txt")
    try:
        with open(additional_requires_path) as f:
            add_files = f.readlines()
    except:
        add_files = []
    return [os.path.join(G.entry_file_path, l.strip()) for l in  add_files]
