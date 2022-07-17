""" (module) fetch
This is functions to fetch things from the database such as user by their user_id
The purpose is to split up these core useful functions into another file so it is more accesable
"""

from typing import Optional

from core.database import asyncpg_connect
from core.models import AuthPerms, AuthorizedUser


async def get_user(username: str) -> Optional[AuthorizedUser]:
    """
    Get user from database and return it as an AuthorizedUser class
    Supposed to be used for the authentication but can be used for normal getting user

    Parameters
    ----------
        username (str): The username of the user to check the db for

    Returns
    -------
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

    Parameters
    ----------
        user_id (int): The user_id of the user to check the db for

    Returns
    -------
        Optional[AuthorizedUser]: If user exists it returns it else returns None

    """
    async with asyncpg_connect() as conn:
        data = await conn.fetch("SELECT * FROM Users WHERE user_id=$1", user_id)
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
            user_id=data[0][0],
            public_key=data[0][5],
            permissions=perms,
        )
    return AuthorizedUser(
        username=data[0][1],
        user_id=data[0][0],
        password=data[0][3],
        email=data[0][2],
        public_key=data[0][5],
        permissions=perms,
    )
