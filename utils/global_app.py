from flask import Flask

app = None


def global_init(name):
    global app

    app = Flask(name)


def get_app():
    global app

    return app
