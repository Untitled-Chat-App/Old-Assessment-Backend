""" (module) chatapp
This contains the Chat_API class (FastAPI subclass)
"""

__all__ = ["Chat_API"]

from fastapi import FastAPI
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler


DESCRIPTION = """
### API/Backend for chat app
"""


class Chat_API(FastAPI):
    """
    The custom subclass of FastAPI called Chat_API

    [API docs](https://github.com/Untitled-Chat-App/Backend/blob/main/docs/docs.md)
    """

    def __init__(self) -> None:
        super().__init__()
        # Docs config
        self.title = "Untitled-Chat API"
        self.version = "1.1.1"
        self.description = DESCRIPTION
        self.license_info = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        }

        # Middleware:

        # CORS
        origins = ["*"]
        self.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Rate limiting
        self.state.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[
                "30/minute"
            ],  # set default rate limit to 30 requests per minute
        )
        self.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        self.add_middleware(SlowAPIMiddleware)
