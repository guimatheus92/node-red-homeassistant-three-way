# app/__init__.py
from flask import Flask, send_from_directory
from dotenv import load_dotenv
import os

def create_app(config_class='config.Config'):
    load_dotenv()  # Load environment variables from .env
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        from . import routes

    # Route to serve the favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

    return app