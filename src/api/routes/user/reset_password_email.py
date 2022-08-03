""" (module)
Code for the endpoint to reset a user's password
"""

__all__ = ["reset_password_endpoint"]

import os
import smtplib, ssl
from datetime import datetime, timedelta

import dotenv
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import Depends, APIRouter, HTTPException, Request

from core.utils import hash_text
from ...auth import check_auth_token
from core.models import AuthorizedUser, AuthPerms
from core.database import get_user_by_id, asyncpg_connect


reset_password_endpoint = APIRouter(
    tags=[
        "Users",
    ]
)


class ResetPasswordBody(BaseModel):
    new_password: str


@reset_password_endpoint.get("/api/users/password/create-reset-token")
async def create_reset_user_password_link(
    request: Request,
    user_id: int,
):
    user = await get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            404, {"detail": "User with username found in token does not exist"}
        )

    data = {"user_id": user.user_id, "type": "password_reset"}
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SIGN"], algorithm="HS256")
    link = f"https://chatapi.fusionsid.xyz/reset-password?reset_token={encoded_jwt}"
    message = f"You have been sent this email because you requested to have your password reset.\n\nYour reset token is: {encoded_jwt}\nIt will be valid for 15 minutes.\n\nLink for reseting password with a (trash) ui:\n{link}"

    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = os.environ["EMAIL"]
    password = os.environ["EMAIL_PASSWORD"]

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        try:
            server.sendmail(sender_email, user.email, message)
        except:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "An error occured on the server side when trying to send email e",
                    "what_err": "idk man Im trYING My besT herE",
                },
            )

    return {"detail": "Reset token & link sent to email"}


@reset_password_endpoint.post("/api/users/password/reset")
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
                404, {"detail": "User with username found in token does not exist"}
            )

    except JWTError:
        raise HTTPException(
            403, {"detail": "Reset token expired lmao get good honestly"}
        )

    password = await hash_text(body.new_password)

    async with asyncpg_connect() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE Users Set password=$1 WHERE user_id=$2", password, user_id
            )

    return await get_user_by_id(user_id)
