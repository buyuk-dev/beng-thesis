import requests
import configuration as config
import urllib


def authorize_user(redirect_uri):
    """ Retrieve authorization page html
    """
    params = {
        "client_id": config.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-read-currently-playing user-read-playback-state"
    }
    endpoint = "https://accounts.spotify.com/authorize"
    query = urllib.parse.urlencode(params)
    url = f"{endpoint}?{query}"
    return url


def request_token(code, redirect_uri):
    """ redirect_uri must be the same as in authorize_user
    """
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET
    }
    resp = requests.post("https://accounts.spotify.com/api/token", data=params)
    return resp.status_code, resp.json()

def get_current_playback_info(token):
    """ Returns current playback info.
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get("https://api.spotify.com/v1/me/player", headers=headers)
    code =  r.status_code

    if code == 200:
        return code, r.json()
    else:
        return code, r.text


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

