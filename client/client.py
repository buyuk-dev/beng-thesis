import requests


HOST = "http://localhost:5000"


def connect_spotify():
    r = requests.get(f"{HOST}/spotify/connect")
    code, response = r.status_code, r.json()
    return code, response

def get_config(userid):
    """ Request config from the /user/<userid>/config endpoint."""
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

def mark_current_song(label):
    r = requests.get(f"{HOST}/mark/{label}")
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

def muse_blocking_data_plot():
    r = requests.get(f"{HOST}/muse/plot")
    code, response = r.status_code, r.json()
    return code, response
    
