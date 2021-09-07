# Extracting User Preferences From Brain Signal Using Muse EEG

TODO: add project overview.

## Installation

Currently official muse-lsl package doesn't support bleak backend, which it doesn't work
on MacOS. There is however a fork of muse-lsl created by xloem, to which i'm contributing as well,
which implements bleak backend. Bleak backend can also be used on all other platforms as well,
and may replace other backends in the future muse-lsl development.

The official version:
https://github.com/alexandrebarachant/muse-lsl

Fork with bleak backend:
https://github.com/xloem/muse-lsl

The following commands will install xloem muse-lsl:
    
    git clone git@github.com:xloem/muse-lsl.git
    cd muse-lsl
    python -m pip install -e .

Additional requirements for this project can be installed using requirements.txt file in this repo:

    python -m pip install  -f requirements.txt

Currently I'm only supporting MacOS actively, I may add instructions for other systems in the future.

## Setup

Create a ./server/secret.py script and add the following entries:
If you're on MacOS you don't need MUSE_MAC_ADDRESS entry, as MacOS uses UUIDs instead.
Spotify API tokens can be acquired as described on [this page](https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app)
 
    MUSE_MAC_ADDRESS="{YOUR MUSE MAC ADDRESS}"
    MUSE_UUID_ADDRESS="{YOUR MUSE UUID ADDRESS}"
    SPOTIFY_CLIENT_ID="{YOUR SPOTIFY API CLIENT_ID}"
    SPOTIFY_CLIENT_SECRET="{YOUR SPOTIFY API CLIENT_SECRET}"

Run configuration.py script to create ./server/config/ directory with default config files.

    python configuration.py

## Usage

The app is split into server and client part. To run it, first start the server, than use client
to control the session.

### Server

Run server with the following command:

    python server.py


### Client

Client is run using cli.py script, which has the following options:

    python cli.py [-h] {config,spotify,muse,session} ...

    positional arguments:
      {config,spotify,muse,session}

    optional arguments:
      -h, --help            show this help message and exit

Session command can be used like:

    python cli.py session [-h] {start,stop,label} ...

    positional arguments:
      {start,stop,label}

    optional arguments:
      -h, --help          show this help message and exit

Spotify command can be used like:

    python cli.py spotify [-h] {connect,playback,mark} ...

    positional arguments:
      {connect,playback,mark}

    optional arguments:
      -h, --help            show this help message and exit

Muse command can be used like:

    python cli.py muse [-h] {connect,disconnect,start,stop,plot} ...

    positional arguments:
      {connect,disconnect,start,stop,plot}

    optional arguments:
      -h, --help            show this help message and exit

Config command can be used like:

    python cli.py config [-h] {show,update} ...

    positional arguments:
      {show,update}

    optional arguments:
      -h, --help     show this help message and exit

In general session setup looks like this:

    python cli.py muse connect
    python cli.py spotify connect
    // Wait until Muse is connected
    python cli.py muse start
    python cli.py session start

A script `client/start_session.sh` does this automatically.
