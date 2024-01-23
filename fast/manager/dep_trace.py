# This file is to support a dependency tracing effort to find the best targets for a supply chain attack
# targeted at the Node blockchain community.
import csv
import celery
import heapq
import itertools
import json
import multiprocessing
from multiprocessing import Pool
import sys
import time
from pathlib import Path

import networkx as nx
import networkx.exception
import requests
from tqdm import tqdm
import argparse

keywords = ['eth', 'ethereum', 'bitcoin', 'btc', 'crypto', 'wallet']
banned_nodes = ['@stdlib/utils' , '@stdlib/math', '@stdlib/assert' , '@stdlib/string', '@stdlib/array', 'google-closure-compiler', 'react-native', 'typescript', 'google-closure-compiler-linux', 'google-closure-compiler-osx', '@firebase@firestore', '@next@swc-darwin-arm64', '@next@swc-darwin-x64-musl', '@next@swc-darwin-x64-gnu', 'npm']


# for each keyword, take the top XX (maybe to a threshold of downloads)
# This forms leaf set that we trace back on dependencies with
# Build graph of depends-on edges
# Look back 2 years? To event-stream? (2018)
# https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md#get-v1search
site = 'https://registry.npmjs.com/'
search_url = site + '-/v1/search'

# text 	String 	Query 	❌ 	full-text search to apply
# size 	integer 	Query 	❌ 	how many results should be returned (default 20, max 250)
# from 	integer 	Query 	❌ 	offset to return results from
# quality 	float 	Query 	❌ 	how much of an effect should quality have on search results
# popularity 	float 	Query 	❌ 	how much of an effect should popularity have on search results
# maintenance 	float 	Query 	❌ 	how much of an effect should maintenance have on search results
search_opt_keys = {'text', 'size', 'from', 'quality', 'popularity', 'maintenance'}

# {'objects': [{'package': {'name': 'eth',
#                           'scope': 'unscoped',
#                           'version': '4.0.1',
#                           'description': 'A fun, productive, and simple '
#                                          'functional language that compiles to '
#                                          'JavaScript.',
#                           'date': '2016-08-06T09:19:45.681Z',
#                           'links': {'npm': 'https://www.npmjs.com/package/eth'},
#                           'author': {'name': 'Frederic Gingras',
#                                      'email': 'frederic@gingras.cc',
#                                      'username': 'kiasaki'},
#                           'publisher': {'username': 'kiasaki',
#                                         'email': 'frederic@gingras.cc'},
#                           'maintainers': [{'username': 'kiasaki',
#                                            'email': 'frederic@gingras.cc'}]},
#               'score': {'final': 0.19222705947987145,
#                         'detail': {'quality': 0.5924633848954479,
#                                    'popularity': 0.02032735283166043,
#                                    'maintenance': 0.021067058629016856}},
#               'searchScore': 100000.08},
#              {'package': {'name': 'web3-eth-abi',
#                           'scope': 'unscoped',
#                           'version': '4.1.1',
#                           'description': 'Web3 module encode and decode EVM '
#                                          'in/output.',
#                           'date': '2023-08-21T16:27:15.941Z',
#                           'links': {'npm': 'https://www.npmjs.com/package/web3-eth-abi',
#                                     'homepage': 'https://github.com/ethereum/web3.js/tree/4.x#readme',
#                                     'repository': 'https://github.com/ethereum/web3.js/tree/4.x',
#                                     'bugs': 'https://github.com/ethereum/web3.js/issues'},
#                           'author': {'name': 'ChainSafe Systems'},
#                           'publisher': {'username': 'jdevcs',
#                                         'email': 'junaid@chainsafe.io'},
#                           'maintainers': [{'username': 'mpetrunic',
#                                            'email': 'marin.petrunic@gmail.com'},
#                                           {'username': 'jdevcs',
#                                            'email': 'junaid@chainsafe.io'},
#                                           {'username': 'gregthegreek',
#                                            'email': 'gregorymarkou@gmail.com'}]},
#               'score': {'final': 0.3477927679326686,
#                         'detail': {'quality': 0.47419091023101667,
#                                    'popularity': 0.2539109377048485,
#                                    'maintenance': 0.3333333333333333}},
#               'searchScore': 7.299955e-06}],
#  'total': 2021,
#  'time': 'Tue Aug 29 2023 01:35:24 GMT+0000 (Coordinated Universal Time)'}
def _npm_search(text: str, size: int=100, offset: int=0, quality:float=0.1, popularity:float=0.8, maintenance:float=0.1):
    resp = requests.get(search_url, params={'text': text, 'size':size, 'from':offset,
                                            'quality':quality,'popularity':popularity, 'maintenance':maintenance})
    return resp.json()


