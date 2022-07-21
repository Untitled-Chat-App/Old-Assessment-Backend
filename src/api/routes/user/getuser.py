""" (module)
Code for the endpoint to request info for a user by username or id
"""

__all__ = ["get_user_endpoint"]


from fastapi import Depends, APIRouter, HTTPException

from ...auth import check_auth_token
from core.models import AuthorizedUser, AuthPerms
from core.database import get_user_by_id, asyncpg_connect


get_user_endpoint = APIRouter()


@get_user_endpoint.get("/api/users/{user_id}")
async def get_user_with_user_id(
    user_id: int, auth_user: AuthorizedUser = Depends(check_auth_token)
):
    """
    Get some users by their userid

    Requirements
    ------------
        user_id
    """
    if (
        auth_user.permissions.get_user_details != True
    ):  # if they dont have the permissions to create users
        return HTTPException(
            status_code=403,
            detail="You don't have permission to use this endpoint (skill issue)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(
        user_id
    )  # Check if someone has the same username/account already exists

    del user.password

    if user is None:
        return HTTPException(
            status_code=409,
            detail="User with this username doesnt exists",
        )

    return user


@get_user_endpoint.get("/api/getAllUsers")
async def get_all_users(auth_user: AuthorizedUser = Depends(check_auth_token)):
    """
    Get all of the users HAHAHAHAA
    """
    if (
        auth_user.permissions.get_user_details != True
    ):  # if they dont have the permissions to create users
        return HTTPException(
            status_code=403,
            detail="You don't have permission to use this endpoint (skill issue)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with asyncpg_connect() as conn:
        database_user_data = await conn.fetch("SELECT * FROM Users")

    users: list[AuthorizedUser] = []

    for data in database_user_data:
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
        if data[4] == 23:  # asked friend for random number
            perms.create_users = True
            perms.delete_users = True
            perms.update_users = True

            user = AuthorizedUser(
                username=data[1],
                password=data[3],
                email=data[2],
                user_id=data[0],
                public_key=data[5],
                permissions=perms,
            )
        else:
            user = AuthorizedUser(
                username=data[1],
                user_id=data[0],
                password=data[3],
                email=data[2],
                public_key=data[5],
                permissions=perms,
            )

        del user.password
        users.append(user)

    return users
