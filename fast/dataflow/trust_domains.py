import sys
from typing import Tuple, Callable, Union, Dict, Any, List
import networkx as nx

import fast.simurun
from .extraction import ObjTypes
from ..simurun.utilities import _SpecialValue
import fast.simurun.graph as graph
from pathlib import Path
import re

prop_td_attr = 'prop_tds'
td_attr = 'trust_domain'
l_td = ':local'
c_td = ':caller'
sys_td = ':sys'
req_td = ':dyn:require'
eval_td = ':dyn:eval'
doc_td = ':sys:frontend:document'
enc_td = ':encoding'
proc_td = 'process'
td_down_edges = ['CONTRIBUTES_TO', 'FUNC_OBJ_TO_RET_VAL', 'PARENT_TO_CHILD']
td_prop_edges = ['PARENT_TO_CHILD', 'FUNC_OBJ_TO_RET_VAL']
local_path = Path(__file__).parent.parent

rel_set = set[tuple[str, str]]
td_map_type = dict[tuple[str,str],list[tuple[str,str]]]
def edge_filter_subgraph(g: nx.Graph, edge_types: list[str]) -> nx.Graph:
    return nx.subgraph_view(g,
                            filter_edge=lambda u, v: (
                                    g.get_edge_data(u, v)['type'] in edge_types)
                            )
any_graph = Union[nx.DiGraph, nx.Graph]
def deny_edge(g: any_graph, u: str, v: str):
    return False
def allow_edge(g: any_graph, u: str, v: str):
    return True
def no_builtin_dest(g: any_graph, u: str, v: str):
    return not g.nodes[v].get('builtin_name')
def edge_filter_subgraph_pred(g: nx.Graph, edge_pred_map: dict[str, Callable[[any_graph, str, str], bool]]):
    return nx.subgraph_view(g,
                            filter_edge = lambda u, v: (
                                edge_pred_map.get(g.get_edge_data(u,v)['type'], deny_edge)(g,u,v)
                            ))
def set_node_td(g: nx.DiGraph, n: str):
    attrs = g.nodes[n]
    obj_type = attrs.get('obj_type')
    attrs[prop_td_attr] = dict() # prop_tds is a map from td -> root -> shortest path from root td to that node
    if not obj_type:
        return
    ast_defs = [e[1] for e in g.out_edges(n, data=True) if e[2].get('type') == 'OBJ_TO_AST']

    if attrs.get(td_attr):
        pass
    elif ast_defs and g.nodes[ast_defs[0]].get('filename') and \
            Path(g.nodes[ast_defs[0]].get('filename')).is_relative_to(local_path):
        p = Path(g.nodes[ast_defs[0]].get('filename'))
        attrs[td_attr] = p.name[0:-3] # Is a builtin from builtin_packages/

    elif obj_type in [ObjTypes.Static, ObjTypes.Container] and not (attrs['type'] == 'function' and attrs.get('pythonfunc'))\
            and not (len(ast_defs) > 0 and (g.nodes[ast_defs[0]].get('artificial') or
                                            g.nodes[ast_defs[0]].get('filename') == 'stdin' or
                                            g.nodes[ast_defs[0]].get('type') == 'AST_TOPLEVEL')
                                            ):
        if obj_type == ObjTypes.Container:
            attrs[td_attr] = l_td + ':obj:' + str(attrs.get('code', ''))
        elif obj_type == ObjTypes.Static:
            attrs[td_attr] = l_td + ':' + str(attrs.get('code', ''))
    elif obj_type == ObjTypes.ExportParam:
        attrs[td_attr] = c_td
    elif obj_type == ObjTypes.Require:
        require_defs = [e[2].get('module_name') for e in g.in_edges(n, data=True) if e[2].get('type') == 'AST_REQUIRE_TO_OBJ' and
                        e[2].get('module_name') and
                        '/' not in e[2].get('module_name')]
        if require_defs:
            attrs[td_attr] = require_defs[0]

    return attrs.get(td_attr)


