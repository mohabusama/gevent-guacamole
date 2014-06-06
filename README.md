# gevent-guacamole (GuacG)

A gevent websocket Guacamole broker.

## Usage

Install requirements (preferably in a virtualenv)

```
$ pip install -r requirements.txt
```

Add **local_settings.py** with RDP connection parameters. Example:

```python
USERNAME = 'mohab'
PASSWORD = 'myPass'

# Windows Application server
HOST = '192.168.20.14'
PORT = 3389
DOMAIN = 'guacg'
APP = '||notepad'
SEC = ''
```

[Install](http://guac-dev.org/doc/gug/installing-guacamole.html) & Run Guacamole **guacd** (0.9.0) server. Preferably in foreground to view the connection output.

```
$ guacd -f
guacd[10352]: INFO:  Guacamole proxy daemon (guacd) version 0.9.0
guacd[10352]: INFO:  Unable to bind socket to host ::1, port 4822: Address family not supported by protocol
guacd[10352]: INFO:  Successfully bound socket to host 127.0.0.1, port 4822
guacd[10352]: INFO:  Listening on host 127.0.0.1, port 4822
```

Then run **guacg** server with *--static* to serve a minimal Flask webapp.

```
$ python guacg.py --static
```

Now the server runs on **localhost:6060**