def npm_search(text: str, quality:float=0.1, popularity:float=0.8, maintenance:float=0.1):
    cur_offset = 0
    limit = None
    sz = 250
    while True:
        result = _npm_search(text=text, size=sz, offset=cur_offset,
                             quality=quality, popularity=popularity, maintenance=maintenance)

        if not limit:
            limit = result['total']
        if not result.get('objects', []):
            break

        for x in result.get("objects", []):
            yield x

        if cur_offset + sz >= limit:
            break
        else:
            cur_offset += sz
def npm_view_package(package_name):
    url = site + f"{package_name}"
    return requests.get(url).json()

def npm_get_deps(package_name, data=None):
    if not data:
        data = npm_view_package(package_name)
    if 'versions' not in data:
        return []
    return data['versions'][data['dist-tags']['latest']].get('dependencies', [])

def leaf_packages(kw = keywords):
    packs = set()
    for k in kw:
        for package in npm_search(k):
            packs.add(package['package']['name'])
    return packs

def build_dep_graph(kw=keywords):
    to_visit = leaf_packages(kw=kw)
    visited = set()
    graph = nx.DiGraph()
    t = tqdm(total=len(to_visit))

    while to_visit:
        cur = to_visit.pop()
        visited.add(cur)
        graph.add_node(cur)
        deps = npm_get_deps(cur)
        for_total = 0
        for d in deps:
            graph.add_edge(cur, d, version=deps[d] )
            if d not in visited:
                to_visit.add(d)
                for_total += 1
        t.total += for_total
        t.update()
        t.refresh()
    return graph

def visit_dep(inq: multiprocessing.Queue, outq: multiprocessing.Queue, graphq: multiprocessing.Queue):
    while not inq.empty():
        cur = inq.get()
        graphq.put(cur)
        try:
            deps = npm_get_deps(cur)
            for d in deps:
                graphq.put((cur, d, deps[d]))
                outq.put(d)
        except celery.exceptions.SoftTimeLimitExceeded as e:
            raise e
        except Exception as e:
            print(f"Error processing {cur}, {e}")
            pass

def ensure_unique(inq: multiprocessing.Queue, outq: multiprocessing.Queue, starting_set=None):
    s = set()
    if starting_set:
        s = s.union(starting_set)

    while True:
        x = inq.get()
        if x not in s:
            outq.put(x)
            s.add(x)

