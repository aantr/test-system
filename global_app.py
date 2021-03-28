from flask import Flask

app = None


def global_init():
    global app

    app = Flask(__name__)


def get_app():
    global app

    return app
