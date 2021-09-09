# CHANGELOG

Here you will find description of what changed in each version of the project.
Versions will roughly correspond to git tags.


## v0.X

The goal of this milestone will be to have a stable, ready-to-use version of a data collection app.

### v0.2 [work in progress]

In this version the goal is to make the app more stable and resistant to failures, by adding unit tests
which are required since the app has reached the point where its difficult to keep track of everything,
as well as refactoring in parallel with testing to make testing easier.

    1. Removed /mark/<label> and /muse/plot commands from the app.

### v0.1

This version marks the point where it is possible to use the app, through the command line interface
of cli.py script to perform recording of labeled data.

    1. App can connect to Muse specified in the configuration.
    2. Server manages configuration and passess it to the client.
    3. Spotify API connection is possible.
    4. Data can be exported into a json file with playback info, timestamps, and eeg signal encoded in base64.
    5. GUI client is unstable, incomplete and generally not recommended.
        May be replaced in the future with a new version, or with a web client.
    6. Exported data can now be viewed using server/viewer.py script which uses matplotlib to plot the EEG signal against recorded timestamps.
        Experimental validation has been performed to verify that the marked timestamps are valid using the labeling timestamp and a forced eye blinking pattern.
    7. Note that the start timestamp, as well as the end timestamp may be offset by up to 1 second + network delay from the actual start / end of the item playback,
        due to the nature of playback change detection procedure, which requires repeatedly polling spotify API for current playback and 'active' change detection.

