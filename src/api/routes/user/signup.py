""" (module)
Code for the endpoint to signup/create a new user
"""

__all__ = ["signup_endpoint"]

import random

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Depends, APIRouter, HTTPException, Request

from ...auth import get_user
from core.models import NewUser
from core.utils import hash_text
from core.database import asyncpg_connect


signup_endpoint = APIRouter(
    tags=[
        "Users",
    ]
)

# Need limiter here because these endpoints have different limit
limiter = Limiter(key_func=get_remote_address)


@limiter.limit("1/hour")
@signup_endpoint.post("/api/users/signup")
async def create_account(
    request: Request,
    user_data: NewUser,
):
    """
    Create a new user. Used when someone is signing up to the app.

    Parameters:
        username (str): The new users username
        email (str): The new users email
        password (str): The new users password
        public_key (str): The new users public_key
    """

    user = await get_user(
        user_data.username
    )  # Check if someone has the same username/account already exists

    if user is not None:
        raise HTTPException(
            status_code=409,
            detail="User with this username already exists",
        )

    async with asyncpg_connect() as conn:
        data = await conn.fetch("SELECT * FROM Users WHERE email=$1", user_data.email)
        if len(data) != 0:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists",
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
        del user.password
        return {"success": True, "detail": "User created successfully", "user": user}
    # if not tell em you failed
    raise HTTPException(
        status_code=500,
        detail="internal error lmao, user failed to be created. Maybe try again",
    )