def apply_td_roots(g: nx.Graph):
    tds = set([set_node_td(g, n) for n in g.nodes])
    if None in tds:
        tds.remove(None)
    return tds

def prop_td_spread(g: nx.DiGraph):
    roots = [n[0] for n in g.nodes(data=True) if n[1].get(td_attr) not in  {None, req_td, eval_td}]
    for n in roots:
        prop_edges = td_prop_edges#['PARENT_TO_CHILD'] if g.nodes[n]['obj_type'] == ObjTypes.Builtin else td_prop_edges
        prop_sg = edge_filter_subgraph(g, prop_edges)
        # prop_sg = edge_filter_subgraph_pred(g,
        #                                     {
        #                                         'PARENT_TO_CHILD': no_builtin_dest,
        #                                         'CALL_EFFECT': allow_edge
        #                                     })
        visited = set()
        cur_td = g.nodes[n][td_attr]
        node_queue: list[tuple[str, tuple[str]]] = [(n, tuple([n]))]
        while node_queue:
            m, path = node_queue.pop()
            # if m in visited or g.nodes[m].get('pythonfunc') in ['eval', 'require']:
            #     continue
            visited.add(m)
            # if g.nodes[m]['obj_type'] == ObjTypes.Builtin:
            #     continue


            if cur_td not in g.nodes[m][prop_td_attr]:
                g.nodes[m][prop_td_attr][cur_td] = {}
            if n not in g.nodes[m][prop_td_attr][cur_td]:
                g.nodes[m][prop_td_attr][cur_td][n] = path
            if len(path) < len(g.nodes[m][prop_td_attr][cur_td][n]):
                g.nodes[m][prop_td_attr][cur_td][n] = path

            # The escape hatches below prevent trust domain 'leakage' from built-in objects
            # across built-in prototypes into target package objects
            # Eg., :sys:frontend:document should propagate through document to document.createElement and to
            # return values of document.createElement, but not through document to document.forms to
            # document.forms.__proto__, which is Array.prototype, then to document.forms.__proto__.join and further
            # to every result of an array join.
            for u, v, attrs in prop_sg.out_edges(m, data=True):
                if attrs.get('type') == 'PARENT_TO_CHILD':
                    # if cur_td == enc_td and m == n:
                    #     continue
                    #if cur_td[0] == ':' and not cur_td.startswith(l_td) and g.nodes[v].get('builtin_name'):
                    if g.nodes[v].get('builtin_name'):
                         continue
                    # elif cur_td in [doc_td, proc_td] and not g.nodes[u]['builtin_name'] and g.nodes[v][
                    #     'builtin_name']:
                    #     continue
                    if False and (g.nodes[n].get('obj_type') != ObjTypes.Builtin
                          and g.nodes[v].get('obj_type') == ObjTypes.Builtin):
                        continue

                if v not in visited:
                    node_queue.append((v, path + tuple([v])))
def add_td_rel_to_map(td_map: td_map_type, td_a: str, td_b: str, root_node: str, arrival_node: str, down_path, prop_path):
    key = (td_a, td_b)
    if key not in td_map:
        td_map[key] = []
    td_map[key].append((down_path, prop_path))

