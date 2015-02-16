

function sendShutter() {
    var side1 = "left"
    var side2 = "right"
    if (Math.random() < .5) {
        side1 = "right";
        side2 = "left"
    }
    doSend({
        command: "shutter",
        side: side1,
        state: "on"
    });
    setTimeout(function() {
        doSend({
            command: "shutter",
            side: side1,
            state: "off"
        });
        setTimeout(function() {
            doSend({
                command: "shutter",
                side: side2,
                state: "on"
            });
            setTimeout(function() {
                doSend({
                    command: "shutter",
                    side: side2,
                    state: "off"
                });

            }, 40);
        }, 40);
    }, 40);
}

function activateShutter() {
    $("#shutterbtn").attr('disabled', false);
    onBeat = $.cas1.shutter;
}

function deactivateShutter() {
    $("#shutterbtn").attr('disabled', true);
    onBeat = function() {};
}
