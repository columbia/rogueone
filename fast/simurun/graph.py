import typing
from functools import cache, lru_cache

import networkx as nx
import sys
import csv

import psutil as psutil
import sty
import io
import logging
import json
from typing import DefaultDict, List, Callable, Optional
from .utilities import BranchTag, BranchTagContainer, DictCounter
from .utilities import _SpecialValue, wildcard
from .logger import *
import uuid
from itertools import chain
from collections import defaultdict, deque
from queue import PriorityQueue
import time

class Graph:

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.cur_objs = []
        self.cur_scope = None
        self.cur_func = None # deprecated
        self.cur_id = 0
        self.entry_file_path = None # for logging purpose only
        self.file_contents = {}
        self.logger = create_logger("graph_logger", level=logging.FATAL, output_type="file")
        self.mark_taint_vals = ['JSCPG_MARK_TAINT']
        self.cpg_node_cache = {}

        # for obj entry point info
        self.store_entry_point_info = True
        self.cur_file_path = None # deprecated, use G.get_cur_file_path() for other uses
        self.cur_entry_point = 'main'

        # for evaluation
        self.covered_num_stat = 0
        self.total_num_stat = 0
        self.covered_stat = set()
        self.all_stat = set()
        self.all_func = set()
        self.covered_func = set()
        self.prev_code_coverage = None
        self.prev_code_coverage_time = None
        self.timed_out_by_code_coverage = False

        # exit immediately when vulnerability is found
        self.finished = False
        self.exit_when_found = False
        self.func_start_time = None
        self.time_limit_reached = False

        # JS internal values
        self.function_prototype = None
        self.object_prototype = None
        self.array_prototype = None
        self.number_prototype = None
        self.string_prototype = None
        self.boolean_prototype = None
        self.regexp_prototype = None
        self.promise_prototype = None
        
        self.builtin_constructors = []
        self.builtin_prototypes = []

        # scope name counter
        self.scope_counter = DictCounter()

        # contains a list of node ids based on the ast id
        self.call_stack = [] # deprecated, only for debugging
        self.for_stack = [] # for debugging
        self.caller_counter = DictCounter() # callers (instead of callees)
        self.caller_stack = []
        self.call_limit = 3 # 3
        self.file_stack = []
        self.require_obj_stack = []
        self.cur_stmt = None # for building data flows
        self.function_returns = defaultdict(lambda: [])

        # Python-modeled built-in modules
        self.builtin_modules = {}

        # prototype pollution
        self.check_proto_pollution = False
        self.proto_pollution = set()
        self.func_entry_point = None

        # internal property tampering
        self.check_ipt = False
        self.ipt_write = set()
        self.ipt_use = set()

        self.run_all = True
        self.no_file_based = False
        self.call_graph_dist = False
        self.two_pass = False
        self.first_pass = False
        self.coarse_only = False
        self.cf_guided = False
        self.finished_num_of_passes = 0
        self.possible_cf_nodes = set()
        self.allowed_exported_funcs = set()
        self.vul_files = set()
        self.function_time_limit = None
        self.single_branch = False
        self.print = False
        self.interactive = False
        self.output_status = False
        # new trace rule (experimental): dummy funcs have dummy stmts
        self.new_trace_rule = False
        self.cf_searches = set()

        # self.func_call_queue = PriorityQueue() # removed
        self.cur_func_call = None
        self.stack1 = []
        self.stack2 = []
        self.rerun_counter = 0
        self.unresolvable_calls = set()
        self.dynamic_calls = set()
        self.static_calls = set()
        self.total_calls = set()
        # self.vul_files_ast = set() # entry points

        self.vul_type = None

        self.exec_counter_limit = 100

        # source code taint highlighting
        self.obj_to_ast = defaultdict(lambda: DictCounter())
        self.highlighted_obj_nodes = set()

        # constraint solver
        self.solve_from = None
        # self.solve_for = None
        self.solve_mode = 0
        self.reverse_names = defaultdict(set) # for logging purpose only
        self.extra_constraints = []
        self.auto_exploit = False
        self.cur_source_name = None

        self.success_detect = False
        self.success_exploit = False

        # control flow & data flow
        self.last_stmts = []
        self.num_of_cf_paths = 0
        self.num_of_prec_cf_paths = 0
        self.num_of_full_cf_paths = 0
        self.dont_quit = False
        self.scope_stack = [] # abandoned

        # task queues
        self.task_queue = deque()
        self.microtask_queue = deque()

        # self.array_obj_node_limit = 1e10
        # self.op_obj_node_limit = 1e10
        # self.op_value_limit = 1e10

        self.array_obj_node_limit = 200
        self.op_obj_node_limit = 200
        self.op_value_limit = 1000

        self.num_of_ast_nodes = None

        csv.field_size_limit(2 ** 31 - 1)
        class joern_dialect(csv.excel_tab):
            doublequote = False
            escapechar = '\\'
        self.csv_dialect = joern_dialect

        self.graph_op_timing = DefaultDict(float)
        self.graph_op_num_of_times = DefaultDict(int)
        self.graph_op_timing_recent = DefaultDict(float)
        self.graph_op_num_of_times_recent = DefaultDict(int)
        self.last_timing_reset_time = None
        self.graph_start_time = time.time()
        self.pass_start_time = time.time()
        self.solver_time = 0

        # Benign builtins for whitelisting
        self.benign_builtins: set[str] = set()
        self.additional_files = []
        self.skipped_files = set()
        self.file_node_nums = dict()
        self.named_builtin_map: dict[str, str] = dict()
        self.last_builtin_id: Optional[int] = None

        # optimizations
        self.name_nodes = set()
        self.toplevel_file_nodes = None
        self.affected_name_nodes = []

        # debug only
        self.cg_paths = []
        self.cf_paths = []
        self.last_time = 0
        self.last_handled = None
        self.last_handled_lineno = None

        self.mem_limit = 20 * 1000 * 1000 * 1000 # 20GB

    def timing(self, op, t):
        return
        self.graph_op_timing[op] += t
        self.graph_op_num_of_times[op] += 1
        self.graph_op_timing_recent[op] += t
        self.graph_op_num_of_times_recent[op] += 1
        if self.last_timing_reset_time is None:
            self.last_timing_reset_time = time.time()
        elif time.time() - self.last_timing_reset_time > 2:
            print(
                sty.ef.inverse + sty.fg.yellow + 'Graph size' +
                sty.rs.all + f' {self.graph.number_of_nodes()} {self.graph.number_of_edges()}'
                + f' {time.time() - self.graph_start_time:.2f}s')
            print( ' ' * 31 +
                sty.ef.inverse + sty.fg.yellow + 'Cumulative' + sty.rs.all + '                   ' +
                sty.ef.inverse + sty.fg.yellow + 'Recent' + sty.rs.all 
                + f' {time.time() - self.last_timing_reset_time:.2f}s')
            for k in sorted(self.graph_op_timing.keys()):
                print(f'{k:30s} {self.graph_op_timing[k]:6.2f}s {self.graph_op_num_of_times[k]:7d}x avg.{int(self.graph_op_timing[k]/self.graph_op_num_of_times[k]*1e6):5d}us ' + 
                        (f'{self.graph_op_timing_recent[k]:.2f}s {self.graph_op_num_of_times_recent[k]:6d}x avg.{int(self.graph_op_timing_recent[k]/self.graph_op_num_of_times_recent[k]*1e6):5d}us'
                            if self.graph_op_num_of_times_recent[k] != 0  else ''))
            self.last_timing_reset_time = time.time()
            self.graph_op_timing_recent.clear()
            self.graph_op_num_of_times_recent.clear()

    # Basic graph operations

    # node

    def _get_new_nodeid(self):
        """
        return a nodeid
        """

        if self.cur_id % 100000 == 0:
            self.check_mem()
        self.cur_id += 1
        return str(self.cur_id - 1)
        # return str(uuid.uuid4().int)

    def add_node(self, node_for_adding, attr={}):
        self.graph.add_node(node_for_adding, **attr)
        return node_for_adding

    def add_node_from_list(self, node_list):
        return self.graph.add_nodes_from(node_list)

    def set_node_attr(self, node_id, attr):
        """
        attr should be a tuple like (key, value)
        will be added to a node id
        """
        self.graph.nodes[node_id][attr[0]] = attr[1]

    def get_node_attr(self, node_id):
        """
        this function will return a dict with all the attrs and values
        """
        assert node_id is not None
        return self.graph.nodes[node_id]

    def get_all_nodes(self):
        """
        return all nodes in the form of dict
        """
        return self.graph.nodes

    def get_nodes_by_type(self, node_type, data=True):
        """
        return a list of nodes with a specific node type
        as tuples of node id and attrs
        """
        return [node for node in self.graph.nodes(data=data) if node[1].get('type') == node_type]

    def get_nodes_by_type_and_flag(self, node_type, node_flag, data=True):
        """
        return a list of nodes with a specific node type and flag
        """
        return [node[0] for node in self.graph.nodes(data=data) if node[1].get('type') == node_type and node[1].get('flags:string[]') == node_flag]

    def get_node_by_attr(self, key, value):
        """
        get a list of node by key and value
        """
        return [node[0] for node in self.graph.nodes(data = True) if key in node[1] and node[1][key] == value]

    def get_require_nodes(self, data=True):
        return [a for a in self.graph.nodes(data=True) if 'flags:string[]' in a[1] and 'REQUIRE' in a[1]['flags:string[]'] ]

    def get_non_require_calls(self, data=True):
        return [a for a in self.graph.nodes(data=True) if
                ('type' in a[1] and a[1]['type'] in ['AST_METHOD_CALL','AST_CALL']) and
                ((not 'flags:string[]' in a[1]) or ('REQUIRE' not in a[1]['flags:string[]']))
                ]

    def edge_filter(self, excluded_edge_list):
        def wf(u, v, attrs):
            attrs = attrs[0]
            if 'type:TYPE' in attrs and attrs['type:TYPE'] in excluded_edge_list:
                return None
            else:
                return 1
        return wf

    #@cache
    def get_local_func_objects(self):
        all_funcs = self.get_node_by_attr('type', 'function')
        local_funcs = []
        for f in all_funcs:
            if self.is_local_func_object(f):
                local_funcs.append(f)
        return local_funcs

    def is_local_func_object(self, n: str):
        out_edges = self.get_out_edges(n, edge_type='OBJ_TO_AST')
        if not out_edges:
            attrs = self.get_node_attr(n)
            if 'target_func' in attrs:
                return self.is_local_func_object(attrs['target_func'])
        ast_node = out_edges[0][1]
        data = self.get_node_attr(ast_node)
        # TODO: Check file path of definition node and validate that it is defined within the local package
        if ('labels:label' in data and data['labels:label'] == 'Artificial_AST') or \
                ('type' in data and data['type'] in ['AST_TOPLEVEL', 'AST_METHOD_CALL', 'AST_CALL']):
            return False
        return True

    #@cache
    def get_local_func_calls(self):
        objs = self.get_local_func_objects()
        calls = set()

        for obj in objs:
            def_ast_node = self.get_obj_def_ast_node(obj)
            if def_ast_node is None:
                continue
            ast_attrs = self.get_node_attr(def_ast_node)
            if not ('type' in ast_attrs and ast_attrs['type'] == 'AST_FUNC_DECL') and \
                    not ('type' in ast_attrs and ast_attrs['type'] == 'AST_CLOSURE' and 'alias' in ast_attrs):
                continue
            scopes = [e[1] for e in self.get_out_edges(obj, edge_type='OBJ_TO_SCOPE')]
            for s in scopes:
                callers = [c[1] for c in self.get_out_edges(s, edge_type='SCOPE_TO_CALLER')]
                for c in callers:
                    calls.add(c)
        return calls


    @cache
    def get_calls_to_non_local(self):
        result = set()
        for n in self.graph.nodes(data=True):
            attrs = n[1]
            n_id = n[0]
            if attrs.get('type') in ['AST_METHOD_CALL', 'AST_CALL'] and\
                ((not 'flags:string[]' in attrs) or ('REQUIRE' not in attrs['flags:string[]'])) and\
                    n_id not in self.get_local_func_calls():
                result.add(n_id)
        return result

    def remove_nodes_from(self, remove_list):
        """
        remove a list of nodes from the graph
        """
        self.graph.remove_nodes_from(remove_list)

    def relabel_nodes(self):
        """
        relabel all the nodes to a uuid to make the graph globaly useful
        """
        mapping = {}
        for node in self.graph.nodes():
            # make a random uuid
            mapping[node] = str(uuid.uuid4().int)

        self.graph = nx.relabel_nodes(self.graph, mapping)
    
    # edges

    def add_edge(self, from_ID, to_ID, attr):
        """
        insert an edge to graph
        attr is like {key: value, key: value}
        """
        assert from_ID is not None, "Failed to add an edge, from_ID is None."
        assert to_ID is not None, "Failed to add an edge, to_ID is None."
        assert from_ID != 'string' and to_ID != 'string'
        assert from_ID != wildcard
        assert to_ID != wildcard
        # self.graph.add_edges_from([(from_ID, to_ID, attr)])
        self.graph.add_edge(from_ID, to_ID, None, **attr)
    
    def add_edge_if_not_exist(self, from_ID, to_ID, attr):
        """
        insert an edge to the graph if the graph does not already has the same edge
        """
        assert from_ID is not None, "Failed to add an edge, from_ID is None."
        assert to_ID is not None, "Failed to add an edge, to_ID is None."
        assert from_ID != wildcard
        assert to_ID != wildcard
        if not self.graph.has_edge(from_ID, to_ID):
            self.add_edge(from_ID, to_ID, attr)
        else:
            for key, edge_attr in self.graph[from_ID][to_ID].items():
                if edge_attr == attr:
                    self.logger.debug("Edge {}->{} exists: {}, {}. Duplicate edge "
                    "will not be created.".format(from_ID,to_ID,key,edge_attr))
                    return
            self.add_edge(from_ID, to_ID, attr)

    def set_edge_attr(self, from_ID, to_ID, edge_id, attr):
        self.graph[from_ID][to_ID][attr[0]][edge_id] = attr[1]

    def get_edge_attr(self, from_ID, to_ID, edge_id = None):
        if edge_id == None:
            return self.graph.get_edge_data(from_ID, to_ID)
        return self.graph[from_ID][to_ID][edge_id]

    def add_edges_from_list(self, edge_list):
        return self.graph.add_edges_from(edge_list)

    def add_edges_from_list_if_not_exist(self, edge_list):
        for e in edge_list:
            if len(e) != 3:
                self.logger.error("Length of the edge tuple {} is not 3".format(e))
                continue
            self.add_edge_if_not_exist(*e)

    def get_edges_by_type(self, edge_type):
        """
        return the edges with a specific type
        """
        subEdges = [edge for edge in self.graph.edges(data = True, keys=True) if edge[3]['type:TYPE'] == edge_type]
        return subEdges

    def get_edges_by_types(self, edge_types):
        subEdges = [edge for edge in self.graph.edges(data = True, keys=True) if edge[3]['type:TYPE'] in edge_types]
        return subEdges

    def get_edges_between(self, u, v, edge_type = None) -> dict:
        result = {}
        for key, edge_attr in self.graph[u][v].items():
            if not edge_type or edge_attr.get('type:TYPE') == edge_type:
                result[key] = edge_attr
        return result

    def remove_edge(self, u, v, key=None):
        self.graph.remove_edge(u, v, key)

    def remove_all_edges_between(self, u, v):
        while True:
            try:
                self.graph.remove_edge(u, v)
            except nx.NetworkXError:
                break

    def get_out_edges(self, node_id, data = True, keys = True, edge_type = None):
        assert node_id is not None
        if edge_type is None:
            return self.graph.out_edges(node_id, data = data, keys = keys)
        idx = 2
        if keys:
            idx = 3
        if not data:
            data='type:TYPE'
            edges = self.graph.out_edges(node_id, data=data, keys=keys)
            return [edge for edge in edges if edge[idx] == edge_type]

        edges = self.graph.out_edges(node_id, data = data, keys = keys)
        return [edge for edge in edges if 'type:TYPE' in edge[idx] and edge[idx]['type:TYPE'] == edge_type]

    def get_in_edges(self, node_id, data = True, keys = True, edge_type = None):
        assert node_id is not None
        if edge_type is None:
            return self.graph.in_edges(node_id, data = data, keys = keys)
        idx = 2
        if keys:
            idx = 3
        if not data:
            data='type:TYPE'
            edges = self.graph.in_edges(node_id, data=data, keys=keys)
            return [edge for edge in edges if edge[idx] == edge_type]

        edges = self.graph.in_edges(node_id, data = data, keys = keys)
        return [edge for edge in edges if 'type:TYPE' in edge[idx] and edge[idx]['type:TYPE'] == edge_type]

    def get_sub_graph_by_edge_type(self, edge_type):
        """
        only keep edges with specific type
        return a sub graph
        """
        subEdges = self.get_edges_by_type(edge_type)
        return nx.MultiDiGraph(subEdges)

    def test_code_from_if_elem(self, if_node: str) -> Optional[str]:
        outs = self.get_out_edges(if_node, 'PARENT_OF')
        if len(outs) < 1:
            return None

        outs = self.get_out_edges(list(outs)[0][1], edge_type="PARENT_OF")
        if len(outs) < 1:
            return None

        return list(outs)[0][1]

    def set_if_elems_code_to_test(self) -> None:
        ifs = self.get_nodes_by_type('AST_IF_ELEM')
        for if_elem_id, if_elem_attrs in ifs:
            code_node = self.test_code_from_if_elem(if_elem_id)
            if code_node:
                code_node_attrs = self.get_node_attr(code_node)
                self.get_node_attr(if_elem_id)['code'] = code_node_attrs['code']

        ifs = self.get_nodes_by_type('AST_IF')
        for if_elem_id, if_elem_attrs in ifs:
            outs = list(self.get_out_edges(if_elem_id, edge_type='PARENT_OF'))
            if len(outs) > 0:
                test_node_attrs = self.get_node_attr(outs[0][1])
                if if_elem_attrs['code'] in [None, '']:
                    if_elem_attrs['code'] = test_node_attrs['code']


    def get_ancestors_in(self, node_id, edge_types=None, node_types=None,
        candidates=None, step=1):
        '''
        Deprecated
        '''
        results = []
        if step > 1:
            _candidates = None
        else:
            _candidates = candidates
        for edge_type in edge_types:
            for e in self.get_in_edges(node_id, edge_type=edge_type):
                node = e[0]
                if _candidates is not None and node not in _candidates:
                    continue
                if node_types is not None and \
                    self.get_node_attr(node).get('type') not in node_types:
                    continue
                if step == 1:
                    results.append(node)
                else:
                    results.extend(self.get_ancestors_in(node, edge_types,
                        node_types, candidates, step - 1))
        return results

    # traversal

    def dfs_edges(self, source, depth_limit = None):
        """
        Iterate over edges in a depth-first-search (DFS).
        """
        return nx.dfs_edges(self.graph, source, depth_limit)

    def has_path(self, source, target):
        '''
        Return True if there is a path from source to target, False
        otherwise.
        '''
        return nx.algorithms.shortest_paths.generic.has_path(
            self.graph, source, target)

    # import/export

    def import_from_string(self, string):
        try:
            nodes, rels = string.split('\n\n')[:2]
        except ValueError as e:
            self.logger.error('AST generation failed!')
            raise e
        with io.StringIO(nodes) as fp:
            reader = csv.DictReader(fp, dialect=self.csv_dialect)
            for row in reader:
                if 'id:ID' not in row:
                    continue
                cur_id = row['id:ID']
                self.add_node(cur_id)
                for attr, val in row.items():
                    if attr == 'id:ID': continue
                    self.set_node_attr(cur_id, (attr, val))

        with io.StringIO(rels) as fp:
            reader = csv.DictReader(fp, dialect=self.csv_dialect)
            edge_list = []
            for row in reader:
                attrs = dict(row)
                try:
                    del attrs['start:START_ID']
                except:
                    continue
                del attrs['end:END_ID']
                edge_list.append((row['start:START_ID'], row['end:END_ID'], attrs))
            self.add_edges_from_list(edge_list)
        self.logger.info(sty.ef.inverse + "Finished Importing" + sty.rs.all)

        # self.relabel_nodes()
        # reset cur_id
        self.cur_id = self.graph.number_of_nodes()
        # print('cur_id is reset to', self.cur_id)

        if self.num_of_ast_nodes is None:
            self.num_of_ast_nodes = self.graph.number_of_nodes()
        
        self.prev_code_coverage_time = None
        
        self.toplevel_file_nodes = \
            self.get_nodes_by_type_and_flag('AST_TOPLEVEL', 'TOPLEVEL_FILE')
        self.set_if_elems_code_to_test()


    def import_from_CSV(self, nodes_file_name, rels_file_name, offset=0):
        with open(nodes_file_name) as fp:
            reader = csv.DictReader(fp, dialect=self.csv_dialect)
            for row in reader:
                cur_id = row['id:ID']
                self.add_node(cur_id)
                for attr, val in row.items():
                    if attr == 'id:ID': continue
                    self.set_node_attr(cur_id, (attr, val))

        with open(rels_file_name) as fp:
            reader = csv.DictReader(fp, dialect=self.csv_dialect)
            edge_list = []
            for row in reader:
                attrs = dict(row)
                del attrs['start:START_ID']
                del attrs['end:END_ID']
                edge_list.append((row['start:START_ID'], row['end:END_ID'], attrs))
            self.add_edges_from_list(edge_list)
        self.logger.info(sty.ef.inverse + "Finished Importing" + sty.rs.all)
    
        # self.relabel_nodes()
        # reset cur_id
        self.cur_id = self.graph.number_of_nodes()

        if self.num_of_ast_nodes is None:
            self.num_of_ast_nodes = self.graph.number_of_nodes()
        
        self.prev_code_coverage_time = None
        
        self.toplevel_file_nodes = \
            self.get_nodes_by_type_and_flag('AST_TOPLEVEL', 'TOPLEVEL_FILE')

    def export_to_CSV(self, nodes_file_name, rels_file_name, light = False):
        """
        export to CSV to import to neo4j
        """
        with open(nodes_file_name, 'w') as fp:
            headers = ['id:ID','labels:label','type','flags:string[]','lineno:int','code','childnum:int','funcid:int','classname','namespace','endlineno:int','name','doccomment']
            writer = csv.DictWriter(fp, dialect=self.csv_dialect, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            nodes = list(self.graph.nodes(data = True))
            # for node in nodes:
            #     if type(node[0]) != str:
            #         print(node)
            nodes.sort(key = lambda x: int(x[0]))
            for node in nodes:
                node_id, attr = node
                try:
                    if int(node_id) >= self.num_of_ast_nodes:
                        break
                except ValueError:
                    pass
                row = dict(attr)
                row['id:ID'] = node_id
                writer.writerow(row)

        with open(rels_file_name, 'w') as fp:
            headers = ['start:START_ID','end:END_ID','type:TYPE','var','taint_src','taint_dst']
            writer = csv.DictWriter(fp, dialect=self.csv_dialect, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            light_edge_type = ['FLOWS_TO', 'REACHES', 'OBJ_REACHES', 'ENTRY', 'EXIT']
            edges = []
            if light:
                for edge_type in light_edge_type:
                    edges += self.get_edges_by_type(edge_type)
            else:
                edges = list(self.graph.edges(data = True, keys = True))
            for edge in edges:
                edge_from, edge_to, _, attr = edge
                try:
                    if (int(edge_from) >= self.num_of_ast_nodes
                            or int(edge_to) >= self.num_of_ast_nodes):
                        continue
                except ValueError:
                    pass
                # if attr['type:TYPE'] not in ['FLOWS_TO', 'CALLS']:
                if attr['type:TYPE'] not in ['CALLS']:
                    continue
                row = dict(attr)
                row['start:START_ID'] = edge_from
                row['end:END_ID'] = edge_to
                writer.writerow(row)

        self.logger.info("Finished Exporting to {} and {}".format(nodes_file_name, rels_file_name))

    def testing_benchmark_export_graph(self, file_path):
        """
        export graph to pickle format
        """
        nx.readwrite.write_gpickle(self.graph, file_path)
        
    def export_graph(self, file_path):
        """
        export graph to pickle format
        """
        self.relabel_nodes()
        nx.readwrite.write_gpickle(self.graph, file_path)

    def import_graph(self, file_path):
        """
        import a graph from a exported file
        """
        with open(file_path, 'r') as fp:
            dict_graph = json.load(fp)
            
        self.graph = nx.Graph(dict_graph)

    def recount_cur_id(self):
        self.cur_id = 0
        for node in self.graph.nodes:
            node_id = int(self.get_node_attr(node).get('id:ID'))
            if node_id >= self.cur_id:
                self.cur_id = node_id + 1

    def clear(self):
        self.graph.clear()
        self.cur_objs = []
        self.cur_scope = None
        self.cur_id = 0
        self.file_contents = {}

        # initialize all variables, holy shit!

        self.finished = False
        self.first_pass = False

        self.stack1 = []
        self.stack2 = []

        # for evaluation    # CF-filtered run cannot cover all code # ??
        self.covered_num_stat = 0
        self.total_num_stat = 0
        self.covered_stat = set()
        self.all_stat = set()
        self.all_func = set()
        self.covered_func = set()
        self.prev_code_coverage = None
        self.prev_code_coverage_time = None

        # JS internal values
        self.function_prototype = None
        self.object_prototype = None
        self.array_prototype = None
        self.number_prototype = None
        self.string_prototype = None
        self.boolean_prototype = None
        self.regexp_prototype = None
        self.promise_prototype = None
        
        self.builtin_constructors = []
        self.builtin_prototypes = []
    
        # scope name counter
        self.scope_counter = DictCounter()

        self.call_stack = [] # deprecated, only for debugging
        self.for_stack = [] # for debugging
        self.caller_counter = DictCounter() # callers (instead of callees)
        self.caller_stack = []
        self.call_limit = 1 # 3
        self.file_stack = []
        self.require_obj_stack = []
        self.function_returns = defaultdict(lambda: [])
    
        # Python-modeled built-in modules
        self.builtin_modules = {}

        # prototype pollution
        self.proto_pollution = set()
        # internal property tampering
        self.ipt_write = set()
        self.ipt_use = set()

        # source code taint highlighting
        self.obj_to_ast = defaultdict(lambda: DictCounter())
        self.highlighted_obj_nodes = set()

        # constraint solver
        self.reverse_names = defaultdict(set) # for logging purpose only
        self.extra_constraints = []
        
        # control flow & data flow
        self.last_stmts = []

        # task queues
        self.task_queue = deque()
        self.microtask_queue = deque()

        # optimizations
        self.name_nodes = set()
        self.toplevel_file_nodes = None
        self.affected_name_nodes = []

    # AST & CPG

    def _get_childern_by_childnum(self, node_id):
        """
        helper function, get the childern nodeid of the node_id
        return a dict, with {childnum: node_id}
        """
        edges = self.get_out_edges(node_id, edge_type = "PARENT_OF")
        res = {}
        for edge in edges:
            node_attr = self.get_node_attr(edge[1])
            if 'childnum:int' not in node_attr:
                continue
            res[node_attr['childnum:int']] = edge[1]
        return res

    def get_ordered_ast_child_nodes(self, node_id):
        """
        return AST children of a node in childnum order
        """
        if isinstance(node_id, typing.Hashable):
            return self.cached_ast_child_nodes(node_id)
        children = sorted(self._get_childern_by_childnum(node_id).items(),
                            key=lambda x: int(x[0]))
        if children:
            children = list(zip(*children))[1]
        return children
        # children = sorted([(x[1], self.get_node_attr(x[1]).get('childnum:int')) for x in
        #  self.get_out_edges(node_id, edge_type='PARENT_OF')], key=lambda x:int(x[1]))
        # return [c[0] for c in children if c[1]]
    @lru_cache(maxsize=1024)
    def cached_ast_child_nodes(self, node_id):
        """
        return AST children of a node in childnum order
        """
        children = sorted(self._get_childern_by_childnum(node_id).items(),
                            key=lambda x: int(x[0]))
        if children:
            children = list(zip(*children))[1]
        return children
        # children = sorted([(x[1], self.get_node_attr(x[1]).get('childnum:int')) for x in
        #  self.get_out_edges(node_id, edge_type='PARENT_OF')], key=lambda x:int(x[1]))
        # return [c[0] for c in children if c[1]]


    def get_child_nodes(self, node_id, edge_type=None, child_name=None,
        child_type=None, child_label=None):
        """
        Return children of the node (with a specific edge type, name,
        node label, or node type).
        """
        if edge_type is None and child_name is None and child_type is None \
                and child_label is None:
            return list(self.graph.successors(node_id))
        res = set()
        edges = self.get_out_edges(node_id, edge_type=edge_type)
        for edge in edges:
            aim_node_attr = self.get_node_attr(edge[1])
            if child_type is not None and aim_node_attr.get('type') != child_type:
                continue
            if child_name is not None and aim_node_attr.get('name') != child_name:
                continue
            if child_label is not None and aim_node_attr.get('labels:label') != child_label:
                continue
            res.add(edge[1])
        return list(sorted(res))

    get_successors = get_child_nodes

    def get_name_from_child(self, nodeid, max_depth=None, order=0, funcName=False):
        """
        try to find the name of a nodeid
        we have to use bfs strategy
        """
        bfs_queue = []
        visited = set()
        bfs_queue.append((nodeid, 0))

        while(len(bfs_queue)):
            cur_node, cur_depth = bfs_queue.pop(0)
            if max_depth and cur_depth > max_depth: break
            # if visited before, stop here
            if cur_node in visited:
                continue
            else:
                visited.add(cur_node)

            cur_attr = self.get_node_attr(cur_node)

            if 'type' not in cur_attr:
                continue
            if cur_attr['type'] == 'string':
                if cur_attr.get('name'):
                    return cur_attr['name']
                if cur_attr.get('code'):
                    return cur_attr['code']
            elif cur_attr['type'] == 'integer' and not funcName:
                return str(cur_attr['code'])

            if order == 0:
                children = self.get_child_nodes(cur_node, edge_type='PARENT_OF')
            elif order > 0:
                children = self.get_ordered_ast_child_nodes(cur_node)
            else:
                children = self.get_ordered_ast_child_nodes(cur_node)[::-1]
            bfs_queue += [(child, cur_depth + 1) for child in children]

        return None

    def get_stmt_by_line_no(self, ast_node, lineno, upward=True):
        parent = ast_node
        if upward:
            while self.get_node_attr(parent).get('type') != 'AST_STMT_LIST':
                edges = self.get_in_edges(parent, edge_type='PARENT_OF')
                if edges:
                    parent = edges[0][0]
                else:
                    return None
        children = self.get_ordered_ast_child_nodes(parent)
        for child in children:
            child_lineno = self.get_node_attr(child).get('lineno:int')
            child_endlineno = self.get_node_attr(child).get('endlineno:int')
            try:
                if int(lineno) == int(child_lineno):
                    return child
                elif child_endlineno and int(lineno) >= int(child_lineno) and \
                    int(lineno) <= int(child_endlineno):
                    return child
            except (TypeError, ValueError) as e:
                pass
        for child in children:
            if self.get_node_attr(child).get('type') in ['AST_IF', 'AST_FOR',
                'AST_WHILE', 'AST_SWITCH', 'AST_IF_ELEM', 'AST_SWITCH_LIST',
                'AST_SWITCH_CASE']:
                return self.get_stmt_by_line_no(child, lineno, upward=False)

    def is_statement(self, node_id):
        """
        Return whether a node is a statement node or not

        Args:
            node_id: the node_id
        """
        parent_edges = self.get_in_edges(node_id, edge_type = "PARENT_OF")
        if parent_edges is None or len(parent_edges) == 0:
            return False 
        parent_node = parent_edges[0][0]
        parent_node_attr = self.get_node_attr(parent_node)
        if parent_node_attr.get('type') in ["AST_STMT_LIST"] and \
                parent_node_attr.get('labels:label') != "Artificial_AST":
            return True
        return False


    def find_nearest_upper_CPG_node(self, node_id):
        """
        Return the nearest upper CPG node of the input node.
        
        A CPG node is defined as a child of a block node
        (AST_STMT_LIST).
        """
        # follow the parent_of edge to research the stmt node
        if node_id in self.cpg_node_cache:
            return self.cpg_node_cache[node_id]
        ori_node_id = node_id

        while True:
            assert node_id is not None
            parent_edges = self.get_in_edges(node_id, edge_type = "PARENT_OF")
            # print('goes to', node_id, self.get_node_attr(node_id), parent_edges)
            if parent_edges is None or len(parent_edges) == 0:
                # workaround for eval
                # TODO: check if code in eval has scopes
                self.cpg_node_cache[ori_node_id] = node_id
                return node_id 
            parent_node = parent_edges[0][0]
            parent_node_attr = self.get_node_attr(parent_node)
            if parent_node_attr.get('type') in ["AST_STMT_LIST"]:
                self.cpg_node_cache[ori_node_id] = node_id
                return node_id 
            node_id = parent_node

    def get_all_child_nodes(self, node_id, max_depth = None):
        """
        return a list of child node id, by bfs order
        Args:
            node_id: the node id of the start node

        Return:
            a list of node in bfs order
        """
        bfs_queue = []
        visited = set()
        bfs_queue.append((node_id, 0))

        while(len(bfs_queue)):
            cur_node, cur_depth = bfs_queue.pop(0)
            if max_depth and cur_depth > max_depth: break

            # if visited before, stop here
            if cur_node in visited:
                continue
            else:
                visited.add(cur_node)

            cur_attr = self.get_node_attr(cur_node)

            out_edges = self.get_out_edges(cur_node, edge_type = 'PARENT_OF')
            out_nodes = [(edge[1], cur_depth + 1) for edge in out_edges]
            bfs_queue += out_nodes

        # sort the set to make it deterministic
        return sorted(visited, key=lambda v: int(v))

    # Object graph

    # name nodes and object nodes

    def add_obj_node(self, ast_node=None, js_type='object', value=None):
        '''
        Add an object node (including literal).
        
        Args:
            ast_node (optional): The corresponding AST node.
                Defaults to None.
            js_type (str, optional): JavaScript type. Use None to avoid
                adding prototype (but type is still set to 'object').
                Use 'array' to quickly create an array (type is still
                'object'). Defaults to 'object'.
            value (str, optional): Value of a literal, represented by
                JavaScript code. Defaults to None.
        
        Returns:
            Added object node's node id.
        '''
        obj_node = str(self._get_new_nodeid())
        self.add_node(obj_node)
        self.set_node_attr(obj_node, ('labels:label', 'Object'))

        if ast_node is not None:
            self.add_edge(obj_node, ast_node, {"type:TYPE": "OBJ_TO_AST"})

        # Literals' constructors are immutable.
        # Even if you assigned another function to the constructors
        # (e.g. Object = function(){}), objects are still created with
        # original constructors (and prototypes).
        if js_type is None:
            js_type = 'object'
        elif js_type == "function":
            self.add_obj_as_prop("prototype", ast_node, "object",
                    parent_obj=obj_node)
            if self.function_prototype is not None:
                # prevent setting __proto__ before setup_object_and_function runs
                self.add_obj_as_prop(prop_name="__proto__", parent_obj=
                    obj_node, tobe_added_obj=self.function_prototype)
                self.add_obj_as_prop(prop_name="constructor", parent_obj=
                    obj_node, tobe_added_obj=self.function_cons)
        elif js_type == "object":
            if self.object_prototype is not None:
                # prevent setting __proto__ before setup_object_and_function runs
                self.add_obj_as_prop(prop_name="__proto__", parent_obj=
                obj_node, tobe_added_obj=self.object_prototype)
                self.add_obj_as_prop(prop_name="constructor", parent_obj=
                    obj_node, tobe_added_obj=self.object_cons)
                if self.check_proto_pollution and value == wildcard:
                    self.add_obj_as_prop(prop_name="__proto__", parent_obj=
                    obj_node, tobe_added_obj=self.array_prototype)
                    self.add_obj_as_prop(prop_name="__proto__", parent_obj=
                    obj_node, tobe_added_obj=self.number_prototype)
                    self.add_obj_as_prop(prop_name="__proto__", parent_obj=
                    obj_node, tobe_added_obj=self.string_prototype)
                    self.add_obj_as_prop(prop_name="constructor", parent_obj=
                    obj_node, tobe_added_obj=self.array_cons)
                    self.add_obj_as_prop(prop_name="constructor", parent_obj=
                    obj_node, tobe_added_obj=self.number_cons)
                    self.add_obj_as_prop(prop_name="constructor", parent_obj=
                    obj_node, tobe_added_obj=self.string_cons)
        elif js_type == "array":
            # js_type = 'object'     # don't change, keep 'array' type in graph
            if self.array_prototype is not None:
                self.add_obj_as_prop(prop_name="__proto__", parent_obj=
                obj_node, tobe_added_obj=self.array_prototype)
                self.add_obj_as_prop(prop_name="constructor", parent_obj=
                    obj_node, tobe_added_obj=self.array_cons)
        elif js_type == "string":
            if self.string_prototype is not None:
                # prevent setting __proto__ before setup_object_and_function runs
                self.add_obj_as_prop(prop_name="__proto__", parent_obj=
                obj_node, tobe_added_obj=self.string_prototype)
                self.add_obj_as_prop(prop_name="constructor", parent_obj=
                    obj_node, tobe_added_obj=self.string_cons)
            if value is None or value == wildcard:
                length = wildcard
            else:
                value = str(value)
                length = len(value)
            self.add_obj_as_prop(prop_name="length", parent_obj=
            obj_node, js_type='number', value=length)

        self.set_node_attr(obj_node, ('type', js_type))

        if value is not None:
            self.set_node_attr(obj_node, ('code', value))

        # entry point info for inter-package analysis
        if self.store_entry_point_info:
            if self.cur_file_path:
                rel_path = os.path.relpath(self.cur_file_path, self.entry_file_path)
            else:
                rel_path = self.entry_file_path
            self.set_node_attr(obj_node,
                ('defined_in', (rel_path, self.cur_entry_point)))

        return obj_node

    def add_name_node(self, name, scope=None):
        """
        helper function
        add a namenode to scope
        """
        cur_scope = self.cur_scope
        if scope != None:
            cur_scope = scope 

        new_name_node = str(self._get_new_nodeid())
        self.add_edge(cur_scope, new_name_node, {"type:TYPE": "SCOPE_TO_VAR"})
        self.set_node_attr(new_name_node, ('labels:label', 'Name'))
        self.set_node_attr(new_name_node, ('name', name))
        self.name_nodes.add(new_name_node)
        
        if self.BASE_SCOPE and cur_scope == self.BASE_SCOPE:
            self.add_edge(self.BASE_OBJ, new_name_node, {"type:TYPE": "OBJ_TO_PROP"})

        return new_name_node

    def add_prop_name_node(self, name, parent_obj):
        """
        Add an empty name node (without a corresponding object) as a
        property of another object.

        obj -> name node

        For left side of an assignment (such that no dummy object node
        is created).
        """
        new_name_node = str(self._get_new_nodeid())
        self.add_node(new_name_node)
        self.set_node_attr(new_name_node, ('labels:label', 'Name'))
        self.set_node_attr(new_name_node, ('name', name))
        self.add_edge_if_not_exist(parent_obj, new_name_node,
            {"type:TYPE": "OBJ_TO_PROP"})
        self.name_nodes.add(new_name_node)

        if self.BASE_OBJ and parent_obj == self.BASE_OBJ:
            self.add_edge(self.BASE_SCOPE, new_name_node, {"type:TYPE": "SCOPE_TO_VAR"})

        return new_name_node

    def add_obj_as_prop(self, prop_name=None, ast_node=None, js_type='object', 
        value=None, parent_obj=None, tobe_added_obj=None, combined=True,
        kind=None):
        """
        add (or put) an obj as a property of another obj
        parent_obj -> name node -> new obj / tobe_added_obj
        add edge from ast node to obj generation node
        """
        assert parent_obj is not None

        name_node = self.get_prop_name_node(prop_name, parent_obj)

        if name_node is None:
            self.logger.debug(f'{sty.ef.b}Add name node{sty.rs.all} {prop_name} under obj {parent_obj}')
            name_node = self.add_prop_name_node(prop_name, parent_obj)

        if tobe_added_obj is None:
            tobe_added_obj = self.add_obj_node(ast_node, js_type, value)

        self.add_edge(name_node, tobe_added_obj, 
            {"type:TYPE": "NAME_TO_OBJ", "kind": kind})
        if self.affected_name_nodes:
            self.affected_name_nodes[-1].add(name_node)

        if combined and parent_obj == self.BASE_OBJ:
            self.add_obj_to_scope(name=prop_name, scope=self.BASE_SCOPE,
                tobe_added_obj=tobe_added_obj, combined=False)
        return tobe_added_obj


    def add_obj_to_scope(self, name=None, ast_node=None, js_type='object',
        value=None, scope=None, tobe_added_obj=None, combined=True):
        """
        add a obj to a scope, if scope is None, add to current scope
        return the added node id
        """
        if scope == None:
            scope = self.cur_scope 

        # check if the name node exists first
        name_node = self.get_name_node(name, scope=scope, follow_scope_chain=False)
        if name_node == None:
            self.logger.debug(f'{sty.ef.b}Add name node{sty.rs.all} {name} in scope {scope}')
            name_node = str(self._get_new_nodeid())
            self.add_edge(scope, name_node, {"type:TYPE": "SCOPE_TO_VAR"})
            self.set_node_attr(name_node, ('labels:label', 'Name'))
            self.set_node_attr(name_node, ('name', name))
            self.name_nodes.add(name_node)

        if tobe_added_obj == None:
            # here we do not add obj to current obj when add to scope
            # we just add a obj to scope
            tobe_added_obj = self.add_obj_node(ast_node, js_type, value)

        self.add_edge(name_node, tobe_added_obj, {"type:TYPE": "NAME_TO_OBJ"})
        if self.affected_name_nodes:
            self.affected_name_nodes[-1].add(name_node)

        if combined and scope == self.BASE_SCOPE:
            self.add_obj_as_prop(prop_name=name, parent_obj=self.BASE_OBJ,
                tobe_added_obj=tobe_added_obj, combined=False)

        return tobe_added_obj

    add_obj_to_name = add_obj_to_scope

    def add_obj_to_name_node(self, name_node, ast_node=None, js_type='object',
        value=None, tobe_added_obj=None):
        """
        Add a new object (or put a existing object) under a name node.

        name node -> new obj / tobe_added_obj
        """
        if tobe_added_obj is None:
            tobe_added_obj = self.add_obj_node(ast_node, js_type, value)

        self.add_edge(name_node, tobe_added_obj, {"type:TYPE": "NAME_TO_OBJ"})
        if self.affected_name_nodes:
            self.affected_name_nodes[-1].add(name_node)

        return tobe_added_obj

    def get_name_node(self, var_name, scope = None, follow_scope_chain = True):
        """
        Get the name node of a name based on scope.
        """
        if scope == None:
            scope = self.cur_scope

        while True:
            var_edges = self.get_out_edges(scope, data = True, keys = True, edge_type = "SCOPE_TO_VAR")
            for cur_edge in var_edges:
                cur_var_attr = self.get_node_attr(cur_edge[1])
                if cur_var_attr['name'] == var_name:
                    return cur_edge[1]
            if not follow_scope_chain:
                break
            scope_edges = self.get_in_edges(scope, data = True, keys = True, edge_type = "PARENT_SCOPE_OF")
            if len(scope_edges) == 0:
                break
            scope = list(scope_edges)[0][0]
        return None

    def get_objs_by_name_node_2(self, name_node, branches=None):
        '''
        Get corresponding object nodes of a name node.
        
        Args:
            name_node: the name node.
            branches (BranchTagContainer, optional): branch information.
                Default to None.
        
        Returns:
            list: list of object nodes.
        '''
        if name_node is None:
            return []
        out_edges = self.get_out_edges(name_node, edge_type='NAME_TO_OBJ')
        # objs = set([edge[1] for edge in out_edges])
        objs = []
        getter_objs = []
        setter_objs = []
        for edge in out_edges:
            kind = edge[-1].get('kind')
            if kind == 'get':
                getter_objs.append(edge[1])
            elif kind == 'set':
                setter_objs.append(edge[1])
            else:
                objs.append(edge[1])
        if branches:
            # initiate a dictionary that records if the object exists in the current branch
            has_obj = {}
            for obj in objs:
                has_obj[obj] = False
            # check edges without branch tag
            for _, obj, _, attr in self.get_out_edges(name_node, edge_type='NAME_TO_OBJ'):
                branch_tag = attr.get('branch')
                for_tags = self.get_node_attr(obj).get('for_tags')
                if branch_tag is None:
                    has_obj[obj] = True
            # for each branch in branch history
            # we check from the oldest (shallowest) to the most recent (deepest)
            for branch in branches:
                # check which edge matches the current checking branch
                for _, obj, _, attr in self.get_out_edges(name_node, edge_type='NAME_TO_OBJ'):
                    tag = attr.get('branch')
                    if tag and tag.point == branch.point and tag.branch == branch.branch:
                        if tag.mark == 'A':
                            # if the object is added (assigned) in that branch
                             has_obj[obj] = True
                        elif tag.mark == 'D':
                            # if the object is removed in that branch
                            has_obj[obj] = False
                    for tag in self.get_node_attr(obj).get('for_tags', []):
                        if tag.point == branch.point:
                            if branch.branch is not None and \
                                tag.branch != branch.branch:
                                # if the object is used as the loop variable
                                # or created in another branch of that
                                # branching point
                                has_obj[obj] = False
                                break
            return list(filter(lambda x: has_obj[x], objs)), getter_objs, setter_objs
        else:
            return list(objs), getter_objs, setter_objs

    def get_objs_by_name_node(self, name_node, branches=None):
        '''
        Get corresponding object nodes of a name node.
        
        Args:
            name_node: the name node.
            branches (BranchTagContainer, optional): branch information.
                Default to None.
        
        Returns:
            list: list of object nodes.
        '''
        if name_node is None:
            return []
        out_edges = self.get_out_edges(name_node, edge_type='NAME_TO_OBJ')
        objs = set([edge[1] for edge in out_edges])
        if branches:
            # initiate a dictionary that records if the object exists in the current branch
            has_obj = {}
            for obj in objs:
                has_obj[obj] = False
            # check edges without branch tag
            for _, obj, _, attr in self.get_out_edges(name_node, edge_type='NAME_TO_OBJ'):
                branch_tag = attr.get('branch')
                for_tags = self.get_node_attr(obj).get('for_tags')
                if branch_tag is None:
                    has_obj[obj] = True
            # for each branch in branch history
            # we check from the oldest (shallowest) to the most recent (deepest)
            for branch in branches:
                # check which edge matches the current checking branch
                for _, obj, _, attr in self.get_out_edges(name_node, edge_type='NAME_TO_OBJ'):
                    tag = attr.get('branch')
                    if tag and tag.point == branch.point and tag.branch == branch.branch:
                        if tag.mark == 'A':
                            # if the object is added (assigned) in that branch
                             has_obj[obj] = True
                        elif tag.mark == 'D':
                            # if the object is removed in that branch
                            has_obj[obj] = False
                    for tag in self.get_node_attr(obj).get('for_tags', []):
                        if tag.point == branch.point:
                            if branch.branch is not None and \
                                tag.branch != branch.branch:
                                # if the object is used as the loop variable
                                # or created in another branch of that
                                # branching point
                                has_obj[obj] = False
                                break
            return list(filter(lambda x: has_obj[x], objs))
        else:
            return list(objs)

    get_obj_nodes = get_objs_by_name_node

    def get_objs_by_name(self, var_name, scope=None, branches=[]):
        '''
        Get object nodes by a variable name.
        
        Args:
            var_name (str): variable name.
            scope (optional): scope to find the variable in. Defaults to
                current scope.
            branches (list, optional): branch information.
        
        Returns:
            list: list of object nodes.
        '''
        # if var_name == 'this':    # "this" will be handled in handle_node
        #     return self.cur_objs
        name_node = self.get_name_node(var_name, scope)
        if name_node == None:
            return []
        return self.get_objs_by_name_node(name_node, branches)

    def get_prop_names(self, parent_obj, exclude_proto=True,
        numeric_only=False, exclude_wildcard=False):
        s = set()
        for name_node in self.get_prop_name_nodes(parent_obj):
            name = self.get_node_attr(name_node).get('name')
            if exclude_proto and name in [
                    'prototype', '__proto__', 'constructor']:
                continue
            if numeric_only:
                if not (name == wildcard or isinstance(name, _SpecialValue)):
                    try: # check if x is an integer
                        _ = int(name)
                    except ValueError:
                        continue
            if exclude_wildcard and name == wildcard:
                continue
            if name is not None:
                s.add(name)
        return list(s)

    get_keys = get_prop_names

    def get_prop_name_nodes(self, parent_obj=None, exclude_proto=False,
        numeric_only=False, exclude_wildcard=False):
        name_nodes = self.get_child_nodes(parent_obj, edge_type='OBJ_TO_PROP')
        if exclude_proto:
            name_nodes = filter(
                lambda x: self.get_node_attr(x).get('name') not in
                    ['prototype', '__proto__', 'constructor'],
                name_nodes)
        if numeric_only:
            def is_name_int(node):
                name = self.get_node_attr(node).get('name')
                if name == wildcard:
                    return True
                elif isinstance(name, _SpecialValue):
                    return False
                else:
                    try: # check if x is an integer
                        _ = int(name)
                    except ValueError:
                        return False
                    return True
            name_nodes = filter(is_name_int, name_nodes)
        if exclude_wildcard:
            name_nodes = filter(
                lambda x: self.get_node_attr(x).get('name') != wildcard,
                name_nodes)
        return list(name_nodes)

    def get_prop_name_node(self, prop_name, parent_obj=None):
        for name_node in self.get_prop_name_nodes(parent_obj):
            if self.get_node_attr(name_node).get('name') == prop_name:
                return name_node
        return None

    def get_prop_obj_nodes(self, parent_obj, prop_name=None,
        branches: List[BranchTag]=[], exclude_proto=True,
        numeric_only=False):
        '''
        Get object nodes of an object's property.
        
        Args:
            parent_obj (optional): Defaults to None (current object).
            prop_name (str, optional): Property name. Defaults to None,
                which means get all properties' object nodes.
            branches (List[BranchTag], optional): branch information.
                Defaults to [].
            exclude_proto (bool, optional): Whether exclude prototype
                and __proto__ when getting all properties.
                Defaults to True.
        
        Returns:
            list: object nodes.
        '''
        s = set()
        if prop_name is None: # this caused inconsistent run results
            name_nodes = self.get_prop_name_nodes(parent_obj,
                exclude_proto=exclude_proto, numeric_only=numeric_only)
            for name_node in name_nodes:
                s.update(self.get_obj_nodes(name_node, branches))
        else:
            name_node = self.get_prop_name_node(prop_name, parent_obj)
            s.update(self.get_obj_nodes(name_node, branches))
        return list(s)

    def assign_obj_nodes_to_name_node(self, name_node, obj_nodes, multi=False,
        branches=BranchTagContainer()):
        '''
        Assign (multiple) object nodes to a name node.
        
        Args:
            name_node: where to put the objects.
            obj_nodes: objects to be assigned.
            multi (bool, optional):
                True: do NOT delete edges.
                False: delete existing edges.
                Defaults to False.
            branches (List[BranchTag], optional):
                List of branch tags. Defaults to [].
        '''
        branch = branches.get_last_choice_tag()
        # remove previous objects
        pre_objs = self.get_objs_by_name_node(name_node, branches)
        self.logger.debug(f'Assigning {obj_nodes} to {name_node}, ' \
            f'pre_objs={pre_objs}, branches={branches}')
        if pre_objs and not multi:
            for obj in pre_objs:
                if branch:
                    # check if any addition (assignment) exists
                    # in current branch
                    flag = False
                    for key, edge_attr in self.get_edges_between(name_node, obj,
                        'NAME_TO_OBJ').items():
                        tag = edge_attr.get('branch', BranchTag())
                        if tag == BranchTag(branch, mark='A'):
                            # if addition exists, delete the addition edge
                            self.graph.remove_edge(name_node, obj, key)
                            flag = True
                    if not flag:
                        # if no addition, add a deletion edge
                        self.add_edge(name_node, obj,{'type:TYPE':
                        'NAME_TO_OBJ', 'branch': BranchTag(branch, mark='D')})
                        if self.affected_name_nodes:
                            self.affected_name_nodes[-1].add(name_node)
                else:
                    # do not use "remove_edge", which cannot remove all edges
                    self.remove_all_edges_between(name_node, obj)
                    self.logger.debug('  Remove ' + obj)
        # add new objects to name node
        for obj in obj_nodes:
            if branch:
                self.add_edge(name_node, obj, {"type:TYPE": "NAME_TO_OBJ",
                "branch": BranchTag(branch, mark='A')})
            else:
                self.add_edge(name_node, obj, {"type:TYPE": "NAME_TO_OBJ"})
            if self.affected_name_nodes:
                self.affected_name_nodes[-1].add(name_node)

    def get_obj_def_ast_node(self, obj_node, aim_type=None):
        """
        Find where in the AST an object (especially a function) is
        defined.
        
        The AST node is the successor of the object node via the
        OBJ_TO_AST edge.
        """
        aim_map = {
                'function': ['AST_FUNC_DECL', 'AST_CLOSURE', 'AST_METHOD'],
                }
        tmp_edge = self.get_out_edges(obj_node, data = True, keys = True,
            edge_type = "OBJ_TO_AST")
        if not tmp_edge:
            return None
        else:
            if aim_type is not None:
                for edge in tmp_edge:
                    cur_type = self.get_node_attr(edge[1]).get('type')
                    if cur_type in aim_map[aim_type]:
                        return edge[1]
            else:
                for edge in tmp_edge:
                    cur_type = self.get_node_attr(edge[1]).get('type')
                    if cur_type not in aim_map['function']:
                        return edge[1]

            return tmp_edge[0][1]


    def copy_obj(self, obj_node, ast_node=None, copied=None, deep=False):
        '''
        Copy an object and its properties.
        '''
        start = time.time()
        if copied is None:
            copied = set()
        # copy object node
        new_obj_node = str(self._get_new_nodeid())
        self.add_node(new_obj_node, self.get_node_attr(obj_node))
        # copy properties
        for i in self.get_out_edges(obj_node, edge_type='OBJ_TO_PROP'):
            # copy property name node
            prop_name_node = i[1]
            new_prop_name_node = str(self._get_new_nodeid())
            self.add_node(new_prop_name_node,
                          self.get_node_attr(prop_name_node))
            self.add_edge(new_obj_node, new_prop_name_node,
                          {'type:TYPE': 'OBJ_TO_PROP'})
            if self.get_node_attr(prop_name_node).get('name') == '__proto__':
                for j in self.get_out_edges(prop_name_node, edge_type=
                    'NAME_TO_OBJ'):
                    self.add_edge(new_prop_name_node, j[1],
                        {'type:TYPE': 'NAME_TO_OBJ'})
                    if self.affected_name_nodes:
                        self.affected_name_nodes[-1].add(new_prop_name_node)
                continue
            # copy property object nodes
            for j in self.get_out_edges(prop_name_node, edge_type=
                'NAME_TO_OBJ'):
                if deep:
                    # sometimes this loop may dead inside a graph with a circle
                    # check whether we copied this node before
                    if j[1] in copied:
                        continue
                    copied.add(j[1])
                    new_prop_obj_node = self.copy_obj(j[1], ast_node, copied, deep)
                    # self.add_node(new_prop_obj_node, self.get_node_attr(j[1])) # ?
                    self.add_edge(new_prop_name_node, new_prop_obj_node,
                        {'type:TYPE': 'NAME_TO_OBJ'})
                    if self.affected_name_nodes:
                        self.affected_name_nodes[-1].add(new_prop_name_node)
                else:
                    self.add_edge(new_prop_name_node, j[1],
                        {'type:TYPE': 'NAME_TO_OBJ'})
                    if self.affected_name_nodes:
                        self.affected_name_nodes[-1].add(new_prop_name_node)
        # copy OBJ_DECL edges
        for e in self.get_out_edges(obj_node, edge_type='OBJ_DECL'):
            self.add_edge(new_obj_node, e[1], {'type:TYPE': 'OBJ_DECL'})
        if ast_node is not None:
            # assign new OBJ_TO_AST edges
            self.add_edge(new_obj_node, ast_node, {'type:TYPE': 'OBJ_TO_AST'})
        else:
            # copy OBJ_TO_AST edges
            for e in self.get_out_edges(obj_node, edge_type='OBJ_TO_AST'):
                self.add_edge(new_obj_node, e[1], {'type:TYPE': 'OBJ_TO_AST'})
        self.timing('copy_obj', time.time() - start)
        return new_obj_node


    # scopes

    def add_scope(self, scope_type, decl_ast=None, scope_name=None,
        decl_obj=None, caller_ast=None, func_name=None, parent_scope=None):
        """
        Add a new scope under current scope.

        If the scope already exists, return it without adding a new one.
        """
        new_scope_node = str(self._get_new_nodeid())
        self.add_node(new_scope_node, {'labels:label': 'Scope',
            'type': scope_type, 'name': scope_name})
        if decl_ast is not None:
            self.add_edge(new_scope_node, decl_ast,
                {'type:TYPE': 'SCOPE_TO_AST'})
        if parent_scope is None:
            if self.cur_scope is not None:
                self.add_edge(self.cur_scope, new_scope_node,
                    {'type:TYPE': 'PARENT_SCOPE_OF'})
            else:
                self.cur_scope = new_scope_node
        else:
            self.add_edge(parent_scope, new_scope_node,
                {'type:TYPE': 'PARENT_SCOPE_OF'})
        if decl_obj is not None:
            self.add_edge(decl_obj, new_scope_node,
                {'type:TYPE': 'OBJ_TO_SCOPE'})
        if caller_ast is not None:
            self.add_edge(new_scope_node, caller_ast,
                {'type:TYPE': 'SCOPE_TO_CALLER'})
        if func_name is not None:
            self.set_node_attr(new_scope_node, ('func_name', func_name))
        return new_scope_node

    def find_ancestor_scope(self, scope_types=['FUNC_SCOPE', 'FILE_SCOPE'],
        cur_scope=None):
        '''
        Find ancestor (file/function) scope from the current (block)
        scope.
        '''
        if cur_scope is None:
            cur_scope = self.cur_scope
        while True:
            if self.get_node_attr(cur_scope).get('type') in scope_types:
                return cur_scope
            edges = self.get_in_edges(cur_scope, edge_type='PARENT_SCOPE_OF')
            if edges:
                cur_scope = edges[0][0]
            else:
                return None

    # functions and calls

    def get_func_decl_objs_by_ast_node(self, ast_node, scope=None):
        start = time.time()
        objs = []
        edges = self.get_in_edges(ast_node, edge_type='OBJ_TO_AST')
        for edge in edges:
            # avoid function run objects
            if (self.get_node_attr(edge[0]).get('type') == 'function' or
                    self.get_node_attr(edge[0]).get('code') == wildcard): # converted func
                objs.append(edge[0])
        if scope is not None:
            # for obj in objs:
            #     try:
            #         print('!!@@', scope, obj, nx.shortest_path(self.graph, scope, obj))
            #     except nx.NetworkXNoPath:
            #         pass
            def _filter_obj(obj):
                nonlocal scope
                q = [obj]
                while q:
                    h = q.pop(0)
                    for e in self.get_in_edges(h):
                        if e[0] == scope:
                            return True
                        elif self.get_node_attr(e[0]).get('labels:label') in ['Scope', 'Name']:
                            q.append(e[0])
                return False
            # objs = list(filter(lambda obj: self.has_path(scope, obj), objs))
            objs = list(filter(_filter_obj, objs))
            if len(objs) > 1:
                self.logger.warning('Function {} is declared as multiple objects in scope {}'
                    .format(ast_node, scope))
        self.timing('get_func_decl_objs_by_ast_node', time.time() - start)
        return objs

    def get_func_scopes_by_obj_node(self, obj_node):
        if obj_node == None:
            return None
        scope_edges = self.get_out_edges(obj_node, edge_type = "OBJ_TO_SCOPE")
        return [edge[1] for edge in scope_edges]

    def add_blank_func_to_scope(self, func_name, scope=None, python_func:Callable=None):
        '''
        Add a blank function with object graph nodes to a scope.
        
        Args:
            func_name (str): function's name.
            scope (optional): where to add the function. Defaults to
                None, referring to the current scope.
            python_func (optional): a special Python function in lieu of
                the blank JS AST function. Defaults to None.
        '''
        func_obj = self.add_blank_func_with_og_nodes(func_name)
        self.add_obj_to_name(func_name, scope=scope, tobe_added_obj=func_obj)
        if python_func is not None:
            self.set_node_attr(func_obj, ('pythonfunc', python_func))
        return func_obj

    def add_blank_func_as_prop(self, func_name, parent_obj=None, python_func:Callable=None):
        '''
        Add a blank function with object graph nodes as a property of
        another object.
        
        Args:
            func_name (str): function's name.
            parent_obj (optional): function's parent object. Defaults to
                None, referring to the current object.
            python_func (optional): a special Python function in lieu of
                the blank JS AST function. Defaults to None.
        '''
        func_obj = self.add_blank_func_with_og_nodes(func_name)
        self.add_obj_as_prop(func_name, parent_obj=parent_obj,
                             tobe_added_obj=func_obj)
        if python_func is not None:
            self.set_node_attr(func_obj, ('pythonfunc', python_func))
        return func_obj

    def convert_obj_node_type_to_function(self, obj, func_ast=None):
        '''
        Convert an object node of any type to function.
        Function's prototype will also be added.

        Args:
            obj: The object node.
            func_ast (optional): Function's AST node. Default to None.
        '''
        assert obj != self.undefined_obj
        assert obj != self.null_obj
        if self.get_node_attr(obj).get('code') != wildcard:
            self.set_node_attr(obj, ('type', 'function'))
        self.add_obj_as_prop("prototype", func_ast, "object", 
                parent_obj=obj)
        if self.function_prototype is not None:
            # prevent setting __proto__ before setup_object_and_function runs
            self.add_obj_as_prop(prop_name="__proto__", parent_obj=obj,
            tobe_added_obj=self.function_prototype)

        """
        # for existing variable we do not need to remove obj to ast
            # remove old OBJ_TO_AST edges
        if func_ast is not None:
            edges = self.get_out_edges(obj, edge_type="OBJ_TO_AST")
            for edge in edges:
                self.graph.remove_edge(edge[0], edge[1])
        """

        if func_ast is not None:
            self.add_edge(obj, func_ast, {"type:TYPE": "OBJ_TO_AST"})

    def add_blank_func_with_og_nodes(self, func_name, func_obj=None,
        python_func=None):
        '''
        Add a blank function with object graph nodes (name node, function
        scope, and function declaration object node).
        
        Args:
            func_name (str): Function's name.
            func_obj (optional): Function's object node if known. Use it
                when you want to overwrite an existing object node.
                Default to None.
        '''
        ast_node = self.add_blank_func(func_name)
        if func_obj is None:
            func_obj = self.add_obj_node(ast_node, "function")
            self.set_node_attr(func_obj, ('name', func_name))
        else:
            self.convert_obj_node_type_to_function(func_obj, ast_node)
        if python_func is not None:
            self.set_node_attr(func_obj, ('pythonfunc', python_func))
        self.logger.debug(sty.fg(179) + "Dummy function"
            + sty.rs.all + " {} assigned to obj {}".format(ast_node, func_obj))
        return func_obj

    def add_blank_func(self, func_name):
        """
        add a blank func
        used for built-in functions
        we need to run the function after the define
        """
        # add a function decl node first
        func_ast = self._get_new_nodeid()
        self.logger.debug(sty.ef.inverse + sty.fg(179) + "Add dummy function"
            + sty.rs.all + " name: {}".format(func_name)
            + ", AST node: {}".format(func_ast))
        self.add_node(func_ast)
        # self.set_node_attr(func_ast, ('funcid', func_ast))
        self.set_node_attr(func_ast, ('type', "AST_CLOSURE"))
        self.set_node_attr(func_ast, ('labels:label', 'Artificial_AST'))

        # add a node as the name of the function
        name_id = self._get_new_nodeid()
        self.add_node(name_id)
        self.set_node_attr(name_id, ('type', 'string'))
        self.set_node_attr(name_id, ('name', func_name))
        self.set_node_attr(name_id, ('labels:label', 'Artificial_AST'))
        self.set_node_attr(name_id, ('childnum:int', 0))

        entry_id = self._get_new_nodeid()
        self.add_node(entry_id)
        self.set_node_attr(entry_id, ('funcid:int', func_ast))
        self.set_node_attr(entry_id, ('type', 'CFG_FUNC_ENTRY'))
        self.set_node_attr(entry_id, ('labels:label', 'Artificial'))

        exit_id = self._get_new_nodeid()
        self.add_node(exit_id)
        self.set_node_attr(exit_id, ('funcid:int', func_ast))
        self.set_node_attr(exit_id, ('type', 'CFG_FUNC_EXIT'))
        self.set_node_attr(exit_id, ('labels:label', 'Artificial'))

        null_id = self._get_new_nodeid()
        self.add_node(null_id)
        self.set_node_attr(null_id, ('funcid:int', func_ast))
        self.set_node_attr(null_id, ('type', 'NULL'))
        self.set_node_attr(null_id, ('labels:label', 'Artificial_AST'))
        self.set_node_attr(null_id, ('childnum:int', 1))

        params_id = self._get_new_nodeid()
        self.add_node(params_id)
        self.set_node_attr(params_id, ('funcid:int', func_ast))
        self.set_node_attr(params_id, ('type', 'AST_PARAM_LIST'))
        self.set_node_attr(params_id, ('labels:label', 'Artificial_AST'))
        self.set_node_attr(params_id, ('childnum:int', 2))

        body_id = self._get_new_nodeid()
        self.add_node(body_id)
        self.set_node_attr(body_id, ('funcid:int', func_ast))
        self.set_node_attr(body_id, ('type', 'AST_STMT_LIST'))
        self.set_node_attr(body_id, ('labels:label', 'Artificial_AST'))
        self.set_node_attr(body_id, ('childnum:int', 3))

        dummy_stmt_id = self._get_new_nodeid()
        self.add_node(dummy_stmt_id)
        self.set_node_attr(dummy_stmt_id, ('funcid:int', func_ast))
        self.set_node_attr(dummy_stmt_id, ('type', 'DUMMY_STMT'))
        self.set_node_attr(dummy_stmt_id, ('labels:label', 'Artificial_AST'))
        self.set_node_attr(dummy_stmt_id, ('childnum:int', 0))

        # add edges
        self.add_edge(func_ast, entry_id, {'type:TYPE': "ENTRY"})
        self.add_edge(func_ast, exit_id, {'type:TYPE': "EXIT"})
        self.add_edge(func_ast, name_id, {'type:TYPE': "PARENT_OF"})
        self.add_edge(func_ast, null_id, {'type:TYPE': "PARENT_OF"})
        self.add_edge(func_ast, params_id, {'type:TYPE': "PARENT_OF"})
        self.add_edge(func_ast, body_id, {'type:TYPE': "PARENT_OF"})
        self.add_edge(body_id, dummy_stmt_id, {'type:TYPE': "PARENT_OF"})
        self.add_edge(entry_id, exit_id, {'type:TYPE': "FLOWS_TO"})

        # we need to run the function 
        return func_ast

    def get_self_invoke_node_by_caller(self, caller_id):
        """
        Deprecated

        get the closure of self invoke function by the caller id
        
        Args:
            caller_id: the node id of the caller
        """
        return self._get_childern_by_childnum(caller_id)['0']

    def get_cur_file_path(self, cur_scope=None):
        file_scope = self.find_ancestor_scope(cur_scope=cur_scope,
            scope_types=['FILE_SCOPE'])
        if file_scope is None:
            return None
        file_ast = self.get_out_edges(file_scope,
                        edge_type='SCOPE_TO_AST')[0][1]
        if file_ast is None:
            return None
        return self.get_node_attr(file_ast).get('name')

    # prototype

    def _get_upper_level_prototype(self, obj_node):
        """
        get the upper level of prototype
        used for a helper function to link __proto__ and prototype

        Args:
            obj_node: the child obj node
            relation: obj_node -OBJ_DECL-> AST_FUNC_DECL -OBJ_TO_AST-> 
            FUNC_DECL -OBJ_TO_PROP-> prototype -NAME_TO_OBJ-> PROTOTYPE
        """
        ast_upper_func_node = self.get_child_nodes(obj_node, 
                edge_type = "OBJ_DECL")[0]
        edges = self.get_in_edges(ast_upper_func_node,
                edge_type = "OBJ_TO_AST")
        func_decl_obj_node = None
        for edge in edges:
            if self.get_node_attr(edge[0])['type'] == "function":
                func_decl_obj_node = edge[0]
                break
        if func_decl_obj_node is None: # TODO: what is cause of this bug?
            self.logger.error('Cannot find function object node!')
            return []
        else:
            prototype_obj_nodes = self.get_prop_obj_nodes(
                parent_obj=func_decl_obj_node, prop_name='prototype')
            self.logger.debug(f'prototype obj node is {prototype_obj_nodes}')
            return prototype_obj_nodes
    
    def build_proto(self, obj_node):
        """
        build the proto strcture of a object node

        Args:
            obj_node: the obj node need to be build
        """
        upper_level_prototype_objs = self._get_upper_level_prototype(obj_node)
        for obj in upper_level_prototype_objs:
            self.add_obj_as_prop('__proto__', parent_obj=obj_node,
                                 tobe_added_obj=obj)

    # Misc

    def setup1(self):
        """
        the init function of setup a run
        """
        # base scope is not related to any file
        self.BASE_SCOPE = self.add_scope("BASE_SCOPE", scope_name='Base')

        self.BASE_OBJ = self.add_obj_to_scope(name='global',
                            scope=self.BASE_SCOPE, combined=False)
        #TODO: Add 'window' as an alias of global
        self.cur_objs = [self.BASE_OBJ]

        # setup JavaScript built-in values
        self.null_obj = self.add_obj_to_scope(name='null', value='null',
                                              scope=self.BASE_SCOPE)

        self.true_obj = self.add_obj_node(None, 'boolean', 'true')
        self.add_obj_to_name('true', scope=self.BASE_SCOPE,
                             tobe_added_obj=self.true_obj)
        self.false_obj = self.add_obj_node(None, 'boolean', 'false')
        self.add_obj_to_name('false', scope=self.BASE_SCOPE,
                             tobe_added_obj=self.false_obj)

    def setup2(self):
        # self.tainted_user_input = self.add_obj_to_scope(
        #     name='pyTaintedUserInput', js_type=None,
        #     value='*', scope=self.BASE_SCOPE)
        # self.logger.debug("{} is mared as tainted for user input".format(self.tainted_user_input))
        # self.set_node_attr(self.tainted_user_input, ('tainted', True))

        # setup JavaScript built-in values
        self.undefined_obj = self.add_obj_node(None, 'undefined',
                                                value='undefined')
        self.add_obj_to_name('undefined', scope=self.BASE_SCOPE,
                             tobe_added_obj=self.undefined_obj)
        self.infinity_obj = self.add_obj_node(None, 'number', 'Infinity')
        self.add_obj_to_name('Infinity', scope=self.BASE_SCOPE,
                             tobe_added_obj=self.infinity_obj)
        self.negative_infinity_obj = self.add_obj_node(None, 'number',
                                                       '-Infinity')
        self.nan_obj = self.add_obj_node(None, 'number', float('nan'))
        self.add_obj_to_name('NaN', scope=self.BASE_SCOPE,
                             tobe_added_obj=self.nan_obj)

        self.add_obj_as_prop(prop_name='__proto__', js_type='object',
            parent_obj=self.BASE_OBJ)

        self.internal_objs = {
            'undefined': self.undefined_obj,
            'null': self.null_obj,
            'global': self.BASE_OBJ,
            'infinity': self.infinity_obj,
            '-infinity': self.negative_infinity_obj,
            'NaN': self.nan_obj,
            'true': self.true_obj,
            'false': self.false_obj
        }
        self.inv_internal_objs = {v: k for k, v in self.internal_objs.items()}
        self.logger.debug(sty.ef.inverse + 'Internal objects\n' + 
            str(self.internal_objs)[1:-1] + sty.rs.all)

        self.builtin_prototypes = [
            self.object_prototype, self.string_prototype,
            self.array_prototype, self.function_prototype,
            self.number_prototype, self.boolean_prototype,
            self.regexp_prototype, self.promise_prototype
        ]
        self.pollutable_objs = set(chain(*
            [self.get_prop_obj_nodes(p) for p in self.builtin_prototypes]))
        self.pollutable_name_nodes = set(chain(*
            [self.get_prop_name_nodes(p) for p in self.builtin_prototypes]))

    def get_parent_object_def(self, node_id):
        """
        get the obj number and defination of the parent object 

        Args:
            node_id: current node id, means the child id
        Return:
            parent_obj: the list of parent obj node of current node id
            def_id: the list of statements that defines the parent object
        """
        parent_obj_nodes = []
        parent_obj_defs = []
        name_nodes = []
        # get the name node first
        name_edges = self.get_in_edges(node_id, edge_type="NAME_TO_OBJ")
        for name_edge in name_edges:
            name_node = name_edge[0]

            parent_obj_edges = self.get_in_edges(name_node, edge_type="OBJ_TO_PROP")
            for parent_obj_edge in parent_obj_edges:
                def_edges = self.get_out_edges(parent_obj_edge[0], edge_type="OBJ_TO_AST")
                if len(def_edges) == 0:
                    def_edges = [(parent_obj_edge[0], '1')]
                    #continue

                parent_obj_nodes.append(parent_obj_edge[0])
                name_nodes.append(name_node)
                for def_edge in def_edges:
                    # we return the flatten array
                    # if one obj has multiple defs, defs can not match obj
                    parent_obj_defs.append(def_edge[1])

        return parent_obj_nodes, parent_obj_defs, name_nodes

    def generate_obj_graph_for_python_obj(self, py_obj=None, ast_node=None):
        if py_obj is None:
            return self.null_obj
        elif type(py_obj) in [int, float]:
            return self.add_obj_node(ast_node=ast_node, js_type='number',
                value=py_obj)
        elif type(py_obj) is str:
            return self.add_obj_node(ast_node=ast_node, js_type='string',
                value=py_obj)
        elif type(py_obj) is list:
            obj = self.add_obj_node(ast_node=ast_node, js_type='array',
                value=py_obj)
            for i, u in enumerate(py_obj):
                member = self.generate_obj_graph_for_python_obj(u)
                self.add_obj_as_prop(prop_name=i, tobe_added_obj=member,
                    parent_obj=obj)
            return obj
        elif type(py_obj) is dict:
            obj = self.add_obj_node(ast_node=ast_node, js_type='object',
                value=py_obj)
            for k, v in py_obj.items():
                member = self.generate_obj_graph_for_python_obj(v)
                self.add_obj_as_prop(prop_name=k, tobe_added_obj=member,
                    parent_obj=obj)
            return obj

    def add_entry_node(self, parent=None, type="block"):
        entry_node = str(self._get_new_nodeid())
        self.add_node(entry_node)
        self.set_node_attr(entry_node, ('labels:label', 'Artificial'))
        self.set_node_attr(entry_node, ('type', f'CFG_{str(type).upper()}_ENTRY'))
        if parent is not None:
            self.add_edge(parent, entry_node, {"type:TYPE": "ENTRY"})
        return entry_node

    def add_exit_node(self, parent=None, type="block"):
        exit_node = str(self._get_new_nodeid())
        self.add_node(exit_node)
        self.set_node_attr(exit_node, ('labels:label', 'Artificial'))
        self.set_node_attr(exit_node, ('type', f'CFG_{str(type).upper()}_EXIT'))
        if parent is not None:
            self.add_edge(parent, exit_node, {"type:TYPE": "EXIT"})
        return exit_node

    # Analysis

    def _dfs_upper_by_edge_type(self, source=None, edge_type='OBJ_REACHES', depth_limit=None):
        """
        dfs a specific type of edge upper from a node id

        Args:
            node_id: the start node id
            edge_types: we only consider some types of edge types
        Return:
            nodes: list, nodes on the pathes
            objs: dict, the objs on the edge, {str(from_to): [obj numbers]} 
        """
        start_time = time.time()
        G = self.graph
        pathes = []
        if source is None:
            # edges for all components
            nodes = G
        else:
            # edges for components with source
            nodes = [source]
        visited = set()
        if depth_limit is None:
            depth_limit = len(G)
        for start in nodes:
            # we do not have a global visited
            # each path, or stack should have a visited list but not global
            """
            if start in visited:
                continue
            visited.add(start)
            """

            edge_group = self.get_in_edges(start, edge_type=edge_type)
            nodes_group = set(edge[0] for edge in edge_group)

            stack = [(start, depth_limit, iter(nodes_group))]
            while stack:
                parent, depth_now, children = stack[-1]
                try:
                    child = next(children)
                    if child not in [s[0] for s in stack]:
                        visited.add(child)
                        if depth_now > 1:
                            edge_group = self.get_in_edges(child, edge_type=edge_type)
                            nodes_group = set(edge[0] for edge in edge_group)
                            stack.append((child, depth_now - 1, iter(nodes_group)))
                            if len(nodes_group) == 0:
                                new_path = [node[0] for node in stack]
                                str_pathes = [str(p) for p in pathes]
                                if str(new_path) not in str_pathes:
                                    pathes.append(new_path)
                except StopIteration:
                    stack.pop()
        self.timing('_dfs_upper_by_edge_type', time.time() - start_time)
        return pathes

    def get_node_file_path(self, node_id):
        # it's a ast so a node only has one parent
        orig_node_attrs = self.get_node_attr(node_id)
        if 'filename' in orig_node_attrs:
            return orig_node_attrs['filename']

        while True:
            node_attrs = self.get_node_attr(node_id)
            if node_attrs.get('flags:string[]') == 'TOPLEVEL_FILE':
                orig_node_attrs['filename'] = node_attrs.get('name')
                return node_attrs.get('name')
            in_edges = self.get_in_edges(node_id, edge_type="PARENT_OF", data=False)
            if in_edges:
                node_id = in_edges[0][0]
            else:
                # should be built in
                orig_node_attrs['filename'] = node_attrs.get('name')
                return None

    def get_node_line_code(self, node_id):
        """
        return the line code of a node
        """
        node_attr = self.get_node_attr(node_id)
        if "lineno:int" in node_attr:
            lineno = node_attr['lineno:int']
        else:
            lineno = None
        if lineno is not None:
            file_content = self.get_node_file_content(node_id)
            return "{}: {}".format(lineno, file_content[int(lineno)])
        return None

    def get_node_file_content(self, node_id):
        """
        find the file of a node
        return the dict with numbers and contents
        """
        file_name = self.get_node_file_path(node_id)
        if file_name is None:
            return None
        if file_name not in self.file_contents:
            content_dict = ['']
            with open(file_name, 'r') as fp:
                for file_line in fp:
                    content_dict.append(file_line)
            self.file_contents[file_name] = content_dict.copy()
        return self.file_contents[file_name]

    def get_node_file_content_highlighted(self, node_id):
        highlighted_obj_nodes = set()
        def dfs(now):
            nonlocal self, highlighted_obj_nodes
            if now in highlighted_obj_nodes:
                return
            if self.get_node_attr(now).get('tainted'):
                highlighted_obj_nodes.add(now)
            for child in self.get_child_nodes(now, edge_type='CONTRIBUTES_TO'):
                dfs(child)
        for obj_node in self.highlighted_obj_nodes:
            dfs(obj_node)
        content = [str(l) for l in self.get_node_file_content(node_id)]
        file_name = self.get_node_file_path(node_id)
        # print(f'st {highlighted_obj_nodes} {self.highlighted_obj_nodes}')
        for obj_node in highlighted_obj_nodes:
            # print(f'{obj_node} AST {self.obj_to_ast[obj_node].keys()}')
            for ast_node in self.obj_to_ast[obj_node].keys():
                # start = self.get_node_attr(ast_node).get('lineno:int')
                # end = self.get_node_attr(ast_node).get('endlineno:int')
                # code = self.get_node_attr(ast_node).get('code')
                # if self.get_node_attr(ast_node).get('type') == 'AST_VAR':
                #     code = self.get_node_attr(self.get_ordered_ast_child_nodes(
                #         ast_node)[0]).get('code')
                # if not code:
                #     continue
                # if not end:
                #     end = start
                # try:
                #     start = int(start)
                #     end = int(end) + 1
                #     matched = False
                #     for l in range(start, end):
                #         try:
                #             new, c = re.subn(r'\b' + code + r'\b', 
                #                 sty.fg.li_red + code + sty.rs.all, content[l])
                #             if c > 0:
                #                 matched = True
                #             content[l] = new
                #         except IndexError:
                #             pass
                # except (ValueError, TypeError) as e:
                #     print(e)                    
                #     # pass

                # print(file_name, self.get_node_file_path(ast_node))
                if file_name != self.get_node_file_path(ast_node):
                    continue
                location = self.get_node_attr(ast_node).get(
                                                    'namespace', '').strip()
                # print(ast_node, self.get_node_attr(ast_node), 'location:', location)
                if location:
                    sl, sc, el, ec = location.split(':')
                    # print(sl, sc, el, ec)
                    if not el:
                        el = sl
                    try:
                        sl = int(sl)
                        el = int(el)
                        if sc:
                            sc = int(sc)
                        else:
                            sc = 0
                        if ec:
                            ec = int(ec)
                        else:
                            ec = sys.maxsize
                        for l in range(sl, el + 1):
                            try:
                                line = content[l]
                                # print(f'line {l}: {content[l]}')
                                if l == sl and l == el:
                                    line = line[0:sc] + sty.fg.li_red + line[
                                            sc:ec] + sty.rs.all + line[ec:]
                                elif l == sl and l != el:
                                    line = line[0:sc] + sty.fg.li_red + \
                                        line[sc:] + sty.rs.all
                                elif l != sl and l == el:
                                    line = sty.fg.li_red + line[0:ec] + \
                                        sty.rs.all + content[l][ec:]
                                else:
                                    line = sty.fg.li_red + line + sty.rs.all
                                # print(f'line {l}: {line}')
                                content[l] = line
                            except IndexError:
                                pass
                    except (ValueError, TypeError) as e:
                        print(e)    
                        # pass
        return content

    def check_signature_functions(self, func_names):
        """
        checking whether one of the func_names exist in the graph
        if not, we do not need to build the obj graph
        Args:
            func_names: the possible function names, if length is 0, return True
        Return:
            True for exist or False for not exist
        """
        if len(func_names) == 0:
            return True

        func_nodes = self.get_node_by_attr('type', 'AST_METHOD_CALL')
        func_nodes += self.get_node_by_attr('type', 'AST_CALL')
        for func_node in func_nodes:
            func_name = self.get_name_from_child(func_node)
            if func_name in func_names:
                return True
        return False

    def get_total_num_statements(self):
        """
        return the total number of statements of AST
        """
        if len(self.all_stat) != 0:
            return len(self.all_stat)

        all_nodes = self.get_all_nodes()
        for n in all_nodes:
            attrs = self.get_node_attr(n)
            if 'type' in attrs:
                if 'AST_' in attrs['type'] and self.is_statement(n):
                    self.all_stat.add(n)
                    self.total_num_stat += 1
        # print(len(set(self.all_stat_list)), len(set(self.covered_list)), len(self.covered_list))
        return len(self.all_stat)

    def get_total_num_functions(self):
        """
        return the total number of statements of AST
        """
        if len(self.all_func) != 0:
            return len(self.all_func)

        all_nodes = self.get_all_nodes()
        for n in all_nodes:
            if 'type' in all_nodes[n]:
                if all_nodes[n]['type'] in ['AST_FUNC_DECL', 'AST_CLOSURE']:
                    if 'labels:label' in all_nodes[n] and \
                            all_nodes[n]['labels:label'] == 'Artificial_AST':
                        pass
                    else:
                        self.all_func.add(n)
        return len(self.all_func)


    def get_AST_num(self, node_id):
        num = 0
        children = self.get_ordered_ast_child_nodes(node_id)
        if len(children)>0:
            for child in children:
                num += self.get_AST_num(child)
        # self add 1
        num += 1
        return num

    def check_mem(self):
        if not self.mem_limit:
            return
        else:
            mem = psutil.Process(os.getpid()).memory_info().rss
            if mem > self.mem_limit:
                raise MemoryLimitExceededError()

class MemoryLimitExceededError(Exception):
    pass