def td_rel_map(g: nx.DiGraph, scripts=None, fully_handled_scripts=set(), consolidate_tds=False, odgen_graph=None):
    tds = apply_td_roots(g)
    tds.add(c_td)
    tds.add(l_td)
    prop_td_spread(g)

    # Initialize data structures
    #dict from td -> set of tds
    td_map: td_map_type = dict()
    def add_td_rel(td_a: str, td_b: str, root_node: str, arrival_node: str, down_path: tuple, prop_path: tuple):
        add_td_rel_to_map(td_map, td_a, td_b, root_node, arrival_node, down_path, prop_path)
        if not g.nodes[arrival_node].get('td_rel_paths'):
            g.nodes[arrival_node]['td_rel_paths'] = {}
        if not g.nodes[arrival_node]['td_rel_paths'].get(cur_td):
            g.nodes[arrival_node]['td_rel_paths'][cur_td] = []
        g.nodes[arrival_node]['td_rel_paths'][cur_td].append(down_path)

    # dict from td -> set of visited nodes
    visited: dict[str, set[str]] = dict((td, set()) for td in tds)
    # Annotate install scripts if present
    if scripts:
        tds.add('install_scripts')
        for k in ['preinstall', 'install', 'postinstall']:
            if k in scripts and (not odgen_graph or k not in odgen_graph.fully_matched_scripts):
                td_map[(l_td,'install_scripts')]= [('0', '0')]

    for n in g.nodes:
        if g.nodes[n].get('exported'):
            # if n is exported, any prop_td or root td there is connected to the caller td
            for td in g.nodes[n].get(prop_td_attr, {}):
                for td_root_node in g.nodes[n][prop_td_attr][td]:
                    add_td_rel(c_td, td, td_root_node, n, (td_root_node, n), (td_root_node, n))
            if g.nodes[n].get(td_attr):
                add_td_rel(c_td, g.nodes[n][td_attr], n, n, (n, n), (n, n))

        cur_td = g.nodes[n].get(td_attr)
        # TODO: there could still be prop_tds we need to propogate down
        if not cur_td or cur_td == req_td:
            continue
        if 'pythonfunc' in g.nodes[n]:
            if g.nodes[n]['pythonfunc'] == 'handle_require':
                continue
        # We perform bfs from every root
        node_queue = [(n, tuple([n]))]
        while node_queue:
            m, path_to_m = node_queue.pop()

            if m in visited[cur_td] and not (n == m and g.nodes[n].get('obj_type') == ObjTypes.APIRetVal):
                continue
            if 'pythonfunc' in g.nodes[m]:
                if g.nodes[m]['pythonfunc'] == 'handle_require':
                    continue
            visited[cur_td].add(m)
            if g.nodes[m].get(td_attr) and not g.nodes[m].get('builtin_name'):
                add_td_rel(cur_td, g.nodes[m][td_attr], n, m, path_to_m, tuple([m]))

            for prop_td in g.nodes[m][prop_td_attr]:
                prop_td_root_list = g.nodes[m][prop_td_attr][prop_td]
                for ptdr in prop_td_root_list:
                    prop_path = prop_td_root_list[ptdr]
                    edge_pairs = zip(prop_path, prop_path[1:])
                    edge_names = [prop_td]
                    for ep in edge_pairs:
                        ep_attr = g.edges[ep]
                        t = ep_attr.get('type')
                        if t == 'PARENT_TO_CHILD':
                            name = ep_attr.get('name')
                            if name or isinstance(name, int):
                                edge_names.append(str(ep_attr.get('name')))
                            else:
                                print(f"WARNING: PARENT_TO_CHILD edge with no name: {ep}")
                        elif t == 'FUNC_OBJ_TO_RET_VAL':
                            pass
                        else:
                            pass

                    #edge_names = [str(g.edges[ep].get('name')) for ep in edge_pairs]
                    #edge_names.insert(0, prop_td)
                    full_prop_td = '.'.join(edge_names)
            # if (True or not g.nodes[m].get('api_return_obj')) or n == m:
            #     for e in g.out_edges(m, data=True):
            #         # The main phase 2 propagation mechanism is through CONTRIBUTES_TO edges.
            #         # However, consider this example.
            #         # var lib = require('lib');
            #         # lib.readdir(process.argv[2]);
            #         # The process trust domain must propagate through to lib.readdir, but not to the prototype.
            #         if e[1] not in visited[cur_td] and (
            #                 e[2]['type'] in td_down_edges or
            #                 (e[2]['type'] in td_prop_edges and not (False and g.nodes[n].get('obj_type') != ObjTypes.Builtin
            #                                                     and g.nodes[e[1]].get('obj_type') == ObjTypes.Builtin)
            #                     and not (g.nodes[e[1]].get('builtin_name'))
            #                 )
            #         ):
            #             node_queue.append(e[1])
                    if not g.nodes[m].get('builtin_name'):
                        add_td_rel(cur_td, full_prop_td, ptdr, m, path_to_m, tuple(prop_path))
            if True or g.nodes[m].get('obj_type') != ObjTypes.APIRetVal or n == m:
                for e in g.out_edges(m, data=True):
                    if (e[2]['type'] in td_down_edges or (e[2]['type'] == 'PARENT_TO_CHILD' and e[2].get('name') not in ['__proto__', 'prototype', 'hasOwnProperty', 'constructor'])) and e[1] not in visited[cur_td]:
                        node_queue.append((e[1], path_to_m + tuple([e[1]])))


    # For each node n:
        # Annotate if n is exported
        # If this node has no td_attr, or it is require, move on.
        # let cur_td be the td from this node
        # If this node is the handle_require function, move on.
        # Initialize node_queue to [n]
        # Popping m from node_queue:
            # Annotate that at node m, cur_td reaches m td? from ?
            # continue if m has already been visited by cur_td
            # If m is not an APIRetVal or n is m
                # append the td_down_edge descendents of m to the queue

    # At node A, trust domain X reaches trust domain Y from root node B


    # td_1 in td_man[td_2] ==> td_2 sends data to td_1
    apply_filters(td_map)
    if consolidate_tds:
        return consolidate_rel_map_tds(td_map)
    # if odgen_graph:
    #     for rel in td_map:
    #         for id_pair in td_map[rel]:
    #             for i in id_pair:
    #                 if not code_loc_for_id(odgen_graph, i):
    #                     print(f"No code loc for {i}")

    return td_map

