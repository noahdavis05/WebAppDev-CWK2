import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Enable CSRF protection
    WTF_CSRF_ENABLED = True

    # Secret key for CSRF protection
    SECRET_KEY = os.urandom(32)

    # Database URI (app.db will be created in the main directory)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
