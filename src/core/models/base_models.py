""" (module) base_models
Contains pydantic.BaseModel subclasses for api form data
"""

__all__ = ["NewUser", "AuthUser", "Token", "AuthorizedUser", "AuthPerms", "NewRoom"]

from pydantic import BaseModel

# new user class which is used as input for creating a new user (signup endpoint)
class NewUser(BaseModel):
    """
    Used to make a new user in the signup endpoint

    Attributes:
        username (str): The new users username
        email (str): The new users email
        password (str): The new users password
        public_key (str): The new users public_key
    """

    username: str
    email: str
    password: str
    public_key: str


# Token that will be returned to the function
class Token(BaseModel):
    """
    Basemodel class for an access token

    Attributes:
        access_token (str): The access token (JWT token) to the users account
        token_type (str): Type of token (usualy it is Literal["Bearer"])
    """

    access_token: str
    token_type: str


# class that is used for the form when getting a token
class AuthUser(BaseModel):
    """
    Baseclass for AuthorizedUser
    This is used for login and getting an access_token

    Attributes:
        username (str): Username to the account
        password (str): password to the account
    """

    username: str
    password: str


# Permissions class for a usr
class AuthPerms(BaseModel):
    """
    Permissions a user can have
    This is usually checked for tasks that require higher perms like creating or deleting in the db
    """

    # User
    get_self: bool = True
    mofify_self: bool = True
    delete_self: bool = False

    get_other_users: bool = True

    # Chat rooms
    join_rooms: bool = True
    create_rooms: bool = False

    # Admin perms
    ban_users: bool = False
    unban_users: bool = False

    create_users: bool = False
    delete_users: bool = False
    update_users: bool = False


class AuthorizedUser(AuthUser):
    """
    Subclass of authuser but with perms
    This will be used cause its basically a User class but i didnt wanna call it that

    Attributes:
        username (str): The username of the user
        password (str): Password of the user
        email (str): Email of the user
        permissions (AuthPerms): AuthPerms class of permissions the user has
        public_key (str): Users public key
        user_id (int): Users user_id
    """

    email: str
    permissions: AuthPerms
    public_key: str
    user_id: int


class NewRoom(BaseModel):
    """
    Basemodel form to create a new room

    Attributes:
        room_name (str): The name of the room to create
        room_description (str): the description of the room
    """

    room_name: str
    room_description: str
