import fast.manager.engine as engine
import json
import argparse
from fast.manager.models import *
import sqlalchemy
import sqlalchemy as sa
from pprint import pp
import tasks
import sys
import networkx as nx
import fast.dataflow.cross_package as cp
import fast.dataflow.trust_domains as td


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Direct console access.")
    ap.add_argument("--db", action="store", default=False, required=False)
    ap.add_argument("--echo", action="store_true", default=False, required=False)
    args = ap.parse_args()

    if args.db:
        try:
            with open(args.db) as f:
                db = json.load(f)
        except FileNotFoundError as e:
            sys.stderr.write(f"No db config file found at {args.db}.\n")
            sys.exit(1)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Could not load json db config file at {args.db}.\n")
            sys.exit(1)
        db_uri = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"
        engine, Session = engine.init(db_uri, echo=args.echo)
    else:
        engine, Session = engine.init()
    sess = Session()
    session = sess
    sei = 'system_extra_info'


