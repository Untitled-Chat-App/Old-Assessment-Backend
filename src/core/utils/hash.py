""" (module)
Functions for hashing passwords to be stored in the database
"""

__all__ = ["hash_text"]

from argon2 import PasswordHasher

from dotenv import load_dotenv

load_dotenv()


async def hash_text(text: str) -> str:
    """
    Hashes text using the argon2 algorithm\n
    This function will be mainly used for storing passwords in a safe and secure way

    Parameters:
        text (str): The text to hash

    Returns:
        str: The hashed output of the function
    """
    password_hasher = PasswordHasher()
    hashed_output = password_hasher.hash(text)

    return hashed_output
