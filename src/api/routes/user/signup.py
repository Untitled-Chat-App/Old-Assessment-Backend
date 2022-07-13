import random

from fastapi import Depends, APIRouter, HTTPException

from core.database import asyncpg_connect
from core.models import NewUser
from core.utils import hash_text

signup_endpoint = APIRouter()


@signup_endpoint.post("/api/users/signup")
async def create_account(user_data: NewUser):
    hashed_password = await hash_text(user_data.password)
    async with asyncpg_connect() as conn:
        async with conn.transaction():
            user_id = None
            while True:
                user_id = random.randint(0, 1_000_000_000)
                data = await conn.fetch("SELECT * FROM Users WHERE user_id=$1", user_id)
                if len(data) == 0:
                    break
            await conn.execute(
                """INSERT INTO Users (
                    user_id, username, email, password, public_key
                ) VALUES ($1, $2, $3, $4, $5)""",
                user_id,
                user_data.username,
                user_data.email,
                hashed_password,
                user_data.public_key
            )
