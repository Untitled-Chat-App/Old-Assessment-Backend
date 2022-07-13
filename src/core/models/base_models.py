""" (module) base_models
Contains pydantic.BaseModel subclasses for api form data
"""

__all__ = ["User"]

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

