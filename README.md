# 🏁 F1 Fantasy League

A comprehensive Formula 1 fantasy league web application built with Flask. Create your fantasy F1 team, compete with friends, and track your performance throughout the racing season.

## 🚀 Features

- **User Management**: Secure user registration and authentication with Flask-Security
- **Fantasy Teams**: Create and manage your fantasy F1 team with driver selections
- **League System**: Create or join leagues to compete with friends and other fans
- **Real-time Data**: Integration with FastF1 for live race data and statistics
- **Scoring System**: Comprehensive points system based on real F1 race results
- **Draft System**: Multiple draft formats including snake draft and auction
- **Admin Panel**: Full administrative interface for league management
- **Responsive Design**: Modern, mobile-friendly Bootstrap UI

## 📋 Prerequisites

- **Operating System**: Ubuntu 20.04+ or similar Linux distribution
- **Python**: 3.8 or higher
- **System Access**: sudo privileges for installation
- **Network**: Internet connection for F1 data synchronization

## ⚡ Quick Install

### Option 1: Automated Installation (Recommended)

**Fully automated (no prompts)**:
```bash
curl -sSL https://raw.githubusercontent.com/famgala/f1_fantasy/main/deploy/install.sh | sudo bash
```

**Or if you prefer to review the script first**:
```bash
wget https://raw.githubusercontent.com/famgala/f1_fantasy/main/deploy/install.sh
chmod +x install.sh
sudo ./install.sh
```

**Interactive mode (with confirmation prompts)**:
```bash
wget https://raw.githubusercontent.com/famgala/f1_fantasy/main/deploy/install.sh
chmod +x install.sh
sudo ./install.sh --interactive
```

**Access your application**:
- Open your browser to `http://your-server-ip:8000`
- Login with the admin credentials displayed during setup

The installer will:
- ✅ Clone the latest code from GitHub
- ✅ Install all system dependencies
- ✅ Create a dedicated `f1fantasy` system user
- ✅ Set up Python virtual environment with all dependencies
- ✅ Configure SQLite database with proper schema
- ✅ Create admin user with secure credentials
- ✅ Set up systemd service for auto-start
- ✅ Configure firewall rules
- ✅ Generate secure encryption keys

### Option 2: Development Setup

1. **Clone and setup environment**:
   ```bash
   git clone https://github.com/famgala/f1_fantasy.git
   cd f1_fantasy
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run in development mode**:
   ```bash
   cd deploy
   python3 wsgi.py
   ```

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables (automatically configured by installer):

- `SECRET_KEY`: Flask secret key for session security
- `SECURITY_PASSWORD_SALT`: Salt for password hashing
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Application environment (testing/production)

### Database

- **Default**: SQLite database stored in `/opt/f1fantasy/data/`
- **Schema**: Automatically created with proper Flask-Security tables
- **Migrations**: Handled automatically by Flask-Migrate

## 👤 Admin Access

After installation, you'll receive admin credentials in this format:

```
============================================================
🔑 IMPORTANT: ADMIN LOGIN CREDENTIALS
============================================================
Email:    test@famgala.com
Username: test
Password: [GENERATED_PASSWORD]
============================================================
⚠️  SAVE THIS PASSWORD - You will need it to log in!
============================================================
```

**First Login Steps**:
1. Navigate to `http://your-server:8000/auth/login`
2. Use the provided email and password
3. Access admin panel at `/admin`
4. Update your profile and change password if desired

## 🎮 Usage

### For Players

1. **Register**: Create an account or have an admin invite you
2. **Join League**: Use invite codes to join existing leagues
3. **Draft Team**: Participate in the draft to select your drivers
4. **Track Performance**: Monitor your team's performance throughout the season
5. **Compete**: Climb the leaderboard and win your league!

### For League Commissioners

1. **Create League**: Set up new leagues with custom settings
2. **Invite Players**: Generate invite codes for participants
3. **Manage Draft**: Configure and oversee draft sessions
4. **Scoring Rules**: Customize point systems for your league
5. **Season Management**: Handle trades, waivers, and adjustments

## 🔒 Security Features

- **Flask-Security**: Industry-standard authentication and authorization
- **Password Hashing**: Bcrypt encryption for secure password storage
- **CSRF Protection**: Built-in protection against cross-site request forgery
- **Session Security**: Secure session management with configurable timeouts
- **Role-based Access**: Admin and user role separation
- **Firewall Configuration**: Automated UFW setup blocking unnecessary ports

## 📊 System Management

### Service Management
```bash
# Check status
sudo systemctl status f1fantasy

# Start/Stop service
sudo systemctl start f1fantasy
sudo systemctl stop f1fantasy

# View logs
sudo journalctl -u f1fantasy -f

# Restart service
sudo systemctl restart f1fantasy
```

### Database Management
```bash
# Access database
sqlite3 /opt/f1fantasy/data/f1fantasy_test.db

# Backup database
sudo /opt/f1fantasy/deploy/backup.sh
```

### Application Logs
- **Location**: `/var/log/f1fantasy/app.log`
- **Rotation**: Automatic log rotation (10MB max, 10 backups)
- **Level**: Configurable via `LOG_LEVEL` environment variable

## 🛠️ Development

### Project Structure
```
f1_fantasy/
├── f1_fantasy/           # Main application package
│   ├── models.py         # Database models
│   ├── security.py       # Authentication & authorization
│   └── ...
├── deploy/               # Deployment scripts and configs
│   ├── install.sh        # Automated installer
│   ├── wsgi.py          # WSGI entry point
│   └── ...
├── templates/            # HTML templates
├── requirements.txt      # Python dependencies
└── setup.py             # Package configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit: `git commit -m "Description of changes"`
5. Push: `git push origin feature-name`
6. Create a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Installation fails with permission errors**:
```bash
# Ensure you're running with sudo
sudo ./deploy/install.sh
```

**Application won't start**:
```bash
# Check service status
sudo systemctl status f1fantasy

# Check logs
sudo journalctl -u f1fantasy -f
```

**Can't access on port 8000**:
```bash
# Check firewall
sudo ufw status

# Ensure port is open
sudo ufw allow 8000
```

**Database errors**:
```bash
# Check database permissions
ls -la /opt/f1fantasy/data/

# Recreate database (⚠️ will lose data)
sudo rm /opt/f1fantasy/data/*.db
sudo systemctl restart f1fantasy
```

### Getting Help

- **Issues**: Report bugs on [GitHub Issues](https://github.com/famgala/f1_fantasy/issues)
- **Discussions**: Join discussions on [GitHub Discussions](https://github.com/famgala/f1_fantasy/discussions)
- **Wiki**: Check the [project wiki](https://github.com/famgala/f1_fantasy/wiki) for detailed guides

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastF1**: For providing excellent F1 data and telemetry
- **Flask**: For the robust web framework
- **Flask-Security**: For comprehensive authentication features
- **Bootstrap**: For responsive UI components
- **Formula 1**: For the amazing sport that inspired this project

## 📈 Roadmap

- [ ] Live timing integration during race weekends
- [ ] Advanced statistics and analytics
- [ ] Mobile app companion
- [ ] Multi-season league support
- [ ] Enhanced trade system
- [ ] Social features and chat
- [ ] Custom scoring formulas
- [ ] Integration with F1 Fantasy official

---

**Happy Racing! 🏎️💨**