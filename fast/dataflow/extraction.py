from functools import cache

from fast.simurun.graph import Graph
from fast.simurun.utilities import _SpecialValue
import networkx as nx
from enum import Enum
from itertools import chain
from fast.simurun.opgen import builtin_path
# Assume get_calls_to_non_local is totes working
# Then get the ancestors for those calls in the CONTRIBUTES_TO subgraph

def callsite_nodes(g: Graph) -> list[str]:
    nodes = g.get_calls_to_non_local()
    #nodes = [n for n in nodes if (g.graph.nodes[n].get('filename', 'stdin') != 'stdin' or
    #                              g.get_node_file_path(n) != 'stdin')]
    return nodes

def edge_filter_subgraph(g: nx.Graph, edge_types: list[str]) -> nx.Graph:
    return nx.subgraph_view(g,
                            filter_edge=lambda u, v, k: (
                                    g.get_edge_data(u, v, k)['type:TYPE'] in edge_types))
def nodes_with_code(g: nx.Graph, code) -> list[str]:
    return [n[0] for n in g.nodes(data=True) if type(n[1].get('code')) == str and code in n[1]['code']]

def df_subgraph(g: nx.Graph) -> nx.Graph:
    return edge_filter_subgraph(g, edge_types=["CONTRIBUTES_TO"])
def return_obj_for_callsite(g: Graph, cs: str) -> set[str]:
    # Get a list of objects created at this callsite
    objs_from_ast = [e[0] for e in g.graph.in_edges(cs, data=True) if e[2].get('type:TYPE') == 'OBJ_TO_AST']
    called_func_objects = [e[1] for e in g.get_out_edges(cs, edge_type='AST_CALL_TO_FUNC_OBJ')]
    called_func_object_children = [g.get_out_edges(o, edge_type='FUNC_OBJ_TO_RET_VAL') for o in set(called_func_objects)]
    result = set()
    for child_children in called_func_object_children:
        for child_child in child_children:
            if child_child[1] in objs_from_ast:
                result.add(child_child[1])
    #local_objects = [l for l in local_objects if l in referred_objects and l not in called_func_objects]
    return result

@cache
def callsite_return_objs(g: Graph) -> set[str]:
    return_obj_lists = map(lambda x: return_obj_for_callsite(g, x), callsite_nodes(g))
    return set(chain(*return_obj_lists))

def sources_for_ret_obj(g: Graph, ret: str):
    df_sg = df_subgraph(g.graph)
    return nx.ancestors(df_sg, ret)
def source_objs_for_callsite(g: Graph, cs:str):
    ret_obj = list(return_obj_for_callsite(g, cs))[0]
    return sources_for_ret_obj(g, ret_obj)

class ObjTypes(Enum):
    Static = 1
    ExportParam = 2
    CallbackParam = 3
    APIRetVal = 4
    Require = 5
    Container = 6
    Child = 7
    Builtin = 8
    Other = 99

def ast_parent(g: Graph, n):
    parents = [e[0] for e in g.graph.in_edges(n, data=True) if e[2]['type:TYPE'] == 'PARENT_OF']
    assert len(parents) == 1
    return parents[0]

def ast_for_obj(g: Graph, n):
    ast_def = [e[1] for e in g.graph.out_edges(n, data=True) if e[2]['type:TYPE'] == 'OBJ_TO_AST']
    assert len(ast_def) == 1
    return ast_def[0]

# def set_require_obj_types(g: Graph) -> None:
#     req_nodes = [e[1] for e in g.graph.edges(data=True) if e[2].get('type:TYPE') == 'AST_REQUIRE_TO_OBJ']
#     for n in req_nodes:
#         attrs = g.graph.nodes[n]
#         if not 'fake_arg' in attrs:
#             attrs['obj_type'] = ObjTypes.Require

