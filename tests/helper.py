import contextlib
import os
from glob import glob
import fast.dataflow.extraction as ex
from fast.manager.package_changes import build_package_json_changes
from fast.simurun import launcher
from pathlib import Path

single_v_folder = os.path.join(os.path.dirname(__file__), 'dataflow_fixtures', "single_version")
single_folders = glob(os.path.join(single_v_folder, '*/'))
dual_v_folder = os.path.join(os.path.dirname(__file__), 'dataflow_fixtures', "dual_version")
dep_folder = os.path.join(os.path.dirname(__file__), 'dataflow_fixtures', "with_dependencies")

dual_v_folders = glob(os.path.join(dual_v_folder, '*/'))

gen_graph_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'fast', 'generate_graph.py')
@contextlib.contextmanager
def remember_cwd():
    curdir= os.getcwd()
    try: yield
    except Exception as e: raise e
    finally: os.chdir(curdir)
def single_v_idg(f, scripts=None):
    if single_v_folder in f:
        folder = f
    else:
        folder = os.path.join(single_v_folder, f)
    #launcher_cmd = ['python3', gen_graph_path, '-t', 'data_flow', '-f', '800', '--json', '--module', '--run-all']
    #launcher_cmd.append(folder)

    result, g, result_paths =  launcher.unittest_main(folder, vul_type='data_flow', module=True, original_path=folder,
                                                      scripts=scripts)
    return ex.extract_idg(g), g

def dual_v_idg(f):
    folder = Path(dual_v_folder) / f
    v1_folder = glob(os.path.join(folder, '*v1*'))[0]
    v2_folder = glob(os.path.join(folder, '*v2*'))[0]
    scripts = build_package_json_changes(v1_folder, v2_folder)
    return *single_v_idg(v1_folder, scripts=scripts), *single_v_idg(v2_folder, scripts=scripts)
