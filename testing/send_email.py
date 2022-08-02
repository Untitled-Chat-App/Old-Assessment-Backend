import smtplib, ssl
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import dotenv

dotenv.load_dotenv()

port = 465
smtp_server = "smtp.gmail.com"
sender_email = "siddheshadsv@gmail.com"
receiver_email = "siddheshadsv@icloud.com"
password = "qkhhigsrsqjcpqnb"

data = {"userid": 12214, "type": "password_reset"}
to_encode = data.copy()
expire = datetime.utcnow() + timedelta(minutes=15)
to_encode.update({"exp": expire})  # add in expiry time

encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SIGN"], algorithm="HS256")
print(encoded_jwt)

message = """\
Email Reset link: {}
"""

# context = ssl.create_default_context()
# with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_email, message)
