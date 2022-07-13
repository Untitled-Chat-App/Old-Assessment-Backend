import asyncio

from context import asyncpg_connect


async def create_user_db():
    async with asyncpg_connect() as conn:
        async with conn.transaction():
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS Users (
                    user_id INTEGER PRIMARY KEY, 
                    username VARCHAR(64) NOT NULL, 
                    email VARCHAR(64) NOT NULL, 
                    password VARCHAR(64) NOT NULL,
                    permission_level INTEGER NOT NULL DEFAULT 1,
                    public_key TEXT
                )"""
            )


async def main():
    await create_user_db()

asyncio.run(main())


