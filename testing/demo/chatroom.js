const API_URL = "https://chatapi.fusionsid.xyz"

async function getAccessToken(username = null, password = null) {
    let token;

    // Format login details into query params
    let login_details = new URLSearchParams({
        username: username,
        password: password,
    }).toString();

    await fetch(`${API_URL}/token`, {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: login_details,
    })
        .then((response) => response.json())
        .then((data) => {
            token = data["access_token"];
        });

    return token;
}

async function getRoomById(room_id, access_token) {
    await fetch(`${API_URL}/api/chatroom/${room_id}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access_token}`,
        },
    })
        .then((response) => response.json())
        .then((json_data) => {
            data = json_data;
        });

    return data;
}

var room_data;

window.addEventListener("load", async function (event) {
    var username = prompt("Enter username", username);
    var password = prompt("Enter password", password);
    var room_id = prompt("Enter password", room_id);

    let token = await getAccessToken(username, password)
    room_data = await getRoomById(room_id, token)
    const title = document.querySelector("#room-title-text");
    title.innerHTML = room_data.room_name;

    start(token);
});

function start(access_token) {
    ws = new WebSocket(
        `wss://chatapi.fusionsid.xyz/api/ws/chatroom?access_token=${access_token}&room_id=${room_data.room_id}`
    );

    ws.onmessage = function (event) {
        let msg = event.data;
        var messages = document.getElementById("messages");

        // The div:
        var message = document.createElement("div");
        message.className = "message";

        var message_author_span = document.createElement("span");
        var message_content_span = document.createElement("span");
        var message_time_span = document.createElement("span");

        message_author_span.className = "message-author";
        message_time_span.className = "message-time";
        message_content_span.className = "message-content";

        // Time
        let now = new Date();

        let current_time = new Intl.DateTimeFormat("default", {
            hour12: true,
            hour: "numeric",
            minute: "numeric",
        }).format(now);

        var msgTime = document.createTextNode(current_time);
        message_time_span.appendChild(msgTime);

        // Convert ws response to js object
        while (typeof msg !== "object") {
            msg = JSON.parse(msg);
        }

        if (msg["event"] !== undefined) {
            // On Events
            if (msg["event"] === "User Disconnect") {
                user = JSON.parse(msg["user"]);
                var what_happened = document.createTextNode(
                    `${user["username"]} left the chat`
                );
                message_content_span.style.color = "red";
                message_content_span.appendChild(what_happened);
            }
            if (msg["event"] === "User Join") {
                user = JSON.parse(msg["user"]);
                var what_happened = document.createTextNode(
                    `${user["username"]} joined the chat`
                );
                message_content_span.style.color = "red";
                message_content_span.appendChild(what_happened);
            }
        } else {
            // On normal message:
            var msgAuthor = document.createTextNode(
                msg["message_author"]["username"]
            );
            var msgContent = document.createTextNode(msg["messsage_content"]);

            message_content_span.appendChild(msgContent);
            message_author_span.appendChild(msgAuthor);
        }

        message.appendChild(message_author_span);
        var br = document.createElement("br");
        message.appendChild(br);
        var br = document.createElement("br");
        message.appendChild(br);
        message.appendChild(message_content_span);
        var br = document.createElement("br");
        message.appendChild(br);
        var br = document.createElement("br");
        message.appendChild(br);
        message.appendChild(message_time_span);

        messages.appendChild(message);

        const scrollIntoViewOptions = { behavior: "smooth", block: "center" };
        message.scrollIntoView(scrollIntoViewOptions);
    };

    function sendMessage(event) {
        event.preventDefault();
        var input = document.getElementById("messageText");
        if (
            input.value === null ||
            input.value === undefined ||
            input.value.replace(" ", "") === ""
        ) {
        } else {
            ws.send(
                JSON.stringify({
                    message_content: input.value,
                    access_token: access_token,
                })
            );
        }
        input.value = "";
    }

    const form = document.querySelector("#message-send-div");
    form.addEventListener("submit", sendMessage);
}

/*
How it looks 

<div class="message">
    <span class="message-author"></span>
    <br>
    <br>
    <span class="message-content"></span>
    <br>
    <br>
    <span class="message-time"></span>
</div>
*/
