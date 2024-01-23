import argparse
import itertools
import json
import re
import sys
import os
from tempfile import TemporaryDirectory
from pathlib import Path

import networkx as nx

import fast.dataflow.trust_domains as td
import fast.dataflow.cross_package as cp

from rogue_one_runner import process_package, pr

def analyze_dep_upgrade(args:dict):
    # Use npm-check-updates to get the possible updates  (--jsonUpgraded)
    # Do a single-version analysis of the current project

    # Do a dual-version analysis of the dependency upgrade
    pass
def noop(*args):
    pass

def cap_report(args: dict):
    with TemporaryDirectory() as logging_dir:
        if args.get('before') and args.get('after'):
            res = dual_version_capabilities(Path(args['before']).absolute(), Path(args['after']).absolute(), logging_dir, printer=noop)
        elif args.get('single') and not args.get('with_deps'):
            res = single_version_capabilities(Path(args['single']).absolute(), Path(logging_dir), printer=noop)
        elif args.get('single') and args.get('with_deps'):
            res = with_deps_capabilities(Path(args['single']).absolute(), Path(logging_dir), printer=noop)
    json.dump(res, sys.stdout, indent=True)
    # Do a single version analysis of the current project
    # For each dependency, do a single-version analysis
    # Generate a capability for every path in the agglomerated graph to a system API.



def sv_analyze(target: os.PathLike, out_dir: os.PathLike, printer=pr, args=None):
    idg, odg, odg_time, idg_time = \
        process_package(target, printer=printer, args=args, logging_dir=out_dir)
    return (idg, odg, odg_time, idg_time)

def with_deps_capabilities(target: os.PathLike, out_dir: os.PathLike, printer=pr, args=None):
    target = Path(target)
    nm_path = target / 'node_modules'
    pkg_paths: list[Path] = [target] + [x for x in nm_path.glob('*/') if x.is_dir() and (x / 'package.json').exists()]
    caps = [single_version_capabilities(p, Path(out_dir) / p.parts[-1], printer=printer, args=args) for p in pkg_paths] # Can a package depend on a different version of itself?
    package_name = caps[0]['packageInfo']['name']
    res = {
        'packageInfo': caps[0]['packageInfo'],
        'capabilityInfo': [],
        'packages': {
            c['packageInfo']['name']: c for c in caps
        }
    }

    def trace_cap(cap, curPath):
        if len(curPath) > 10:
            return curPath
        if 'sourceTrustDomain' not in cap and 'depPath' in cap:
            source_td = cap['depPath'].split(' ')[0]
        elif 'sourceTrustDomain' in cap:
            source_td = cap['sourceTrustDomain']
        else:
            return None
        if source_td.startswith(td.c_td):
            looking_for = [(cap['packageName'], exp) for exp in cap['occursInExport']]
            if looking_for:
                target_td, export = looking_for[0]
                all_caps = itertools.chain(
                    *[p['capabilityInfo'] for pName, p in res['packages'].items() if pName != cap['packageName']])
                target_td_caps = [c for c in all_caps if 'destTrustDomain' in c and
                                  c.get('destTrustDomain', '') == target_td]
                target_exp_caps = [x for x in target_td_caps if
                                   x.get('depPath', '').endswith('.'.join([target_td, export]))]
                cap_lists = [trace_cap(c, [c] + curPath) for c in target_exp_caps]
                tested_cap_lists = [c for c in cap_lists if c]
                return sum(tested_cap_lists, [])
        elif source_td.startswith(td.l_td):
            if source_td in [td.l_td, td.l_td + ':', td.l_td + ':obj:']:
                return None
            else:
                return [curPath]
        elif source_td.split('.')[0] in cp.node_builtins:
            return [curPath]


    for pkgName, pkg in res['packages'].items():
        for cap in pkg['capabilityInfo']:
            if 'destTrustDomain' in cap and cap.get('destTrustDomain','') in cp.node_builtins:
                if cap['packageName'] == package_name:
                    if not cap['depPath'].split()[0] in [td.l_td, td.l_td + ':', td.l_td + ':obj:']:
                        res['capabilityInfo'].append(cap)
                    continue
                full_caps = trace_cap(cap, [cap])
                for cap_path in full_caps:
                    summary = ' '.join([cap_path[0]['depPath'].split(' ')[0]] +
                                            [inner_cap['depPath'].split(' ')[1] for inner_cap in cap_path])
                    res['capabilityInfo'].append({
                        'packageName': package_name,
                        'depPath': summary,
                        'paths': [cap_path]
                    })
    return res

