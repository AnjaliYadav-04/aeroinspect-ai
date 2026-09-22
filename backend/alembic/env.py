import sys
sys.path.append("..")
from src.config import settings
from src.database import Base
from src.models import inspection, detection, asset, report, user
from alembic import context
from sqlalchemy import create_engine, pool

target_metadata = Base.metadata

def get_url():
    # Convert async URL to sync for Alembic
    url = settings.DATABASE_URL
    if url.startswith("sqlite+aiosqlite"):
        url = url.replace("sqlite+aiosqlite", "sqlite")
    return url

def run_migrations_offline():
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = get_url()
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
