from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.storage.models import Base


DATABASE_URL = settings.database_url

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    Path(settings.db_dir).mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def migrate_audit_columns(sync_conn):
            from sqlalchemy import text
            res = sync_conn.execute(text("PRAGMA table_info(audit_logs)")).fetchall()
            existing_cols = {row[1] for row in res}
            if existing_cols:
                if "prev_hash" not in existing_cols:
                    sync_conn.execute(text("ALTER TABLE audit_logs ADD COLUMN prev_hash VARCHAR(64)"))
                if "record_hash" not in existing_cols:
                    sync_conn.execute(text("ALTER TABLE audit_logs ADD COLUMN record_hash VARCHAR(64)"))

        await conn.run_sync(migrate_audit_columns)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
