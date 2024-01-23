import argparse
import json
import sys
from pathlib import Path

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import text
from tqdm import tqdm

import fast.manager.engine as engine
from fast.manager.registry import fetch_npm_registry_with_path
import celery

def update_sql_tables(session) -> bool:
    try:
        check_column = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='package' and column_name='description';
        """
        if not session.execute(text(check_column)).fetchall():
            add_description = "ALTER TABLE package ADD COLUMN description VARCHAR(1000)"
            session.execute(text(add_description))
        change_nullable = """
        ALTER TABLE version 
        ALTER COLUMN disk_location DROP NOT NULL,
        ALTER COLUMN package_json DROP NOT NULL;
        """
        session.execute(text(change_nullable))

    except sqlalchemy.exc.ProgrammingError as e:
        sys.stderr.write(f"Caught SQL Error {e} when updating tables.\n")
        return False
    return True


def add_sql_download_field(session) -> bool:
    """
    This segment adds a "downloads" field for the version, if we are tracking version downloads
    """
    try:
        version_column = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='version' and column_name='downloads';
        """
        if not session.execute(text(version_column)).fetchall():
            add_description = "ALTER TABLE version ADD COLUMN downloads INTEGER"
            session.execute(text(add_description))
    except sqlalchemy.exc.ProgrammingError as e:
        sys.stderr.write(f"Caught SQL Error {e} when updating tables.\n")
        return False
    return True


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description="Runner to detect NPM security markers")
    ap.add_argument("--db", action="store", default=False, required=False)
    ap.add_argument("--sample_folder", action="store", help="A folder containing folders of datasets, each of which has \
    folders of before/after update pairs.  e.g. given Samples/30_backstabber_samples/pack_0.1-->pack_0.2/pack_0.1/ as a\
     sample, the argument should be just Samples, so that the samples are captured by **/**/*/", required=False)
    args = ap.parse_args()
    global db_uri
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
        engine, Session = engine.init(db_uri, echo=False)
    else:
        engine, Session = engine.init()
    sess = Session()

    if not update_sql_tables(sess):
        sys.stderr.write(f"Could not update SQL tables to new format.\n")
        sys.exit(1)
    if not add_sql_download_field(sess):
        sys.stderr.write("Could not update SQL table to have download field.\n")
        sys.exit(1)

    dirs = [x for x in Path(args.sample_folder).glob("*/*") if x.is_dir()]
    sys.stdout.write(f"Found {len(dirs)} total packages.\n")

    # Concurrent Implementation?
    with tqdm(total=len(dirs)) as pbar:
        for file in dirs:
            try:
                sess.commit()
                fetch_npm_registry_with_path(sess, file)
            except celery.exceptions.SoftTimeLimitExceeded as e:
                raise e
            except Exception as e:
                sys.stderr.write(f"Failed to fetch for {file}: {e}")
                sess.rollback()
            pbar.update()
