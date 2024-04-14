from sqlalchemy import MetaData

from data_base.database import get_engine, Base
from data_base.utils import create_database


async def innit_db():
    engine = get_engine()
    db_url = engine.url
    await create_database(db_url)

    async with engine.begin() as conn:
        # create tables, functions, triggers and other db objects
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    return db_url
