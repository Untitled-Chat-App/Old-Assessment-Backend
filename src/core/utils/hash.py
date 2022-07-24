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
    """
    Hashes text using pbkdf2_hmac and sha256 algorithm\n
    This function will be mainly used for storing passwords in a safe and secure way

    Parameters:
        text (str): The text to hash

    Returns:
        str: The hashed output of the function
    """
    SALT = (
        os.environ["SALT"]
    ).encode()  # the salt that will be sprinkled in to make it harder to crack.
    ITERATIONS = int(
        os.environ["ITERATIONS"]
    )  # The amount of times the algorithm will be repeated

    encrypted = hashlib.pbkdf2_hmac("sha256", text.encode(), SALT, ITERATIONS)

    return binascii.hexlify(encrypted).decode()
