import requests
import configuration as config
import urllib


def authorize_user(username, password, callback_uri):
    """ Retrieve authorization page html
    """
    params = {
        "client_id": config.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": callback_uri,
        "scope": "user-read-currently-playing user-read-playback-state"
    }
    endpoint = "https://accounts.spotify.com/authorize"
    query = urllib.parse.urlencode(params)
    url = f"{endpoint}?{query}"
    print(url)
    return url


def get_current_playback_info():
    """ Returns current playback info.
    """
    return None


def add_item_to_liked_songs(item):
    """ Adds item to the liked items playlist.
    """
    pass


def add_item_to_disliked_songs(item):
    """ Adds item to the disliked items playlist.
    """
    pass


def add_item_to_meh_songst(item):
    """ Adds item to the meh items playlist.
    """
    pass

