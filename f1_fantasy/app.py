from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_security import current_user, login_required
from f1_fantasy.models import db
from f1_fantasy.security import init_security, create_default_roles
from f1_fantasy.setup import init_setup
import os

# Create main blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

def create_app(config=None):
    app = Flask(__name__)
    
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
    
    # Register blueprints
    app.register_blueprint(main)
    
    # Create database tables and run setup wizard
    with app.app_context():
        db.create_all()
        create_default_roles()
        init_setup(app)
    
    return app 