#!/bin/bash
set -e

# F1 Fantasy Test Stack Installation Script
# This script sets up a simple test environment with SQLite

echo "🏁 F1 Fantasy Test Stack Installation 🏁"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Function to prompt for confirmation
confirm_action() {
    local action="$1"
    local reason="$2"
    echo ""
    echo "🔐 SUDO OPERATION REQUIRED:"
    echo "Action: $action"
    echo "Reason: $reason"
    echo ""
    read -p "Do you want to proceed? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Operation cancelled by user"
        exit 1
    fi
}

# Variables
APP_NAME="f1fantasy"
APP_USER="f1fantasy"
APP_DIR="/opt/f1fantasy"
DATA_DIR="/opt/f1fantasy/data"
LOG_DIR="/var/log/f1fantasy"

echo "📦 Installing system dependencies..."

# Update system
confirm_action "Update system packages (apt update && apt upgrade)" "Ensures all system packages are up to date before installation"
apt update && apt upgrade -y

# Install required packages (simplified for test stack)
confirm_action "Install system packages (Python3, pip, git, etc.)" "Required system packages for running the F1 Fantasy application"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-gunicorn \
    git \
    curl \
    htop \
    ufw

echo "👤 Creating application user..."

# Create app user
confirm_action "Create dedicated system user '$APP_USER'" "Creates a separate user account for security - the app won't run as root"
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$APP_DIR" "$APP_USER"
else
    echo "ℹ️ User $APP_USER already exists, skipping creation"
fi

# Create application directories
confirm_action "Create system directories (/opt/f1fantasy, /var/log/f1fantasy)" "Creates proper system directories for the application and logs"
mkdir -p "$APP_DIR" "$DATA_DIR" "$LOG_DIR"
chown "$APP_USER:$APP_USER" "$APP_DIR" "$DATA_DIR" "$LOG_DIR"

echo "📁 Copying application files..."

# Copy application to deployment directory
if [ -f "$(pwd)/setup.py" ] && [ -d "$(pwd)/deploy" ]; then
    confirm_action "Copy application files to system directory" "Copies your F1 Fantasy code to the system installation directory"
    cp -r . "$APP_DIR/"
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
else
    echo "❌ Please run this script from the F1 Fantasy project directory"
    echo "Expected files: setup.py and deploy/ directory"
    exit 1
fi

echo "🔧 Creating missing application structure..."

# Create f1_fantasy package if it doesn't exist
if [ ! -d "$APP_DIR/f1_fantasy" ]; then
    echo "📦 Creating f1_fantasy package structure..."
    sudo -u "$APP_USER" mkdir -p "$APP_DIR/f1_fantasy"
    
    # Create __init__.py
    sudo -u "$APP_USER" cat > "$APP_DIR/f1_fantasy/__init__.py" << 'EOF'
"""F1 Fantasy Application Package"""
__version__ = "0.1.0"
EOF

    # Create minimal app.py
    sudo -u "$APP_USER" cat > "$APP_DIR/f1_fantasy/app.py" << 'EOF'
from flask import Flask, render_template, redirect, url_for
from flask_security import current_user, login_required
from f1_fantasy.models import db
from f1_fantasy.security import init_security, create_default_roles
from f1_fantasy.setup import init_setup
import os

def create_app(config=None):
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
    
    # Load configuration
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///f1_fantasy.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key'),
        SECURITY_PASSWORD_SALT=os.getenv('SECURITY_PASSWORD_SALT', 'dev-salt'),
    )
    
    if config:
        app.config.update(config)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize security
    init_security(app)
    
    # Create database tables and run setup wizard
    with app.app_context():
        db.create_all()
        create_default_roles()
        init_setup(app)
    
    # Routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    return app
EOF

    # Create minimal models.py
    sudo -u "$APP_USER" cat > "$APP_DIR/f1_fantasy/models.py" << 'EOF'
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

# Association table for user roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    
    # Flask-Security tracking fields
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer())
    
    roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))
