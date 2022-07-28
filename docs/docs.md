# API Documentation/Reference

---

## Table Of Contents
e

---

## Introduction

This is a [Websocket](https://en.wikipedia.org/wiki/WebSocket) and [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) based api. It will be used as a second backend for my electron.js chat app and it will interact with the postgresql database. Most of the processing of data, messages, authentication and more will be handled here remotely and securely.

Most endpoints will return and accept an [`application/json`](https://en.wikipedia.org/wiki/JSON) type of input for POST and some query parameters.

Also most endpoints will require Authentication/Authorization with OAuth JWT bearer tokens. 

### Examples format:
For each endpoint I will include the type of, and what data you will need to use for the request, an example response, if the endpoint it requires authentication, rate limits and more aditional information you might need when using it.   

**The code/design**  
Also i will include a drop down read more section where i will briefly explain how the endpoint works (on the code side) and why I made a certain decision.  

**Format for example parameters/arguments:**  
Another thing to note is that if I say something like `[username]` you need to replace the username with your actual username. If a parameter/argument is wrapped with angled brackets (`<argument>`) that means that it is required. If it is optional it will be wrapped in square brackets (`[argument]`)

Examples will be shown in [`curl`](https://en.wikipedia.org/wiki/CURL)

## Base URL

This is the base url for all requests:

[`https://chatapi.fusionsid.xyz/`](https://chatapi.fusionsid.xyz/)

I will include only the part after so if I write [`/api/user/me`](https://chatapi.fusionsid.xyz/api/user/me) The full URL of the endpoint will be at https://chatapi.fusionsid.xyz/api/user/me

---

## Authentication & Authorization

### Authentication

To be able to use most endpoints of this api you will require an access token. This can be obtained at the `/token` endpoint

### `POST: /token`

This endpoint unlike most (that use application/json), uses `application/x-www-form-urlencoded` as the content type. So when submiting the details its done like `username=<username>&password=<password>&scope=[scopes]`

**Username** Username to the account
**Password** Password to the account

**Scopes:**

Each user has a default set of permissions which is things they can do with the API (see Permissions section under Users for info on each one). If a user requires additional permissions that are not in the default set of permissions they can request them. This is done by adding the scopes wanted to the scopes parameter when requesting a token.

Scopes List:   
`"create_rooms"`: The ability to create chatrooms  
`"delete_self"`: Permission to delete the current user/delete your own account

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

## User Permissions

`get_self: bool`: Be able to get details about the current user (you)  
`mofify_self: bool`: Permission to modify the current user's account details  
`delete_self: bool`: Be able to delete your account. Requires the `"delete_self"` scope so make sure to include that in your token request.

`get_other_users: bool`: Permission to get details on other users

**Room permissions:**  
`join_rooms: bool`: Be able to join chatrooms
`create_rooms: bool` Permission to create rooms. By default this is off and requires a request (put it in the scopes list) when getting an access token.   
See Authentication/Permissions for details on how you can get that permission

**Admin perms**

All of these permissions cannot be access unless you have a admin account. These permissions also canot be requested.

`ban_users: bool`  
`unban_users: bool`    
`create_users: bool`    
`delete_users: bool`  
`update_users: bool`  

---