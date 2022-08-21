""" (module)
Code for the endpoint to update a user or delete them
"""

__all__ = ["get_user_endpoint"]

from pydantic import BaseModel
from fastapi import Depends, APIRouter, HTTPException, Request

from ...auth import check_auth_token
from core.utils import hash_text, validate_user
from core.models import AuthorizedUser, UpdateBody
from core.database import get_user_by_id, asyncpg_connect, update_username_everywhere


other_user_endpoints = APIRouter(
    tags=[
        "Users",
    ]
)


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

    return await update_user(user, update_details)


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

    return await update_user(user, update_details)


async def update_user(user: AuthorizedUser, update_details: UpdateBody):
    """
    Function to update user

    Parameters:
        user (AuthorizedUser): The user to update
        update_details (UpdateBody): The attribute to update and the new value to update it to
    """
    OPTIONS = ["username", "email", "public_key", "password"]

    # execptions for this endpoint
    username_conflict_error = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "User with this username already exists",
            "username_provided": str(update_details.new_value),
            "tip": "Change the username",
            "extra": "Skill issue",
        },
    )

    email_conflict_error = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "User with this email already exists",
            "email_provided": str(update_details.new_value),
            "tip": "Change the email",
            "extra": "Skill issue",
        },
    )

    invalid_username = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "Username failed checks",
            "username_provided": str(update_details.new_value),
            "tip": "Follow the criteria",
            "criteria": [
                "username must be 3-32 characters long",
                "no _ or . allowed at the beginning",
                "no __ or _. or ._ or .. inside",
                "no _ or . at the end" "Allowed Characters: a-z A-Z 0-9 . _",
            ],
        },
    )

    invalid_option = HTTPException(
        status_code=400,
        detail={
            "success": False,
            "detail": "Invalid attribute provided",
            "options": OPTIONS,
            "tip": "Read the options and do it right this time",
            "extra": "Skill issue",
        },
    )

    missing_perms = HTTPException(
        status_code=403,
        detail={
            "success": False,
            "detail": "You don't have the permissions to perform this request",
            "tip": "Request the perms as a scope in your token request.",
            "extra": "Skill issue",
            "permission_needed": ["mofify_self"],
        },
    )

    failed_to_create = HTTPException(
        status_code=500,
        detail={
            "success": False,
            "detail": "An error occured server side when trying to update the user.",
            "tip": "Try running this endpoint again",
            "extra": "Skill issue",
        },
    )

    if update_details.attribute not in OPTIONS:
        raise invalid_option

    if user.permissions.mofify_self != True:
        raise missing_perms

    async with asyncpg_connect() as conn:
        async with conn.transaction():
            match update_details.attribute:
                case "password":
                    password = await hash_text(update_details.new_value)

                    async with asyncpg_connect() as conn:
                        async with conn.transaction():
                            await conn.execute(
                                "UPDATE Users Set password=$1 WHERE user_id=$2",
                                password,
                                user.user_id,
                            )

                case "public_key":
                    await conn.execute(
                        "UPDATE Users Set public_key=$1 WHERE user_id=$2",
                        update_details.new_value,
                        user.user_id,
                    )

                case "email":
                    email_search = await conn.fetch(
                        "SELECT * FROM Users WHERE LOWER(email)=LOWER($1)",
                        update_details.new_value,
                    )
                    if len(email_search):
                        raise email_conflict_error

                    await conn.execute(
                        "UPDATE Users Set email=$1 WHERE user_id=$2",
                        update_details.new_value,
                        user.user_id,
                    )

                case "username":
                    username_search = await conn.fetch(
                        "SELECT * FROM Users WHERE LOWER(username)=LOWER($1)",
                        update_details.new_value,
                    )
                    if len(username_search):
                        raise username_conflict_error

                    if not await validate_user(update_details.new_value):
                        raise invalid_username

                    await update_username_everywhere(
                        user.user_id, update_details.new_value
                    )

    updated_user = await get_user_by_id(user.user_id)

    if updated_user == user:
        raise failed_to_create

    del updated_user.password
    del user.password

    return {
        "success": True,
        "detail": "User updated successfully",
        "updated_user": updated_user,
        "old_user": user,
    }
