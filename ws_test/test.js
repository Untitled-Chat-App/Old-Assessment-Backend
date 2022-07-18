const {WebSocket} = require("ws")

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGdXNpb25TaWQiLCJleHAiOjE2NTgxODk0OTh9._-hhWKSbJW1bHkfjGjF5_yNkuoqWIyiuY8Ae3Ic2tTw"
room_name = "e"

var ws = new WebSocket(`ws://0.0.0.0:443/api/ws/chatroom?access_token=${access_token}&room_name=${room_name}`);
ws.onmessage = function (event) {
    console.log(event.data)
};
