""" (module)
Code for the chatroom http/s endpoints
"""

__all__ = ["chatroom_endpoints"]

import random
import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from ...auth import check_auth_token
from core.database import asyncpg_connect, get_room
from core.models import AuthorizedUser, Room, RoomMessage, RoomUser, ChatRoom, NewRoom


chatroom_endpoints = APIRouter()


@chatroom_endpoints.post("/api/chatroom/new")
async def create_new_chatroom(
    room_data: NewRoom, auth_user: AuthorizedUser = Depends(check_auth_token)
):
    room_name = room_data.room_name
    room_description = room_data.room_description

    if await get_room(room_name=room_name) is not None:
        raise HTTPException(status_code=409, detail="Room already exists")

    room_id = None
    async with asyncpg_connect() as conn:
        async with conn.transaction():
            while True:
                room_id = random.randint(0, 1_000_000_000)
                data = await conn.fetch("SELECT * FROM Rooms WHERE room_id=$1", room_id)
                if len(data) == 0:
                    break
            await conn.execute(
                """INSERT INTO Rooms (
                    room_id, room_name, room_created_at, room_description
                ) VALUES ($1, $2, $3, $4)""",
                room_id,
                room_name,
                datetime.datetime.utcnow().timestamp(),
                room_description,
            )

    if (room := await get_room(room_id=room_id)) is None:
        return HTTPException(500, "An error occured in the creation of the room")

    return room


@chatroom_endpoints.get("/api/chatroom/{room_id}")
async def get_room_by_id(room_id: int, auth_user: AuthorizedUser = Depends(check_auth_token)):
    return await get_room(room_id)

