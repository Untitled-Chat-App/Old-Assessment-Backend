""" (module)
Code for the endpoint to request public keys for a user
"""

__all__ = ["get_user_endpoint"]


from fastapi import Depends, APIRouter, HTTPException

from ...auth import check_auth_token
from core.models import AuthorizedUser
from core.database import get_user_by_id


get_user_endpoint = APIRouter()


@get_user_endpoint.get("/api/users/{user_id}")
async def get_user_with_user_id(
    user_id: int, auth_user: AuthorizedUser = Depends(check_auth_token)
):
    """
    Get some users by their userid

    Requirements
    ------------
        user_id
    """
    if (
        auth_user.permissions.get_user_details != True
    ):  # if they dont have the permissions to create users
        return HTTPException(
            status_code=403,
            detail="You don't have permission to use this endpoint (skill issue)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(
        user_id
    )  # Check if someone has the same username/account already exists

    if user is None:
        return HTTPException(
            status_code=409,
            detail="User with this username doesnt exists",
        )

    return user
