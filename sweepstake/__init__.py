import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config=None):

    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.from_object(config)

    from sweepstake import auth, home, user, competition, models

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app, db)
    login_manager.login_view = "auth.login"

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(competition.bp)
    app.register_blueprint(home.bp)
    app.add_url_rule("/", endpoint="index")

    return app