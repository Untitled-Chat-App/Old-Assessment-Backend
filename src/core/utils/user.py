import re


async def validate_user(username: str) -> bool:
    """
    Takes in a username and checks if it is valid.

    Parameters:
        username (str): The username of the person signing up

    Criteria:
        ^(?=.{3,32}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$
        └─────┬────┘└───┬──┘└─────┬─────┘└─────┬─────┘ └───┬───┘
            │         │         │            │           no _ or . at the end
            │         │         │            │
            │         │         │            allowed characters
            │         │         │
            │         │         no __ or _. or ._ or .. inside
            │         │
            │         no _ or . allowed at the beginning
            │
            username must be 3-32 characters long

    Returns:
        bool: If username is value it returns True else False
    """
    if len(username) < 1:
        return False

    if username[0].isnumeric():
        return False

    if not re.match(
        "^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$", username
    ):
        return False

    return True
