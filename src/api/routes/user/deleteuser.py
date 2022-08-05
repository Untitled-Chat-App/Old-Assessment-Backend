""" (module)
Code for the endpoint to delete users
"""

__all__ = ["delete_user_endpoint"]

from fastapi import Depends, APIRouter, HTTPException, Request

from ...auth import check_auth_token
from core.models import AuthorizedUser, AuthPerms
from core.database import get_user_by_id, asyncpg_connect

delete_user_endpoint = APIRouter(
    tags=[
        "Users",
    ]
)


@delete_user_endpoint.delete("/api/users/{user_id}")
async def delete_specific_user(
    request: Request,
    user_id: int,
    auth_user: AuthorizedUser = Depends(check_auth_token),
):

    if auth_user.permissions.delete_users != True:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You don't have the permissions to perform this request.",
                "permission_needed": ["delete_users"],
            },
        )

    user = await get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "User with id provided does not exist",
                "id_provided": user_id,
            },
        )

    async with asyncpg_connect() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM Users WHERE user_id=$1", user_id)


@delete_user_endpoint.delete("/api/user/me")
async def delete_me(
    request: Request, auth_user: AuthorizedUser = Depends(check_auth_token)
):

    if auth_user.permissions.delete_self != True:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You don't have the permissions to perform this request.",
                "permission_needed": ["delete_self"],
            },
        )

    async with asyncpg_connect() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM Users WHERE user_id=$1", auth_user.user_id)

    is_deleted = await get_user_by_id(auth_user.user_id)

    if is_deleted is not None:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occured on the server side when updating the user",
                "what_err": "idk man, Im trYING My besT herE",
            },
        )

    return {"detail": "User was deleted succesfully"}
