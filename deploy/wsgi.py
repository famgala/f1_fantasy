#!/usr/bin/env python3
"""
WSGI entry point for F1 Fantasy application (Test Environment)
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from f1_fantasy.app import create_app
from deploy.test import TestConfig

def create_test_app():
    """Create and configure the test Flask application."""
    
    # Set environment
    os.environ.setdefault('FLASK_ENV', 'testing')
    
    # Create config dict from TestConfig class
    config_dict = {}
    for attr in dir(TestConfig):
        if not attr.startswith('_'):
            config_dict[attr] = getattr(TestConfig, attr)
    
    # Create app with test config
    app = create_app(config_dict)
    
    # Configure logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist - use absolute path
        log_file_path = TestConfig.LOG_FILE
        if not os.path.isabs(log_file_path):
            log_file_path = os.path.join(project_dir, log_file_path)
        
        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up rotating file handler
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, TestConfig.LOG_LEVEL))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, TestConfig.LOG_LEVEL))
        app.logger.info('F1 Fantasy Test Stack startup')
    
    return app

# Create the application instance
application = create_test_app()

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8000) 