var waveData = []; //waveform - from 0 - 1 . no sound is 0.5. Array [binCount]
var levelsData = []; //levels of each frequecy - from 0 - 1 . no sound is 0. Array [levelsCount]
var level = 0; // averaged normalized level from 0 - 1
var bpmTime = 0; // bpmTime ranges from 0 to 1. 0 = on beat. Based on tap bpm
var ratedBPMTime = 550; //time between beats (msec) multiplied by BPMRate
var levelHistory = []; //last 256 ave norm levels
var bpmStart;

var freqByteData; //bars - bar data is from 0 - 256 in 512 bins. no sound is 0;
var timeByteData; //waveform - waveform data is from 0-256 for 512 bins. no sound is 128.
var levelsCount = 16; //should be factor of 512

var binCount = 512;
var levelBins;

var levelHistory = [];

var BEAT_HOLD_TIME = 5; //num of frames to hold a beat
var BEAT_DECAY_RATE = 0.91;
var BEAT_MIN = 0.1; //a volume less than this is no beat
var isPlayingAudio = false;
var count = 0;
var msecsFirst = 0;
var msecsPrevious = 0;
var msecsAvg = 633; //time between beats (msec)

var timer;
var gotBeat = false;
var beatCutOff = 0;
var beatTime = 0;

var source;
var buffer;
var audioBuffer;
var dropArea;
var audioContext;
var analyser;


function audioInit() {

    audioContext = new window.webkitAudioContext();
    freqByteData = new Uint8Array(binCount);
    timeByteData = new Uint8Array(binCount);
    var length = 256;
    for (var i = 0; i < length; i++) {
        levelHistory.push(0);
    }
    levelBins = Math.floor(binCount / levelsCount);
    getMicInput();
}

function getMicInput() {

    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;

    if (navigator.getUserMedia) {

        navigator.getUserMedia(

            {
                audio: true
            },

            function(stream) {

                //reinit here or get an echo on the mic
                source = audioContext.createBufferSource();
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 1024;
                analyser.smoothingTimeConstant = 0.3;

                var microphone = audioContext.createMediaStreamSource(stream);
                microphone.connect(analyser);
                isPlayingAudio = true;
                update();
                // console.log("here");
            },

            // errorCallback
            function(err) {
                alert("The following error occured: " + err);
            }
        );

    } else {
        alert("Could not getUserMedia");
    }
}


function update() {

    if (!isPlayingAudio) return;

    //GET DATA
    analyser.getByteFrequencyData(freqByteData); //<-- bar chart
    analyser.getByteTimeDomainData(timeByteData); // <-- waveform

    //console.log(freqByteData);

    //normalize waveform data
    for (var i = 0; i < binCount; i++) {
        waveData[i] = ((timeByteData[i] - 128) / 128);
    }
    //TODO - cap levels at 1 and -1 ?

    //normalize levelsData from freqByteData
    for (var i = 0; i < levelsCount; i++) {
        var sum = 0;
        for (var j = 0; j < levelBins; j++) {
            sum += freqByteData[(i * levelBins) + j];
        }
        levelsData[i] = sum / levelBins / 256; //freqData maxs at 256

        //adjust for the fact that lower levels are percieved more quietly
        //make lower levels smaller
        //levelsData[i] *=  1 + (i/levelsCount)/2;
    }
    //TODO - cap levels at 1?

    //GET AVG LEVEL
    var sum = 0;
    for (var j = 0; j < levelsCount; j++) {
        sum += levelsData[j];
    }

    level = sum / levelsCount;
    levelHistory.push(level);
    levelHistory.shift(1);

    //BEAT DETECTION
    if (level > beatCutOff && level > BEAT_MIN) {
        onBeat();
        beatCutOff = level * 1.1;
        beatTime = 0;
        $("#beatCheck").addClass("label-danger");
        $("#beatCheck").removeClass("label-default");
    } else {
        if (beatTime <= BEAT_HOLD_TIME) {
            beatTime++;
        } else {
            beatCutOff *= BEAT_DECAY_RATE;
            beatCutOff = Math.max(beatCutOff, BEAT_MIN);
            $("#beatCheck").removeClass("label-danger");
            $("#beatCheck").addClass("label-default");
        }
    }
    $("#beatLevel").css("width", (level*300) + "%");
    requestAnimationFrame(update);
}

var onBeat = function() {}