def generalize_local_td(td: str) -> str:
    if td.startswith(l_td):
        return l_td
    return td
def generalize_local_rel(pair: tuple[str, str]) -> tuple[str, ...]:
    return tuple([generalize_local_td(a) for a in pair])
def aggregated_local_td_rel_map(g: nx.DiGraph, scripts=None, odgen_graph=None):
    m = td_rel_map(g, scripts=scripts, odgen_graph=odgen_graph)
    td_map: td_map_type = dict()

    for k in m:
        td_a, td_b = generalize_local_rel(k)
        if td_a == td_b:
            continue
        for node_pair in m[k]:
            add_td_rel_to_map(td_map, td_a, td_b, None, None, node_pair[0], node_pair[1])

    return td_map

def code_loc_for_id(g: graph.Graph, n: str) -> str:
    ast_edges = g.get_out_edges(n, edge_type='OBJ_TO_AST')
    if ast_edges:
        ast_node = ast_edges[0][1]
        ast_attrs = g.get_node_attr(ast_node)
        code_loc = ast_attrs.get('namespace', '')
        file = ast_attrs.get('filename')
        localPath = Path(__file__).parent.parent
        if file and Path(file).is_relative_to(g.entry_file_path):
            relfile = str(Path(file).relative_to(g.entry_file_path))
        elif file and Path(file).is_relative_to(localPath):
            relfile = f'JS-Modeled Builtin Package: {Path(file).relative_to(localPath)}'
        elif file:
            relfile = file
        else:
            relfile = ''
        return relfile + ':' + code_loc
    elif n in g.named_builtin_map:
        return "Builtin object: " + g.named_builtin_map[n]
    else:
        return ''



def apply_filters(td_map: dict[tuple[str,str], list[tuple[str,str]]]):
    # Given trust domain td, we don't care that it reaches itself
    for rel in list(td_map.keys()):
        if rel[0] == rel[1] or (rel[0].startswith(l_td) and rel[1].startswith(l_td)):
            del td_map[rel]
            continue
        if rel[0].startswith(c_td) and rel[1].startswith(l_td):
            del td_map[rel]
            continue
        if rel[0].startswith(rel[1]) or rel[1].startswith(rel[0]):
            del td_map[rel]
            continue

        occurrences = set(td_map[rel])
        td_map[rel] = list(occurrences)
        # if l_td in td_map[td]:
        #     td_map[td].remove(l_td)

    # Remove trust domains we have no rels for
    removals = []
    for rel in td_map:
        if len(td_map[rel]) == 0:
            removals.append(rel)
    for r in removals:
        del td_map[r]

