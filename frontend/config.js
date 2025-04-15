let token = '';
let userId = '';
let channelId = '';
var twitch = window.Twitch.ext;
var ajaxUri = 'https://<YOUR-RAILWAY-APP-URL>.railway.app';
const clientId = "<YOUR-SPOTIFY-CLIENT-ID>";

let authPopup = null;
let popupCheckInterval = null;

var requests = {};

function checkConnectionStatus() {
    if (!token) {
        $('#connectSpotify').show().prop('disabled', false);
        $('#disconnectSpotify').hide().prop('disabled', false);
        return;
    }

    $('#status').text('Checking connection status...').removeClass('error success');

    $.ajax({
        url: ajaxUri + '/spotify/status',
        type: 'GET',
        headers: { 'Authorization': 'Bearer ' + token },
        success: function(response) {
            if (response && response.isConnected) {
                $('#connectSpotify').hide().prop('disabled', false);
                $('#disconnectSpotify').show().prop('disabled', false);
                if (!$('#status').hasClass('error') && !$('#status').text().includes('disconnecting')) {
                     $('#status').text('Connected to Spotify.').removeClass('error').addClass('success');
                }
            } else {
                $('#connectSpotify').show().prop('disabled', false);
                $('#disconnectSpotify').hide().prop('disabled', false);
                 if (!$('#status').hasClass('error') && !$('#status').text().includes('disconnect')) {
                     $('#status').text('Not connected to Spotify.').removeClass('success error');
                 }
            }
        },
        error: function(xhr, status, error) {
            let errorMsg = "Could not check status";
             try {
                const errData = JSON.parse(xhr.responseText);
                errorMsg = errData.error || errData.message || status;
             } catch(e) {

             }
            $('#status').text('Error checking status: ' + errorMsg).removeClass('success').addClass('error');
            $('#connectSpotify').show().prop('disabled', false);
            $('#disconnectSpotify').hide().prop('disabled', false);
        }
    });
}

$(document).ready(function() {
    $('#connectSpotify').click(function() {
        if (!token) {
            $('#status').text('Error: Twitch authorization token not found. Please refresh.').addClass('error');
            return;
        }

        
        const redirectUri = ajaxUri + '/spotify/auth_callback';
        const scope = 'user-read-currently-playing user-read-playback-state';
        const authUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}&show_dialog=true&state=${token}`;

        $('#status').text('Redirecting to Spotify...').removeClass('error success');
        $('#connectSpotify').prop('disabled', true);

        authPopup = window.open(authUrl, 'Spotify Authorization', 'width=500,height=600');

        if (popupCheckInterval) {
            clearInterval(popupCheckInterval);
        }

        popupCheckInterval = setInterval(function() {
            if (authPopup && authPopup.closed) {
                clearInterval(popupCheckInterval);
                popupCheckInterval = null;
                authPopup = null;

                $('#connectSpotify').prop('disabled', false);
                $('#disconnectSpotify').prop('disabled', false);

                checkConnectionStatus();

            } else if (!authPopup && popupCheckInterval) {
                 clearInterval(popupCheckInterval);
                 popupCheckInterval = null;
                 $('#connectSpotify').prop('disabled', false);
                 $('#status').text('Failed to open Spotify window.').addClass('error');
            }
        }, 500);
    });

    $('#disconnectSpotify').click(function() {
        if (!token) {
             $('#status').text('Error: Twitch authorization token not found. Please refresh.').addClass('error');
             return;
        }
        $('#status').text('Disconnecting...').removeClass('error success');
        $('#disconnectSpotify').prop('disabled', true);

        $.ajax({
            url: ajaxUri + '/spotify/disconnect',
            type: 'POST',
            headers: { 'Authorization': 'Bearer ' + token },
            success: function(response) {
                $('#status').text('Successfully disconnected from Spotify').removeClass('error').addClass('success');
                $('#connectSpotify').show().prop('disabled', false);
                $('#disconnectSpotify').hide().prop('disabled', false);
            },
            error: function(xhr, status, error) {
                let errorMsg = xhr.responseText || error || "Unknown error";
                 try {
                   const errData = JSON.parse(xhr.responseText);
                   errorMsg = errData.error || errData.message || errorMsg;
                } catch(e) { }
                $('#status').text('Error disconnecting: ' + errorMsg).removeClass('success').addClass('error');
                $('#disconnectSpotify').prop('disabled', false);
                checkConnectionStatus();
            }
        });
    });

    window.addEventListener('message', function(event) {
        const expectedOrigin = new URL(ajaxUri).origin;
        if (event.origin !== expectedOrigin) {
           $('#connectSpotify').prop('disabled', false);
           return;
        }

        if (event.data && event.data.type === 'spotifyAuthSuccess') {
            $('#status').text('Successfully connected! Updating status...').removeClass('error').addClass('success');

            if (popupCheckInterval) {
                clearInterval(popupCheckInterval);
                popupCheckInterval = null;
            }

            if (authPopup && !authPopup.closed) {
                 authPopup.close();
                 authPopup = null;
            }

            $('#connectSpotify').prop('disabled', false);
            $('#disconnectSpotify').prop('disabled', false);
            checkConnectionStatus();

        } else {
             const errorMessage = event.data?.error || "Unknown message type/error received from popup.";
             $('#status').text('Error: ' + errorMessage).removeClass('success').addClass('error');
             $('#connectSpotify').prop('disabled', false);
             $('#disconnectSpotify').prop('disabled', false);
             checkConnectionStatus();
        }
    }, false);

    checkConnectionStatus();
});

twitch.onContext(function(context) { });

twitch.onAuthorized(function(auth) {
    token = auth.token;
    userId = auth.userId;
    channelId = auth.channelId;

    checkConnectionStatus();
});