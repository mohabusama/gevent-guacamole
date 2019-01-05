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

# Remote Application server
PROTOCOL = 'rdp'  # or 'vnc'
HOST = '192.168.20.14'
PORT = 3389  # or '5901' for VNC
DOMAIN = 'guacg'  # if required!
APP = '||notepad'  # if required!
SEC = ''
```

[Install](https://guacamole.apache.org/doc/gug/guacamole-docker.html) & Run Guacamole **guacd** server. Preferably using built Docker image.

```
$ docker run --name guacd -p 4822:4822 guacamole/guacd
guacd[1]: INFO: Guacamole proxy daemon (guacd) version 0.9.14 started
guacd[1]: INFO: Listening on host 0.0.0.0, port 4822
```

Then run **guacg** server with *--static* to serve a minimal Flask webapp.

```
$ cd guacg
$ python guacg.py --static
```

Now the server runs on **localhost:6060**