def rels_as_tuples(m: dict[str, set[str]]) -> set[tuple[str, str]]:
    result = set()
    for k in m:
        s = m[k]
        for td in s:
            result.add((k, td))
    return result

def flagged_rels_from_tuples(before_tuples: rel_set, after_tuples: rel_set) -> rel_set:
    if before_tuples and type(list(before_tuples)[0][0]) == tuple or after_tuples and type(list(after_tuples)[0][0]) == tuple:
        before_tuples = set([a[0] for a in before_tuples])
        after_tuples = set([a[0] for a in after_tuples])
    return after_tuples.difference(before_tuples)
# Propagation rules:
# An ExportParam is caller - BASE
# A Static is local - BASE
# A child <- parents - Along PARENT_TO_CHILD
# any object <- contributors - Along CONTRIBUTES_TO
# APIRetVal <- Contributors - Along CONTRIBUTES_TO
# APIRetVal <- Called Func Object - Along FUNC_OBJ_TO_RET_VAL
# CallbackParam <- called func object - CONTRIBUTES_TO


def generalize_to_old_locals_rel(rel, old_locals):
    first = generalize_local_td(rel[0]) if rel[0] in old_locals else rel[0]
    second = generalize_local_td(rel[1]) if rel[1] in old_locals else rel[1]
    return first, second

def generalize_new_td(td: str) -> str:
    if td.startswith(l_td):
        return l_td + ":new"
    else:
        return td
def generalize_to_new_locals_rel(rel):
    first = generalize_new_td(rel[0])
    second = generalize_new_td(rel[1])
    return first, second

def flagged_new_local_rels_from_tuples(before_tuples: rel_set, after_tuples: rel_set) -> rel_set:
    old_locals = set()
    old_local_rels = set()
    before_rels = [a[0] for a in before_tuples]
    for rel, _ in before_tuples:
        for td in rel:
            if td.startswith(l_td):
                old_local_rels.add(generalize_local_rel(rel))
                old_locals.add(td)

    result = set()
    for rel, _ in after_tuples:
        if rel in before_tuples:
            continue
        elif generalize_to_old_locals_rel(rel, old_locals) in old_local_rels:
            continue
        elif generalize_to_new_locals_rel(rel) not in before_rels:
            result.add(generalize_to_new_locals_rel(rel))
    return result

def apply_rel_filters(rels: rel_set) -> rel_set:
    res = set()
    for a, b in rels:
        if a.startswith(l_td) and (b.startswith(l_td) or b == c_td):
            continue
        elif b.startswith(l_td) and (a.startswith(l_td) or a == c_td):
            continue
        else:
            res.add((a, b))
    return res
def flagged_single_local_rels_from_tuples(before_tuples: rel_set, after_tuples: rel_set) -> rel_set:
    if before_tuples and type(list(before_tuples)[0][0]) == tuple or after_tuples and type(list(after_tuples)[0][0]) == tuple:
        before_tuples = set([a[0] for a in before_tuples])
        after_tuples = set([a[0] for a in after_tuples])
    f_before = set([generalize_local_rel(r) for r in before_tuples])
    f_after = set([generalize_local_rel(r) for r in after_tuples])
    return apply_rel_filters(flagged_rels_from_tuples(f_before, f_after))
def suspicious(before_idg, after_idg, scripts=None):
    return apply_rel_filters(flagged_rels_from_tuples(rels_as_tuples(td_rel_map(before_idg)),
                                    rels_as_tuples(td_rel_map(after_idg, scripts=scripts))))

