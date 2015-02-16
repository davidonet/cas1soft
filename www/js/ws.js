function zeroFill(number, width) {
    width -= number.toString().length;
    if (width > 0) {
        return new Array(width + (/\./.test(number) ? 2 : 1)).join('0') + number;
    }
    return number + ""; // always return a string
}

function doConnect(onOpen) {
    websocket = new WebSocket("ws://" + window.location.hostname + ":8888/");
    websocket.onopen = onOpen;
    websocket.onclose = function(evt) {
        onClose(evt);
    };
    websocket.onmessage = function(evt) {
        onMessage(evt);
    };
    websocket.onerror = function(evt) {
        onError(evt);
    };
}


function onClose(evt) {
    writeToScreen("disconnected\n");
}

function onMessage(evt) {
    msg = JSON.parse(evt.data);
    $.cas1.msg = msg;

    if (typeof msg.actidx !== 'undefined') {
        updateUI(msg);
    }

    if (msg.collection) {
        collectionReceived(msg);
    }
    if (msg.fadefinished) {
        callback_fade();
    }
    if (msg.endreached) {
        endReached(msg);
    }
}

function onError(evt) {
    writeToScreen('error: ' + evt.data + '\n');
    websocket.close();
}

function doSend(message) {
    msg = JSON.stringify(message);
    //writeToScreen("sent: " + msg + '\n');
    websocket.send(msg);
}

function doDisconnect() {
    websocket.close();
}

function writeToScreen(message) {
    console.log(message);
}


function updateUI(msg) {

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

    $("#cur_act").text("Acte " + (msg.actidx + 1));
    $("#cur_track").text("Piste " + (msg.trackidx + 1));
    var totalleft = Math.floor(theCollection[msg.actidx].tracks[msg.trackidx].duration_left / 1000);
    var totalright = Math.floor(theCollection[msg.actidx].tracks[msg.trackidx].duration_right / 1000);
    if (totalright < totalleft) {
        var timeplayed = msg.left_screen.time;
        for (var i = 0; i < msg.sequenceidx; i++) {
            timeplayed += Math.floor(theCollection[msg.actidx].tracks[msg.trackidx].videos_left[i].duration / 1000);
        };
        var remain = totalleft - timeplayed;
        $("#track_progress").css("width", 100 * (timeplayed / totalleft) + "%");
    } else {
        var timeplayed = msg.right_screen.time;
        for (var i = 0; i < msg.sequenceidx; i++) {
            timeplayed += Math.floor(theCollection[msg.actidx].tracks[msg.trackidx].videos_right[i].duration / 1000);
        };
        var remain = totalright - timeplayed;
        $("#track_progress").css("width", 100 * (timeplayed / totalright) + "%");
    }
    $("#cur_track_remain").text(Math.floor(remain / 60) + " min " + (remain % 60));
}

function collectionReceived(msg) {
    theCollection = msg.collection;
    var aCol = theCollection;
    for (var i = aCol.length - 1; i >= 0; i--) {
        var anAct = aCol[i];
        var $panel = $("<div class='row'></div>");
        var $actElt = $("<div class='panel panel-primary'><div class='panel-heading'><h2 style='margin-top:0;margin-bottom:0'>Acte " + anAct.act + "</h2></div></div>");
        $('#trace').prepend($panel);
        $panel.append($actElt);
        for (var j = 0; j < anAct.tracks.length; j++) {
            var aTrack = anAct.tracks[j];
            aplayact = "onclick=playVideo(" + (anAct.act - 1) + "," + j + "," + 0 + ")";
            var $trkElt = $("<div class='panel-body'><h3 ><a class='btn btn-info btn-sm' " + aplayact + "><span class='glyphicon glyphicon-play'/></a> Piste " + aTrack.track + "</h3></div>");
            $actElt.append($trkElt);
            var ahtmlTab = "<table class='table table-bordered'><thead><tr><th>&nbsp;</th><th>Gauche</th><th>Droite</th></tr></thead><tbody>";
            ahtmlTab += "<tr><td>Durée totale</td><td>" + Math.floor(aTrack.duration_left / 1000) + "s</td><td>" + Math.floor(aTrack.duration_right / 1000) + "s</td></tr>";
            for (var k = 0; k < aTrack.videos_left.length; k++) {
                aplayseq = "onclick=playVideo(" + (anAct.act - 1) + "," + j + "," + k + ")";
                ahtmlTab += "<tr><td><a class='btn btn-success btn-xs' " + aplayseq + "><span class='glyphicon glyphicon-play'/></a> Sequence : " + aTrack.videos_left[k].sequence + "</td>";
                ahtmlTab += "<td>" + aTrack.videos_left[k].name + "<br/>" + Math.floor(aTrack.videos_left[k].duration / 1000) + "s </td>";
                ahtmlTab += "<td>" + aTrack.videos_right[k].name + "<br/>" + Math.floor(aTrack.videos_right[k].duration / 1000) + "s </td></tr>";
            }
            ahtmlTab += "</tbody></table>";
            $trkElt.append(ahtmlTab);
        }
    }
    $("#analyzebox").modal('hide');
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
    if ($("#playnext").prop('checked')) {
        if (msg.sequenceidx < theCollection[msg.actidx].tracks[msg.trackidx].videos_left.length - 1) {
            $("#fadeout").attr("checked", false);
            setTimeout(function() {
                playVideo(msg.actidx, msg.trackidx, msg.sequenceidx + 1);
            }, 250);
        }
    }
}
