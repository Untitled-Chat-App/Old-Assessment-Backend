""" (script)
This is the file that will be run to start the API
"""

__authors__ = ["Siddhesh Zantye"]
__version__ = "0.0.1"

import os
import uvicorn
from fastapi import Depends
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse

from api.routes import signup_endpoint, get_user_endpoint, websocket_endpoints
from core.models import Chat_API, AuthorizedUser
from api.auth import oauth2_endpoint, check_auth_token

load_dotenv()
app = Chat_API()

app.include_router(signup_endpoint)
app.include_router(oauth2_endpoint)
app.include_router(get_user_endpoint)
app.include_router(websocket_endpoints)


@app.get("/")
async def home():
    """
    The home page, Redirects to docs
    """
    return RedirectResponse("/docs")


@app.get("/api/user/me")
async def me(user: AuthorizedUser = Depends(check_auth_token)):
    """
    Quick endpoint to check if youre logged in
    """
    return user


# Run
if __name__ == "__main__":
    # Start the api
    if os.environ["PRODUCTION"] == "False":
        uvicorn.run("main:app", host="0.0.0.0", port=443, reload=False)
        # I prefer to use this (cli uvicorn) though for dev:
        # uvicorn main:app --reload --host="0.0.0.0" --port=443


    # If its the actual hosted one:
    uvicorn.run(app, reload=False, host="0.0.0.0", port=443, ssl_keyfile="./key.pem", ssl_certfile="./cert.pem")