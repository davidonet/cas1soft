$(function() {

    $.cas1 = [];

    $.cas1.init = function() {
        doConnect(function() {
            doSend({
                command: "init"
            });
        });
    };
    $.cas1.start = function() {
        doSend({
            command: "play",
            prefix: "/opt/storage/CAS1_SRC/ACTE 4/A4-P1/CAS1_A4P1V20"
        });
    }
});
