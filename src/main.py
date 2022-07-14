""" (script)
This is the file that will be run to start the API
"""

__authors__ = ["Siddhesh Zantye"]
__version__ = "0.0.1"

import uvicorn
from fastapi import Depends
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

from api.routes import signup_endpoint
from core.models import Chat_API, AuthorizedUser
from api.auth import oauth2_endpoint, check_auth_token

load_dotenv()
app = Chat_API()

app.include_router(signup_endpoint)
app.include_router(oauth2_endpoint)


@app.get("/")
async def home():
    """
    The home page, Redirects to docs
    """
    return RedirectResponse("/docs")


@app.get("/api/users/me")
async def me(user: AuthorizedUser = Depends(check_auth_token)):
    """
    Quick endpoint to check if youre logged in
    """
    return user


# Run
if __name__ == "__main__":
    # For some reason it wont print the normal fastapi stuff so I put this (will remove once testing done):
    print("http://192.168.68.125:443/")
    # Start the api
    uvicorn.run(app, host="0.0.0.0", port=443, reload=False)
