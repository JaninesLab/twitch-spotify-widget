var token = "";
var tuid = "";
var lastUpdate = 0;
var refreshRate = 20000;

var ajaxUri = 'https://<YOUR-RAILWAY-APP-URL>.railway.app';
var twitch = window.Twitch.ext;

var requests = {
    get: createRequest('GET', 'data')
};

let currentSong = null;
let history = [];


function createRequest(type, method) {
    return {
        type: type,
        url: ajaxUri + '/spotify/' + method,
        success: updateData,
        headers: {},
        error: function (xhr, status, error) {
            twitch.rig.log('NowPlayingWidget: Error: EBS request returned ' + status + ' (' + error + ')');
            displayError("Could not retrieve song data.");
        }
    };
}

function setAuth(token) {
    Object.keys(requests).forEach((req) => {
        requests[req].headers = { 'Authorization': 'Bearer ' + token };
    });
}

function doUpdate() {
    if (lastUpdate + 10000 <= Date.now()) {
        lastUpdate = Date.now();
        $.ajax(requests.get)
          .done(function(data, textStatus, jqXHR) {
              updateData(data);
          })
          .fail(function(jqXHR, textStatus, errorThrown) {
              displayError("Could not retrieve song data.");
          });
    }
}

function updateData(data) {
    if (!data) {
        displayError("No data from server.");
        return;
    }

    try {
        $('#extNotConfigured').toggle(data.extNotConfigured ? true : false);

        if (data.item) {
            const songUrl = data.item.external_urls?.spotify || "#";
            const artistUrl = data.item.artists?.[0]?.external_urls?.spotify || "https://open.spotify.com";

            const newSong = {
                title: data.item.name || "Unknown Title",
                artist: data.item.artists?.[0]?.name || "Unknown Artist",
                cover: data.item.album?.images?.[0]?.url || "na.png",
                duration: data.item.duration_ms || 0,
                url: songUrl,
                artist_url: artistUrl
            };

            if (currentSong && (newSong.title !== currentSong.title)) {
                history.unshift({
                    title: currentSong.title,
                    artist: currentSong.artist,
                    cover: currentSong.cover,
                    url: currentSong.url,
                    artist_url: currentSong.artist_url
                });
                if (history.length > 3) history.pop();
                renderHistory();
            }

            currentSong = newSong;

            $('.now-playing-link').attr('href', newSong.url);
            $('.now-playing-link').attr('href', newSong.url).attr('target', '_blank');
            $('#nowPlaying .front').attr('src', newSong.cover);
            $('#songTitle').text(newSong.title);
            $('#artist').text(newSong.artist);
            $('#artist').attr('href', newSong.artist_url);
            $('#nowPlaying').show();

        } else {
            displayNoSong();
        }

    } catch (e) {
        twitch.rig.log('NowPlayingWidget: error processing data: ' + e.message);
        displayError("Could not update song information.");
    }
}

function displayNoSong() {
    $('.now-playing-link').attr('href', 'https://open.spotify.com').removeAttr('target');
    $('#nowPlaying .front').attr('src', 'na.png');
    $('#songTitle').text('No song is playing...');
    $('#artist').text('Waiting...').attr('href', '#').removeAttr('target');
    $('#nowPlaying').show();
}

function displayError(message) {
    $('#songTitle').text(message);
    $('#artist').text('').attr('href', '#').removeAttr('target');
    $('.now-playing-link').attr('href', '#').removeAttr('target');
    $('#nowPlaying .front').attr('src', 'na.png');
    $('#nowPlaying').show();
}

function renderHistory() {
    const $historyDiv = $('#history');
    $historyDiv.empty();

    history.forEach((song, index) => {
        const $link = $('<a>', {
            href: song.url || '#',
            target: '_blank',
            class: 'history-link'
        });

        const $item = $('<div class="history-item">');

        const $flipContainer = $('<div class="flip-container">');
        const $flipper = $('<div class="flipper">');
        const $frontImg = $('<img>', {
            class: 'front',
            src: song.cover || 'na.png',
            alt: 'Cover'
        });
        const $backImg = $('<img>', {
            class: 'back',
            src: 'spotify.png',
            alt: 'Spotify Logo'
        });

        $flipper.append($frontImg, $backImg);
        $flipContainer.append($flipper);

        const $songInfo = $('<div class="song-info">');
        const $title = $('<b>').text(song.title || 'Unknown Title');
        const $artist = $('<div>').text(song.artist || 'Unknown Artist');

        $songInfo.append($title, $artist);
        $item.append($flipContainer, $songInfo);
        $link.append($item);
        $historyDiv.append($link);

        setTimeout(() => $item.css({
            opacity: 1,
            transform: 'translateY(0)'
        }), index * 100);
    });
}

twitch.onContext(function(context) {
    twitch.rig.log(context);
});

twitch.onAuthorized(function(auth) {
    token = auth.token;
    tuid = auth.userId;
    setAuth(token);
    doUpdate();
    setInterval(doUpdate, refreshRate);
});