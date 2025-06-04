"""
Test Configuration for F1 Fantasy App
"""
import os
from datetime import timedelta

class TestConfig:
    """Test configuration for F1 Fantasy application."""
    
    # Basic Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test-secret-key-change-this'
    DEBUG = False  # Keep False for test stack to be production-like
    TESTING = False
    
    # Database Configuration - Using SQLite for simplicity
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:////opt/f1fantasy/data/f1fantasy_test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # Flask-Security Configuration
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'test-salt-change-this'
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGEABLE = True
    
    # Session Configuration - Relaxed for testing
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Allow HTTP for test environment
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Mail Configuration (optional for test)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@f1fantasy.test'
    
    # Security Headers - Relaxed for test
    PREFERRED_URL_SCHEME = 'http'
    
    # Application-specific settings
    F1_API_KEY = os.environ.get('F1_API_KEY')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or '/var/log/f1fantasy/app.log'
    
    # Simple file-based caching for test environment
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # No rate limiting for test environment
    # RATELIMIT_STORAGE_URL = None 