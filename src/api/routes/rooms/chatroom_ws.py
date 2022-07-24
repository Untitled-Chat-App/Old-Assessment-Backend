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

from core.database import get_room
from ...auth import check_auth_token
from core.models import RoomMessage, RoomUser, ChatRoom, Room


chatroom_websockets = APIRouter()

rooms = {}


@chatroom_websockets.websocket("/api/ws/chatroom")
async def connect_ws(websocket: WebSocket, access_token: str, room_id: int):
    """
    Connects a user to a room

    Parameters:
        access_token (str): The access token for the account
        room_id (int): Id of the room to join
    """
    try:
        user = await check_auth_token(access_token)
    except HTTPException:  # means that it is an invalid access token
        await websocket.accept()
        return await websocket.close(
            reason="Error: Invalid access token.\nNote: Tokens expire 24 hours after their creation"
        )
    del user.password
    if (room := await get_room(room_id)) is None:
        await websocket.accept()
        return await websocket.close(reason="Error: Invalid Room ID")

    connection = RoomUser(user=user, websocket=websocket)

    chatroom = rooms.get(room_id)

    if chatroom is None:
        chatroom = ChatRoom(
            room_id=room.room_id,
            room_name=room.room_name,
            created_at=room.created_at,
            room_description=room.room_description,
        )

        rooms[room_id] = chatroom

    await chatroom.broadcast({"event": "User Join", "user": connection.user.json()})
    await chatroom.join_room(connection)

    try:
        while True:
            data = await connection.websocket.receive_text()
            message: RoomMessage = await process_message_json(data, room)
            await chatroom.broadcast(message)

    except WebSocketDisconnect:
        chatroom.connected_users.remove(connection)
        await chatroom.broadcast(
            {"event": "User Disconnect", "user": connection.user.json()}
        )


async def process_message_json(data: str, room: Room) -> RoomMessage:
    """
    Process data sent from the user connected to the websocket
    Converts to a RoomMessage object, handles ID, created_at, author etc

    Parameters:
        data (str): Data recieved from the websocket (RoomUser.websocket.receive_text())
        room (Room): The room currently connected to

    Returns:
        RoomMessage: The message created using the data
    """
    data = json.loads(data)

    content = data["message_content"]
    user = await check_auth_token(data["access_token"])
    del user.password
    msg_id = 123  # will use real ids later
    created_at = datetime.datetime.utcnow().timestamp()
    message = RoomMessage(
        chatroom=room,
        message_id=msg_id,
        created_at=created_at,
        messsage_content=content,
        message_author=user,
    )
    return message
