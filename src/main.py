""" (script)
This is the file that will be run to start the API
"""

__authors__ = ["Siddhesh Zantye"]
__version__ = "0.0.1"

import os
import uvicorn
from fastapi import Depends
from dotenv import load_dotenv

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    signup_endpoint,
    get_user_endpoint,
    chatroom_websockets,
    chatroom_endpoints,
    other_user_endpoints,
    reset_password_endpoint
)
from core.models import Chat_API, AuthorizedUser
from api.auth import oauth2_endpoint, check_auth_token

load_dotenv()  # laod enviroment variables from the .env file
app = Chat_API()

# Add all the APIRouters (Endpoints) to the app
app.include_router(oauth2_endpoint)
app.include_router(signup_endpoint)
app.include_router(get_user_endpoint)
app.include_router(chatroom_websockets)
app.include_router(chatroom_endpoints)
app.include_router(reset_password_endpoint)
app.include_router(other_user_endpoints)

# cors
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/demo", tags=["Non API / Other"])
async def home(request: Request):
    """
    The demo page
    """
    with open("../testing/demo/index.html") as f:
        data = f.read()
    return HTMLResponse(content=data)


@app.get("/", tags=["Non API / Other"])
async def home(request: Request):
    """
    The home page, Redirects to docs
    """
    return RedirectResponse("/docs")


@app.get("/documentation", tags=["Non API / Other"])
async def home(request: Request):
    """
    Actual docs for the endpoints
    """
    return RedirectResponse(
        "https://github.com/Untitled-Chat-App/Backend/blob/main/docs/docs.md"
    )


@app.get("/api/user/me", tags=["Users"])
async def me(request: Request, user: AuthorizedUser = Depends(check_auth_token)):
    """
    Quick endpoint to check if youre logged in
    """
    return user


HOST_IP = os.environ["HOST_IP"]


# Run
if __name__ == "__main__":
    # Start the api
    if os.environ["PRODUCTION"] == "False":
        uvicorn.run("main:app", host=HOST_IP, port=443, reload=False)
        # I prefer to use this (cli uvicorn) though for dev:
        # uvicorn main:app --reload --host="0.0.0.0" --port=443
        # or just: make test cause im lazy

    # If its the actual hosted one:
    uvicorn.run(
        app,
        reload=False,
        host=HOST_IP,
        port=443,
        ssl_keyfile="./key.pem",
        ssl_certfile="./cert.pem",
    )
