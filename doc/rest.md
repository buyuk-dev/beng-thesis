# Data Collection Server REST API Documentation


## Configuration

GET /user/<userid>/config
POST /user/<userid>/config


## Spotify

### GET /spotify/connect

Use this request to connect app to the spotify account. Server will open the
browser window which may ask you to log in to your Spotify account. If authentication
is successful, Spotify will send the access token to the /callback endpoint.

Responses:

    HTTP 200
    {
    }


### GET /spotify/status

Check if access token exists for Spotify API.
**Current implementation does not check if the token has expired.**

Responses:

    HTTP 200
    {
        "status": <true if token exists, false otherwise>
    }


### GET /spotify/playback

Retrieve current playback info from Spotify.

Responses:

1. Unauthorized (access token not available)

    HTTP 401
    {
        "error": "Spotify not authorized."
    }    

2. Failed to get playback info

    HTTP 400
    {
        "error": "Failed to get current playback info from Spotify."
    } 

3. Nothing is playing right now

    HTTP 200
    {
    }

4. Success

    HTTP 200
    {
        "artists": <first artist name>,
        "song": <song title>,,
        "uri": <song uri>,
        "popularity": <populatiry metric>,
        "album": <album name>, 
        "released": <album release date> 
        "duration": <duration in seconds>,
        "progress": <playback progress in seconds>
    }


### CALLBACK /callback

This is a special endpoint used to receive authorization token after
authenticating with Spotify. It's not really part of the API, but it needs to
be configured in the app settings in the project settings on Spotify Developer.

Authorization flow:

1. Spotify should send a HTTP GET request to this endpoint once user authorizes the app.
2. Once we receive the `auth_code` from Spotify, server attempts to request API token.
3. If token was retrieved it is stored in the server's configuration.
4. If token was not retrieved an error is reported and authorization fails.
3. If authorization was successful, server requests user's profile info.
4. If user's profile was received, server requests access to user's playlist.


## Muse

### GET /muse/connect/<address>

Request connection attempt to the configured Muse device.
Currently <address> argument is ignored, instead the device specified
in the server's configuration will be used.

If the request is successful, the Muse should be connected, and LSL stream
will be setup. After this its possible to use tools like "muselsl view" etc.

Responses:

    HTTP 200
    {
    }


### GET /muse/start

Connect to the LSL stream and start processing data.
TODO: Not sure if this makes sense, perhaps its best to just merge it with /muse/connect.

Responses:

1. Success

    HTTP 200
    {
    }

2. Muse is not connected

    HTTP 400
    {
        "error": "Muse needs to be connected before streaming is possible."
    }


### GET /muse/stop

Disconnects from the LSL stream and stops data processing. Muse is still connected
and LSL stream still exists. The app is just not using it anymore.

Responses:

1. Success

    HTTP 200
    {
    }

2. Muse is not connected

    HTTP 400
    {
        "error": "Muse is not connected."
    }


### GET /muse/disconnect

Disconnects from Muse device. Destroys the LSL stream.

Responses:

1. Success

    HTTP 200
    {
    }

2. Muse is not connected

    HTTP 400
    {
        "error": "Muse is not connected."
    }


### GET /muse/status

Returns Muse connection status.

Responses:

    HTTP 200
    {
        "stream": <true if muse is connected and lsl stream exists | false otherwise>
        "collector": <ture if app is connected to the lsl stream and processing is running | false otherwise>
    }


### /muse/plot

DEPRECATED, will be removed in the future versions.

Shows real time Muse EEG signal plot. Blocks until plot is closed.
It is better to view the signal using other means, like `muselsl view` command.

Responses:

1. LSL stream not connected.

    HTTP 400
    {
        "error": "Data collector is not set."
    }

2. Success (after closing the matplotlib window)

    HTTP 200
    {
    }


## Session

### /session/start

Initialize data collection session.

Responses:

1. Success

    HTTP 200
    {
    }

2. Spotify unauthorized

    HTTP 400
    {
        "error": "Spotify access token unavailable. Connect to Spotify."
    }

3. Muse not connected

    HTTP 400
    {
        "error": "Muse is not connected. Connect to Muse."
    }

4. LSL stream not connected

    HTTP 400
    {
        "error": "Data collection needs to be started first."
    }


### /session/stop

Stop data collection session.

Responses:

1. Success

    HTTP 200
    {
    }

2. No active session

    HTTP 400
    {
        "error": "No active session exists."
    }


### /session/label/<label>

Label current playback with the given label.

Responses:

1. Success

    HTTP 200
    {
    }

2. No active session

    HTTP 400
    {
        "error": "No active session exists."
    }


## Other

### /mark/<value>

DEPRECATED, will be removed in the future versions.

Labels current song as
Session commands should be used instead.
