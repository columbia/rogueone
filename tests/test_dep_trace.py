import unittest
import fast.manager.dep_trace as dep_trace

class DepTraceTest(unittest.TestCase):
    def test_npm_search_base(self):
        resp = dep_trace._npm_search('eth', size=2)
        self.assertIsNotNone(resp)

    def test_npm_search(self):
        count = 0
        for x in dep_trace.npm_search('tree-monkey'):
            count+= 1
        assert count > 0

    def test_npm_search_nothing(self):
        count = 0
        for x in dep_trace.npm_search('awoifjap;owijgp;aoeirjg'):
            count+= 1
        assert count == 0
    def test_fetch(self):
        resp = dep_trace.npm_view_package('eth')
        self.assertIsNotNone(resp)
        assert resp['_id'] == 'eth'

    def test_leaf_packages(self):
        res = dep_trace.leaf_packages(kw=['tree-monkey'])
        assert res is not None
    def test_build_dep_graph(self):
        res = dep_trace.build_dep_graph(['tree-monkey'])
        assert res is not None

    def test_build_dep_graph_parallel(self):
        res = dep_trace.build_dep_graph_parallel(['tree-monkey'])
        dep_trace.write_dep_graph(res, "test_graph.gexf")
        assert res is not None
if __name__ == '__main__':
    unittest.main()
