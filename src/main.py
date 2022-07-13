""" (script)
This is the file that will be run to start the API
"""

__authors__ = ["Siddhesh Zantye"]
__version__ = "0.0.1"

import uvicorn
from fastapi import Depends
from dotenv import load_dotenv

from core.models import Chat_API, AuthUser
from api.routes import signup_endpoint
from api.auth import oauth2_endpoint, check_auth_token

load_dotenv()
app = Chat_API()
app.include_router(signup_endpoint)
app.include_router(oauth2_endpoint)

@app.get("/")
async def home(user: AuthUser =  Depends(check_auth_token)):
    return user

# Run
if __name__ == "__main__":
    print("http://192.168.68.125:443/")
    uvicorn.run(app, host="0.0.0.0", port=443, reload=False)
