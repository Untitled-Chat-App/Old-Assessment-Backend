""" (module) base_models
Contains pydantic.BaseModel subclasses for api form data
"""

__all__ = ["NewUser", "Token", "AuthUser"]

from pydantic import BaseModel


class NewUser(BaseModel):
    username: str
    email: str
    password: str
    public_key: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthUser(BaseModel):
    username: str
    password: str


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


class AuthorizedUser(AuthUser):
    permissions: AuthPerms
