import gevent

from guacamole.client import GuacamoleClient
from guacamole.instruction import GuacamoleInstruction as Instruction


class ParkingLot(dict):
    """
    Parking lot for GuacamoleClient(s). The purpose of this class is to retain
    GuacamoleClient (items) connections with guacd server.
    """

    def __init__(self, *args, **kwargs):
        super(ParkingLot, self).__init__()

    def __setitem__(self, key, value):
        """
        Add a new GuacamoleClient to the lot.
        """
        if self.__contains__(key):
            # Do not allow overriding existing clients.
            return

        if not isinstance(value, GuacamoleClient):
            # @TODO: add custom exceptions!
            raise RuntimeError(
                'Invalid value. Value must be instance of GuacamoleClient.')

        # Create a client parking space.
        space = ClientSpace(key, value)

        super(ParkingLot, self).__setitem__(key, space)

    def __getitem__(self, key):
        """
        Get GuacamoleClient with key.
        """
        space = super(ParkingLot, self).__getitem__(key)

        return space.client

    def __delitem__(self, key):
        """
        Delete GuacamoleClient.
        """
        space = self.__getitem__(key)
        space.stop_listener()

        super(ParkingLot, self).__delitem__(key)

    def pop(self, key, *args):
        """
        Pop specific GuacamoleClient.
        """
        space = super(ParkingLot, self).pop(key, *args)

        if not isinstance(space, ClientSpace):
            return space

        # Stop the listener
        space.stop_listener()

        # Return the GuacamoleClient, not the space!
        return space.client

    def popitem(self):
        """
        Pop first item.
        """
        key, space = super(ParkingLot, self).popitem()

        space.stop_listener()

        return key, space.client

    def clear(self):
        """
        Clear all spaces.
        """
        for space in self.values():
            space.stop_listener()

        super(ParkingLot, self).clear()


class ClientSpace():
    """
    A GuacamoleClient parking space.
    """

    def __init__(self, key, client):
        self.key = key
        self.client = client
        self._listener = None

        print 'PARKING CLIENT: ' + self.key

        self.start_listener()

    def start_listener(self):
        """
        Start a client listener.
        """
        if self._listener:
            self.stop_listener()
        self._listener = gevent.spawn(self.client_listener)
        self._listener.start()

    def stop_listener(self):
        """
        Stop client listener.
        """
        if self._listener:
            self._listener.kill()
            self._listener = None

    def client_listener(self):
        """
        A listener to retain GuacamoleClient connection with guacd server.
        """
        print 'STARTED PARKED LISTENER!'
        while True:
            instruction = Instruction.load(self.client.receive())
            self.respond(instruction)

    def respond(self, instruction):
        """
        Respond to guacd server with expected response!

        :param instruction: A valid GuacamoleInstruction.
        """
        if instruction.opcode == 'sync':
            # respond with a sync message
            print 'RESPONDING TO SYNC!'
            ts = instruction.args[0]
            response = Instruction('sync', ts)
            self.client.send_instruction(response)
