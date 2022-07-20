""" (module)
Code for the chatroom websocket endpoints
"""

__all__ = ["chatroom_websockets"]

import json
import datetime

from fastapi import (
    APIRouter,
    WebSocket,
    HTTPException,
    WebSocketDisconnect,
)

from ...auth import check_auth_token
from core.database import get_user_by_id, asyncpg_connect, get_room
from core.models import AuthorizedUser, Room, RoomMessage, RoomUser, ChatRoom


chatroom_websockets = APIRouter()


@chatroom_websockets.websocket("/api/ws/chatroom")
async def connect_ws(websocket: WebSocket, access_token: str, room_id: int):

    try:
        user = await check_auth_token(access_token)
    except HTTPException:  # means that it is an invalid access token
        await websocket.accept()
        return await websocket.close(reason="Invalid access token")

    if (room := await get_room(room_id)) is None:
        await websocket.accept()
        return await websocket.close(reason="Invalid room id")

    connection = RoomUser(user=user, websocket=websocket)

    room = ChatRoom(
        room_id=room.room_id,
        room_name=room.room_name,
        created_at=room.created_at,
        room_description=room.room_description,
    )
    await room.join_room(connection)

    try:
        while True:
            print("e")
            data = await connection.websocket.receive_text()
            print("e")
            message: RoomMessage = await process_message_json(data, room)
            print("e")
            await room.broadcast(json.dumps(message.json()))
            print("e")
            await room.broadcast({"hi":"hi"})
            print("e")

    except WebSocketDisconnect:
        room.connected_users.remove(connection)

    for user in room.connected_users:
        await user.websocket.send_json(
            {"event": "User Disconnect", "user": connection.user.json()}
        )


async def process_message_json(data, room) -> RoomMessage:
    print("e")
    data = json.loads(data)
    content = data["message_content"]
    user = await check_auth_token(data["access_token"])
    msg_id = 123
    created_at = datetime.datetime.utcnow().timestamp()
    print("e")
    message = RoomMessage(
        chatroom=room,
        message_id=msg_id,
        created_at=created_at,
        messsage_content=content,
        message_author=user,
    )
    print(message)