EOF

    # Create minimal security.py
    sudo -u "$APP_USER" cat > "$APP_DIR/f1_fantasy/security.py" << 'EOF'
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
EOF

    # Create minimal setup.py
    sudo -u "$APP_USER" cat > "$APP_DIR/f1_fantasy/setup.py" << 'EOF'
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
        print("=== F1 Fantasy Setup Wizard ===")
        
        # Create admin user
        admin_email = "test@famgala.com"
        admin_username = "test"
        admin_password = secrets.token_urlsafe(10)
        
        print(f"Admin email address: {admin_email}")
        print(f"Admin username: {admin_username}")
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
        
        # Create admin user
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin = User(
                email=admin_email,
                username=admin_username,
                password=hash_password(admin_password),
                active=True,
                confirmed_at=datetime.now(),
                fs_uniquifier=secrets.token_hex(16)
            )
            admin.roles.append(admin_role)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created: {admin_email}")
        
        print("Setup completed successfully!")
        print("=" * 60)
        print("🔑 IMPORTANT: ADMIN LOGIN CREDENTIALS")
        print("=" * 60)
        print(f"Email:    {admin_email}")
        print(f"Username: {admin_username}")
        print(f"Password: {admin_password}")
        print("=" * 60)
        print("⚠️  SAVE THIS PASSWORD - You will need it to log in!")
        print("=" * 60)
        
        # Mark setup as complete
        os.makedirs(os.path.dirname(setup_file), exist_ok=True)
        with open(setup_file, 'w') as f:
            f.write('1')
EOF

    echo "✅ Created minimal f1_fantasy package structure"
fi

# Create basic templates if they don't exist
if [ ! -d "$APP_DIR/templates" ]; then
    echo "📄 Creating basic templates..."
    sudo -u "$APP_USER" mkdir -p "$APP_DIR/templates/security"
    
    # Create base template
    sudo -u "$APP_USER" cat > "$APP_DIR/templates/base.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>F1 Fantasy League</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">F1 Fantasy League</a>
            <ul class="navbar-nav ms-auto">
                {% if current_user.is_authenticated %}
                    <li class="nav-item"><a class="nav-link" href="/dashboard">Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="/auth/logout">Logout</a></li>
                {% else %}
                    <li class="nav-item"><a class="nav-link" href="/auth/login">Login</a></li>
                {% endif %}
            </ul>
        </div>
    </nav>
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF

    # Create index template
    sudo -u "$APP_USER" cat > "$APP_DIR/templates/index.html" << 'EOF'
{% extends "base.html" %}
{% block content %}
<div class="jumbotron">
    <h1>Welcome to F1 Fantasy League</h1>
    <p class="lead">Create your fantasy F1 team and compete with friends!</p>
    <a class="btn btn-primary btn-lg" href="/auth/login">Get Started</a>