def build_dep_graph_parallel(kw=keywords):
    print("Retrieving leaf packages.")
    to_visit = leaf_packages(kw=kw)
    graph = nx.DiGraph()

    to_be_visited = multiprocessing.Queue()
    to_be_verified_unique = multiprocessing.Queue()
    to_put_in_graph = multiprocessing.Queue()

    print("Populating initial queue.")
    for p in to_visit:
        to_be_visited.put(p)

    procs = []
    print("Starting workers.")
    for _ in range(0,int(multiprocessing.cpu_count()/2)):
        procs.append(multiprocessing.Process(target=visit_dep, args=[to_be_visited, to_be_verified_unique, to_put_in_graph]))
    uniquer = multiprocessing.Process(target=ensure_unique, args=[to_be_verified_unique, to_be_visited])

    for p in procs:
        p.start()
    uniquer.start()
    print("Started child processes.  Waiting for something to analyze.")

    while to_put_in_graph.empty():
        time.sleep(1)
    count = 0
    print("Populating graph.")
    min_to_pass = to_be_visited.qsize()
    t = tqdm(total=to_be_visited.qsize())
    while True:
        x = to_put_in_graph.get()
        count += 1
        if type(x) == str:
            graph.add_node(x)
        if type(x) == tuple:
            u, v, version = x
            if u != v:
                graph.add_edge(u, v, version=version)
        if count % 1000 == 0:
            print(f"Checkpointing {graph.number_of_nodes()}, {graph.number_of_edges()}")
            write_dep_graph(graph, 'checkpoint.gexf')
        t.update()
        if count >= min_to_pass and to_put_in_graph.empty():
            t.total = to_be_visited.qsize()
            t.n = 0
            t.refresh()
            time.sleep(1)
            if to_put_in_graph.empty():
                time.sleep(1)
                if to_put_in_graph.empty():
                    time.sleep(1)
                    if to_put_in_graph.empty():
                        time.sleep(1)
                        if to_put_in_graph.empty():
                            break

    print("Joining procs.")
    for p in procs:
        p.join()
    uniquer.terminate()

    t.n = 0
    t.total = to_put_in_graph.qsize()
    t.refresh()
    while not to_put_in_graph.empty():
        x = to_put_in_graph.get()
        if type(x) == str:
            graph.add_node(x)
        if type(x) == tuple:
            u, v, version = x
            if u != v:
                graph.add_edge(u, v, version=version)
        t.update()


    return graph
def write_dep_graph(graph, fn):
    nx.write_gexf(graph,fn)
def read_dep_graph(fn):
    return nx.read_gexf(fn)

def remove_banned_nodes(graph: nx.DiGraph, banned=banned_nodes):
    for n in banned:
        try:
            graph.remove_node(n)
        except networkx.exception.NetworkXError as e:
            pass

def de_cycle(graph: nx.DiGraph):
    cycles = nx.simple_cycles(graph)

    for c in cycles:
        try:
            graph.remove_edge(c[-1], c[0])
        except networkx.exception.NetworkXError as e:
            pass

def prioritize_packages(graph: nx.classes.digraph.DiGraph):
    topo = nx.topological_sort(graph)
    # Starting from the side with no descendants:
    # Priority number = 1 + sum of priorities of descendants
    # return map node -> int
    q = []
    m = {}
    for n in topo:
        if n in m:
            pri = m[n]
        else:
            pri = 1
        for np in nx.descendants_at_distance(graph, n, 1):
            if np in m:
                m[np] += pri
            else:
                m[np] = pri + 1

        heapq.heappush(q, (pri, n))
    return q

def print_pri_q(q: list[tuple[int,str]], fn='crypto_dep_list.csv'):
    with open(fn,'w') as f:
        c = csv.writer(f)
        c.writerow(['Number of depending packages', 'Package Name'])
        while q:
            p = heapq.heappop(q)
            c.writerow(p)

def tarball_url(p: str, v: str):
    # 'https://registry.npmjs.org/foo/-/foo-1.0.0.tgz
    scoped = p[0] == '@'
    if scoped:
        scopeless_name = p.split('/')[1]
    else:
        scopeless_name = p
    return site + p + '/-/' + scopeless_name + '-' + v + '.tgz'

done_map = {}

