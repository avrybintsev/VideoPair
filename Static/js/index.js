window.requestAnimFrame = function () {
    return (
        window.requestAnimationFrame ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            window.oRequestAnimationFrame ||
            window.msRequestAnimationFrame ||
            function (/* function */ callback) {
                window.setTimeout(callback, 1000 / 60);
            }
        );
}();

var videos = [],
    videos_el = [],

    progress_total = total * 2,
    progress_current = 0,
    controls = {
        loader: $("#loader-block"),
        finish: $("#finish-block"),
        progress_block: $("#progress-block"),
        begin_block: $("#begin-block"),
        begin_button: $("#begin-button"),
        progress: $("#progress"),
        progress_total: $("#progress-total"),
        progress_current: $("#progress-current"),
        questions: []
    },

    progress = {},
    current = -1,

    retries = 0,
    max_retries = 10;

for (var i=0; i < total; i++) {
    videos_el.push({
        left: $("#player-video-left"+i)[0],
        right: $("#player-video-right"+i)[0]
    });
    videos.push({
        left: Popcorn("#player-video-left"+i),
        right: Popcorn("#player-video-right"+i)
    });
    controls.questions.push($("#question"+i));
}

update_progress = function() {
    var progress_percent = Math.round((progress_current / progress_total) * 100);
    controls.progress.attr("aria-valuemax", progress_total);
    controls.progress.attr("aria-valuenow", progress_current);
    controls.progress.css("width", progress_percent+"%");
    controls.progress_total.text(progress_total);
    controls.progress_current.text(progress_current);
};

load_video = function(element, mp4_path, webm_path) {
    var r = new XMLHttpRequest();
    r.onload = function() {
        element.src = URL.createObjectURL(r.response);
        //console.log("loaded!" + element.id);
    };
    r.onerror = function() {
        console.log("error");
        retries++;
        if (retries < max_retries) {
            setTimeout(function () {load_video(element, mp4_path, webm_path);}, 500);
        }
    };
    if (element.canPlayType('video/mp4')) {
        r.open("GET", mp4_path);
    }
    else {
        r.open("GET", webm_path);
    }
    r.responseType = "blob";
    r.send();
};

next_question = function () {
    if (current >= 0) {
        controls.questions[current].hide();
    }
    current++;
    if (current < total) {
        sync();
        controls.questions[current].show();
        videos[current].left.play();
    } else {
        controls.finish.show();
    }
};

on_success = function (data) {
    var status_object = $.parseJSON(data);
    if (status_object.status == "ok") {
        //console.log("ok");
        next_question();
    } else {
        //console.log("error");
    }
};

prepare = function() {
    videos.forEach(function (video) {
        var event = "play";
        video.left.on(event, function () {
            video.right[ event ]();
        });
    });

    $(".answer-form").ajaxForm({url: '/ans', type: 'post', success: on_success});

    controls.begin_button.click(function () {
        controls.loader.hide();
        next_question();
    });

    controls.progress_block.hide();
    controls.begin_block.show();
};

videos.forEach(function (video) {
    Popcorn.forEach(video, function (media, type) {
        progress[media.id] = false;
        media.on("canplayall",function () {
            //console.log("canplayall" + media.id);
            progress[media.id] = true;
            progress_current++;
            update_progress();
            if (Object.keys(progress).every(function(key){ return progress[key] })) {
                //console.log("start playing!");
                prepare();
            }
        })
    });
});

function sync() {
    if ((current < total) && (videos[current].right.media.readyState === 4 )) {
        left_time = videos[current].left.currentTime();
        right_time = videos[current].right.currentTime();
        if (Math.abs(left_time - right_time) > 0.1) {
            videos[current].right.currentTime(left_time);

        }
    }
    requestAnimFrame( sync );
}