import logging
from flask import Flask
from .models import db, bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from .models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize extensions
csrf = CSRFProtect(app)
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configure logging
if not app.debug:  
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)  
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

from . import views
