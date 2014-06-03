from gevent import monkey
monkey.patch_all()

import argparse

from geventwebsocket import WebSocketServer, Resource

from webapp.webapp import get_webapp_resources

from app import GuacamoleApp


def run(address='', port=6060, endpoint='/', static=False, debug=False):
    """
    Run our websocket server with configured urls.
    """

    resources = {'/ws': GuacamoleApp}

    if static:
        # we need to serve static webapp as well
        resources.update(get_webapp_resources(debug))

    WebSocketServer(
        (address, port),
        Resource(resources),
        debug=debug
    ).serve_forever()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="""
        Gevent-Guacamole is a Websocket server that acts as a broker for
        Guacamole RDP server.
        """
    )

    parser.add_argument('-H', '--host', default='localhost', dest='host',
                        help='Server host address.')

    parser.add_argument('-p', '--port', default=6060, dest='port',
                        help='Server listening port.')

    parser.add_argument('-e', '--endpoint', default='/ws', dest='endpoint',
                        help='Server endpoint (default: /ws).')

    parser.add_argument('-s', '--static', dest='serve_static',
                        action='store_true', help='Serve static web app')

    parser.add_argument('-d', '--debug', dest='debug',
                        action='store_true', help='Run in debug mode')

    args = parser.parse_args()

    # start the server
    run(
        address=args.host,
        port=args.port,
        endpoint=args.endpoint,
        static=args.serve_static,
        debug=args.debug
    )
