from flask import Flask

app = None
directory = None


def global_init(name, dir):
    global app, directory

    app = Flask(name)
    directory = dir


def get_app():
    global app
    return app


def get_dir():
    global directory
    return directory
