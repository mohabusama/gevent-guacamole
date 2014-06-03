import os

from flask import Flask, render_template, send_from_directory
from werkzeug.debug import DebuggedApplication

WEBAPP_PATH = os.path.abspath(os.path.dirname(__file__))
STATIC_PATH = os.path.join(WEBAPP_PATH, 'static')

flask_app = Flask(__name__)


@flask_app.route('/')
def index():
    return render_template('rdp.html')


@flask_app.route('/static/<string:filename>')
def send_static(filename):
    return send_from_directory(STATIC_PATH, filename)


def get_webapp_resources(debug=False):
    """
    Return Flask webapp urls dict, to be included in guacg Resources.
    """
    flask_app.debug = debug
    app = DebuggedApplication(flask_app)
    return {
        '^/$': app,
        '^/static/.*$': app
    }
