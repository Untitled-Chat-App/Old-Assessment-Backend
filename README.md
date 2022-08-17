# Backend

[API DOCS](https://github.com/Untitled-Chat-App/Backend/wiki/introduction#introduction)

This is the backend (api) for an app I am making for a school programming assessment and to present at an open evening for our school.    
The app is a chat app and will use web sockets to let users communicate in real time.  
It will also use oauth2 authentication, hashing and end to end encryption to ensure the user data is stored securely and that the app is secure.  
This api is written in python which is my main and favorite language whereas the frontend will be written in JS using Electron to make a desktop app.

Structure:
```bash
└── src # all code for the api
    ├── api # actual routes and endpoints
    │   ├── auth
    │   │   ├── __init__.py
    │   │   └── authentication.py # authentication and authorization system code
    │   └── routes # api rest / websocket routes
    │       ├── __init__.py
    │       ├── rooms # room endpoints (http/s and ws/s)
    │       │   ├── chatroom_api.py
    │       │   └── chatroom_ws.py
    │       └── user # user endpoints (http/s)
    │           ├── deleteuser.py
    │           ├── getuser.py
    │           ├── modify_user.py
    │           ├── reset_password_email.py
    │           └── signup.py
    ├── cert.pem # ssl certificate file for https
    ├── core # this has utils, classes/models, database functions etc
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
    ├── html # html files for pages like the demo page
    │   ├── demo.html
    │   └── imagine_forgeting.html
    ├── key.pem # ssl keyfile for https
    ├── main.py # file to start the api and actually run it
    └── requirements.txt # package / library requirements
```