import secrets
from datetime import datetime
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from f1_fantasy.models import db, User, Role

# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

def init_security(app: Flask) -> None:
    """Initialize security for the Flask application."""
    app.config.update(
        SECURITY_URL_PREFIX='/auth',
        SECURITY_LOGIN_URL='/login',
        SECURITY_LOGOUT_URL='/logout',
        SECURITY_REGISTER_URL='/register',
        SECURITY_REGISTERABLE=True,
        SECURITY_RECOVERABLE=True,
        SECURITY_CHANGEABLE=True,
        SECURITY_CONFIRMABLE=False,
        SECURITY_TRACKABLE=True,
        SECURITY_PASSWORD_HASH='bcrypt',
        SECURITY_USERNAME_ENABLE=True,
        SECURITY_USERNAME_REQUIRED=True,
        SECURITY_PASSWORD_LENGTH_MIN=8,
        SECURITY_EMAIL_VALIDATOR_ARGS={"check_deliverability": False},
        SECURITY_SEND_REGISTER_EMAIL=False,
        SECURITY_SEND_PASSWORD_CHANGE_EMAIL=False,
        SECURITY_SEND_PASSWORD_RESET_EMAIL=False,
    )
    
    security.init_app(app, user_datastore)

def create_default_roles():
    """Create default roles."""
    if not user_datastore.find_role('admin'):
        user_datastore.create_role(name='admin', description='Administrator')
    if not user_datastore.find_role('user'):
        user_datastore.create_role(name='user', description='Regular User')
    db.session.commit()

def create_admin_user(email: str, password: str, username: str = None) -> None:
    """Create an admin user if it doesn't exist."""
    if not user_datastore.find_user(email=email):
        if not username:
            username = email.split('@')[0]
        user_datastore.create_user(
            email=email,
            username=username,
            password=hash_password(password),
            roles=['admin'],
            confirmed_at=datetime.now(),
            fs_uniquifier=secrets.token_hex(16)
        )
        db.session.commit() 