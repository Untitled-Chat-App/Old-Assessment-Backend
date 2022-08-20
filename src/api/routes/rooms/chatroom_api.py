""" (module)
Code for the chatroom http/s endpoints
"""

__all__ = ["chatroom_endpoints"]

import random
import datetime

from fastapi import APIRouter, Depends, HTTPException, Request

from ...auth import check_auth_token
from core.models import AuthorizedUser, NewRoom
from core.database import asyncpg_connect, get_room


chatroom_endpoints = APIRouter(
    tags=[
        "Chatrooms",
    ]
)


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
                room_id = random.randint(0, 2_000_000_000)
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


@chatroom_endpoints.get("/api/chatroom/get_messages")
async def get_room_by_id(
    request: Request,
    room_id: int,
    limit: int = None,
    author_id: int = None,
    auth_user: AuthorizedUser = Depends(check_auth_token),
):
    """
    Get old messages from a room

    Parameters:
        room_id (int): The id of the room to search for
        limit (Optional[int]): How many messages to get. If none it will get all.
        author_id (Optional[int]): Search for a specific user
        get_usernames (Optional[bool]): Include usernames in result (SUPER SLOW PLEASE USE ASYNC)
    """
    room = await get_room(room_id)

    if room is None:
        return HTTPException(
            404, {"detail": "Room with this id doesnt exists", "id_provided": room_id}
        )

    if auth_user.permissions.get_old_messages != True:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You don't have the permissions to perform this request.",
                "permission_needed": ["get_old_messages"],
            },
        )

    async with asyncpg_connect() as conn:
        if author_id is None:
            data = await conn.fetch(
                "SELECT * FROM room_messages WHERE message_room_id=$1", room_id
            )
        else:
            data = await conn.fetch(
                "SELECT * FROM room_messages WHERE message_room_id=$1 AND message_author_id=$2",
                room_id,
                author_id,
            )

    data = list(reversed(data))

    if limit is not None:
        data = data[:limit]

    return data


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
    room = await get_room(room_id)

    if room is None:
        return HTTPException(
            404, {"detail": "Room with this id doesnt exists", "id_provided": room_id}
        )

    return room
