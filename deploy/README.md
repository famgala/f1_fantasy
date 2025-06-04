# F1 Fantasy Test Stack Deployment

This directory contains everything needed to deploy F1 Fantasy as a **permanent test stack** with a simple, production-like setup using SQLite.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Internet    │────│   Port 8000     │────│   Gunicorn      │
│                 │    │  (Direct Access)│    │  (WSGI Server)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │     SQLite      │────│  F1 Fantasy App │
                       │   (Database)    │    │  (Flask App)    │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Installation

**Prerequisites:** Ubuntu 20.04+ or Debian 11+ with sudo access

```bash
# Clone your repository to the server
git clone <your-repo-url> f1fantasy
cd f1fantasy

# Make the installation script executable
chmod +x deploy/install.sh

# Run the installation (as root)
sudo ./deploy/install.sh
```

That's it! The script will install everything automatically and the app will be accessible on port 8000.

## 📁 File Structure

```
deploy/
├── install.sh          # Automated installation script
├── test.py            # Test environment Flask configuration
├── wsgi.py            # WSGI entry point for Gunicorn
├── gunicorn.conf.py   # Gunicorn server configuration
├── f1fantasy.service  # Systemd service definition
├── environment.env    # Environment variables template
├── backup.sh          # Database and file backup script
└── README.md          # This documentation
```

## 🔧 Manual Installation Steps

If you prefer to install manually:

### 1. System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    git curl htop ufw
```

### 2. Application Setup

```bash
# Create application user and directories
sudo useradd -r -s /bin/bash -d /opt/f1fantasy f1fantasy
sudo mkdir -p /opt/f1fantasy /opt/f1fantasy/data /var/log/f1fantasy
sudo chown f1fantasy:f1fantasy /opt/f1fantasy /opt/f1fantasy/data /var/log/f1fantasy

# Copy application files
sudo cp -r . /opt/f1fantasy/
sudo chown -R f1fantasy:f1fantasy /opt/f1fantasy

# Create virtual environment and install dependencies
sudo -u f1fantasy python3 -m venv /opt/f1fantasy/venv
sudo -u f1fantasy /opt/f1fantasy/venv/bin/pip install -r /opt/f1fantasy/requirements.txt
sudo -u f1fantasy /opt/f1fantasy/venv/bin/pip install gunicorn
```

### 3. Configuration

```bash
# Copy environment file
sudo -u f1fantasy cp /opt/f1fantasy/deploy/environment.env /opt/f1fantasy/.env

# Edit configuration (update secrets, etc.)
sudo -u f1fantasy nano /opt/f1fantasy/.env
```

### 4. Services Setup

```bash
# Install systemd service
sudo cp /opt/f1fantasy/deploy/f1fantasy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable f1fantasy
```

### 5. Database Initialization

```bash
cd /opt/f1fantasy
sudo -u f1fantasy bash -c "source venv/bin/activate && FLASK_ENV=testing python -c '
from deploy.wsgi import application
with application.app_context():
    from f1_fantasy.models import db
    db.create_all()
'"
```

### 6. Start Services

```bash
sudo systemctl start f1fantasy
```

## 🔐 Security Configuration

### Firewall Setup

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw enable
```

## 📊 Monitoring & Management

### Service Management

```bash
# Check service status
sudo systemctl status f1fantasy

# View logs
sudo journalctl -u f1fantasy -f

# Restart application
sudo systemctl restart f1fantasy
```

### Log Files

- Application logs: `/var/log/f1fantasy/app.log`
- Gunicorn logs: `/var/log/f1fantasy/gunicorn_*.log`
- System logs: `journalctl -u f1fantasy`

### Performance Monitoring

```bash
# Check system resources
htop

# Monitor application processes
ps aux | grep gunicorn

# Access SQLite database
sqlite3 /opt/f1fantasy/data/f1fantasy_test.db
```

## 💾 Backup & Recovery

### Automated Backups

```bash
# Make backup script executable
chmod +x /opt/f1fantasy/deploy/backup.sh

# Run backup manually
sudo /opt/f1fantasy/deploy/backup.sh

# Schedule daily backups (add to crontab)
echo "0 2 * * * /opt/f1fantasy/deploy/backup.sh" | sudo crontab -
```

### Manual Backup

```bash
# Database backup
cp /opt/f1fantasy/data/f1fantasy_test.db backup_$(date +%Y%m%d).db

# Files backup
tar -czf f1fantasy_backup.tar.gz /opt/f1fantasy
```

### Recovery

```bash
# Stop service first
sudo systemctl stop f1fantasy

# Database restore
cp backup_YYYYMMDD.db /opt/f1fantasy/data/f1fantasy_test.db
sudo chown f1fantasy:f1fantasy /opt/f1fantasy/data/f1fantasy_test.db

# Start service
sudo systemctl start f1fantasy
```

## 🔧 Configuration Options

### Environment Variables

Edit `/opt/f1fantasy/.env`:

```bash
# Security (REQUIRED)
SECRET_KEY=your-unique-secret-key
SECURITY_PASSWORD_SALT=your-unique-salt

# Database (SQLite)
DATABASE_URL=sqlite:////opt/f1fantasy/data/f1fantasy_test.db

# F1 API (optional)
F1_API_KEY=your-f1-api-key-if-needed
```

### Scaling

To handle more traffic:

1. **Increase Gunicorn workers** in `gunicorn.conf.py`
2. **Add more memory/CPU** to the server
3. **Consider switching to PostgreSQL** for better performance

## 🌐 Access

### Direct Access

The application is accessible directly on port 8000:

- **Local**: `http://localhost:8000`
- **Remote**: `http://YOUR_SERVER_IP:8000`

### Setting up a Domain (Optional)

If you want to use a domain name, you can:

1. Point your domain to the server IP
2. Set up a reverse proxy (nginx) separately
3. Use a service like Cloudflare for SSL termination

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**
```bash
sudo journalctl -u f1fantasy -n 50
```

**Database file missing:**
```bash
ls -la /opt/f1fantasy/data/
sudo -u f1fantasy touch /opt/f1fantasy/data/f1fantasy_test.db
```

**Permission issues:**
```bash
sudo chown -R f1fantasy:f1fantasy /opt/f1fantasy
sudo chmod +x /opt/f1fantasy/deploy/wsgi.py
```

**Port 8000 not accessible:**
```bash
sudo ufw status
sudo systemctl status f1fantasy
netstat -tlnp | grep 8000
```

### Performance Issues

**High memory usage:**
- Reduce Gunicorn workers in `gunicorn.conf.py`
- Check for memory leaks in logs
- Restart service: `sudo systemctl restart f1fantasy`

**SQLite locking issues:**
- Check for long-running transactions
- Consider connection pooling
- Monitor database access patterns

## 📞 Support

For issues or questions:

1. Check the application logs: `sudo journalctl -u f1fantasy -f`
2. Review this documentation
3. Check the F1 Fantasy repository issues
4. Contact the development team

---

**🏁 Happy Testing! 🏁**

## 🆚 Differences from Production

This test stack differs from a production setup in several ways:

- **Database**: SQLite instead of PostgreSQL
- **Reverse Proxy**: Direct port access instead of nginx
- **SSL**: HTTP instead of HTTPS
- **Caching**: Simple file-based instead of Redis
- **Security**: Relaxed settings for testing
- **Performance**: Lower resource allocation

This makes it perfect for testing, development, and proof-of-concept deployments! 