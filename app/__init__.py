from flask import Flask
from .routes.crypto import crypto_bp
from .routes.psx import psx_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Register blueprints
    app.register_blueprint(crypto_bp)
    app.register_blueprint(psx_bp)

    return app
