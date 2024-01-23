import unittest
import json
import os
import sys
import pickle
sys.path.append('../')
from pathlib import Path
import fast.dataflow.trust_domains as td
fixture_path = Path(os.path.dirname(__file__)) /  "dataflow_fixtures"
data_file = fixture_path /  "cross_package.json"
import fast.dataflow.cross_package as cp

# with open(fixture_path / "gulp-istanbul.pickle", 'rb') as f:
#     gi_data = pickle.load(f)

with open(fixture_path / "kraken-api.pickle", 'rb') as f:
    ka_data = pickle.load(f)
def test_rel_map_simplification():
    with open(data_file) as f:
        data = json.load(f)
    assert data

    filtered_data = {
        k: td.rel_map_to_cross_package_set(data[k])
        for k in data
    }
    assert filtered_data

# def test_get_excluded_nodes():
#     res = cp.get_excluded_nodes(gi_data)
#     assert res
# def test_graphs_from_vp_data():
#     assert gi_data
#     before_graph, after_graph = cp.graphs_from_version_pair_data(gi_data)
#     assert before_graph
#     assert after_graph
#
# def test_graph_differences():
#     before_graph, after_graph = cp.graphs_from_version_pair_data(gi_data)
#     diffs = cp.graph_differences(before_graph, after_graph, gi_data)
#     assert not diffs[0]
#     assert not diffs[1]

def test_ka():
    assert ka_data
    before_graph, after_graph = cp.graphs_from_version_pair_data(ka_data)
    static, user = cp.graph_differences(before_graph, after_graph, ka_data)
    assert before_graph
    assert after_graph
