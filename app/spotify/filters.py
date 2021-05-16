
def playlists(response):
    """ Extract only required fields from user playlists Spotify API response.
    """
    items = response["items"]
    return {
        item["name"]: {
            "id": item["id"],
            "ntracks": item["tracks"]["total"]
        }
        for item in items
        if item["name"].startswith("EEG-")
    }

def playback_info(playback_info):
    """ Extract only the required info from Spotify API response.
    """
    return {
        "artists":      playback_info["item"]["artists"][0]["name"],
        "song":         playback_info["item"]["name"],
        "uri":           playback_info["item"]["uri"],
        "popularity":   playback_info["item"]["popularity"],
        "album":        playback_info["item"]["album"]["name"],
        "released":     playback_info["item"]["album"]["release_date"],
        "duration":     playback_info["item"]["duration_ms"] // 1000,
        "progress":     playback_info["progress_ms"] // 1000
    }

