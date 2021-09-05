# This is a typical recording session scenario for a data collection app:

1. Start the server.
2. Start the client.
3. Connect Spotify.
4. Connect Muse.
5. Start collecting Muse data.
6. Play song on Spotify.
7. When app detects a change in playback info the **start timestamp** is set for the current item.
8. User listens to the song with Muse on their head.
9. User decides what they think about the current song and labels it with an adequate label {like, dislike, meh}.
10. **Labeling timestamp** is set for the current item.
11. Labeled song is added to the Spotify playlist corresponding to the label it was assigned by the user.
12. User can listen to the remaining portion of the song, or skip to the next one.
13. When the app detects playback change, it sets the **end timestamp** for the finished item.
14. After the end timestamp has been set, the collected data frame is exported to the json file.
15. New playback item is initialized.
