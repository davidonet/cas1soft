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
    $.cas1.fadeout = function() {
        doSend({
            command: "fadeout"
        });
    }
});


function collectionReceived(msg) {
    var aCol = msg.collection;
    for (var i = aCol.length - 1; i >= 0; i--) {
        var anAct = aCol[i];
        var $actElt = $("<div><h1>Acte " + anAct.act + "</h1></div>");
        $('#trace').prepend($actElt)
        for (var j = 0; j < anAct.tracks.length; j++) {
            var aTrack = anAct.tracks[j];
            var $trkElt = $("<div><h2><a class='btn btn-info btn-sm '><span class='glyphicon glyphicon-play'/></a> Piste " + aTrack.track + "</h2></div>");
            $actElt.append($trkElt);
            var ahtmlTab = "<table class='table table-bordered'><thead><tr><th>&nbsp;</th><th>Gauche</th><th>Droite</th></tr></thead><tbody>";
            ahtmlTab += "<tr><td>Durée totale</td><td>" + Math.floor(aTrack.duration_left / 1000) + "s</td><td>" + Math.floor(aTrack.duration_right / 1000) + "s</td></tr>";
            for (var k = 0; k < aTrack.videos_left.length; k++) {
                aplay = "onclick=playVideo(" + (anAct.act - 1) + "," + j + "," + k + ")";
                ahtmlTab += "<tr><td><a class='btn btn-success btn-xs' " + aplay + "><span class='glyphicon glyphicon-play'/></a> Sequence : " + aTrack.videos_left[k].sequence + "</td><td>" + aTrack.videos_left[k].name + "<br/>" + Math.floor(aTrack.videos_left[k].duration / 1000) + "s </td>"
                ahtmlTab += "<td>" + aTrack.videos_right[k].name + "<br/>" + Math.floor(aTrack.videos_right[k].duration / 1000) + "s </td></tr>";
            }
            ahtmlTab += "</tbody></table>";
            $trkElt.append(ahtmlTab);
        }
    }
}


function playVideo(act, trk, seq) {
    callback_fade = function() {
        doSend({
            command: "play",
            actidx: act,
            trackidx: trk,
            sequenceidx: seq,
            fadeout: $("#fadeout").prop('checked')
        });
        callback_fade = function() {};
    };
    if ($("#fadeout").prop('checked')) {
        doSend({
            command: "fadeout"
        });
    } else {
        callback_fade();
    }
}

function endReached(msg) {
    $("#left_progress").css("width", 0 + "%");
    $("#left_time").text(zeroFill(0, 4));
    $("#left_length").text(zeroFill(0, 4));
    $("#left_title").text("");
    $("#right_progress").css("width", 0 + "%");
    $("#right_time").text(zeroFill(0, 4));
    $("#right_length").text(zeroFill(0, 4));
    $("#right_title").text("");
}
