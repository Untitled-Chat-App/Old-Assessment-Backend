""" (script)
Create the database in case it got deleted or smth or i wanted to redo it
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
                    user_id INTEGER PRIMARY KEY NOT NULL, 
                    username TEXT NOT NULL, 
                    email TEXT NOT NULL, 
                    password TEXT NOT NULL,
                    permission_level INTEGER NOT NULL DEFAULT 1,
                    public_key TEXT NOT NULL
                )"""
            )


async def create_room_db():
    """
    Creates Rooms table in the database

    Takes no parameters and doesn't return anything
    """
    async with asyncpg_connect() as conn:  # connect
        async with conn.transaction():  # start a transaction incase something goes wrong
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS Rooms (
                    room_id INTEGER PRIMARY KEY NOT NULL, 
                    room_name TEXT NOT NULL, 
                    room_created_at INTEGER NOT NULL,
                    room_description TEXT
                )"""
            )


async def main():
    await create_user_db()
    await create_room_db()


asyncio.run(main())
