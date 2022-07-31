# API Documentation/Reference

---

## Contents

### Info and objects:

* [Introduction](#introduction)
  * [Base URL](#base-url)
  * [Format for endpoints](#format-for-endpoints)
* [Authentication & Authorization](#authentication--authorization)
  * [Authentication](#authentication)
  * [Access tokens](#access-tokens)
  * [Authorization](#authorization)
* [Users](#users)
  * [User Object / Structure / Examples](#user-object)
  * [User Attributes](#user-attributes)
  * [User Permissions](#user-permissions)
* [Chatrooms](#chatrooms)
  * [Chatroom Object](#chatroom-object)
  * [Chatroom Attributes](#room-attributes)

### [Endpoints](#endpoints):
* [Ratelimits](#ratelimits)
* [Validation Error](#validation-error)
* [User Endpoints](#user-endpoints)
  * [Get current user](#get-current-logged-in-user)
  * [Create new user](#create-new-usersignup)

Also if you want checkout the redoc url for a UI version of this with less detail: [Link to redoc](https://chatapi.fusionsid.xyz/redoc)

---

## Introduction

This is a [Websocket](https://en.wikipedia.org/wiki/WebSocket) and [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) based api. It will be used as a second backend for my electron.js chat app and it will interact with the postgresql database. Most of the processing of data, messages, authentication and more will be handled here remotely and securely.

Most endpoints will return and accept an [`application/json`](https://en.wikipedia.org/wiki/JSON) type of input for POST and some query parameters.

Also most endpoints will require Authentication/Authorization with OAuth JWT bearer tokens. 

### Format for endpoints:
For each endpoint I will include the type of, and what data you will need to use for the request, an example response, if the endpoint it requires authentication, rate limits and more aditional information you might need when using it. I will also try to include a link to try out the endpoint.

**Format for example parameters/arguments:**  
Another thing to note is that if I say something like `[username]` you need to replace the username with your actual username. If a parameter/argument is wrapped with angled brackets (`<argument>`) that means that it is required. If it is optional it will be wrapped in square brackets (`[argument]`)

**Example requests will be shown in [`curl`](https://en.wikipedia.org/wiki/CURL)**

## Base URL

This is the base url for all requests:

[`https://chatapi.fusionsid.xyz/`](https://chatapi.fusionsid.xyz/)

In most examples I will include only the part after the base url.  
**Example:** If I write [`/api/user/me`](https://chatapi.fusionsid.xyz/api/user/me), The full URL will be at https://chatapi.fusionsid.xyz/api/user/me

**Encryption**  
All services and protocols (REST & WebSocket) within the API are using HTTPS and WSS which has TLS (Transport Layer Security) encryption.

**Aditional Cloudflare Security**  
I also use cloudflare as a middle man for requests. This helps with caching, security because they have functions for that, anylytics and more

---

# Authentication & Authorization

### Authentication

To be able to use most endpoints of this api you will require an access token. This can be obtained at the `/token` endpoint

### `POST: /token`

### Try is out here: [Link](https://chatapi.fusionsid.xyz/docs#/Get%20access%20token/login_for_access_token_token_post)

This endpoint unlike most (that use application/json), uses `application/x-www-form-urlencoded` as the content type. So when submiting the details its done like `username=<username>&password=<password>&scope=[scopes]`

### Arguments:

**Username:**  
(string) Username to the account  

**Password:**  
(string) Password to the account  

**Scopes:**

Each user has a default set of permissions which is things they can do with the API (see Permissions section under Users for info on each one). If a user requires additional permissions that are not in the default set of permissions they can request them. This is done by adding the scopes wanted to the scopes parameter when requesting a token.

**Scopes List:**   
* `"create_rooms"`: The ability to create chatrooms  
* `"delete_self"`: Permission to delete the current user/delete your own account  
* `"mofify_self"`: Be able to modify your own account

Image of schema:

<img src="./images/token_request_schema.jpg" alt="drawing" width="690" height="auto"/>

**Example Request:**
```bash
curl -X 'POST' \
  'https://chatapi.fusionsid.xyz/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=<username>&password=<password>&scope=[scopes]'
```

**Example Response:**
```json
// status code: 200
{
  "access_token": "string", // Your access token
  "token_type": "string" // should be: "Bearer"
}
```

**Note:**  
If you dont want to request any scopes you can just do `&scope=`

---

### Access Tokens

Access tokens for users are of type `Bearer`. This prefix should be include when the endpoint needs the token in the header (see authorization bellow).  

The access tokens are JWT (json web tokens). They are signed so mofifying them automatically makes them invalid.  
Payload of the token is user_id, scopes (if none empty list), and expiry time.

#### Access tokens expire in 1440 minutes (24 hours / 1 day) after they were created.

---

### Authorization:

For all HTTP endpoints that require authentication, the access_token is put into the `Authorization` HTTP header. 

**Format:**

```json
{
    "Authorization": "Bearer [access_token]"
}
```

**Example:**

```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/user/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer super_secret_access_token'
```
---

# Users

Users are very important part of this app. (cause without people to use it, it wont work).  
Users in this app are stored in a database with their passwords hashed.  
They also have a default set of permissions but can request more.  


## User Object:

### User Structure 

	
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "permissions": {
    "perm_name": boolean,
    ...
  },
  "public_key": "string",
  "user_id": integer
}
```

**Example User:**
```json
{
  "username": "CoolUser",
  "password": "$argon2id$v=19$m=65536,t=3,p=4$e62IAa7wkzWZJVihV+IiRQ$YCQGST6V1IhjunNDZn1QJRad9EgX4nyFu0kg9T94kRg",
  "email": "cool.user@example.com",
  "permissions": {
    "get_self": true,
    "mofify_self": true,
    "delete_self": false,
    "get_other_users": true,
    "join_rooms": true,
    "create_rooms": false,
    "ban_users": false,
    "unban_users": false,
    "create_users": false,
    "delete_users": false,
    "update_users": false
  },
  "public_key": "-----BEGIN PUBLIC KEY-----\\n ... \\n-----END PUBLIC KEY-----",
  "user_id": 123456789
}
```

### User Attributes:

| name        | type    | what it is                                                                                                    |
|-------------|---------|---------------------------------------------------------------------------------------------------------------|
| username    | `string`  | The username to the account                                                                                   |
| password    | `string`  | Hashed version of the users password                                                                          |
| email       | `string`  | the users email                                                                                               |
| permissions | `dict`    | A dictionary of the users permissions. Each permission is in format: perm_name (`string`): `boolean` (true/false). See bellow for info |
| public_key  | `string`  | The users RSA public key. Used for end to end encryption in DMs.                                                  |
| user_id     | `integer` | The user's id. Will not change as it is used to identify the user no matter the username                      |

## User Permissions:

Every user has certain permissions. If they are not a super (cool, awesome) user and they haven't requested any permissions then they get the default set.  
User permissions is important because it allows them to access endpoints in the API that they didnt have access to before.

**List of current permissions:**

If permission has `= False` it means that it is off by default and needs to be requested

**User permissions:**  
* `get_self: boolean`: Be able to get details about the current user (you)
* `mofify_self: boolean = False`: Permission to modify the current user's account details.
* `delete_self: boolean = False`: Be able to delete your account
* `get_other_users: boolean`: Permission to get details on other users

**Room permissions:**  
* `join_rooms: boolean`: Be able to join chatrooms  
* `create_rooms: boolean = False`: Permission to create rooms

**Admin permissions:**

All of these permissions cannot be access unless you have a admin account. These permissions also canot be requested. I wil not explain them because its obvious.

* `ban_users: boolean`  
* `unban_users: boolean`    
* `create_users: boolean`    
* `delete_users: boolean`  
* `update_users: boolean`  


**Default list of permissions:**

* `get_self`  
* `get_other_users`  
* `join_rooms`  

Want more? Ask nicely and request them :)

---

# Chatrooms

One of the features of this app is chatrooms. Chat rooms similar to irc rooms or group chats are a way for multiple users to communicate. All messages sent in the room are brodcasted to all people in the room. Users can create and join chatrooms.

## Chatroom Object:

### Chatroom structure:

```json
{
  "room_id": "string",
  "room_name": "string",
  "created_at": integer,
  "room_description": "string"
}
```

**Example Room:**

```json
{
  "room_id": 166198832,
  "room_name": "Rickrollers",
  "created_at": 1659055993,
  "room_description": "People who deeply appreciate rick astley"
}
```

### Room Attributes
| name             | type    | description                                                                                |
|------------------|---------|--------------------------------------------------------------------------------------------|
| room_id          | integer | ID of the room. Used to identify the room and just like user_ids, it cannot be changed.    |
| room_name        | string  | Name of the room. Shown to users who join it                                               |
| room_description | string  | Description of the room. This is optional and can be used to describe what the room is for |
| created_at       | integer | Unix (UTC) timestamp of when the room was created.                                         |



---

# API Endpoints:

---

## Ratelimits

All endpoints on this api have a default rate limit of 30 requests per minute.  
If a specific endpoint has a different rate limit I will specify that in that endpoints section.

If you make a request to the API after execding the rate limit you will get an error like this:

```json
// Status code: 429
{
  "error": "Rate limit exceeded: 30 per 1 minute"
}
```

\*results may vary if the endpoint has a different limit

If you exceede the limit. STOP WHAT YOURE DOING RIGHT NOW. why you spamming me. I dont like it. Also after the minute ends you can continue making your requests. Also imagine tryna spam and getting ratelimited (skill issue)


---
## Common Errors

These are errors that you can get on pretty much all endpoints. This is why im gonna keep them all here so i dont have to put them in each endpoints section. If the endpoint has any aditional errors to be noted i wil include them in that endpoints section.


## Validation Error

If incorrect input has been passed to the api, you might get a validation error.  
This should be on every endpoint so keep that in mind when making a request.  
The status code of that error will be 422 and it will look like this:

**Schema:**

<img src="./images/validation_error.jpg" alt="drawing" width="690" height="auto"/>

**What it will look like:**

```json
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### Example:

**Invalid Request:**
```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/users/kjgbewt235' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <access token>'
```

The error here is that that endpoint requires the input to be an integer and i passed in `"kjgbewt235"` which is not a valid integer. Here is what you get back:

**Unsuccessful Response:**

```json
{
  "detail": [
      {
          "loc": ["path", "user_id"],
          "msg": "value is not a valid integer",
          "type": "type_error.integer",
      }
  ]
}
```

In the response it will tell you what value was an incorrect value and what exactly the error was. 

---

## Not authenticated error

Most endpoints on this api require authorization.  
If authorization has not been provided (bearer token not in Authorization header), you will an error.

Example of a request which will give an error:

**Invalid Request:**
```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/user/me' \
  -H 'accept: application/json'
```

The reason this raises an error is because no token has been passed in.  
So you get this:

**Unsuccessful Response** 
```json
// status code: 401
{
  "detail": "Not authenticated"
}
```

---

## User/Users endpoints:

---

### Get current logged in user:
### `GET /api/user/me`

**Authorization required for this endpoint**

Returns the currently logged in user. To see who is logged in it checks who the access token from the Authorization header belongs too. 

If authenticated successfull the response will be a user object like this:  

**Request:**
```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/user/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <access_token>'
```

**Response:**

```json
// status code if success: 200
{
  "username": "string",
  "password": "string",
  "email": "string",
  "permissions": {
    "perm_name": boolean,
    ...
  },
  "public_key": "string",
  "user_id": integer
}
```

### Try the endpoint out here: [Link](https://chatapi.fusionsid.xyz/docs#/Users/me_api_user_me_get)

---

### Create new user/signup:
### `POST /api/users/signup`

**Authentication not required for this endpoint**

This endpoint is used to signup users/create new users for the app.  

**Request Schema:**

<img src="./images/signup_request_schema.jpg" alt="drawing" width="690" height="auto"/>

**Request**  
A request to this endpoint will look like this:

```bash
curl -X 'POST' \
  'https://chatapi.fusionsid.xyz/api/users/signup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "string",
  "email": "string",
  "password": "string",
  "public_key": "string"
}'
```

If sucessfull you will get a user object response.
 
**Example successfull response:**

```json
{
  "success": true,
  "detail": "User created successfully",
  "user": {
    "username": "string",
    "password": "string",
    "email": "string",
    "permissions": {
      "perm_name": boolean,
      ...
    },
    "public_key": "string",
    "user_id": integer
  }
}
```

### Errors

If you make a request and the username is the same as some user that already exists you will get an error like this:

**Unsuccessful Response:**

```json
// Status code: 409
{
  "detail": "User with this username already exists"
}

```


### Try the endpoint out here: [Link](https://chatapi.fusionsid.xyz/docs#/Users/create_account_api_users_signup_post)

---


### Get all users
### `GET /api/users/getAllUsers`

**Authentication required for this endpoint**

This endpoint is used to get all users registered to the app / users in the database.  
Its very simple and doesnt require and data passed to it (except auth).

**Request Schema:**

No data/parameters/arguments are needed for this endpoint

**Request**  
```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/users/getAllUsers' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <access token>'
```
 
**Example successful response:**

If succesfull you will get a list of user objects

```json
[
  {
    "username": "string",
    "password": "string",
    "email": "string",
    "permissions": {
      "perm_name": boolean,
      ...
    },
    "public_key": "string",
    "user_id": integer
  },
  ...
]

```

### Try the endpoint out here: [Link](https://chatapi.fusionsid.xyz/docs#/Users/get_all_users_api_users_getAllUsers_get)

---

### Get user by id:
### `GET /api/users/{user_id}`

**Authentication required for this endpoint**

This endpoint if for getting a user object by the id. It searches the database for another user who has the same id and if so it will return it. Since no 2 users can have the same id it will only return one user and if it cant find it, it will return an error.

**Request Schema:**

<img src="./images/get_user_by_id.jpg" alt="drawing" width="690" height="auto"/>

user_id must be passed in the path and must be an integer.

**Example Request**  
```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/users/690420690' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <access token>'
```
 
**Example successful response:**

If user is found you will get a user object:

```json
{
    "username": "string",
    "password": "string",
    "email": "string",
    "permissions": {
      "perm_name": boolean,
      ...
    },
    "public_key": "string",
    "user_id": integer
}
```

### Errors

**Unsuccessful Response:**

If user is not found you will get this error:

```json
{
  "detail": "User with this id doesnt exists"
}
```

### Try the endpoint out here: [Link](https://chatapi.fusionsid.xyz/docs#/Users/get_user_with_user_id_api_users__user_id__get)

---

### Update user details:
### `PATCH /api/users/{user_id}`

**Authentication required for this endpoint**

This endpoint is used to update a specific user. For example changing their password or saved public key.

**Request Schema:**

<img src="./images/update_users_schema.jpg" alt="drawing" width="690" height="auto"/>

The user id just like the get user by id endpoint needs to be passed in the path.

The `attribute` is the name of the value you want to change.  
**Options:**  `"username", "password", "email", "public_key"`  
See the user object section for info about each attribute.  

The `new_value` is the new value of the attribute. So if you want to change the email to `"example@gmail.com"` you would do: 
```json
{
  "attribute": "email",
  "new_value": "example@gmail.com"
}
```

**Example Request**  
```bash
curl -X 'PATCH' \
  'https://chatapi.fusionsid.xyz/api/users/690420690' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <access token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "attribute": "string",
  "new_value": "string"
}'
```
 
**Example successful response:**

If successfull you will get a response with the before and after (user objects) of the user:

```json
{
  "result": "User updated successfully",
  "new_user": {
    "username": "string",
    "password": "string",
    "email": "string",
    "permissions": {
      "perm_name": boolean,
      ...
    },
    "public_key": "string",
    "user_id": integer
  },
  "old_user": {
    "username": "string",
    "password": "string",
    "email": "string",
    "permissions": {
      "perm_name": boolean,
      ...
    },
    "public_key": "string",
    "user_id": integer
  }
}
```

### Errors

**Unsuccessful Response:**

If you enter an attribute that doesn't exist you will get an error like this:

```json
{
  "detail": {
    "error": "Invalid attribute provided.",
    "options": [
      ...
    ]
  }
}
```

If the user is not found you will get an error like this:

```json
{
  "detail": {
    "error": "User with id provided does not exist",
    "id_provided": ...
  }
}
```


### Try the endpoint out here: [Link](https://chatapi.fusionsid.xyz/docs#/Users/update_user_data_api_users__user_id__patch)

---

### Update logged in user's details:
### `PATCH /api/user/me`

**Authentication required for this endpoint**

This endpoint is used to update a the user who is currently logged in.  
It will figure that out by looking at the user id that the token belongs too.  
This endpoint is basically the same as the `PATCH /api/users/{user_id}` endpoint except you dont pass in the user id

**Request Schema:**

<img src="./images/update_me_schema.jpg" alt="drawing" width="690" height="auto"/>

The `attribute` is the name of the value you want to change.  
**Options:**  `"username", "password", "email", "public_key"`  
See the user object section for info about each attribute.  

The `new_value` is the new value of the attribute. So if you want to change the email to `"example@gmail.com"` you would do: 
```json
{
  "attribute": "email",
  "new_value": "example@gmail.com"
}
```

**Example Request**  
```bash
curl -X 'PATCH' \
  'https://chatapi.fusionsid.xyz/api/user/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <access token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "attribute": "string",
  "new_value": "string"
}'
```
 
**Example successful response:**

If successfull you will get a response with the before and after (user objects) of the user:

```json
{
  "result": "User updated successfully",
  "new_user": {
    "username": "string",
    "password": "string",
    "email": "string",
    "permissions": {
      "perm_name": boolean,
      ...
    },
    "public_key": "string",
    "user_id": integer
  },
  "old_user": {
    "username": "string",
    "password": "string",
    "email": "string",
    "permissions": {
      "perm_name": boolean,
      ...
    },
    "public_key": "string",
    "user_id": integer
  }
}
```

### Errors

**Unsuccessful Response:**

If you enter an attribute that doesn't exist you will get an error like this:

```json
{
  "detail": {
    "error": "Invalid attribute provided.",
    "options": [
      ...
    ]
  }
}
```


### Try the endpoint out here: [Link](https://chatapi.fusionsid.xyz/docs#/Users/update_user_auth_data_api_user_me_patch)

---



<!-- ### :
### ``

**Authentication required for this endpoint**


**Request Schema:**

<img src="./images/" alt="drawing" width="690" height="auto"/>

**Request**  
```bash
```
 
**Example successful response:**

```json

```

### Errors

**Unsuccessful Response:**

```json
```


### Try the endpoint out here: [Link]()

--- -->
