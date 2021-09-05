""" During authorization Spotify API requires that an app receives HTTP callback request on a pre-registered address
    that contains an authorization code which will be later used to retrieve the oauth token used for all API calls.

    This requires some kind of basic HTTP server capable of processing single HTTP request at the start of the application.
    First version used Flask development server for this purpose, however it came with several downsides such as difficulty
    terminating the server after handling the request, as well as an unneccessery dependency.

    Thats why I decided to implement a basic socket-level listener which parses first line of the incoming HTTP request only
    and extracts the query parameters from the URI.
"""

import threading
import socket
from urllib.parse import urlparse


class SocketListener(threading.Thread):

    NUMBER_OF_BYTES_TO_READ = 512

    def __init__(self, on_callback, callback_url, *args, **kwargs):
        """ Create callback listener using sockets.
            @param on_callback: function that takes authorization code passed by spotify api in callback query parameters.
            @param address: socket address on which callback hsould be set. Needs to be registered in the spotify developer project settings.
        """
        super().__init__(*args, **kwargs)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.on_callback = on_callback

        url = urlparse(callback_url) 
        self.host, self.port = url.netloc.split(":")
        self.port = int(self.port)

    def receive_callback(self):
        """ Waits for callback request from spotify api and returns its header.
        """
        self.s.bind((self.host, self.port))
        self.s.listen(1)
        client, address = self.s.accept()
        request = client.recv(self.NUMBER_OF_BYTES_TO_READ).decode()
        client.close()
        return request

    def parse_query(self, request):
        """ Extract dict of {key: value} pairs from query.
        """
        idx = request.find("HTTP")
        request = request[:idx]
        query = request.strip().split("?")[-1]
        params_and_values = query.split("&")

        args = {}
        for pv in params_and_values:
            name, value = pv.split("=")
            args[name] = value

        return args
       
    def run(self):
        """ Listen for callback from spotify with auth code. After it arrives parse and request access token.
        """
        request = self.receive_callback()
        params = self.parse_query(request)
        self.on_callback(params["code"])

