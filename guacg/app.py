import json
import uuid
import gevent

from parking import ParkingLot

from geventwebsocket import WebSocketApplication

from guacamole.client import GuacamoleClient, PROTOCOL_NAME

try:
    # Add local_settings.py with RDP connection variables
    from local_settings import USERNAME, PASSWORD, HOST, PORT, DOMAIN, APP, SEC
except ImportError:
    USERNAME = ''
    PASSWORD = ''
    HOST = ''
    PORT = 3389
    DOMAIN = ''
    APP = ''
    SEC = ''


# Paused GuacamoleClients. The key is client Session ID.
PARKED_CLIENTS = ParkingLot()


def park_client(client):
    """
    Park client in ParkingLot.
    """
    PARKED_CLIENTS[client.id] = client


def retrieve_client(id):
    """
    Retrieve client from ParkingLot.
    """
    try:
        return PARKED_CLIENTS.pop(id)
    except KeyError:
        return None


class GuacamoleApp(WebSocketApplication):

    def __init__(self, ws):
        self.client = None
        self._listener = None

        # Guest WS client List.
        self.guests = list()

        # Is connection paused?
        self.paused = False

        self.master = self.control = False
        self.master_session_id = None

        super(GuacamoleApp, self).__init__(ws)

    @classmethod
    def protocol_name(cls):
        """
        Return our protocol.
        """
        return PROTOCOL_NAME

    @property
    def ws_client(self):
        """
        Return current active websocket client.
        """
        return self.ws.handler.active_client

    def on_open(self, *args, **kwargs):
        """
        New Web socket connection opened.
        """
        if self.client:
            # we have a running client?!
            self.client.close()

        # @TODO: get guacd host and port!
        self.client = GuacamoleClient('localhost', 4822)

        # @TODO: Move this to GuacamoleClient.
        self.client.id = uuid.uuid1()

    def on_message(self, message):
        """
        New message received on the websocket.
        """
        if not self.client.connected:
            # Client is not connected, message should include connection args
            return self.connect(message)

        if message.startswith('5.guacg'):
            # This is a guacg custom instruction
            return
        else:
            if self.control:
                # Send message to guacd server if on control!
                self.client.send(message)

    def on_close(self, reason):
        """
        Websocket closed.
        """
        # @TODO: consider reconnect from client. (network glitch?!)
        # @TODO: One solution is to pause client instead of termination.
        if not self.ws_client.master:
            # This is a guest. Let the master know!
            master_ws_client = self._get_ws_client(self.master_session_id)
            if master_ws_client:
                self._leave_client(master_ws_client)

        self._stop_listener()

        if not self.paused:
            # Close connection if we are not paused!
            self.client.close()
            self.client = None

    def connect(self, args):
        """
        Connect to guacd server and start listener.

        :param args: JSON string of client supplied connection args
        """
        connection_args = json.loads(args)

        if connection_args.guest and connection_args.sessionId:
            # A guest is joining an existing session.

            try:
                self.join(connection_args.sessionId)
            except:
                # @TODO: handle error!
                pass

            # Set guest properties
            self.master_session_id = connection_args.sessionId
            self.master = self.control = False
            return
        elif connection_args.resume and connection_args.sessionId:
            # A client is resuming a paused session
            self.resume(connection_args.sessionId)
            self._start_listener()
        else:
            # A client is starting a new session
            # @TODO: get Remote server connection properties
            self.client.handshake(protocol='rdp', hostname=HOST,
                                  port=PORT, username=USERNAME,
                                  password=PASSWORD, domain=DOMAIN,
                                  security=SEC, remote_app=APP)

            self._start_listener()

        # In case of session resume or new session
        self.master = self.control = True

    def join(self, session_id):
        """
        A guest is joining an existing session.

        :param session_id: Existing GuacamoleClient ID.
        """
        if session_id == self.client.id:
            # A master cannot join as a guest!
            return

        master_ws_client = self._get_ws_client(session_id)
        if not master_ws_client:
            # TODO: raise custom exception? return error?
            return

        self._join_client(master_ws_client)

    def resume(self, session_id):
        """
        A session master is resuming a paused session.
        """
        # First, get the parked client, if exists!
        self.client = retrieve_client(session_id)

        if not self.client:
            # Client was not parked!
            # @TODO: Raise custom exception, return error!
            # @TODO: is client controlled by another master WS?!
            return None

        # @TODO: Disconnect if client is controlled by another WS.

        self.paused = False

    def pause(self):
        """
        Pause current session.
        """
        if not self.master:
            # A guest cannot pause a session!
            return

        # To avoid client termination.
        self.paused = True

        park_client(self.client)

    def control(self):
        """
        Taking control on the session.
            - Session Master should be granted control immediately.
            - Guest will issue Control Request, and master should approve.
        """
        return

    def remove(self, guest_id):
        """
        Disconnect guest from shared session.

        :param guest_id: Guest ID.
        """
        if not self.master:
            return

        # Force guest client to be removed!
        self._leave_client(self.ws_client, client_id=guest_id)

        # @TODO: Notify guest!

    def broadcast(self, instruction):
        """
        Broadcast instruction to all connected sockets on this session.

        :param instruction: Instruction string to be delivered to all guests.
        """
        # Only master can broadcast!
        if not self.master:
            return

        for guest in self.guests:
            try:
                guest.ws.send(instruction)
            except:
                # log exception!
                pass

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
        and push directly to client(s) (over websocket).
        """
        while True:
            instruction = self.client.receive()
            self.ws.send(instruction)
            self.broadcast(instruction)

    def _get_ws_client(self, client_id):
        """
        Get client with specified client id.

        :param client_id: Session ID of GuacamoleClient.

        :return: Websocket Client.
        """
        for ws_client in self.ws.handler.server.clients.values():
            if ws_client.client.id == client_id:
                return ws_client

        return None

    def _join_client(self, master):
        """
        Add current client to master client as a guest.

        :param master: Master WS client.
        """
        for guest in master.guests:
            if guest.client.id == self.client.id:
                # Our ws client is already in the guests list!
                return

        # LOCK?!
        master.guests.append(self.ws_client)

        # @TODO: Notify master!

    def _leave_client(self, master, client_id=None):
        """
        Remove current client (or client_id) from master client guest list.

        :param master: Master WS client.

        :param client_id: The guest client ID.
        """
        guest_id = client_id if client_id else self.client.id

        for guest in master.guests:
            if guest.client.id == guest_id:
                # LOCK?!
                master.guests.remove(guest)
                break

        # @TODO: Notify master!
