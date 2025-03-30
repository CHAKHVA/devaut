import os
import sys
from logging.config import fileConfig

from alembic import context

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from sqlmodel import SQLModel  # noqa: E402

from app.models import quiz_models  # noqa: E402, F401

try:
    from app.db.session import engine as app_engine

    if app_engine is None:
        raise ImportError("Database engine is not initialized in app.core.session")
except ImportError as e:
    print(f"Error importing database engine: {e}")
    print("Ensure app.core.session.engine is correctly initialized.")
    sys.exit(1)

target_metadata = SQLModel.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    try:
        from app.core.config import settings

        if settings.DATABASE_URL is None:
            raise ValueError("settings.DATABASE_URL is not configured.")
        url = str(settings.DATABASE_URL)
    except Exception as e:
        print(f"Error getting DATABASE_URL from settings for offline mode: {e}")
        sys.exit(1)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = app_engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
