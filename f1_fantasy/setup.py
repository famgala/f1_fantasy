import os
import secrets
from datetime import datetime
from f1_fantasy.models import db, User, Role
from f1_fantasy.security import user_datastore
from flask_security.utils import hash_password

def init_setup(app):
    """Initialize setup wizard."""
    setup_file = os.path.join(app.instance_path, 'setup_complete')
    
    if not os.path.exists(setup_file):
        with app.app_context():
            print("=== F1 Fantasy Setup Wizard ===")
            
            # Create admin user with username only
            admin_username = "admin"
            admin_email = "admin@example.com"
            admin_password = secrets.token_urlsafe(10)
            
            print(f"✅ Generated secure admin password: {admin_password}")
            
            # Create roles
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin', description='Administrator')
                db.session.add(admin_role)
                
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                user_role = Role(name='user', description='Regular User')
                db.session.add(user_role)
            
            db.session.commit()
            
            # Create admin user without email
            existing_admin = User.query.filter_by(username=admin_username).first()
            if not existing_admin:
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
                print(f"Admin user created: {admin_username} ({admin_email})")
            else:
                # Ensure existing admin has admin role
                if admin_role not in existing_admin.roles:
                    existing_admin.roles.append(admin_role)
                    db.session.commit()
                    print(f"Admin role assigned to existing user: {admin_username}")
            
            print("Setup completed successfully!")
            print("=" * 60)
            print("🔑 IMPORTANT: ADMIN LOGIN CREDENTIALS")
            print("=" * 60)
            print(f"Username: {admin_username}")
            print(f"Email: {admin_email}")
            print(f"Password: {admin_password}")
            print("=" * 60)
            print("⚠️  SAVE THIS PASSWORD - You will need it to log in!")
            print("💡 You can log in using either username or email.")
            print("=" * 60)
            
            # Mark setup as complete
            os.makedirs(os.path.dirname(setup_file), exist_ok=True)
            with open(setup_file, 'w') as f:
                f.write('1') 