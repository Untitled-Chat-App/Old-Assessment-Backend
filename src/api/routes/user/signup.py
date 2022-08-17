""" (module)
Code for the endpoint to signup/create a new user
"""

__all__ = ["signup_endpoint"]

import os
import ssl
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    username_conflict_error = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "User with this username already exists",
            "username_provided": str(user_data.username),
            "error": "",
            "tip": "Change the username",
            "extra": "Skill issue",
        },
    )

    email_conflict_error = HTTPException(
        status_code=409,
        detail={
            "success": False,
            "detail": "User with this email already exists",
            "email_provided": str(user_data.username),
            "error": "",
            "tip": "Change the email",
            "extra": "Skill issue",
        },
    )

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
            user_id = random.randint(0, 1_000_000_000_000_000)
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
                "error": "",
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


async def get_message(user):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to Untitled-Chat"
    message["From"] = os.environ["EMAIL"]
    message["To"] = user.email

    html = """
    <!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
    <meta content="width=device-width, initial-scale=1" name="viewport">
    <style type="text/css">
        @import url(https://fonts.googleapis.com/css?family=Nunito);

        img {
            max-width: 600px;
            outline: none;
            text-decoration: none;
            -ms-interpolation-mode: bicubic;
        }

        html {
            margin: 0;
            padding: 0;
        }

        a {
            text-decoration: none;
            border: 0;
            outline: none;
            color: #bbbbbb;
        }

        a img {
            border: none;
        }

        td,
        h1,
        h2,
        h3 {
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 400;
        }

        td {
            text-align: center;
        }

        body {
            -webkit-font-smoothing: antialiased;
            -webkit-text-size-adjust: none;
            width: 100%;
            height: 100%;
            color: #666;
            background: #fff;
            font-size: 16px;
            height: 100vh;
            width: 100%;
            padding: 0px;
            margin: 0px;
        }

        table {
            border-collapse: collapse !important;
        }

        .headline {
            color: #444;
            font-size: 36px;
        }

        .force-full-width {
            width: 100% !important;
        }
    </style>
    <style media="screen" type="text/css">
        @media screen {

            td,
            h1,
            h2,
            h3 {
                font-family: 'Nunito', 'Helvetica Neue', 'Arial', 'sans-serif' !important;
            }
        }
    </style>
    <style media="only screen and (max-width: 480px)" type="text/css">
        /* Mobile styles */
        @media only screen and (max-width: 480px) {

            table[class="w320"] {
                width: 320px !important;
            }
        }
    </style>
    <style type="text/css"></style>

</head>

<body bgcolor="#fff" class="body"
    style="padding:20px; margin:0; display:block; background:#ffffff; -webkit-text-size-adjust:none">
    <table align="center" cellpadding="0" cellspacing="0" height="100%" width="100%">
        <tbody>
            <tr>
                <td align="center" bgcolor="#fff" class="" valign="top" width="100%">
                    <table cellpadding="0" cellspacing="0" class="w320" style="margin: 0 auto;" width="600">
                        <tbody>
                            <tr>
                                <td align="center" class="" valign="top">
                                    <table cellpadding="0" cellspacing="0" style="margin: 0 auto;" width="100%">
                                    </table>
                                    <table bgcolor="#fff" cellpadding="0" cellspacing="0" class=""
                                        style="margin: 0 auto; width: 100%; margin-top: 100px;">
                                        <tbody style="margin-top: 15px;">
                                            <tr class="">
                                                <td class="">
                                                    <img alt="robot picture" class=""
                                                        src="https://raw.githubusercontent.com/Untitled-Chat-App/Frontend/main/src/assets/images/logos/nobg_logo_text.png"
                                                        width="420"> <br><br><br>
                                                </td>
                                            </tr>
                                            <tr class="">
                                                <td class="headline">Welcum to Untitled-Chat!</td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <table cellpadding="0" cellspacing="0" class=""
                                                        style="margin: 0 auto;" width="75%">
                                                        <tbody class="">
                                                            <tr class="">
                                                                <td class="" style="color:#444; font-weight: 400;">
                                                                    <br>
                                                                    Hello {username}!<br>
                                                                    Thank you so much for creating an account, we are so happy you're here.<br><br>
                                                                    <strong>Useful Links:</strong><br>
                                                                    <h3>
                                                                        <a href="https://chatapi.fusionsid.xyz/">API Url</a><br>
                                                                        <a href="https://chatapi.fusionsid.xyz/documentation">API Docs</a><br>
                                                                        <a href="https://github.com/Untitled-Chat-App">Github / Source Code</a><br>
                                                                    </h3>
                                                                    <br><br>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class="">
                                                    <div class="">
                                                        <a style="background-color:#674299;border-radius:4px;color:#fff;display:inline-block;font-family:Helvetica, Arial, sans-serif;font-size:18px;font-weight:normal;line-height:50px;text-align:center;text-decoration:none;width:350px;-webkit-text-size-adjust:none;"
                                                            href="https://chatapi.fusionsid.xyz/web?room_id=690420690">Join "We be copy pastin" Room :)</a>
                                                    </div>
                                                    <br>
                                                </td>
                                            </tr>
                                        </tbody>

                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </tbody>
    </table>
</body>

</html>
    """.replace(
        "{username}", user.username
    )
    html_message = MIMEText(html, "html")
    message.attach(html_message)

    return message.as_string()
