""" 2021 Created by michal@buyuk-dev.com
"""

import urllib
import requests

from server import configuration


def authorize_user(redirect_uri):
    """Retrieve authorization page html"""
    params = {
        "client_id": configuration.spotify.get_client_id(),
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(
            [
                "user-read-currently-playing",
                "user-read-playback-state",
                "playlist-modify-public",
            ]
        ),
    }
    endpoint = "https://accounts.spotify.com/authorize"
    query = urllib.parse.urlencode(params)
    url = f"{endpoint}?{query}"
    return url


def request_token(code, redirect_uri):
    """redirect_uri must be the same as in authorize_user"""
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": configuration.spotify.get_client_id(),
        "client_secret": configuration.spotify.get_client_secret(),
    }
    resp = requests.post("https://accounts.spotify.com/api/token", data=params)
    return resp.status_code, resp.json()


def get_current_playback_info(token):
    """Returns current playback info."""
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get("https://api.spotify.com/v1/me/player", headers=headers)
    code = resp.status_code

    if code == 200:
        return code, resp.json()
    return code, resp.text


def get_user_profile(token):
    """Returns current user id."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get("https://api.spotify.com/v1/me", headers=headers)
    code = resp.status_code

    if code == 200:
        return code, resp.json()
    return code, resp.text


def get_user_playlists(token, user_id):
    """Returns authorization method."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers
    )
    code = resp.status_code

    if code == 200:
        return code, resp.json()
    return code, resp.text


def add_item_to_playlist(token, playlist_id, track_uri):
    """Add item to the playlist."""
    headers = {"Authorization": f"Bearer {token}"}

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={track_uri},"
    resp = requests.post(url, headers=headers)

    code = resp.status_code
    if code == 201:
        return code, resp.json()
    return code, resp.text
