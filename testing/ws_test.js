const { WebSocket } = require("ws");

access_token =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGdXNpb25TaWQiLCJleHAiOjE2NTgzNzMwODd9.8AfVopE3TE_T14ThNOjGZn3TgjEcCTQoPuu3f_wzPc4";
room_name = 648061937;

var ws = new WebSocket(
    `ws://0.0.0.0:443/api/ws/chatroom?access_token=${access_token}&room_id=${room_name}`
);

ws.onmessage = function (event) {
    let message = recursive_parse(event.data);
    console.log(message);
};

ws.onclose = function (event) {
    console.log(event.reason);
};

ws.onopen = function (event) {
    ws.send(
        JSON.stringify({ message_content: "hi", access_token: access_token })
    );
};

function recursive_parse(msg) {
    console.log(msg)
    if (typeof (message) === "object") {
        console.log()
        return message;
    }
    message = JSON.parse(msg);
    recursive_parse(message);
}
