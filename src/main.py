""" (script)
This is the file that will be run to start the API
"""

__authors__ = ["Siddhesh Zantye"]
__version__ = "0.0.1"

import uvicorn
from dotenv import load_dotenv

from core.models import Chat_API

load_dotenv()
app = Chat_API()

# Run
if __name__ == "__main__":
    print("http://192.168.68.125:443/")
    uvicorn.run(app, host="0.0.0.0", port=443, reload=False)
