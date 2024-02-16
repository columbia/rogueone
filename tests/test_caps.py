import sys
from tempfile import TemporaryDirectory

sys.path.append('../')

import caps
from helper import *

def test_sv_analyze():
    target = Path(single_v_folder) / 'simplest'
    with TemporaryDirectory() as td:
        res = caps.sv_analyze(target, td)
        assert res


def test_cap_simplest():
    target = Path(single_v_folder) / 'simplest'
    with TemporaryDirectory() as td:
        res = caps.single_version_capabilities(target, td)

    assert 'capabilityInfo' in res
    cap = res['capabilityInfo'][0]

    assert cap['packageName'] == 'simplest'

    assert res['packageInfo'] == {
            'name': 'simplest'
        }

def test_file_loader_before():
    target = Path(dual_v_folder) / 'file-loader_6.1.1-->6.r.1' / 'file-loader-6.1.1'
    with TemporaryDirectory() as td:
        res = caps.single_version_capabilities(target, td)
    assert  res

def test_file_loader_after():
    target = Path(dual_v_folder) / 'file-loader_6.1.1-->6.r.1' / 'file-loader-6.r.1'
    with TemporaryDirectory() as td:
        res = caps.single_version_capabilities(target, td)
    assert  res

def test_file_loader_dual():
    target = Path(dual_v_folder) / 'file-loader_6.1.1-->6.r.1'
    with TemporaryDirectory() as td:
        res = caps.dual_version_capabilities(target / 'file-loader-6.1.1', target / 'file-loader-6.r.1', td)
    assert  res

def test_dep_not_analyzed_single():
    target = Path(dep_folder) / 'mkdirp'
    with TemporaryDirectory() as td:
        idg, odg, _, _ = caps.sv_analyze(target, td)
    assert not [x for x in idg.nodes(data=True) if 'filename' in x[1] and x[1]['filename'] and 'minimist_index.js' in x[1]['filename']]

def test_with_dep_has_dep_cap():
    target = Path(dep_folder) / 'mkdirp'
    with TemporaryDirectory() as td:
        res = caps.single_version_capabilities(target, td)
    assert res
    assert any([x['depPath'].endswith('minimist') for x in res['capabilityInfo']])

def test_dep_analyzed():
    target = Path(dep_folder) / 'mkdirp'
    with TemporaryDirectory() as td:
        res = caps.with_deps_capabilities(target, td)
    assert res['packageInfo']['name'] == 'mkdirp'
    assert 'mkdirp' in res['packages']
    assert 'minimist' in res['packages']
    assert any([x['depPath'] == 'process.argv fake_net_lib.get https.get' for x in res['capabilityInfo']])