def single_version_capabilities(target: os.PathLike, out_dir: os.PathLike, printer=pr, args=None):
    if not Path(out_dir).exists():
        Path(out_dir).mkdir(exist_ok=True, parents=True)
    with open(Path(target) / 'package.json') as f:
        package_json = json.load(f)
    package_name = package_json.get('name', 'NO_NAME_PRESENT')
    idg, odg, odg_time, idg_time = sv_analyze(target, out_dir, printer, args)
    rel_map = td.td_rel_map(idg, odgen_graph=odg, consolidate_tds=False)
    # cp_graph = cp.graph_from_rel_map_sets({package_name: rel_map}, package_name, consolidate_tds=False)
    # paths = {
    #     'caller':  nx.single_source_dijkstra_path(cp_graph, package_name + cp.ud),
    #     'static': nx.single_source_dijkstra_path(cp_graph, package_name + cp.sd),
    # }
    caps = []


    for rel in rel_map:
        #ast_path_pairs = []
        cap = {
            'packageName': package_name,
            'depPath': ' '.join(rel),
            'paths': [],
        }

        for path_pair in rel_map[rel]:
            ast_path_pair = []
            for path in path_pair:
                ast_path = []
                for n in path:
                    ast_n = [x[1] for x in idg.out_edges(n, data=True) if x[2]['type'] == 'OBJ_TO_AST']
                    if ast_n:

                        ast_path.append(ast_n[0])
                    else:
                        ast_path.append(None)
                ast_path_pair.append(ast_path)

            cap_path = {
                'dataPath': [],
                'propPath': [],
            }
            for k, path, ast_path in [('dataPath', path_pair[0], ast_path_pair[0]),
                                      ('propPath', path_pair[1], ast_path_pair[1])]:
                for i, (n, ast_n) in enumerate(zip(path, ast_path)):
                    attrs = idg.nodes[n]
                    cap_path_node = {}
                    if 'code' in attrs and str(attrs['code']) not in ['', '*', None]:
                        cap_path_node['name'] = attrs['code']
                    elif ast_n and 'code' in idg.nodes[ast_n] and idg.nodes[ast_n]['code'] not in ['', '*', None]:
                        cap_path_node['name'] = idg.nodes[ast_n]['code']
                    else:
                        cap_path_node['name'] = '*'
                        continue
                    if k == 'propPath' and isinstance(cap_path_node['name'], str) and len(cap_path_node['name']) > 10:
                        name_re = re.compile('([\w\._]+)\(.*\)')
                        m = name_re.fullmatch(cap_path_node['name'])
                        if m and m[1] != 'require':
                            cap_path_node['name'] = m[1]
                    if ast_n:
                        ast_attrs = idg.nodes[ast_n]
                        if ast_attrs.get('code_loc'):
                            code_points = ast_attrs['code_loc'].split(':')
                            cap_path_node['site'] =  {
                                'filename': ast_attrs['filename'],
                                # 'line': code_points[0],
                                # 'column': code_points[1] if code_points[1] else '1',
                                'code_loc': ast_attrs['code_loc'],
                            }
                    if 'trust_domain' in attrs:
                        cap_path_node['trust_domain'] = attrs['trust_domain']
                    if 'defined_in' in attrs:
                        d = [d.removeprefix('module.exports').removeprefix('.')
                                                        for d in attrs['defined_in'] if d.startswith('module.exports')]
                        if d and d != [""]:
                            cap_path_node['exportDefs'] = d

                    cap_path[k].append(cap_path_node)
                #for i, cpn in enumerate(cap_path[k]):
                #    if i not in [0, len(cap_path[k])-1] and 'site' in cpn:
                #        del cpn['site']
                cap_path[k] = [x for i,x in enumerate(cap_path[k]) if  i == len(cap_path[k])-1 or x['name'] != cap_path[k][i+1]['name']]
            cap['paths'].append(cap_path)
        for k, t in [('dataPath', 'sourceTrustDomain'), ('propPath', 'destTrustDomain')]:
            tds = [cap_path[k][0]['trust_domain'] for cap_path in cap['paths'] if cap_path[k] and 'trust_domain' in cap_path[k][0]]
            if tds:
                cap[t] = tds[0]
        for k, t in [('dataPath', 'occursInExport')]:
            tds = [cap_path[k][-1]['exportDefs'] for cap_path in cap['paths'] if cap_path[k] and 'exportDefs' in cap_path[k][-1]]
            if tds:
                cap[t] = tds[0]
        for k, t in [('propPath', 'destExport')]:
            tds = [cap_path[k][-1]['trust_domain'] for cap_path in cap['paths'] if cap_path[k] and 'trust_domain' in cap_path[k][-1]]
            if tds:
                cap[t] = tds[0]
        cap['paths'].sort(key=lambda x: str(x['dataPath'][0]['name']) if x['dataPath'] else str(x['propPath'][0]['name']))
        caps.append(cap)
    caps.sort(key=lambda x: x['depPath'])

    return {

        'capabilityInfo': caps,
        'packageInfo': {
            'name': package_name
        }
    }

def cap_diff(capabilities_before, capabilities_after):
    cap_name_set_before = { x['depPath'] for x in capabilities_before['capabilityInfo']}
    new_caps = [x for x in capabilities_after['capabilityInfo'] if x['depPath'] not in cap_name_set_before]
    return new_caps
def dual_version_capabilities(target_before: os.PathLike,target_after: os.PathLike,
                              out_dir: os.PathLike, printer=pr, args=None):
    res1, res2 = map(lambda x: single_version_capabilities(x[0], Path(out_dir) / x[1], printer=printer, args=args), [(target_before, 'v1'),(target_after, 'v2')])

    res = cap_diff(res1, res2)
    return {
        'new': res,
        'before': res1,
        'after': res2,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Command line interface for running RogueOne on a local Node project.")
    ap.add_argument("--with-deps", action="store_true", help="For use with single, analyzes dependencies in node_modules.", default=False)
    ap.add_argument("--single", action="store", help="The directory of the single module to be analyzed.")
    ap.add_argument("--before", action="store", help="For analyzing an update, the first version.")
    ap.add_argument("--after", action="store", help="For analyzing an update, the second version.")

    ap.add_argument("--config", action="store", help="A config file defining various options.  Defaults to "
                                                     "<rogue_one_dir>/db.json.")

    #ap.add_argument("--dep", "store", description="Which dependency should be analyzed for update.")
    cli_args = ap.parse_args()
    s_arg = (cli_args.single and not (cli_args.before and cli_args.after))
    u_arg = ((cli_args.before and cli_args.after) and not cli_args.single)
    if not (s_arg or u_arg):
        ap.error('Please supply either one argument to --single or arguments to both --before and --after.')

    cap_report(vars(cli_args) )
