""" (module)
Code for the endpoint to update a user or delete them
"""

__all__ = ["get_user_endpoint"]

from pydantic import BaseModel
from fastapi import Depends, APIRouter, HTTPException, Request

from core.utils import hash_text
from ...auth import check_auth_token
from core.models import AuthorizedUser
from core.database import get_user_by_id, asyncpg_connect


other_user_endpoints = APIRouter(
    tags=[
        "Users",
    ]
)


class UpdateBody(BaseModel):
    attribute: str
    new_value: str | int | bool


@other_user_endpoints.patch("/api/users/{user_id}")
async def update_user_data(
    request: Request,
    user_id: int,
    update_details: UpdateBody,
    auth_user: AuthorizedUser = Depends(check_auth_token),
):
    """
    Update a user in the database

    Parameters:
        user_id (int): The id of the user to modify
        update_details {
            attribute (str): The attribute of the user you want to modify (eg "username")
            new_value (str|int|bool): The new value of that attribute
        }
    """
    OPTIONS = list(AuthorizedUser.__fields__.keys())
    OPTIONS.remove("user_id")
    OPTIONS.remove("permissions")

    if update_details.attribute not in OPTIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "detail": "Invalid attribute provided",
                "options": OPTIONS,
                "error": "",
                "tip": "Read the options and do it right this time",
                "extra": "Skill issue",
            },
        )

    if auth_user.permissions.update_users != True:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "detail": "You don't have the permissions to perform this request",
                "error": "",
                "tip": "Get the perms dude",
                "extra": "Skill issue",
                "permission_needed": ["update_users"],
            },
        )
    user = await get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "detail": "No user found with user id provided",
                "id_provided": user_id,
                "error": "",
                "tip": "Check if you put the right id",
                "extra": "Skill issue",
            },
        )

    if update_details.attribute == "password":
        password = await hash_text(update_details.new_value)

        async with asyncpg_connect() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE Users Set password=$1 WHERE user_id=$2", password, user_id
                )

    elif update_details.attribute in ["email", "public_key", "username"]:
        async with asyncpg_connect() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE Users Set {} = $1 WHERE user_id=$2".format(
                        update_details.attribute
                    ),
                    update_details.new_value,
                    user_id,
                )
                if update_details.attribute == "username":
                    await update_username_everywhere(user_id, update_details.new_value)

    updated_user = await get_user_by_id(user_id)

    if updated_user == user:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "detail": "An error occured server side when trying to update the user.",
                "error": "",
                "tip": "Try running this endpoint again",
                "extra": "Skill issue",
            },
        )

    return {
        "result": "User updated successfully",
        "updated_user": updated_user,
        "old_user": user,
    }


@other_user_endpoints.patch("/api/user/me")
async def update_user_auth_data(
    request: Request,
    update_details: UpdateBody,
    user: AuthorizedUser = Depends(check_auth_token),
):
    """
    Update signed in user in the database

    Parameters:
        update_details {
            attribute (str): The attribute of the user you want to modify (eg "username")
            new_value (str|int|bool): The new value of that attribute
        }
    """
    OPTIONS = list(AuthorizedUser.__fields__.keys())
    OPTIONS.remove("user_id")
    OPTIONS.remove("permissions")

    if update_details.attribute not in OPTIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "detail": "Invalid attribute provided",
                "options": OPTIONS,
                "error": "",
                "tip": "Read the options and do it right this time",
                "extra": "Skill issue",
            },
        )

    if user.permissions.mofify_self != True:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "detail": "You don't have the permissions to perform this request",
                "error": "",
                "tip": "Request the perms as a scope in your token request.",
                "extra": "Skill issue",
                "permission_needed": ["mofify_self"],
            },
        )

    if update_details.attribute == "password":
        password = await hash_text(update_details.new_value)

        async with asyncpg_connect() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE Users Set password=$1 WHERE user_id=$2",
                    password,
                    user.user_id,
                )

    elif update_details.attribute in ["email", "public_key", "username"]:
        async with asyncpg_connect() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE Users Set {} = $1 WHERE user_id=$2".format(
                        update_details.attribute
                    ),
                    update_details.new_value,
                    user.user_id,
                )
                if update_details.attribute == "username":
                    await update_username_everywhere(
                        user.user_id, update_details.new_value
                    )

    updated_user = await get_user_by_id(user.user_id)

    if updated_user == user:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "detail": "An error occured server side when trying to update the user.",
                "error": "",
                "tip": "Try running this endpoint again",
                "extra": "Skill issue",
            },
        )

    return {
        "result": "User updated successfully",
        "updated_user": updated_user,
        "old_user": user,
    }


async def update_username_everywhere(user_id: str, new_username: str):
    async with asyncpg_connect() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE room_messages Set message_author_username = $1 WHERE message_author_id=$2",
                new_username,
                user_id,
            )