def sanitize_and_export(g: nx.Graph, path):
    for n in g.nodes:
        to_del = ['defined_in', prop_td_attr]
        if g.nodes[n].get(td_attr):
            g.nodes[n]['label'] = str(n) + ": " +  g.nodes[n].get(td_attr)

        for k in ['code', 'obj_type']:
            g.nodes[n][k] = str(g.nodes[n].get(k))

        for k in g.nodes[n]:
            if type(g.nodes[n][k]) in [set, _SpecialValue, tuple, list, type(suspicious), type(None), dict] or g.nodes[n][k] in [None, _SpecialValue]:
                g.nodes[n][k] = ''
                to_del.append(k)
        for k in to_del:
            if k in g.nodes[n]:
                del g.nodes[n][k]

    i = 0
    for e in g.edges(data=True):
        e[2]['label'] = e[2].get('type')
        to_del = ['defined_in', prop_td_attr]

        for k in e[2]:
            if type(e[2][k]) in [set, _SpecialValue, tuple, list, type(suspicious), type(None), dict] or e[2][k] in [None, _SpecialValue]:
                e[2][k] = ''
                to_del.append(k)
        for k in to_del:
            if k in e[2]:
                del e[2][k]
        e[2]['id'] = str(i)
        i = i+1
        pass
    sg = g.subgraph([n for n in g.nodes if 'AST' not in g.nodes[n].get('type', '') and 'AST' not in g.nodes[n].get('type:TYPE', '')])
    nx.write_graphml(sg, path, edge_id_from_attribute='id')


def code_locs_from_rel_map(odg: fast.simurun.graph.Graph,
                           rel_map: dict[tuple[str, str],list[tuple[str,str]]]) -> dict[str,str]:
    m = {}
    for k in rel_map:
        for root, target in rel_map[k]:
            m[str(root)] = code_loc_for_id(odg, root)
            m[str(target)] = code_loc_for_id(odg, target)
    return m

sq = "'([^']+)'"
dq = "\"([^\"]+)\""
tuple_parsers = [re.compile(f"\({sq}, {sq}\)"),
re.compile(f"\({sq}, {dq}\)"),
re.compile(f"\({dq}, {sq}\)"),
re.compile(f"\({dq}, {dq}\)"),
re.compile(f"\({dq}, '(:local):.*\)"),
re.compile(f"\({sq}, '(:local):.*\)"),
re.compile(f"\('(:local):.*, {dq}\)"),
re.compile(f"\('(:local):.*, {sq}\)"),
re.compile(f"\({dq}, \"(:local):.*\)"),
re.compile(f"\({sq}, \"(:local):.*\)"),
re.compile(f"\(\"(:local):.*, {dq}\)"),
re.compile(f"\(\"(:local):.*, {sq}\)"),
                 ]
# Filter a full rel_map with AST node numbers to a simpler map for cross package analysis
def rel_map_to_cross_package_map(rel_map: dict[tuple[str,str],list[tuple[str,str]]],
                                 consolidate_tds=True, err_mark='') -> dict:
    result = dict()
    for k in rel_map:
        orig_k = k
        if type(k) == str:
            ks = None
            for p in tuple_parsers:
                ks = p.findall(k)
                if ks:
                    k = ks[0]
                    break
            if not ks:
                sys.stderr.write(f"Warning! {err_mark}: Dropping rel {k} due to parsing failure!\n")
                continue
        if consolidate_tds:
            new_k = generalize_local_rel(k)
        else:
            new_k = k
        result[new_k] = rel_map[orig_k]
    return result

def consolidate_td(td:str) -> str:
    return td.split('.')[0]
def consolidate_rel_map_tds(rel_map: td_map_type) -> td_map_type:
    new_map: td_map_type = {}
    for rel in rel_map:
        new_rel = (consolidate_td(rel[0]), consolidate_td(rel[1]))
        if new_rel not in new_map:
            new_map[new_rel] = []
        for tup in rel_map[rel]:
            new_map[new_rel].append(tup)

    return new_map
def rel_map_to_cross_package_set(rel_map: dict[tuple[str,str],list[tuple[str,str]]],
                                 consolidate_tds=True, err_mark='') -> set[tuple[str,str]]:
    return set(rel_map_to_cross_package_map(rel_map, consolidate_tds=consolidate_tds, err_mark=err_mark).keys())
