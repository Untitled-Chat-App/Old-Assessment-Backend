""" (module)
Code for the endpoint to update a user or delete them
"""

__all__ = ["get_user_endpoint"]

from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from ...auth import check_auth_token
from core.models import AuthorizedUser
from core.database import get_user_by_id, asyncpg_connect
from core.utils import hash_text


other_user_endpoints = APIRouter()


class UpdateBody(BaseModel):
    attribute: str
    new_value: str | int | bool


@other_user_endpoints.patch("/api/users/{user_id}")
async def update_user_data(
    user_id: int,
    update_details: UpdateBody,
    auth_user: AuthorizedUser = Depends(check_auth_token),
):
    OPTIONS = list(AuthorizedUser.__fields__.keys())
    OPTIONS.remove("user_id")
    OPTIONS.remove("permissions")

    if update_details.attribute not in OPTIONS:
        return HTTPException(
            status_code=400,
            detail={"error": "Invalid attribute provided.", "options": OPTIONS},
        )

    if auth_user.permissions.update_users != True:
        return HTTPException(
            status_code=403,
            detail={
                "error": "You don't have the permissions to perform this request.",
                "permission_needed": {"update_users": True},
            },
        )

    user = await get_user_by_id(user_id)

    if user is None:
        return HTTPException(
            status_code=404,
            detail={
                "error": "User with id provided does not exist",
                "id_provided": user_id,
            },
        )

    if update_details.attribute == "password":
        password = await hash_text(update_details.new_value)

        async with asyncpg_connect() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE Users Set password=$1 WHERE user_id=$2", password, user_id
                )

    elif update_details.attribute in ["email", "public_key", "username"]:
        async with asyncpg_connect() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"UPDATE Users Set {update_details.attribute}=$1 WHERE user_id=$2",
                    update_details.new_value,
                    user_id,
                )

    updated_user = await get_user_by_id(user_id)

    if updated_user == user:
        return HTTPException(
            status_code=500,
            detail={
                "error": "An error occured on the server side when updating the user",
                "what_err": "idk man Im trYING My besT herE",
            },
        )

    return JSONResponse(
        {
            "result": "New user created successfully",
            "new_user": updated_user,
            "old_user": user,
        },
        200,
    )
