""" (script)
Create the database incase it got deleted or smth or wanted to redo it
"""

import asyncio

from context import asyncpg_connect


async def create_user_db():
    """
    Creates Users table in the database

    Takes no parameters and doesn't return anything
    """
    async with asyncpg_connect() as conn:  # connect
        async with conn.transaction():  # start a transaction incase something goes wrong
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
