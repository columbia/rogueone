from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from fast.manager.models import *
from pathlib import Path
import json

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Version.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
DB_PATH = Path(__file__).parent.parent / 'db.json'
try:
    with open(DB_PATH) as f:
        DB_JSON = json.load(f)
except FileNotFoundError as e:
    sys.stderr.write(f"No db config file found at {DB_PATH}.\n")
    sys.exit(1)
except json.JSONDecodeError as e:
    sys.stderr.write(f"Could not load json db config file at {DB_PATH}.\n")
    sys.exit(1)

section = config.config_ini_section
#sqlalchemy.url = %(driver)://%(user):%(pass)@%(host):%(port)/%(db)
config.set_section_option(section, 'driver', 'postgresql+psycopg2')
config.set_section_option(section, 'username',   DB_JSON['username'])
config.set_section_option(section, 'password',   DB_JSON['password'])
config.set_section_option(section, 'host',   DB_JSON['host'])
config.set_section_option(section, 'port',   DB_JSON['port'])
config.set_section_option(section, 'dbname', DB_JSON['db'])

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