def obj_type(g: Graph, n: str) -> ObjTypes:
    node = g.graph.nodes[n]
    if node.get('obj_type'):
        return node['obj_type']
    if node.get('fake_arg') == 'export':
        return ObjTypes.ExportParam
    elif node.get('fake_arg') == 'callback':
        return ObjTypes.CallbackParam
    else:
        ast_defs = [e[1] for e in g.graph.out_edges(n, data=True) if e[2].get('type:TYPE') == 'OBJ_TO_AST']
        # require_defs = [e[0] for e in g.graph.in_edges(n, data=True) if e[2].get('type:TYPE') == 'AST_REQUIRE_TO_OBJ']
        # if len(require_defs) > 0:
        #     return ObjTypes.Require
        if ast_defs and 'Artificial' not in g.graph.nodes[ast_defs[0]].get('labels:label', ''):
            ast_def_type = g.graph.nodes[ast_defs[0]].get('type')
            if ast_def_type == 'AST_ARRAY':
                return ObjTypes.Container
            elif ast_def_type == 'AST_NEW':
                return ObjTypes.APIRetVal
            elif node.get('code') and node.get('code') != _SpecialValue('*'):
                return ObjTypes.Static
            elif node.get('name') == '{anon}' and node.get('type') == 'function':
                return ObjTypes.Static
            elif ast_def_type == 'AST_METHOD_CALL' and \
                    node.get('type') == 'object' and node.get('code') == _SpecialValue('*') \
                    and n in return_obj_for_callsite(g, ast_defs[0]):
                return ObjTypes.APIRetVal
        elif n in g.named_builtin_map:
            return ObjTypes.Builtin
        # elif g.get_parent_object_def(n)[0]:
        #     return ObjTypes.Child
        elif n in callsite_return_objs(g):
            return ObjTypes.APIRetVal
        elif int(n) <= g.last_builtin_id:
            return ObjTypes.Builtin
    return ObjTypes.Other
        # if node.get('type') == 'string' and type(node.get('code')) == str and ast_defs and\
    #         node.get('code') in g.graph.nodes[ast_defs[0]].get('code'):
    #     return ObjTypes.Static
    # elif node.get('type') == 'function' and ast_def_type == 'AST_CLOSURE':
    #     return ObjTypes.Static
    # elif node.get('type') == 'number' and ast_def_type in ['integer']:
    #     return ObjTypes.Static

    # A node can be SpecialValue * but still be a require node.

