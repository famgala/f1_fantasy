#!/usr/bin/env python3
"""
Development runner for F1 Fantasy application
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from f1_fantasy.app import create_app
from dev_config import DevelopmentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] in %(module)s: %(message)s'
)

def create_dev_app():
    """Create development application instance."""
    return create_app('development')

if __name__ == '__main__':
    app = create_dev_app()
    
    # Enable auto-reload for all relevant files
    extra_files = [
        'f1_fantasy/templates/**/*.html',  # Watch all HTML templates
        'f1_fantasy/static/**/*',          # Watch all static files
        'f1_fantasy/**/*.py',              # Watch all Python files
        'instance/**/*'                    # Watch instance files
    ]
    
    logging.info("F1 Fantasy development application startup")
    print("🏁 F1 Fantasy Development Server")
    print("================================")
    print("🌐 URL: http://localhost:5000")
    print("🔧 Debug mode: ON")
    print("📊 Database: SQLite (dev_f1fantasy.db)")
    print("📝 Logs: ./logs/dev_app.log")
    print("================================")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        extra_files=extra_files
    ) 