import gevent

from geventwebsocket import WebSocketApplication

from guacamole.client import GuacamoleClient, PROTOCOL_NAME

try:
    # Add local_settings.py with RDP connection variables
    from local_settings import (
        PROTOCOL, USERNAME, PASSWORD, HOST, PORT, DOMAIN, APP, SEC)
except ImportError:
    USERNAME = ''
    PASSWORD = ''
    HOST = ''
    PORT = 3389
    DOMAIN = ''
    APP = ''
    SEC = ''


class GuacamoleApp(WebSocketApplication):

    def __init__(self, ws):
        self.client = None
        self._listener = None

        super(GuacamoleApp, self).__init__(ws)

    @classmethod
    def protocol_name(cls):
        """
        Return our protocol.
        """
        return PROTOCOL_NAME

    def on_open(self, *args, **kwargs):
        """
        New Web socket connection opened.
        """
        if self.client:
            # we have a running client?!
            self.client.close()

        # @TODO: get guacd host and port!
        self.client = GuacamoleClient('localhost', 4822)

        # @TODO: get Remote server connection properties
        self.client.handshake(protocol=PROTOCOL, hostname=HOST,
                              port=PORT, username=USERNAME,
                              password=PASSWORD, domain=DOMAIN,
                              security=SEC, remote_app=APP)

        self._start_listener()

    def on_message(self, message):
        """
        New message received on the websocket.
        """
        # send message to guacd server
        self.client.send(message)

    def on_close(self, reason):
        """
        Websocket closed.
        """
        # @todo: consider reconnect from client. (network glitch?!)
        self._stop_listener()
        self.client.close()
        self.client = None

    def _start_listener(self):
        if self._listener:
            self._stop_listener()
        self._listener = gevent.spawn(self.guacd_listener)
        self._listener.start()

    def _stop_listener(self):
        if self._listener:
            self._listener.kill()
            self._listener = None

    def guacd_listener(self):
        """
        A listener that would handle any messages sent from Guacamole server
        and push directly to browser client (over websocket).
        """
        while True:
            instruction = self.client.receive()
            self.ws.send(instruction)
