""" (module) base_models
Contains pydantic.BaseModel subclasses for api form data
"""

__all__ = ["NewUser", "AuthUser", "Token", "AuthorizedUser", "AuthPerms"]

from pydantic import BaseModel

# new user class which is used as input for creating a new user (signup endpoint)
class NewUser(BaseModel):
    username: str
    email: str
    password: str
    public_key: str


# Token that will be returned to the function
class Token(BaseModel):
    access_token: str
    token_type: str


# class that is used for the form when getting a token
class AuthUser(BaseModel):
    username: str
    password: str


# Permissions class for a usr
class AuthPerms(BaseModel):
    # User
    get_user_details: bool
    update_user_details: bool

    # Messages
    get_messages: bool
    send_messages: bool

    # Admin perms
    create_users: bool
    delete_users: bool
    update_users: bool


# Subclass of authuser but with perms 
# This will be used cause its basically a User class but i didnt wanna call it that
class AuthorizedUser(AuthUser):
    email: str
    permissions: AuthPerms
    public_key: str
    user_id: int
