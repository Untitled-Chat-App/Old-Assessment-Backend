""" (module)
Code for the chatroom endpoints
"""

__all__ = ["chatroom_endpoints"]

import json
from dataclasses import dataclass

from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Request,
)

from ...auth import check_auth_token
from core.models import AuthorizedUser
from core.database import get_user_by_id


@dataclass
class User:
    user: AuthorizedUser
    websocket: WebSocket


class ChatRoom:
    def __init__(self, room_name: str):
        self.room_name: str = room_name
        self.connected_users: list[User] = []

    async def join_room(self, user: User):
        await user.websocket.accept()
        self.connected_users.append(user)

    def disconnect(self, user: User):
        self.connected_users.remove(user)

    async def send_to_user(self, message: str, user: User):
        await user.websocket.send_text(message)

    async def broadcast(self, message: str):
        for user in self.connected_users:
            await user.websocket.send_json(message)


websocket_endpoints = APIRouter()

rooms = {}


@websocket_endpoints.websocket("/api/ws/chatroom")
async def connect_ws(websocket: WebSocket, access_token: str, room_name: str):
    room = rooms.get(room_name)

    if room is None:
        room = ChatRoom(room_name)
        rooms[room_name] = room

    connection = User(None, websocket)
    await room.join_room(connection)

    try:
        user = await check_auth_token(access_token)
    except HTTPException:  # means that it is an invalid access token
        await room.send_to_user("Invalid access token", connection)
        room.disconnect(connection)
        return

    room.connected_users.remove(connection)
    connection = User(user, websocket)
    room.connected_users.append(connection)

    try:
        dict_user_perms = connection.user.permissions.__dict__
        dict_user = connection.user.__dict__
        dict_user["permissions"] = dict_user_perms
        while True:
            data = await connection.websocket.receive_text()

            await room.broadcast(
                {"message": data, "user": json.dumps(dict_user)}
            )
    except WebSocketDisconnect:
        room.disconnect(connection)
    await room.broadcast({"message": "*Left the room*", "user": json.dumps(dict_user)})
