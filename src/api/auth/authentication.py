""" (module)
The code for the oauth system for the api
"""

__all__ = ["oauth2_endpoint", "check_auth_token", "get_user"]

import os
from typing import Optional
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, APIRouter, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.utils import hash_text
from core.database import get_user
from core.models import Token, AuthorizedUser

load_dotenv()

oauth2_endpoint = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)  # set the /token endpoint as the oauth2 endpoint


async def correct_password(hashed_password: str, db_password: str) -> bool:
    """
    Very simple function to check if input1 == input2

    Parameters
    ----------
        hashed_password (str): The password that was entered by the user
        db_password (str): The real password that in the db

    Returns
    -------
        bool: True/False if they password is correct
    """
    return hashed_password == db_password


async def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a jwt access token. Token will be encoded with data. Since it uses JWT it can be decoded
    But it is signed so if you try modifiying it without knowing the sign... (spoiler: it wont work cause you have a skill issue)

    Parameters
    ----------
        data (dict): The data to be encoded and put in the JWT token
        expires_delta (timedelta, Optional): How long the token should last. If not provided it will expire in 15min

    Returns
    -------
        str: The JWT token with expiry and username encoded in
    """
    to_encode = data.copy()
    if expires_delta:  # set expire time for the token
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=15
        )  # if not provided time then set to 15min
    to_encode.update({"exp": expire})  # add in expiry time
    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SIGN"], algorithm="HS256")
    return encoded_jwt


async def check_auth_token(token: str = Depends(oauth2_scheme)) -> AuthorizedUser:
    """
    Checks the token to see if its legit

    Parameters
    ----------
        token (str): The oauth2 JWT access token you got from the /token endpoint

    Returns
    -------
        AuthorizedUser: If token is correct and not expired it will return the User. If not it raises an error.

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Token is expired or incorrect. Maybe request a new token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, os.environ["JWT_SIGN"], algorithms=["HS256"]
        )  # decode token
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(
        username=username
    )  # get user from the username that was in the token and check if they exist
    if user is None:
        raise credentials_exception
    return user


async def authenticate_user(username: str, password: str) -> AuthorizedUser | bool:
    """
    Authenticate user and check if they exists and password is correct

    Parameters
    ----------
        username (str): The username to your account
        password (str): Password to the account

    Returns
    -------
        Union[AuthorizedUser, bool]: If user is authorised then it returns the user if not it returns False
    """
    user = await get_user(username)  # check if user exists
    if user is None:
        return False
    if not await correct_password(
        password, user.password
    ):  # check if password is correct
        return False
    return user


@oauth2_endpoint.post("/token", response_model=Token)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Request an oauth2 access token

    Requirements
    ------------
        username & password to the account
    """
    form_data.password = await hash_text(form_data.password)
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=1440)  # you only get a day
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Auth permissions
# 1 = normal user
# 23 = super user with access to db aka all perms
# users with 1 can request additional perms such as get user, send message, get message etc
# see core.models.base_models.AuthPerms for perms
