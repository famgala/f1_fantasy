#!/usr/bin/env python3
"""
Test script to debug login functionality
"""
import os
import sys
from flask import Flask
from flask_security.utils import verify_password, get_identity_attribute

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from f1_fantasy.app import create_app
from f1_fantasy.models import db, User
from f1_fantasy.security import user_datastore
from dev_config import DevelopmentConfig

def test_login():
    """Test login functionality directly."""
    
    # Create config dict from DevelopmentConfig class
    config_dict = {}
    for attr in dir(DevelopmentConfig):
        if not attr.startswith('_'):
            config_dict[attr] = getattr(DevelopmentConfig, attr)
    
    # Create app
    app = create_app(config_dict)
    
    with app.app_context():
        # Find the admin user
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ Admin user not found!")
            return
        
        print(f"✅ Admin user found:")
        print(f"   ID: {admin_user.id}")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Active: {admin_user.active}")
        print(f"   Password hash: {admin_user.password[:50]}...")
        print(f"   Roles: {[role.name for role in admin_user.roles]}")
        print(f"   fs_uniquifier: {admin_user.fs_uniquifier}")
        
        # Test password verification
        test_password = "tOmPf3wZzDXBIg"
        is_valid = verify_password(test_password, admin_user.password)
        print(f"\n🔐 Password verification for '{test_password}': {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        # Test user datastore find_user methods
        print("\n🔍 Testing user datastore lookup methods:")
        user_by_email = user_datastore.find_user(email='admin@example.com')
        user_by_username = user_datastore.find_user(username='admin')
        print(f"   find_user(email='admin@example.com'): {'Found' if user_by_email else 'Not found'}")
        print(f"   find_user(username='admin'): {'Found' if user_by_username else 'Not found'}")
        
        # Check Flask-Security configuration
        print(f"\n⚙️ Flask-Security Configuration:")
        print(f"   USERNAME_ENABLE: {app.config.get('SECURITY_USERNAME_ENABLE')}")
        print(f"   USER_IDENTITY_ATTRIBUTES: {app.config.get('SECURITY_USER_IDENTITY_ATTRIBUTES')}")
        
        # Test login with both username and email
        print("\n🔑 Testing login with both username and email:")
        print("1. Try logging in with username 'admin'")
        print("2. Try logging in with email 'admin@example.com'")
        print("\nPlease try both methods in your browser at: http://localhost:5000/auth/login")

if __name__ == "__main__":
    test_login() 