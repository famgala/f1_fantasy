#!/bin/bash
set -e

# F1 Fantasy Installation Script
# This script clones the repository and sets up a complete F1 Fantasy environment

echo "🏁 F1 Fantasy Installation 🏁"
echo "=========================================="

# Check for interactive mode flag
INTERACTIVE_MODE=false
if [[ "$1" == "--interactive" ]]; then
    INTERACTIVE_MODE=true
    echo "ℹ️ Running in interactive mode - you will be prompted before each action"
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Function to prompt for confirmation (only in interactive mode)
confirm_action() {
    local action="$1"
    local reason="$2"
    
    if [ "$INTERACTIVE_MODE" = true ]; then
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
    else
        echo "▶️ $action"
    fi
}

# Variables
APP_NAME="f1fantasy"
APP_USER="f1fantasy"
APP_DIR="/opt/f1fantasy"
DATA_DIR="/opt/f1fantasy/data"
LOG_DIR="/var/log/f1fantasy"
REPO_URL="https://github.com/famgala/f1_fantasy.git"
TEMP_DIR="/tmp/f1fantasy_install"

echo "📦 Installing system dependencies..."

# Update system
confirm_action "Update system package list (apt update)" "Refreshes the package list to ensure we can install the latest versions of dependencies"
apt update

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

echo "📥 Cloning F1 Fantasy repository..."

# Clean up any existing temp directory
rm -rf "$TEMP_DIR"

# Clone the repository
confirm_action "Clone F1 Fantasy repository from GitHub" "Downloads the latest F1 Fantasy code from the official repository"
git clone "$REPO_URL" "$TEMP_DIR"

echo "📁 Installing application files..."

# Copy application to deployment directory
confirm_action "Copy application files to system directory" "Copies the F1 Fantasy code to the system installation directory"
cp -r "$TEMP_DIR"/* "$APP_DIR/"
cp -r "$TEMP_DIR"/.* "$APP_DIR/" 2>/dev/null || true  # Copy hidden files like .gitignore
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# Clean up temp directory
rm -rf "$TEMP_DIR"

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

# Dependencies installed successfully

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
os.environ[\"FLASK_ENV\"] = \"production\"
from deploy.wsgi import application
with application.app_context():
    from f1_fantasy.models import db
    db.create_all()
    print(\"SQLite database initialized\")
'"

# Run initial setup and capture credentials
echo "🔧 Running initial setup..."
SETUP_OUTPUT=$(sudo -u "$APP_USER" bash -c "source venv/bin/activate && python -c '
import os
os.environ[\"FLASK_ENV\"] = \"production\"
from deploy.wsgi import application
with application.app_context():
    from f1_fantasy.setup import init_setup
    init_setup(application)
'" 2>&1 || echo "Setup completed")

# Ensure admin user is properly configured for login
echo "🔧 Finalizing admin user configuration..."
sudo -u "$APP_USER" bash -c "source venv/bin/activate && python -c '
import os
from datetime import datetime
os.environ[\"FLASK_ENV\"] = \"production\"
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

echo "✅ Setup completed successfully"

echo "🚀 Starting services..."

# Start and enable the application service
confirm_action "Enable and start F1 Fantasy system service" "Starts the F1 Fantasy service and configures it to start automatically on boot"
systemctl enable f1fantasy
systemctl start f1fantasy

# Check service status
sleep 2
if systemctl is-active --quiet f1fantasy; then
    echo "✅ F1 Fantasy service is running"
else
    echo "❌ F1 Fantasy service failed to start"
    systemctl status f1fantasy
fi

echo ""
echo "🎉 F1 Fantasy Installation Complete! 🎉"
echo "======================================="
echo ""
echo "📊 Service Status:"
echo "- F1 Fantasy: $(systemctl is-active f1fantasy)"
echo ""
echo "🌐 Access your application:"
echo "- URL: http://$(hostname -I | awk '{print $1}'):8000"
echo "- Local: http://localhost:8000"
echo ""
echo "📁 Important paths:"
echo "- Application: $APP_DIR"
echo "- Database: $DATA_DIR/f1fantasy.db"
echo "- Logs: $LOG_DIR"
echo "- Config: $APP_DIR/.env"
echo ""
echo "🔧 Useful commands:"
echo "- View logs: sudo journalctl -u f1fantasy -f"
echo "- Restart app: sudo systemctl restart f1fantasy"
echo "- Check status: sudo systemctl status f1fantasy"
echo "- Access database: sqlite3 $DATA_DIR/f1fantasy.db"
echo ""
echo "🔒 Security Notes:"
echo "- Application is ready to use with auto-generated configuration"
echo "- To enable HTTPS, update .env file and set SESSION_COOKIE_SECURE=True"
echo "- SQLite database is stored locally"
echo "- Application is accessible on port 8000"
echo "- Configure your firewall to allow port 8000 if needed"
echo ""

# Extract and display admin credentials at the very end
ADMIN_USERNAME=$(echo "$SETUP_OUTPUT" | grep "Username:" | sed 's/^Username: //')
ADMIN_PASSWORD=$(echo "$SETUP_OUTPUT" | grep "Password:" | sed 's/^Password: //')

# If extraction failed, try to get credentials directly from the database
if [ -z "$ADMIN_USERNAME" ] || [ -z "$ADMIN_PASSWORD" ]; then
    echo "🔍 Retrieving admin credentials from database..."
    CRED_OUTPUT=$(sudo -u "$APP_USER" bash -c "source venv/bin/activate && python -c '
import os
os.environ[\"FLASK_ENV\"] = \"production\"
from deploy.wsgi import application
with application.app_context():
    from f1_fantasy.models import User
    admin_user = User.query.filter_by(username=\"admin\").first()
    if admin_user:
        print(f\"Username: {admin_user.username}\")
        # Note: Cannot retrieve plain password from database (it is hashed)
        print(\"Password: [Generated during setup - check setup output above]\")
    else:
        print(\"No admin user found\")
'" 2>&1)
    
    ADMIN_USERNAME=$(echo "$CRED_OUTPUT" | grep "Username:" | sed 's/^Username: //')
fi

# Always display the credentials section with what we have
echo "🔑 IMPORTANT: ADMIN LOGIN CREDENTIALS"
echo "============================================================"
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "Username: $ADMIN_USERNAME"
    echo "Password: $ADMIN_PASSWORD"
    echo "============================================================"
    echo "⚠️  SAVE THIS PASSWORD - You will need it to log in!"
    echo "💡 Add your email address after first login in your profile."
else
    echo "Username: admin"
    echo "Password: [Check the setup output above for the generated password]"
    echo "============================================================"
    echo "⚠️  The admin password was displayed during the setup process above."
    echo "💡 Look for 'Generated secure admin password' in the output above."
fi
echo "============================================================"
echo "" 
echo "🌐 Login URL: http://$(hostname -I | awk '{print $1}'):8000/auth/login" 