#!/usr/bin/env python3
"""
Script to create an admin user for development
"""
import os
import sys
import secrets
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment
os.environ.setdefault('FLASK_ENV', 'development')

from f1_fantasy.app import create_app
from dev_config import DevelopmentConfig
from f1_fantasy.models import db, User, Role
from f1_fantasy.security import user_datastore
from flask_security.utils import hash_password

def create_dev_admin():
    """Create an admin user for development."""
    
    # Create config dict from DevelopmentConfig class
    config_dict = {}
    for attr in dir(DevelopmentConfig):
        if not attr.startswith('_'):
            config_dict[attr] = getattr(DevelopmentConfig, attr)
    
    # Create app with development config
    app = create_app(config_dict)
    
    with app.app_context():
        # Admin credentials
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "devpass123"  # Simple password for development
        
        print("🔧 Creating development admin user...")
        
        # Create roles if they don't exist
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            print("✅ Created admin role")
            
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user', description='Regular User')
            db.session.add(user_role)
            print("✅ Created user role")
        
        db.session.commit()
        
        # Delete existing admin user if it exists
        existing_admin = User.query.filter_by(username=admin_username).first()
        if existing_admin:
            print(f"🗑️ Removing existing admin user: {admin_username}")
            db.session.delete(existing_admin)
            db.session.commit()
        
        # Create new admin user
        admin = User(
            username=admin_username,
            email=admin_email,
            password=hash_password(admin_password),
            active=True,
            confirmed_at=datetime.now(),
            fs_uniquifier=secrets.token_hex(16)
        )
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Development admin user created successfully!")
        print("=" * 60)
        print("🔑 DEVELOPMENT ADMIN CREDENTIALS")
        print("=" * 60)
        print(f"Username: {admin_username}")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("=" * 60)
        print("🌐 Login URL: http://localhost:5000/auth/login")
        print("💡 You can log in using either username or email.")
        print("=" * 60)

if __name__ == "__main__":
    create_dev_admin() 