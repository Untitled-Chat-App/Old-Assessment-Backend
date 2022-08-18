""" (module)
Code for the endpoint to reset a user's password
"""

__all__ = ["reset_password_endpoint"]

import os
import ssl
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request

from core.utils import hash_text
from core.utils import reset_password_email
from core.database import get_user_by_id, asyncpg_connect


reset_password_endpoint = APIRouter(
    tags=[
        "Users",
    ]
)


class ResetPasswordBody(BaseModel):
    new_password: str


@reset_password_endpoint.get("/api/users/password/create_reset_link")
async def create_reset_user_password_link(
    request: Request,
    user_id: int,
):
    user = await get_user_by_id(user_id)

    if user is None:
        403, {
            "success": False,
            "detail": "User with user_id provided does not exists",
            "id_provided": user_id,
            "error": "",
            "tip": "Check if you typed the user_id correctly",
            "extra": "Skill issue",
        }

    data = {"user_id": user.user_id, "type": "password_reset"}
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SIGN"], algorithm="HS256")
    message = await get_message(encoded_jwt, user.email)

    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = os.environ["EMAIL"]
    password = os.environ["EMAIL_PASSWORD"]

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        try:
            server.sendmail(sender_email, user.email, message)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "detail": "An error occured on the server side while trying to send this email",
                    "error": str(e),
                    "tip": "The email you used for signup may be incorrect and since you dont know your password gg.",
                    "extra": "Just get better",
                },
            )

    return {"detail": "Reset token & link sent to email"}


@reset_password_endpoint.post("/api/users/password/reset-password")
async def reset_user_password(
    request: Request, reset_token: str, body: ResetPasswordBody
):
    try:
        payload = jwt.decode(reset_token, os.environ["JWT_SIGN"], algorithms=["HS256"])
        user_id: str = payload.get("user_id")
        token_type = payload.get("type")

        if token_type != "password_reset":
            raise HTTPException(403, {"detail", "INVALID token type"})

        if user_id is None:
            raise HTTPException(
                403,
                {
                    "success": False,
                    "detail": "Username found in token does not belong to a real account",
                    "error": "",
                    "tip": "",
                    "extra": "Skill issue also idk how you managed to do that",
                },
            )

    except JWTError as err:
        raise HTTPException(
            403,
            {
                "success": False,
                "detail": "Reset token invalid",
                "error": str(err),
                "tip": "Try gnereating a new token",
                "extra": "Just get good honestly",
            },
        )

    password = await hash_text(body.new_password)

    async with asyncpg_connect() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE Users Set password=$1 WHERE user_id=$2", password, user_id
            )

    return await get_user_by_id(user_id)


async def get_message(encoded_jwt, to):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset Password"
    message["From"] = os.environ["EMAIL"]
    message["To"] = to

    html = reset_password_email.replace("encoded_jwt", encoded_jwt)
    html_message = MIMEText(html, "html")
    message.attach(html_message)

    return message.as_string()