</div>
{% endblock %}
EOF

    # Create dashboard template
    sudo -u "$APP_USER" cat > "$APP_DIR/templates/dashboard.html" << 'EOF'
{% extends "base.html" %}
{% block content %}
<h1>Dashboard</h1>
<p>Welcome to your F1 Fantasy dashboard, {{ current_user.username }}!</p>
{% endblock %}
EOF

    # Create login template
    sudo -u "$APP_USER" cat > "$APP_DIR/templates/security/login.html" << 'EOF'
{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h4>Login</h4></div>
            <div class="card-body">
                <form action="{{ url_for_security('login') }}" method="post">
                    {{ login_user_form.hidden_tag() }}
                    {% if login_user_form.errors %}
                        <div class="alert alert-danger">
                            {% for field, errors in login_user_form.errors.items() %}
                                {% for error in errors %}
                                    <div>{{ error }}</div>
                                {% endfor %}
                            {% endfor %}
                        </div>
                    {% endif %}
                    <div class="mb-3">
                        {{ login_user_form.email.label(class="form-label") }}
                        {{ login_user_form.email(class="form-control") }}
                    </div>
                    <div class="mb-3">
                        {{ login_user_form.password.label(class="form-label") }}
                        {{ login_user_form.password(class="form-control") }}
                    </div>
                    <div class="d-grid">
                        {{ login_user_form.submit(class="btn btn-primary") }}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

    echo "✅ Created basic templates"
fi

echo "🐍 Setting up Python environment..."

# Create virtual environment as app user
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"

# Fix permissions on venv executables
chmod +x "$APP_DIR/venv/bin/"*

# Upgrade pip in the virtual environment using a more basic approach
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" -m ensurepip --upgrade

# Install Python dependencies
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

# Ensure no editable installs and fix any permission issues
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" -m pip uninstall -y f1-fantasy 2>/dev/null || true

# Set proper permissions on the development directory to avoid permission errors
if [ -d "/home/soldev/dev/f1" ]; then
    sudo chmod -R o+r /home/soldev/dev/f1 2>/dev/null || true
fi

echo "⚙️ Configuring services..."

# Copy systemd service
confirm_action "Install systemd service file" "Creates a system service so F1 Fantasy starts automatically on boot"
cp "$APP_DIR/deploy/f1fantasy.service" /etc/systemd/system/
systemctl daemon-reload

echo "🔧 Setting up environment..."

# Create environment file
sudo -u "$APP_USER" cp "$APP_DIR/deploy/environment.env" "$APP_DIR/.env"

# Generate secret keys
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SALT=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update environment file with generated secrets
sudo -u "$APP_USER" sed -i "s/your-test-secret-key-change-this/$SECRET_KEY/" "$APP_DIR/.env"
sudo -u "$APP_USER" sed -i "s/your-test-salt-change-this-too/$SALT/" "$APP_DIR/.env"

echo "🗃️ Initializing SQLite database..."

# Initialize database
cd "$APP_DIR"
sudo -u "$APP_USER" bash -c "source venv/bin/activate && python -c '
import os
os.environ[\"FLASK_ENV\"] = \"testing\"
from deploy.wsgi import application
with application.app_context():
    from f1_fantasy.models import db
    db.create_all()
    print(\"SQLite database initialized\")
'"

# Run initial setup
sudo -u "$APP_USER" bash -c "source venv/bin/activate && FLASK_ENV=testing python f1_fantasy/setup.py" || true

# Ensure admin user is properly configured for login
echo "🔧 Finalizing admin user configuration..."
sudo -u "$APP_USER" bash -c "source venv/bin/activate && python -c '
import os
from datetime import datetime
os.environ[\"FLASK_ENV\"] = \"testing\"
from deploy.wsgi import application
with application.app_context():
    from f1_fantasy.models import db, User, Role
    
    # Find admin user
    admin_user = User.query.filter_by(username=\"admin\").first()
    if admin_user:
        # Ensure user is active and confirmed
        admin_user.active = True
        if not admin_user.confirmed_at:
            admin_user.confirmed_at = datetime.now()
        
        # Ensure admin role exists and is assigned
        admin_role = Role.query.filter_by(name=\"admin\").first()
        if not admin_role:
            admin_role = Role(name=\"admin\", description=\"Administrator\")
            db.session.add(admin_role)
        
        if admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)
        
        db.session.commit()
        print(f\"Admin user configured: {admin_user.email} (confirmed: {admin_user.confirmed_at is not None})\")
    else:
        print(\"WARNING: No admin user found after setup\")
'"

echo "🔥 Configuring firewall..."

# Configure UFW firewall (allow port 8000 for direct access)
confirm_action "Configure system firewall (UFW)" "Sets up firewall rules to allow SSH and port 8000 (F1 Fantasy), blocks other incoming connections for security"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 8000
ufw --force enable

echo "🚀 Starting services..."

# Start and enable the application service
confirm_action "Enable and start F1 Fantasy system service" "Starts the F1 Fantasy service and configures it to start automatically on boot"
systemctl enable f1fantasy
systemctl start f1fantasy

# Check service status
sleep 2
if systemctl is-active --quiet f1fantasy; then
    echo "✅ F1 Fantasy Test Stack service is running"
else
    echo "❌ F1 Fantasy Test Stack service failed to start"
    systemctl status f1fantasy
fi

echo ""
echo "🎉 Test Stack Installation Complete! 🎉"
echo "======================================"
echo ""
echo "📊 Service Status:"
echo "- F1 Fantasy Test Stack: $(systemctl is-active f1fantasy)"
echo ""
echo "🌐 Access your application:"
echo "- URL: http://$(hostname -I | awk '{print $1}'):8000"
echo "- Local: http://localhost:8000"
echo ""
echo "🔑 Admin Login:"
echo "- Check the setup output above for your auto-generated admin credentials"
echo "- Login URL: http://$(hostname -I | awk '{print $1}'):8000/auth/login"
echo ""
echo "📁 Important paths:"
echo "- Application: $APP_DIR"
echo "- Database: $DATA_DIR/f1fantasy_test.db"
echo "- Logs: $LOG_DIR"
echo "- Config: $APP_DIR/.env"
echo ""
echo "🔧 Useful commands:"
echo "- View logs: sudo journalctl -u f1fantasy -f"
echo "- Restart app: sudo systemctl restart f1fantasy"
echo "- Check status: sudo systemctl status f1fantasy"
echo "- Access database: sqlite3 $DATA_DIR/f1fantasy_test.db"
echo ""
echo "🔒 Security Notes:"
echo "- Update the .env file with your actual configuration"
echo "- This is a TEST STACK - not suitable for production"
echo "- SQLite database is stored locally"
echo "- Application is accessible on port 8000"
echo "" 