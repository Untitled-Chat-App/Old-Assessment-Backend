# Backend

[API DOCS](https://github.com/Untitled-Chat-App/Backend/wiki/introduction#introduction)

This is the backend (api) for an app I am making for a school programming assessment and to present at an open evening for our school.    
The app is a chat app and will use web sockets to let users communicate in real time.  
It will also use oauth2 authentication, hashing and end to end encryption to ensure the user data is stored securely and that the app is secure.  
This api is written in python which is my main and favorite language whereas the frontend will be written in JS using Electron to make a desktop app.

Structure:
```
├── Makefile
├── README.md
├── docs
│   ├── docs.md
│   └── images
│       ├── get_room_by_id_schema.jpg
│       ├── get_user_by_id.jpg
│       ├── new_chatroom_schema.jpg
│       ├── signup_request_schema.jpg
│       ├── token_request_schema.jpg
│       ├── update_me_schema.jpg
│       ├── update_users_schema.jpg
│       └── validation_error.jpg
└── src
    ├── api
    │   ├── auth
    │   │   ├── __init__.py
    │   │   └── authentication.py
    │   └── routes
    │       ├── __init__.py
    │       ├── rooms
    │       │   ├── chatroom_api.py
    │       │   └── chatroom_ws.py
    │       └── user
    │           ├── deleteuser.py
    │           ├── getuser.py
    │           ├── modify_user.py
    │           ├── reset_password_email.py
    │           └── signup.py
    ├── cert.pem
    ├── core
    │   ├── database
    │   │   ├── __init__.py
    │   │   ├── context.py
    │   │   ├── fetch.py
    │   │   └── tables.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   ├── base_models.py
    │   │   ├── chatapp.py
    │   │   └── room.py
    │   └── utils
    │       ├── __init__.py
    │       └── hash.py
    ├── html
    │   ├── demo.html
    │   └── imagine_forgeting.html
    ├── key.pem
    ├── main.py
    └── requirements.txt
```