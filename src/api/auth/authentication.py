""" (script)
The code for the oauth system
"""

import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.database import asyncpg_connect
from core.models import AuthUser, Token
from core.utils import hash_text

load_dotenv()

oauth2_endpoint = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def correct_password(hashed_password: str, db_password: str) -> bool:
    return hashed_password == db_password


async def get_user(username: str) -> AuthUser | None:
    async with asyncpg_connect() as conn:
        data = await conn.fetch("SELECT * FROM Users WHERE username=$1", username)
        if not len(data):
            return None
    if data[0][4] != 23:  # asked friend for random number
        return None
    return AuthUser(username=data[0][1], password=data[0][3])


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SIGN"], algorithm="HS256")
    return encoded_jwt


async def check_auth_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials, Maybe get a new token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ["JWT_SIGN"], algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(username=username)
    if user is None:
        raise credentials_exception
    return user


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if user is None:
        return False
    if not await correct_password(password, user.password):
        return False
    return user


@oauth2_endpoint.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
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