def get_package_info(p:list[str]):
    if p[1] in banned_nodes:
        return None

    data = requests.get(site + p[1]).json()
    if 'versions' not in data or 'name' not in data:
        return None


    versions = list(data['versions'].keys())
    version_pairs = zip(versions, versions[1:])
    scoped = data['name'][0] == '@'
    base_folder = Path(args.sample_folder) / "retro_survey"
    base_folder.mkdir(exist_ok=True)
    if scoped:
        pass
        u_name, s_p_name = data['name'].split('/')
        name_for_db = f"{u_name}@{s_p_name}"
    else:
        name_for_db = data['name']

    for v1, v2 in version_pairs:
        if name_for_db in done_map and v2 in done_map[name_for_db]:
            continue
        # create version pair folder

        folder_name = Path(f"{name_for_db}_{v1}-->{v2}")
        folder = base_folder / folder_name
        try:
            if not folder.exists():
                folder.mkdir()
        except OSError:
            # File name too long.
            break
        try:
            for v in [v1, v2]:
                tgz_name = folder / (name_for_db + '@' + v + '.tgz')
                if tgz_name.exists():
                    continue
                with requests.get(tarball_url(data['name'], v), stream=True) as r:
                    r.raise_for_status()
                    with open(tgz_name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            # If you have chunk encoded response uncomment if
                            # and set chunk_size parameter to None.
                            # if chunk:
                            f.write(chunk)
        except requests.exceptions.HTTPError:
            flag_file = folder / 'DONOTANALYZE'
            flag_file.touch(exist_ok=True)
            for v in [v1, v2]:
                tgz_name = folder / (name_for_db + '@' + v + '.tgz')
                tgz_name.touch(exist_ok=True)
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    pass

fn = 'crypto_dep_graph.gexf'
list_fn = 'crypto_dep_list.csv'
if __name__ == '__main__':
    #write_dep_graph(build_dep_graph_parallel(), 'crypto_dep_graph')
    #write_dep_graph(build_dep_graph_parallel(['tree-monkey']), 'crypto_dep_graph')
    ap = argparse.ArgumentParser(description="utilities for dependency tracing to prioritize retrospective analysis.")
    ap.add_argument("--sample_folder", action="store", help="A folder containing folders of datasets, each of which has \
    folders of before/after update pairs.  e.g. given Samples/30_backstabber_samples/pack_0.1-->pack_0.2/pack_0.1/ as a\
     sample, the argument should be just Samples, so that the samples are captured by **/**/*/", required=True)

    ap.add_argument("--db", action="store", default=False, required=False)
    ap.add_argument("--start_at", action="store", default=0, required=False)
    args = ap.parse_args()
    #if args.db:
    #    try:
    #        with open(args.db) as f:
    #            db = json.load(f)
    #    except FileNotFoundError as e:
    #        sys.stderr.write(f"No db config file found at {args.db}.\n")
    #        sys.exit(1)
    #    except json.JSONDecodeError as e:
    #        sys.stderr.write(f"Could not load json db config file at {args.db}.\n")
    #        sys.exit(1)
    #    db_uri = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"
    #    engine, Session = engine.init(db_uri, echo=False)
    #else:
    #    engine, Session = engine.init()
    #session = Session()
    dmp = 'retro_vps_so_far'
    if Path(dmp).exists():
        with open(dmp) as f:
            done_map = json.load(f)

    if Path(list_fn).exists():
        with open(list_fn) as f:
            c = csv.reader(f)
            d = list(c)
        d.reverse()
        with tqdm(total=len(d)) as pbar:
            for x in range(0, int(args.start_at)):
                d.pop(0)
                pbar.update()

            with Pool(int(multiprocessing.cpu_count()*0.7)) as p:
                    #for a in p.map(partial(package_pair_wrapper, args=args), sample_dirs):
                for a in p.imap_unordered(get_package_info, d):
                    pbar.update()

                p.close()
                p.join()

        sys.exit(0)
    if Path(fn).exists():
        g = read_dep_graph(fn)
        remove_banned_nodes(g)
        de_cycle(g)
        q = prioritize_packages(g)
        print_pri_q(q)
    else:
        print(f"Graph file {fn} not found, building.")
        write_dep_graph(build_dep_graph_parallel(), fn)
