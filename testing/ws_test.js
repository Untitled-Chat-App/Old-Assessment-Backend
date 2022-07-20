const { WebSocket } = require("ws");
const prompt = require("prompt-sync")();

const access_token = prompt("Enter your access token: ");
const room_id = 648061937;

var ws = new WebSocket(
    `ws://0.0.0.0:443/api/ws/chatroom?access_token=${access_token}&room_id=${room_id}`
);

ws.onmessage = function (event) {
    let msg = event.data;
    while (typeof msg !== "object") {
        msg = JSON.parse(msg);
    }
    if (msg["event"] !== undefined) {
        if (msg["event"] === "User Disconnect") {
            user = JSON.parse(msg["user"]);
            console.log(`${user["username"]} left the chat`);
        }
        if (msg["event"] === "User Join") {
            user = JSON.parse(msg["user"]);
            console.log(`${user["username"]} joined the chat`);
        }
    } else {
        console.log(
            `${msg["message_author"]["username"]}: ${msg["messsage_content"]}`
        );
    }
};

ws.onclose = function (event) {
    console.log(event.reason);
};

ws.onopen = function (event) {
    console.log(event);
    ws.send(
        JSON.stringify({
            message_content: "Test Message",
            access_token: access_token,
        })
    );
};
