from flask import Flask
from app.config import Config
from app.controllers.gcs_controller import gcs_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(gcs_bp)

    return app
