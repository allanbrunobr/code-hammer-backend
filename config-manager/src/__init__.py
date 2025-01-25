__version__ = "0.1.0"

def create_app():
    from .main import app as app

    app.version = __version__

    return app
