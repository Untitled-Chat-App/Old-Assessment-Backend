""" (module) chatapp
This contains the Chat_API class (FastAPI subclass)
"""

__all__ = ["Chat_API"]

from fastapi import FastAPI
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler


class Chat_API(FastAPI):
    """
    The custom subclass of FastAPI called Chat_API
    """

    def __init__(self) -> None:
        super().__init__()
        # Docs config
        self.title = "Untitled-Chat API"
        self.description = "### API/Backend for chat app"
        self.license_info = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        }

        # Rate limiting
        self.state.limiter = Limiter(key_func=get_remote_address)
        self.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
