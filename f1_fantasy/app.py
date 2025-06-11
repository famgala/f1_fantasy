from flask import Flask, render_template, redirect, url_for
from flask_security import current_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from f1_fantasy.models import db, User, Role, Settings, League, Team
from f1_fantasy.security import init_security, create_default_roles
from f1_fantasy.setup import init_setup
import os
import logging
from f1_fantasy.views.main import bp as main_bp
from f1_fantasy.views.auth import bp as auth_bp
from f1_fantasy.views.admin import bp as admin_bp
from f1_fantasy.views.league import bp as league_bp
from f1_fantasy.views.team import bp as team_bp
import click
from f1_fantasy.extensions import mail

# Initialize Flask-Migrate
migrate = Migrate()

def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///dev_f1fantasy.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key'),
        SECURITY_PASSWORD_SALT=os.getenv('SECURITY_PASSWORD_SALT', 'dev-salt'),
    )
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Add Flask-Security specific logging
    security_logger = logging.getLogger('flask_security')
    security_logger.setLevel(logging.DEBUG)
    
    # Add console handler for Flask-Security
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] in %(module)s: %(message)s')
    console_handler.setFormatter(formatter)
    security_logger.addHandler(console_handler)
    
    # Add file handler for Flask-Security
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, 'security.log'))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    security_logger.addHandler(file_handler)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    mail.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created successfully")
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize security
    init_security(app)
    
    # Initialize setup wizard
    init_setup(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(league_bp)
    app.register_blueprint(team_bp)
    
    # Add CLI commands
    @app.cli.command('check-roles')
    def check_roles():
        """Check user roles in the database."""
        with app.app_context():
            users = User.query.all()
            for user in users:
                print(f"\nUser: {user.username} ({user.email})")
                print("Roles:", [role.name for role in user.roles])
    
    return app