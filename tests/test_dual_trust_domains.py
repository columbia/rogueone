import pytest

from fast.manager.package_changes import build_changed_file_list
import fast.dataflow.trust_domains as td
from helper import *

def single_v_main(f, additional_files=None, scripts=None):
    with remember_cwd():

        if not additional_files:
            additional_files=set()
        folder = os.path.join(single_v_folder, f)
        os.chdir(folder)
        launcher_cmd = [folder, '-t', 'data_flow', '-f', '800', '--json', '--module', '--run-all']

        g =  launcher.main(argv=launcher_cmd, scripts=scripts, additional_files=additional_files)
        return ex.extract_idg(g), g
def dual_v_idg_main(f):
    folder = os.path.join(dual_v_folder, f)
    v1_folder = glob(os.path.join(folder, '*v1*'))[0]
    v2_folder = glob(os.path.join(folder, '*v2*'))[0]
    scripts = build_package_json_changes(v1_folder, v2_folder)
    add_files = build_changed_file_list(v1_folder, v2_folder)
    return (*single_v_main(v1_folder, scripts=dict(), additional_files=add_files),
            *single_v_main(v2_folder, scripts=scripts, additional_files=add_files), scripts)

def test_jas_authsync_simpl():
    before_idg, before_odg, after_idg, after_odg = dual_v_idg('jas_authsync_simpl')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert (td.l_td, 'fs.writeFileSync') in diff

def test_jas_authsync():
    before_idg, before_odg, after_idg, after_odg = dual_v_idg('jas_authsync')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert diff

    diff_new_local = td.flagged_new_local_rels_from_tuples(before_tups, after_tups)
    assert diff_new_local

    diff_one_local = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert diff_one_local

def test_jas_authsync_new_local():
    before_idg, before_odg, after_idg, after_odg = dual_v_idg('jas_authsync_new_local')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    # Failing because we're not catching new static sources
    assert diff

    diff_new_local = td.flagged_new_local_rels_from_tuples(before_tups, after_tups)
    assert diff_new_local

    diff_one_local = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert diff_one_local

def test_removed_source():
    before_idg, before_odg, after_idg, after_odg = dual_v_idg('removed_source')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert not diff


def test_new_dep():
    before_idg, before_odg, after_idg, after_odg = dual_v_idg('new_dep')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)

    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert ((td.c_td, 'newLib') in diff or ('newLib', td.c_td) in diff)
def test_new_dep_flatmap():
    before_idg, before_odg, after_idg, after_odg = dual_v_idg('new_dep_flatmap')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)

    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert ((td.c_td, 'badlib') in diff or ('badlib', td.c_td) in diff)

def test_added_script():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('added_script')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg, scripts=scripts)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert (td.l_td, 'install_scripts') in diff



def test_rpc_websocket_1():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('rpc-websocket-add-daemon')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert not diff

def test_frontend_obfuscated():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('frontend_obfuscated')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert diff

def test_frontend_simpl():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('frontend_simpl')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)

    assert (':local', ':sys:frontend:document.createElement') in diff

def test_overview_ex_bad():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('overview_ex_bad')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert ('logger.send', ':caller') in diff or (':caller', 'logger.send') in diff
    with remember_cwd():
        os.chdir(os.path.join(dual_v_folder, "overview_ex_bad"))
        td.sanitize_and_export(before_idg, "before_idg.graphml")
        td.sanitize_and_export(after_idg, "after_idg.graphml")


def test_overview_ex_ben():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('overview_ex_ben')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert ('logger', ':caller') not in diff
    assert (':caller', 'logger') not in diff
    with remember_cwd():
        os.chdir(os.path.join(dual_v_folder, "overview_ex_ben"))
        td.sanitize_and_export(before_odg.graph, "before_odg.graphml")

        td.sanitize_and_export(before_idg, "before_idg.graphml")
        td.sanitize_and_export(after_idg, "after_idg.graphml")

def test_secure_vs_public_ben():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('secure_vs_public_ben')
    before_rels = td.td_rel_map(before_idg, consolidate_tds=True)
    after_rels = td.td_rel_map(after_idg, consolidate_tds=True)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert not diff
    assert (td.proc_td, 'public-store') not in before_rels
    assert ('public-store', td.proc_td) not in before_rels
    assert (td.proc_td, 'secure-store') in before_rels

def test_secure_vs_public_bad():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('secure_vs_public_bad')
    before_rels = td.td_rel_map(before_idg, consolidate_tds=True)
    after_rels = td.td_rel_map(after_idg, consolidate_tds=True)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert (td.proc_td, 'public-store') in diff


def test_yummy_bolts():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('yummy-bolts')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert diff

def test_max_fp():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('max-fp')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert diff

    diff_new_local = td.flagged_new_local_rels_from_tuples(before_tups, after_tups)
    assert not diff_new_local

    diff_one_local = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert not diff_one_local

def test_design_ex():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('design_ex')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert diff

    diff_new_local = td.flagged_new_local_rels_from_tuples(before_tups, after_tups)
    assert diff_new_local

    diff_one_local = td.flagged_single_local_rels_from_tuples(before_tups, after_tups)
    assert diff_one_local

@pytest.mark.skip(reason="First version does not trigger module.exports entrypoint - bug.")
def test_txtswitch():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('txtswitch')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    # This test is failing because the module.exports entrypoint is not being triggered in the first version.
    # The second version adds a test which triggers it, causing the code to be explored.
    assert not diff

def test_empty():
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('empty_v1-->v2')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert not diff

def test_file_loader():
    # This test checks whether we can detect a change that uses a method defined inside the importing package
    # and reached through `this` in an exported method
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('file-loader_6.1.1-->6.r.1')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert diff

def test_constructor():
    # This test checks whether we can detect a change that uses an exported constructor for an attack
    before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('constructor_attack')
    before_rels = td.td_rel_map(before_idg)
    after_rels = td.td_rel_map(after_idg)
    before_tups = td.rels_as_tuples(before_rels)
    after_tups = td.rels_as_tuples(after_rels)
    diff = td.flagged_rels_from_tuples(before_tups, after_tups)
    assert diff

# def test_xrpl():
#     # This test checks on a timeout
#     before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('xrpl')
#     before_rels = td.td_rel_map(before_idg)
#     after_rels = td.td_rel_map(after_idg)
#     before_tups = td.rels_as_tuples(before_rels)
#     after_tups = td.rels_as_tuples(after_rels)
#     diff = td.flagged_rels_from_tuples(before_tups, after_tups)
#     assert diff
#
# def test_jade():
#     # This test checks on a timeout
#     before_idg, before_odg, after_idg, after_odg, scripts = dual_v_idg_main('jade')
#     before_rels = td.td_rel_map(before_idg)
#     after_rels = td.td_rel_map(after_idg)
#     before_tups = td.rels_as_tuples(before_rels)
#     after_tups = td.rels_as_tuples(after_rels)
#     diff = td.flagged_rels_from_tuples(before_tups, after_tups)
#     assert not diff
