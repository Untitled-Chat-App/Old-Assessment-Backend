""" (module)
Functions for hashing passwords to be stored in the database
"""

__all__ = ["hash_text"]

import os
import hashlib
import binascii

from dotenv import load_dotenv

load_dotenv()


async def hash_text(text: str) -> str:
    SALT = (os.environ["SALT"]).encode()
    ITERATIONS = int(os.environ["ITERATIONS"])

    encrypted = hashlib.pbkdf2_hmac("sha256", text.encode(), SALT, ITERATIONS)

    return binascii.hexlify(encrypted).decode()
