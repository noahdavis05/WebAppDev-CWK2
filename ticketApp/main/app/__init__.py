# app/__init__.py
from flask import Flask
from .models import db, bcrypt
from flask_login import LoginManager

from .models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import views
