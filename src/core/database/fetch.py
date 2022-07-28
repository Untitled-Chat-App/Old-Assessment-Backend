""" (module) fetch
This is functions to fetch things from the database such as user by their user_id
The purpose is to split up these core useful functions into another file so it is more accesable
"""

from typing import Optional

import asyncpg

from core.database import asyncpg_connect
from core.models import AuthPerms, AuthorizedUser, Room


async def get_user(username: str) -> Optional[AuthorizedUser]:
    """
    Get user from database and return it as an AuthorizedUser class
    Supposed to be used for the authentication but can be used for normal getting user

    Parameters:
        username (str): The username of the user to check the db for

    Returns:
        Optional[AuthorizedUser]: If user exists it returns it else returns None

    """
    async with asyncpg_connect() as conn:
        data = await conn.fetch("SELECT * FROM Users WHERE username=$1", username)
        if not len(data):
            return None

    perms = AuthPerms(
        # Normal user perms aka get good skill gap imagine not having perms
        get_user_details=True,
        update_user_details=True,
        get_messages=True,
        send_messages=True,
        # Admin perms
        create_users=False,
        delete_users=False,
        update_users=False,
    )
    if data[0][4] == 23:  # asked friend for random number
        perms.create_users = True
        perms.delete_users = True
        perms.update_users = True

        return AuthorizedUser(
            username=data[0][1],
            password=data[0][3],
            email=data[0][2],
            public_key=data[0][5],
            user_id=data[0][0],
            permissions=perms,
        )
    return AuthorizedUser(
        username=data[0][1],
        password=data[0][3],
        public_key=data[0][5],
        user_id=data[0][0],
        email=data[0][2],
        permissions=perms,
    )


async def get_user_by_id(user_id: int) -> Optional[AuthorizedUser]:
    """
    Get user from database and return it as an AuthorizedUser class
    Supposed to be used for the authentication but can be used for normal getting user

    Parameters:
        user_id (int): The user_id of the user to check the db for

    Returns:
        Optional[AuthorizedUser]: If user exists it returns it else returns None

    """
    async with asyncpg_connect() as conn:
        try:
            data = await conn.fetch("SELECT * FROM Users WHERE user_id=$1", user_id)
        except asyncpg.exceptions.DataError:
            return None
        if not len(data):
            return None

    perms = (
        AuthPerms()
    )  # Normal user perms aka get good skill gap imagine not having perms
    
    if data[0][4] == 23:  # asked friend for random number
        perms.delete_self = True
        perms.create_rooms = True
        perms.ban_users = True
        perms.unban_users = True
        perms.create_users = True
        perms.delete_users = True
        perms.update_users = True

    return AuthorizedUser(
        username=data[0][1],
        user_id=data[0][0],
        password=data[0][3],
        email=data[0][2],
        public_key=data[0][5],
        permissions=perms,
    )


async def get_room(room_id: int = None, room_name: str = None) -> Room | None:
    """
    Fetches a Room from the Rooms table using either the room's id or the name

    Parameters:
        room_id (Optional[int]): The id of the room to search for
        room_name (Optional[str]): The name of the room to search for

    Returns:
        Optional[Room]: The room object if found else it will be None
    """
    if not any([room_id, room_name]) or all([room_id, room_name]):
        return None

    async with asyncpg_connect() as conn:
        if room_id is not None:
            data = await conn.fetch("SELECT * FROM Rooms WHERE room_id=$1", room_id)
        else:
            data = await conn.fetch("SELECT * FROM Rooms WHERE room_name=$1", room_name)

        if not len(data):
            return None

    data = data[0]

    return Room(
        room_id=data[0], room_name=data[1], created_at=data[2], room_description=data[3]
    )
