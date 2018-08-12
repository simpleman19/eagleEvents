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
    from .routes import main_blueprint
    from .routes.event_planners import event_planners_blueprint
    from .routes.customers import customers_blueprint
    from .routes.events import events_blueprint
    from .routes.api.events import events_api_blueprint
    from .routes.api.tables import tables_api_blueprint
    from .routes.api.customers import customers_api_blueprint
    from .routes.api.company import company_api_blueprint
    from .routes.api.users import user_api_blueprint
    from .auth import auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(event_planners_blueprint)
    app.register_blueprint(customers_blueprint)
    app.register_blueprint(events_blueprint)
    app.register_blueprint(events_api_blueprint)
    app.register_blueprint(tables_api_blueprint)
    app.register_blueprint(customers_api_blueprint)
    app.register_blueprint(company_api_blueprint)
    app.register_blueprint(user_api_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
