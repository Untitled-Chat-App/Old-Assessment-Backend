""" (module)
This module contains models and classes for chatrooms
"""

from dataclasses import dataclass

from fastapi import WebSocket
from pydantic import BaseModel

from core.models import AuthorizedUser


@dataclass  # have to use dataclass for this one because pydantic wont work with it
class RoomUser:
    """
    A connection to the chatroom

    Attributes:
        user (AuthorizedUser): The user currently connected to the room
        websocket (WebSocket): The actual websocket connection
    """

    user: AuthorizedUser
    websocket: WebSocket


class Room(BaseModel):
    """
    Base class for a chatroom

    Attributes:
        room_id (int): The id of the room
        room_name (str): The chatrooms name
        created_at (int): UTC timestamp of when the room was created
        room_description (Optional[str]): Description of the room if there is one
    """

    room_id: int
    room_name: str
    created_at: int  # it will be a datetime.datetime.utcnow().timestamp()
    room_description: str = None


class RoomMessage(BaseModel):
    """
    Class for a Message sent in a room

    Attributes:
        chatroom (Room): The room object of the room its in
        message_id (int): Id of the message
        created_at (int): Utc timestamp of when the message was created
        message_content (str): The actual content of the message
        message_author (AuthorizedUser): User class of the person who sent the message
    """

    chatroom: Room
    message_id: int
    created_at: int
    messsage_content: str
    message_author: AuthorizedUser


class ChatRoom(Room):
    """
    Chatroom connection manager and room subclass

    Attributes:
        room_id (int): The id of the room
        room_name (str): The chatrooms name
        created_at (int): UTC timestamp of when the room was created
        room_description (Optional[str]): Description of the room if there is one

        connected_users (list[RoomUser]): List of users currently connected to the room

    Methods:
        (async) join_room: Connects a user to the room by accepting the websocket and
            appending it to the list of connected users
        (async) disconnect: Disconnects a user from the room (close websocket and remove from list)
        (async) send_to_user: Sends a message to only one person in the room
        (async) broadcast: Sends a message (RoomMessage) to all connected users in the room
    """

    connected_users: list = []

    async def join_room(self, user: RoomUser) -> None:
        """
        Connects a user to the room by accepting the websocket and appending it to the list of connected users

        Parameters:
            user (RoomUser): The user to connect to the room
        """
        await user.websocket.accept()
        self.connected_users.append(user)

    async def disconnect(self, user: RoomUser) -> None:
        """
        Disconnect user from room

        Parameters:
            user (RoomUser): The user to disconnect from the room
        """
        try:
            await user.websocket.close()
        except RuntimeError:
            print(f"Error while closing websocket connection with {user.user.username}")
        self.connected_users.remove(user)

    async def send_to_user(self, message: RoomMessage, user: RoomUser) -> None:
        """
        Send a message to only one person in the room

        Parameters:
            message (RoomMessage): The message to send
            user (RoomUser): User to send message to
        """
        await user.websocket.send_json(message.json())

    async def broadcast(self, message: RoomMessage) -> None:
        """
        Send a message to everyone in the room

        Parameters:
            message (RoomMessage): Message to broadcast to the room
        """
        for user in self.connected_users:
            if isinstance(message, RoomMessage):
                await user.websocket.send_text(message.json())
            else:
                await user.websocket.send_json(message)
