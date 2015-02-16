$(function() {

    $.cas1 = [];

    doConnect(function() {
        doSend({
            command: "init"
        });
    });

    $.cas1.start = function() {
        $("#fadeout").attr("checked", false);
        playVideo(0, 0, 0);
    };

    $.cas1.restart = function() {
        playVideo($.cas1.msg.actidx, $.cas1.msg.trackidx, $.cas1.msg.sequenceidx)
    };

    $.cas1.pause = function() {
        doSend({
            command: "pause",
        });
    };

    $.cas1.next = function() {
        if ($.cas1.msg.sequenceidx < theCollection[$.cas1.msg.actidx].tracks[$.cas1.msg.trackidx].videos_left.length - 1)
            playVideo($.cas1.msg.actidx, $.cas1.msg.trackidx, $.cas1.msg.sequenceidx + 1)
    };

    $.cas1.nextact = function() {
        if ($.cas1.msg.actidx < theCollection.length - 1) {
            var track = 0;
            if ($("#randomtrack").prop('checked'))
                track = Math.floor(Math.random() * theCollection[$.cas1.msg.actidx + 1].tracks.length)
            playVideo($.cas1.msg.actidx + 1, track, 0);
        }

    };
    $.cas1.shutter = function() {
        sendShutter();
    };

    $("#playnext").prop('checked', true);
    $("#randomtrack").prop('checked', true);
    $("#shutterbtn").attr('disabled', true);
    $("#fadeout").attr("checked", false);

    audioInit();

    $("#analyzebox").modal('show');
});

function playVideo(act, trk, seq) {
    callback_fade = function() {

        doSend({
            command: "play",
            actidx: act,
            trackidx: trk,
            sequenceidx: seq,
            shutter: ((act == 4) && (seq == 0))
        });

        if ((act == 4) && (seq == 0))
            activateShutter();
        else
            deactivateShutter();

        $("#fadeout").attr("checked", false)

        callback_fade = function() {};

        $('html, body').animate({
            scrollTop: 0
        });
    };

    if ($("#fadeout").prop('checked')) {
        doSend({
            command: "fadeout"
        });
    } else {
        callback_fade();
    }
}
