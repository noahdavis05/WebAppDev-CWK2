from flask import Flask
from .models import db, bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_wtf.csrf import CSRFProtect

from .models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
        
csrf = CSRFProtect(app)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize Flask-Migrate
migrate = Migrate(app, db)  # Add this line

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure views are imported last to avoid circular imports
from . import views
