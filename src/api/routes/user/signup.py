""" (module)
Code for the endpoint to signup/create a new user
"""

__all__ = ["signup_endpoint"]

import re
import os
import ssl
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, HTTPException, Request

from ...auth import get_user
from core.utils import hash_text
from core.utils import welcome_email_html
from core.database import asyncpg_connect
from core.models import NewUser, AuthorizedUser


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

    username_conflict_error = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "User with this username already exists",
            "username_provided": str(user_data.username),
            "tip": "Change the username",
            "extra": "Skill issue",
        },
    )

    email_conflict_error = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "User with this email already exists",
            "email_provided": str(user_data.email),
            "tip": "Change the email",
            "extra": "Skill issue",
        },
    )

    invalid_username = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "Username failed checks",
            "username_provided": str(user_data.username),
            "tip": "Follow the criteria",
            "criteria": [
                "username must be 3-32 characters long",
                "no _ or . allowed at the beginning",
                "no __ or _. or ._ or .. inside",
                "no _ or . at the end"
                "Allowed Characters: a-z A-Z 0-9 . _"
            ],
        },
    )

    if not await validate_user(user_data.username):
        raise invalid_username

    async with asyncpg_connect() as conn:
        email_search = await conn.fetch(
            "SELECT * FROM Users WHERE LOWER(email)=LOWER($1)", user_data.email
        )
        if len(email_search):
            raise email_conflict_error

        username_search = await conn.fetch(
            "SELECT * FROM Users WHERE LOWER(username)=LOWER($1)", user_data.username
        )
        if len(username_search):
            raise username_conflict_error

        # Hash their password (to be stored)
        hashed_password = await hash_text(user_data.password)

        user_id = None

        # Keep generating user ids and check if user with id already exists, if not break
        while True:
            user_id = random.randint(0, 2_000_000_000)
            data = await conn.fetch("SELECT * FROM Users WHERE user_id=$1", user_id)
            if not len(data):
                break

        async with conn.transaction():
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
    if user is None:
        # if not tell em you failed
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "detail": "User failed to be created",
                "tip": "Try signing up again",
                "extra": "Skill issue",
            },
        )

    del user.password

    message = await get_message(user)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(os.environ["EMAIL"], os.environ["EMAIL_PASSWORD"])
        try:
            server.sendmail(os.environ["EMAIL"], user.email, message)

        except Exception as e:
            return {
                "success": True,
                "detail": "User created successfully",
                "user": user,
                "welcome_email": {
                    "success": False,
                    "detail": "An error occured on the server side while trying to send this email",
                    "error": str(e),
                    "tip": "The email you used for signup may be incorrect so if you every forget your password GG",
                    "extra": "Just get better and enter your real email next time",
                },
            }

    return {"success": True, "detail": "User created successfully", "user": user}


async def get_message(user: AuthorizedUser) -> str:
    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to Untitled-Chat"
    message["From"] = "chat@fusionsid.xyz"
    message["To"] = user.email

    html = welcome_email_html.replace("{username}", user.username)
    html_message = MIMEText(html, "html")
    message.attach(html_message)

    return message.as_string()


async def validate_user(username: str) -> bool:
    """
    Takes in a username and checks if it is valid.

    Parameters:
        username (str): The username of the person signing up

    Criteria:
        ^(?=.{3,32}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$
        └─────┬────┘└───┬──┘└─────┬─────┘└─────┬─────┘ └───┬───┘
            │         │         │            │           no _ or . at the end
            │         │         │            │
            │         │         │            allowed characters
            │         │         │
            │         │         no __ or _. or ._ or .. inside
            │         │
            │         no _ or . allowed at the beginning
            │
            username must be 3-32 characters long

    Returns:
        bool: If username is value it returns True else False
    """
    if len(username) < 1:
        return False

    if username[0].isnumeric():
        return False

    if not re.match(
        "^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$", username
    ):
        return False

    return True
