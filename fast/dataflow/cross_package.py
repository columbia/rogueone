import sys

from .trust_domains import rel_map_to_cross_package_map, l_td, c_td
import networkx as nx

sd = ':static_data'
ud = ':caller_input'

node_builtins = [
  '_http_agent',         '_http_client',        '_http_common',
  '_http_incoming',      '_http_outgoing',      '_http_server',
  '_stream_duplex',      '_stream_passthrough', '_stream_readable',
  '_stream_transform',   '_stream_wrap',        '_stream_writable',
  '_tls_common',         '_tls_wrap',           'assert',
  'assert/strict',       'async_hooks',         'buffer',
  'child_process',       'cluster',             'console',
  'constants',           'crypto',              'dgram',
  'diagnostics_channel', 'dns',                 'dns/promises',
  'domain',              'events',              'fs',
  'fs/promises',         'http',                'http2',
  'https',               'inspector',           'module',
  'net',                 'os',                  'path',
  'path/posix',          'path/win32',          'perf_hooks',
  'process',             'punycode',            'querystring',
  'readline',            'readline/promises',   'repl',
  'stream',              'stream/consumers',    'stream/promises',
  'stream/web',          'string_decoder',      'sys',
  'timers',              'timers/promises',     'tls',
  'trace_events',        'tty',                 'url',
  'util',                'util/types',          'v8',
  'vm',                  'wasi',                'worker_threads',
  'zlib'
]
excluded_names = ['util']

def graph_from_rel_map_sets(data, root_package_name: str = None, consolidate_tds=True):
    filtered_data = {
        k: rel_map_to_cross_package_map(data[k], err_mark=root_package_name, consolidate_tds=consolidate_tds)
        for k in data
    }
    nodes = [i for i in filtered_data if i not in excluded_names]

    #for node in list(nodes):
    #    for e in filtered_data[node]:
    #        for td in e:
    #            if td not in [l_td, c_td, 'util', root_package_name]:
    #                nodes.add(td)
    #nodes = list(nodes)

    G = nx.DiGraph()
    if root_package_name:
        for s in (sd, ud):
            G.add_node(root_package_name + s)
        if root_package_name not in filtered_data:
            #raise Exception(f"Performing cross package analysis for {root_package_name}, but root package not present in data")
            sys.stderr.write(f"Performing cross package analysis for {root_package_name}, but root package not present in data.\n")

    noedge_nodes = [l_td, c_td]
    edges = []
    for n in nodes:
        if n not in filtered_data:
            continue
        tmp_edges = [i for i in filtered_data[n]]
        for e in tmp_edges:
            initial_e = e
            if filtered_data[n][initial_e] and len(filtered_data[n][initial_e][0]) > 0:
                prop_desc = {'prop_origin': filtered_data[n][initial_e][0][0],
                                          'prop_dest': filtered_data[n][initial_e][0][1]
                             }
            else:
                prop_desc = {'prop_origin': e[0],
                                          'prop_dest':e[1],
                }
            if e[0] in excluded_names or e[1] in excluded_names:
                pass
            elif e[0] in noedge_nodes and e[1] in noedge_nodes:
                pass
            elif n == root_package_name and (e[0] in noedge_nodes or e[1] in noedge_nodes):
                # For the root package, :caller signifies user data and :local signifies new static package code
                if e[0] ==l_td:
                    e = (root_package_name + sd, e[1])
                if e[0] == c_td:
                    e = (root_package_name + ud, e[1])
                    #edges.append((e[1],e[0])) 
                if e[1] ==l_td:
                    e = (e[0], root_package_name + sd,)
                if e[1] == c_td:
                    e = (e[0], root_package_name + ud)
                    #edges.append((e[1],e[0]))
                edges.append((e[0], e[1], prop_desc))
            elif e[0] in noedge_nodes and e[1] in noedge_nodes:
                pass
            else:
                key_node = e[0] if e[0] not in noedge_nodes else e[1]
                if e[0] in noedge_nodes: # not sure about the direction here
                    e = (n, key_node)
                elif e[1] in noedge_nodes:
                    e = (key_node, n)
                edges.append((e[0], e[1], prop_desc))
    G.add_edges_from(edges)
    return G

# Need to exclude data from packages that didn't get successfully analyzed
always_exclude = {'jquery', 'underscore', 'lodash'}

def get_excluded_nodes(both_version_data: dict):
    before: dict = both_version_data['before']
    after: dict = both_version_data['after']

    data_to_delete = []
    for v in (before, after):
        data_to_delete.extend(v['not_included_dependencies'])

    return set(data_to_delete).union(always_exclude)

def graphs_from_version_pair_data(data: dict):
    excluded_nodes = get_excluded_nodes(data)

    for v in (data['before'], data['after']):
        for n in excluded_nodes:
            if n in v['data']:
                del v['data'][n]
    bg = graph_from_rel_map_sets(data['before']['data'], root_package_name=data['package_name'])
    ag = graph_from_rel_map_sets(data['after']['data'], root_package_name=data['package_name'])
    if data['package_name']+':static_data' not in bg.nodes or data['package_name']+':static_data' not in ag.nodes:
        sys.stderr.write(f"Package {data['package_name']} not present in cross-package analysis result.\n")
        return None, None
    else:
        return bg, ag

def reachables(g, package_name):
     return set(nx.single_source_dijkstra(g, package_name)[0].keys())


def graph_differences(before_graph, after_graph, data) ->  tuple[set, set]:
    static_diff_nodes = reachable_difference(before_graph, after_graph, data, sd[1: ])
    user_diff_nodes = reachable_difference(before_graph, after_graph, data, ud[1:])
    return static_diff_nodes, user_diff_nodes


def reachable_difference(before_graph, after_graph, data, suffix):
    before_accessible_nodes = reachables(before_graph, data['package_name'] + ':' + suffix)
    after_accessible_nodes = reachables(after_graph, data['package_name'] + ':' + suffix)
    #print(after_accessible_nodes)
    diff_nodes = after_accessible_nodes.difference(before_accessible_nodes)
    for dn in list(diff_nodes):
        if dn in data['after']['not_included_dependencies'] or \
                dn in node_builtins or \
                dn[0] == ':':
            pass
        else:
            pass
            #diff_nodes.remove(dn)
    return diff_nodes


def clear_node_data(data):
    for k0 in ('before', 'after'):
        v = data[k0]['data']
        for k1 in v.keys():
            for k2 in v[k1].keys():
                v[k1][k2] = []
    return data
