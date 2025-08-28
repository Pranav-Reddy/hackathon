from flask import Flask
from app.config import Config
from app.controllers.gcs_controller import gcs_bp, bq_bp, image_qna_bp, product_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(gcs_bp)
    app.register_blueprint(bq_bp)
    app.register_blueprint(image_qna_bp)
    app.register_blueprint(product_bp)

    return app
