# app/__init__.py
from flask import Flask
import os
from dotenv import load_dotenv

def create_app(config_class='config.Config'):
    load_dotenv()  # Load environment variables from .env
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        from . import routes

    return app
