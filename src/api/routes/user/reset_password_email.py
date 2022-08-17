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

    html = """
    <!DOCTYPE html>
    <html>
    <head>

    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Password Reset</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style type="text/css">
    @media screen {
        @font-face {
        font-family: 'Source Sans Pro';
        font-style: normal;
        font-weight: 400;
        src: local('Source Sans Pro Regular'), local('SourceSansPro-Regular'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff) format('woff');
        }

        @font-face {
        font-family: 'Source Sans Pro';
        font-style: normal;
        font-weight: 700;
        src: local('Source Sans Pro Bold'), local('SourceSansPro-Bold'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff) format('woff');
        }
    }
    body,
    table,
    td,
    a {
        -ms-text-size-adjust: 100%; /* 1 */
        -webkit-text-size-adjust: 100%; /* 2 */
    }

    table,
    td {
        mso-table-rspace: 0pt;
        mso-table-lspace: 0pt;
    }


    img {
        -ms-interpolation-mode: bicubic;
    }

    a[x-apple-data-detectors] {
        font-family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
        color: inherit !important;
        text-decoration: none !important;
    }


    div[style*="margin: 16px 0;"] {
        margin: 0 !important;
    }

    body {
        width: 100% !important;
        height: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }


    table {
        border-collapse: collapse !important;
    }

    a {
        color: #1a82e2;
    }

    img {
        height: auto;
        line-height: 100%;
        text-decoration: none;
        border: 0;
        outline: none;
    }
    </style>

    </head>
    <body style="background-color: #e9ecef;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
        <td align="center" bgcolor="#e9ecef">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="center" valign="top" style="padding: 36px 24px;">
                <a href="https://chatapi.fusionsid.xyz" target="_blank" style="display: inline-block;">
                    <img src="https://raw.githubusercontent.com/Untitled-Chat-App/Frontend/main/src/assets/images/logos/nobg_logo_text.png" alt="Logo" border="0" width="420" style="display: block;">
                </a>
                </td>
            </tr>
            </table>
        </td>
        </tr>
        <tr>
        <td align="center" bgcolor="#e9ecef">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="left" bgcolor="#ffffff" style="padding: 36px 24px 0; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; border-top: 3px solid #d4dadf;">
                <h1 style="margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;">Reset Your Password</h1>
                </td>
            </tr>
            </table>
        </td>
        </tr>
        <tr>
        <td align="center" bgcolor="#e9ecef">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
                <p style="margin: 0;">Tap the button below to reset your account password. If you didn't request a new password, you can safely delete this email.</p>
                </td>
            </tr>
            <tr>
                <td align="left" bgcolor="#ffffff">
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                    <td align="center" bgcolor="#ffffff" style="padding: 12px;">
                        <table border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            <td align="center" bgcolor="#1a82e2" style="border-radius: 6px;">
                            <a href="https://chatapi.fusionsid.xyz/forgot-password?reset_token=encoded_jwt" target="_blank" style="display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;">Reset Password</a>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                </table>
                </td>
            </tr>
            <tr>
                <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
                <p style="margin: 0;">If that doesn't work, skill issue. Also if you wanna read the API docs here is your reset token (valid for 15 minutes):</p>
                <p style="margin: 0;">encoded_jwt</p>
                </td>
            </tr>
            <tr>
                <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px; border-bottom: 3px solid #d4dadf">
                <p style="margin: 0;">Thanks,<br>FusionSid</p>
                </td>
            </tr>
            </table>
        </td>
        </tr>
        <tr>
        <td align="center" bgcolor="#e9ecef" style="padding: 24px;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="center" bgcolor="#e9ecef" style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
                <p style="margin: 0;">You received this email because we received a request to reset the password for your account. If you didn't request to reset your password you can safely delete/ignore this email.</p>
                </td>
            </tr>
            </table>
        </td>
        </tr>
    </table>
    </body>
    </html>
    """.replace(
        "encoded_jwt", encoded_jwt
    )
    html_message = MIMEText(html, "html")
    message.attach(html_message)

    return message.as_string()
