from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Ensure project root and backend are on sys.path for imports
_HERE = os.path.abspath(os.path.dirname(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, '..'))
_BACKEND = os.path.join(_ROOT, 'backend')
for _p in (_ROOT, _BACKEND):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = None  # We'll set this dynamically


def get_url():
    """Get database URL from config."""
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Import models here to avoid circular imports
    try:
        try:
            # Prefer explicit package import
            from backend.models import Base  # type: ignore
        except Exception:
            # Fallback to direct import if backend is already in path
            from models import Base  # type: ignore
        global target_metadata
        target_metadata = Base.metadata
    except ImportError:
        # If models can't be imported, continue without metadata
        pass
    
    configuration = config.get_section(config.config_ini_section)
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Don't run anything when importing the file
# The functions will be called by Alembic when needed
