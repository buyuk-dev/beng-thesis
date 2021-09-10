""" 2021 Created by michal@buyuk-dev.com
"""


def playlists(response):
    """Extract only required fields from user playlists Spotify API response."""
    items = response["items"]
    return {
        item["name"]: {"id": item["id"], "ntracks": item["tracks"]["total"]}
        for item in items
        if item["name"].startswith("EEG-")
    }


def playback_info(info):
    """Extract only the required info from Spotify API response."""
    return {
        "artists": info["item"]["artists"][0]["name"],
        "song": info["item"]["name"],
        "uri": info["item"]["uri"],
        "popularity": info["item"]["popularity"],
        "album": info["item"]["album"]["name"],
        "released": info["item"]["album"]["release_date"],
        "duration": info["item"]["duration_ms"] // 1000,
        "progress": info["progress_ms"] // 1000,
    }
