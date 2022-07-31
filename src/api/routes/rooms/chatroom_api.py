""" (module)
Code for the chatroom http/s endpoints
"""

__all__ = ["chatroom_endpoints"]

import random
import datetime

from fastapi import APIRouter, Depends, HTTPException, Request

from ...auth import check_auth_token
from core.database import asyncpg_connect, get_room
from core.models import AuthorizedUser, NewRoom


chatroom_endpoints = APIRouter(tags=[
        "Chatrooms",
    ])


@chatroom_endpoints.post("/api/chatroom/new")
async def create_new_chatroom(
    request: Request,
    room_data: NewRoom,
    auth_user: AuthorizedUser = Depends(check_auth_token),
):
    """
    Create a new chatroom

    Parameters:
        room_name (str): The name of the room to create
        room_description (str): the description of the room
    """
    room_name = room_data.room_name
    room_description = room_data.room_description

    if auth_user.permissions.create_rooms != True:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You don't have the permissions to perform this request.",
                "permission_needed": ["create_rooms"],
            },
        )

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
        raise HTTPException(500, "An error occured in the creation of the room")

    return room


@chatroom_endpoints.get("/api/chatroom/{room_id}")
async def get_room_by_id(
    request: Request,
    room_id: int,
    auth_user: AuthorizedUser = Depends(check_auth_token),
):
    """
    Get room by the id

    Parameters:
        room_id (int): The id of the room to search for
    """
    return await get_room(room_id)
