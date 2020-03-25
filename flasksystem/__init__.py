from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flasksystem.config import Config
from flask.ext.mongoalchemy import MongoAlchemy


app.config["MONGOALCHEMY_DATABASE"] = "test"

db = MongoAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

from flasksystem.main.routes import main
from flasksystem.materias.routes import materias
from flasksystem.reactivos.routes import reactivos
from flasksystem.users.routes import users
from flasksystem.errors.handlers import errors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    bcrypt.init_app(app)
    login_manager.init_app(app)


    return app