flag_values = [
    'TOPLEVEL_FILE',
    'JS_DECL_VAR',
    'JS_REQUIRE_EXTERNAL',
    'NAME_NOT_FQ',
]
def extract_idg(g: Graph) -> nx.Graph:
    exG = nx.DiGraph()

    # First, carry over the AST.
    # Second, bring the callsite return object nodes over.
    # Third, from each callsite return object, walk up the CONTRIBUTES_TO tree and add those edges and nodes.

    deferred_edges = []
    all_attrs = {}
    for n in g.graph.nodes(data=True):
        all_attrs.update(n[1])

    ast_nodes = [n for n in g.graph.nodes(data=True) if 'AST' in n[1].get('labels:label', '')]
    for n in ast_nodes:
        old_attrs = n[1]

        new_attrs = {
            'type': old_attrs['type'],
            'code': old_attrs.get('code'),
            'childnum': old_attrs.get('childnum:int'),
            'nearest_func_def': old_attrs.get('funcid:int'),
            'code_loc': old_attrs.get('namespace'),
            'doccoment': old_attrs.get('doccomment'),
            'artificial': 'Artificial' in old_attrs.get('labels:label'),
            'filename': g.get_node_file_path(n[0]),
        }
        if 'AST' not in new_attrs['type']:
            new_attrs['type'] = 'AST_' + new_attrs['type']
        #for k in new_attrs:
        #    if not new_attrs[k]:
        #        del new_attrs[k]
        exG.add_node(n[0], **new_attrs)
        exports = old_attrs.get('module_exports', [])
        if exports:
            for export_id in exports:
                deferred_edges.append((n[0], export_id, {'type': 'AST_TO_MODULE_EXPORT'}))
    for u,v,attrs in [e for e in g.graph.edges(data=True) if e[2]['type:TYPE'] == 'PARENT_OF']:
        if u in exG.nodes and v in exG.nodes:
            attrs['type'] = attrs['type:TYPE']
            exG.add_edge(u,v,**attrs)

    visited = {}
    node_queue = []

    node_queue.extend(callsite_return_objs(g))
    exported_objs = [n[0] for n in g.graph.nodes(data=True) if n[1].get('exported')]
    node_queue.extend(exported_objs)

    require_result_objs = [e[1] for e in g.graph.edges(data=True) if e[2].get('type:TYPE') == 'AST_REQUIRE_TO_OBJ']
    req_res_set = set(require_result_objs)
    node_queue.extend(require_result_objs)

    def add_obj_node(n, **attrs):
       # if n in g.graph.nodes:
       #     return
        old_attrs = g.graph.nodes[n]
        for k in ['code', 'defined_in', 'name', 'exported', 'tainted', 'trust_domain']:
            if k in old_attrs:
                attrs[k] = old_attrs[k]
        t = old_attrs.get('type:TYPE') or old_attrs.get('type') or old_attrs.get('labels:label')
        if 'pythonfunc' in old_attrs:
            attrs['pythonfunc'] = old_attrs['pythonfunc'].__name__
        if n in req_res_set:
            attrs['obj_type'] = ObjTypes.Require
        else:
            attrs['obj_type'] = obj_type(g, n)
        attrs['builtin_name'] = g.named_builtin_map[n] if n in g.named_builtin_map else None
        exG.add_node(n, type=t, **attrs)

    [add_obj_node(n, api_return_obj=True) for n in node_queue]
    visited = set()
    while len(node_queue) > 0:
        n = node_queue.pop()
        if n in visited:
            continue
        visited.add(n)
        in_e = g.graph.in_edges(n, data=True)
        out_e = g.graph.out_edges(n, data=True)

        for e in in_e:
            # TODO: Consider the effect here of having both CONTRIBUTES_TO and PARENT_TO_CHILD edges to
            # between two nodes.  Need to shift CONTRIBUTES_TO to add_edge_if_not_exists
            # or shift to multidigraph
            t = e[2]['type:TYPE']
            if t == 'CONTRIBUTES_TO':
                add_obj_node(e[0], )
                node_queue.append(e[0])
                exG.add_edge(e[0], e[1], type=t)

            elif t == 'AST_REQUIRE_TO_OBJ':
                exG.add_edge(e[0], e[1], type=t, module_name=e[2].get('module_name'))

            elif t == 'FUNC_OBJ_TO_RET_VAL':
                add_obj_node(e[0])
                node_queue.append(e[0])
                exG.add_edge(e[0], e[1], type=t)

            elif t == 'FUNC_OBJ_TO_SYM_PARAM':
                add_obj_node(e[0])
                node_queue.append(e[0])
                exG.add_edge(e[0], e[1], type='CONTRIBUTES_TO')

        for e in out_e:
            t = e[2]['type:TYPE']
            if t == 'OBJ_TO_AST':
                exG.add_edge(n, e[1], type=t)
        # Just as parents are handled, handle children.
            if t == 'OBJ_TO_PROP':
                mid = e[1]
                second_legs = g.get_out_edges(mid, edge_type='NAME_TO_OBJ')
                for sl in second_legs:
                    # What does it mean if an edge has the attribute 'kind': None?
                    prop_obj = sl[1]
                    add_obj_node(prop_obj)
                    node_queue.append(prop_obj)
                    exG.add_edge(n, prop_obj, type='PARENT_TO_CHILD', name=g.graph.nodes[mid].get('name'))

        parents = g.get_parent_object_def(n)
        for parent_trio in zip(*parents):
            if not parent_trio:
                continue
            parent_obj, _, name_obj = parent_trio
            add_obj_node(parent_obj)
            node_queue.append(parent_obj)
            exG.add_edge(parent_obj, n, type='PARENT_TO_CHILD', name=g.graph.nodes[name_obj].get('name'))

    for u,v,attrs in deferred_edges:
        if u not in exG.nodes:
            add_obj_node(u)
        if v not in exG.nodes:
            add_obj_node(v)
        if 'type:TYPE' in attrs:
            attrs['type'] = attrs['type:TYPE']
            del attrs['type:TYPE']
        exG.add_edge(u,v,**attrs)

    return exG
