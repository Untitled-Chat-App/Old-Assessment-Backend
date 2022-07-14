""" (module)
Code for the endpoint to signup/create a new user
"""

import random

from fastapi import Depends, APIRouter, HTTPException

from core.utils import hash_text
from core.database import asyncpg_connect
from ...auth import check_auth_token, get_user
from core.models import NewUser, AuthorizedUser


signup_endpoint = APIRouter()


@signup_endpoint.post("/api/users/signup")
async def create_account(
    user_data: NewUser, auth_user: AuthorizedUser = Depends(check_auth_token)
):
    """
    Create a new user. Used when someone is signing up to the app.

    Requirements
    ------------
        username, password, email, public_key
    """
    if (
        auth_user.permissions.create_users != True
    ):  # if they dont have the permissions to create users
        return HTTPException(
            status_code=403,
            detail="You don't have permission to use this endpoint (skill issue)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user(
        user_data.username
    )  # Check if someone has the same username/account already exists

    if user is not None:
        return HTTPException(
            status_code=409,
            detail="User with this username already exists",
        )

    # Hash their password (to be stored)
    hashed_password = await hash_text(user_data.password)

    async with asyncpg_connect() as conn:
        async with conn.transaction():
            user_id = None
            while (
                True
            ):  # Keep generating user ids and check if user with id already exists, if not break
                user_id = random.randint(0, 1_000_000_000)
                data = await conn.fetch("SELECT * FROM Users WHERE user_id=$1", user_id)
                if len(data) == 0:
                    break
            # insert user into database
            await conn.execute(
                """INSERT INTO Users (
                    user_id, username, email, password, public_key
                ) VALUES ($1, $2, $3, $4, $5)""",
                user_id,
                user_data.username,
                user_data.email,
                hashed_password,
                user_data.public_key,
            )

    user = await get_user(user_data.username)  # fetch user from database

    if user is not None:  # if user exists (user was created properly), return user
        return {"success": True, "detail": "User created successfully", "user": user}
    # if not tell em you failed
    return HTTPException(
        status_code=500,
        detail="internal error lmao, user failed to be created. Maybe try again",
    )
