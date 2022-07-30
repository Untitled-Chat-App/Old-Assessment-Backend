# API Documentation/Reference

---

## Contents

### Info and objects:

* [Introduction](#introduction)
  * [Base URL](#base-url)
  * [Format for endpoints](#format-for-endpoints)
* [Authentication & Authorization](#authentication--authorization)
  * [Authentication](#authentication)
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
* [User Endpoints](#user-endpoints)
  * [Get current user](#get-current-logged-in-user)
  * [Create new user](#create-new-usersignup)


---

## Introduction

This is a [Websocket](https://en.wikipedia.org/wiki/WebSocket) and [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) based api. It will be used as a second backend for my electron.js chat app and it will interact with the postgresql database. Most of the processing of data, messages, authentication and more will be handled here remotely and securely.

Most endpoints will return and accept an [`application/json`](https://en.wikipedia.org/wiki/JSON) type of input for POST and some query parameters.

Also most endpoints will require Authentication/Authorization with OAuth JWT bearer tokens. 

### Format for endpoints:
For each endpoint I will include the type of, and what data you will need to use for the request, an example response, if the endpoint it requires authentication, rate limits and more aditional information you might need when using it.   

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

This endpoint unlike most (that use application/json), uses `application/x-www-form-urlencoded` as the content type. So when submiting the details its done like `username=<username>&password=<password>&scope=[scopes]`

### Arguments:

**Username:**  
(string) Username to the account  

**Password:**  
(string) Password to the account  

**Scopes:**

Each user has a default set of permissions which is things they can do with the API (see Permissions section under Users for info on each one). If a user requires additional permissions that are not in the default set of permissions they can request them. This is done by adding the scopes wanted to the scopes parameter when requesting a token.

**Scopes List:**   
`"create_rooms"`: The ability to create chatrooms  
`"delete_self"`: Permission to delete the current user/delete your own account
`"mofify_self"`: Be able to modify your own account

**Example Request:**
```bash
curl -X 'POST' \
  'https://chatapi.fusionsid.xyz/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=<username>&password=<password>&scope=[scopes]'
```

**Example Response:**
```bash
{
  "access_token": "string", # Your access token
  "token_type": "string" # usually Bearer
}
```

**Note:**  
If you dont want to request any scopes you can just do `&scope=`


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

## User endpoints

---

### Get current logged in user:
### `GET /api/user/me`

**Authorization required for this endpoint**

Returns the currently logged in user. To see who is logged in it checks who the access token from the Authorization header belongs too. 

If no user is logged in (auth token has not been provided) It will return:

**Request:**
```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/user/me' \
  -H 'accept: application/json'
```

**Response** Status Code = 401
```json
{
  "detail": "Not authenticated"
}
```

If authenticated successfull the response will be a user object like this:  

**Request:**
```bash
curl -X 'GET' \
  'https://chatapi.fusionsid.xyz/api/user/me' \
  -H 'accept: application/json'
```

**Response:**

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

Try is out here: [Link](https://chatapi.fusionsid.xyz/docs#/default/me_api_user_me_get)

---

### Create new user/signup:
### `POST /api/users/signup`

**Authentication not required for this endpoint**

...


Try is out here: [Link](https://chatapi.fusionsid.xyz/docs#/default/create_account_api_users_signup_post)

---