from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def ping_database(database_url: str) -> None:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    finally:
        await engine.dispose()
