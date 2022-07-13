const rsa = require("node-rsa")

function generateKeyPair(){
    var key = new rsa().generateKeyPair();

    var publicKey = key.exportKey("public")
    var privateKey = key.exportKey("private")
    console.log(JSON.stringify(publicKey))
}

generateKeyPair()