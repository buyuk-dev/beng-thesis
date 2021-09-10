import requests


HOST = "http://localhost:5000"


def connect_spotify():
    r = requests.get(f"{HOST}/spotify/connect")
    code, response = r.status_code, r.json()
    return code, response


def get_config(userid):
    """Request config from the /user/<userid>/config endpoint."""
    r = requests.get(f"{HOST}/user/{userid}/config")
    code, response = r.status_code, r.json()
    return code, response


def get_current_playback():
    r = requests.get(f"{HOST}/spotify/playback")
    code, response = r.status_code, r.json()
    return code, response


def spotify_status():
    r = requests.get(f"{HOST}/spotify/status")
    code, response = r.status_code, r.json()
    return code, response


def connect_muse(address):
    r = requests.get(f"{HOST}/muse/connect/{address}")
    code, response = r.status_code, r.json()
    return code, response


def disconnect_muse():
    r = requests.get(f"{HOST}/muse/disconnect")
    code, response = r.status_code, r.json()
    return code, response


def start_muse_data_collection():
    r = requests.get(f"{HOST}/muse/start")
    code, response = r.status_code, r.json()
    return code, response


def stop_muse_data_collection():
    r = requests.get(f"{HOST}/muse/stop")
    code, response = r.status_code, r.json()
    return code, response


def get_muse_status():
    r = requests.get(f"{HOST}/muse/status")
    code, response = r.status_code, r.json()
    return code, response


def session_start():
    r = requests.get(f"{HOST}/session/start")
    code, response = r.status_code, r.json()
    return code, response


def session_stop():
    r = requests.get(f"{HOST}/session/stop")
    code, response = r.status_code, r.json()
    return code, response


def session_label(label):
    r = requests.get(f"{HOST}/session/label/{label}")
    code, response = r.status_code, r.json()
    return code, response
