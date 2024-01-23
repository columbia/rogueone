import unittest
import json
import os
import sys
import networkx as nx


sys.path.append('../')

import fast.dataflow.trust_domains as td

data_file = os.path.join(os.path.dirname(__file__), "dataflow_fixtures", "cross_package.json")

G = nx.DiGraph()

def test_rel_map_simplification():
    with open(data_file) as f:
        data = json.load(f)
    assert data

    filtered_data = {
        k: td.rel_map_to_cross_package_set(data[k])
        for k in data
    }
    nodes = [i for i in filtered_data]

    # G.add_nodes_from(nodes)
    noedge_nodes = [':local', ':caller']
    edges = []
    for n in nodes:
        tmp_edges = [i for i in filtered_data[n]]
        for e in tmp_edges:
            if e[0] in noedge_nodes and e[1] in noedge_nodes:
                pass
            else:
                key_node = e[0] if e[0] not in noedge_nodes else e[1]
                if ':local' in e: # not sure about the direction here
                    e = (key_node, n)
                elif ':caller' in e:
                    e = (n, key_node)
                edges.append(e)
    G.add_edges_from(edges)
    print(G.edges)
    print(G.nodes)

if __name__ == '__main__':
    # unittest.main()
    test_rel_map_simplification()


