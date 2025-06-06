import os

class DevelopmentConfig:
    """Development configuration."""
    
    # Flask settings
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///f1_fantasy.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Show SQL queries in development
    
    # Flask-Security settings
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'dev-salt-change-in-production')
    SECURITY_URL_PREFIX = '/auth'
    SECURITY_LOGIN_URL = '/login'
    SECURITY_LOGOUT_URL = '/logout'
    SECURITY_REGISTER_URL = '/register'
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = False
    SECURITY_USER_IDENTITY_ATTRIBUTES = [
        {"email": {"mapper": lambda x: x.lower(), "case_insensitive": True}},
        {"username": {"mapper": lambda x: x.lower(), "case_insensitive": True}}
    ]
    SECURITY_PASSWORD_LENGTH_MIN = 8
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_EMAIL = False
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = './logs/dev_app.log' 