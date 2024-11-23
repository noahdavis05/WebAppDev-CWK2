# app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
import  os
from cryptography.fernet import Fernet

db = SQLAlchemy()
bcrypt = Bcrypt()

#load the secret key from environment variables
secret_key = b'0CHWHXr60JrRm5sCmP40bWwHMHruNpa9AA0N1M2esYQ='
cipher_suite = Fernet(secret_key)

# Encrypt function
def encrypt_key(key: str) -> str:
    """Encrypts the API key"""
    encrypted_key = cipher_suite.encrypt(key.encode())  # Convert the key to bytes and encrypt
    return encrypted_key.decode()  # Return as string

# Decrypt function
def decrypt_key(encrypted_key: str) -> str:
    """Decrypts the API key"""
    decrypted_key = cipher_suite.decrypt(encrypted_key.encode())  # Convert to bytes and decrypt
    return decrypted_key.decode()  # Return as string


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(200), nullable=False)
    event_description = db.Column(db.Text, nullable=True)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(300), nullable=False)
    guests = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float, nullable=True)
    event_owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Event {self.event_name}>"


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    ticket_owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    ticket_used = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    scanned_at = db.Column(db.DateTime, nullable=True)

    event = db.relationship('Event', backref='tickets')

    def __repr__(self):
        return f"<Ticket {self.id}>"
    


class StripeKey(db.Model):
    __tablename__ = 'stripe_keys'

    id = db.Column(db.Integer, primary_key=True)
    # Store the encrypted public and private keys
    _public_key = db.Column('public_key', db.String(255), nullable=False)
    _private_key = db.Column('private_key', db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref=db.backref('stripe_keys', lazy=True))

    def __repr__(self):
        return f"<StripeKey user_id={self.user_id} public_key={self.public_key}>"

    @property
    def public_key(self):
        """Decrypt and return the public key."""
        return decrypt_key(self._public_key)

    @public_key.setter
    def public_key(self, key):
        """Encrypt and set the public key."""
        self._public_key = encrypt_key(key)

    @property
    def private_key(self):
        """Decrypt and return the private key."""
        return decrypt_key(self._private_key)

    @private_key.setter
    def private_key(self, key):
        """Encrypt and set the private key."""
        self._private_key = encrypt_key(key)


