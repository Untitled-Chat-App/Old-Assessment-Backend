""" (module)
Code for the endpoint to request info for a user by username or id
"""

__all__ = ["get_user_endpoint"]


from fastapi import Depends, APIRouter, HTTPException, Request

from ...auth import check_auth_token
from core.models import AuthorizedUser, AuthPerms
from core.database import get_user_by_id, asyncpg_connect


get_user_endpoint = APIRouter(
    tags=[
        "Users",
    ]
)


@get_user_endpoint.get("/api/users/getAllUsers")
async def get_all_users(
    request: Request, auth_user: AuthorizedUser = Depends(check_auth_token)
):
    """
    Get all of the users HAHAHAHAA
    """
    if (
        auth_user.permissions.get_other_users != True
    ):  # if they dont have the permissions to create users
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to use this endpoint (skill issue)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with asyncpg_connect() as conn:
        database_user_data = await conn.fetch("SELECT * FROM Users")

    users: list[AuthorizedUser] = []

    for data in database_user_data:
        perms = AuthPerms()
        if data[4] == 23:  # asked friend for random number
            perms.mofify_self = True
            perms.delete_self = True
            perms.create_rooms = True
            perms.ban_users = True
            perms.unban_users = True
            perms.create_users = True
            perms.delete_users = True
            perms.get_old_messages = True
            perms.update_users = True

        user = AuthorizedUser(
            username=data[1],
            user_id=data[0],
            password=data[3],
            email=data[2],
            public_key=data[5],
            permissions=perms,
        )

        del user.password
        del user.email

        users.append(user)

    return users


@get_user_endpoint.get("/api/users/{user_id}")
async def get_user_with_user_id(
    request: Request,
    user_id: int,
    auth_user: AuthorizedUser = Depends(check_auth_token),
):
    """
    Get some users by their userid

    Parameters:
        user_id (int): The user ID of the user to fetch
    """
    if (
        auth_user.permissions.get_other_users != True
    ):  # if they dont have the permissions to create users
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to use this endpoint (skill issue)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(
        user_id
    )  # Check if someone has the same username/account already exists

    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "detail": "User with id provided doesnt exist",
                "id_provided": user_id,
                "error": "",
                "tip": "Make sure you typed the user id correctly",
                "extra": "Skill issue",
            },
        )

    del user.password
    del user.email

    return user
