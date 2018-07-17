import os

from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()

from . import models


def create_app(config_name=None):
    # This line will allow for overriding configs but defaults to development
    if config_name is None:
        config_name = os.environ.get('EVENTS_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.host = '0.0.0.0'
    # Initialize flask extensions
    db.init_app(app)

    # Register web application routes
    from .routes import main as main_blueprint
    from .auth import auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
