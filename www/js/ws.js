function zeroFill(number, width) {
    width -= number.toString().length;
    if (width > 0) {
        return new Array(width + (/\./.test(number) ? 2 : 1)).join('0') + number;
    }
    return number + ""; // always return a string
}

function doConnect(onOpen) {
    websocket = new WebSocket("ws://localhost:8888/");
    websocket.onopen = onOpen;
    websocket.onclose = function(evt) {
        onClose(evt)
    };
    websocket.onmessage = function(evt) {
        onMessage(evt)
    };
    websocket.onerror = function(evt) {
        onError(evt)
    };
}


function onClose(evt) {
    writeToScreen("disconnected\n");
}

function onMessage(evt) {
    msg = JSON.parse(evt.data);
    if (msg.left_screen) {
        $("#left_progress").css("width", msg.left_screen.pos + "%");
        $("#left_time").text(zeroFill(msg.left_screen.time, 4));
        $("#left_length").text(zeroFill(msg.left_screen.length, 4));
        title = msg.left_screen.mrl.split("/");
        $("#left_title").text(title[title.length - 1]);
    }
    if (msg.right_screen) {
        $("#right_progress").css("width", msg.right_screen.pos + "%");
        $("#right_time").text(zeroFill(msg.right_screen.time, 4));
        $("#right_length").text(zeroFill(msg.right_screen.length, 4));
        title = msg.right_screen.mrl.split("/");
        $("#right_title").text(title[title.length - 1]);
    }
    if (msg.collection) {
        console.log(msg);
        collectionReceived(msg);
    }
    if (msg.fadefinished) {
        console.log(msg);
        callback_fade();
    }
    if (msg.endreached) {
        console.log(msg);
        endReached(msg);
    }
}

function onError(evt) {
    writeToScreen('error: ' + evt.data + '\n');
    websocket.close();
}

function doSend(message) {
    msg = JSON.stringify(message);
    writeToScreen("sent: " + msg + '\n');
    websocket.send(msg);
}

function doDisconnect() {
    websocket.close();
}

function writeToScreen(message) {
    console.log(message)
}
