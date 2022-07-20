import json
from dataclasses import dataclass

from fastapi import WebSocket
from pydantic import BaseModel

from core.models import AuthorizedUser

@dataclass
class RoomUser():
    user: AuthorizedUser
    websocket: WebSocket


# @dataclass
class Room(BaseModel):
    room_id: int
    room_name: str
    created_at: int  # it will be a datetime.datetime.utcnow().timestamp()
    room_description: str = None


class RoomMessage(BaseModel):
    chatroom: Room
    message_id: int
    created_at: int
    messsage_content: str
    message_author: AuthorizedUser


class ChatRoom(Room):
    connected_users: list = []

    async def join_room(self, user: RoomUser):
        await user.websocket.accept()
        self.connected_users.append(user)

    async def disconnect(self, user: RoomUser):
        try:
            await user.websocket.close()
        except RuntimeError:
            print(f"Error while closing websocket connection with {user.user.username}")
        self.connected_users.remove(user)

    async def send_to_user(self, message: RoomMessage, user: RoomUser):
        await user.websocket.send_json(message.json())

    async def broadcast(self, message: RoomMessage):
        for user in self.connected_users:
            if isinstance(message, RoomMessage):
                await user.websocket.send_text(message.json())
            else:
                await user.websocket.send_json(message)
