import secrets
import logging
from datetime import datetime
from flask import Flask, request, current_app, redirect, url_for
from flask_login import current_user
from flask_security import Security, SQLAlchemyUserDatastore, hash_password, verify_password
from f1_fantasy.models import db, User, Role

# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()
logger = logging.getLogger('flask_security')

def init_security(app: Flask) -> None:
    """Initialize security config and hooks for the Flask application."""
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
        SECURITY_USER_IDENTITY_ATTRIBUTES=[
            {"email": {"mapper": lambda x: x.lower(), "case_insensitive": True}}
        ],
        SECURITY_PASSWORD_LENGTH_MIN=8,
        SECURITY_EMAIL_VALIDATOR_ARGS={"check_deliverability": False},
        SECURITY_SEND_REGISTER_EMAIL=False,
        SECURITY_SEND_PASSWORD_CHANGE_EMAIL=False,
        SECURITY_SEND_PASSWORD_RESET_EMAIL=False,
    )
    # Do NOT call security.init_app here!
    # Only set up hooks and config.
    
    @app.before_request
    def before_request():
        if request.endpoint == 'security.register' and request.method == 'POST':
            email = request.form.get('email', '').lower()
            if email:
                # Generate username from email (everything before @)
                username = email.split('@')[0]
                # Add form data to request
                request.form = request.form.copy()
                request.form['username'] = username

    # Add request logging for login attempts - only after security is initialized
    @app.before_request
    def log_request_info():
        if not app.config.get('TESTING') and request.path == '/auth/login' and request.method == 'POST':
            logger.debug('Login attempt received')
            email = request.form.get("email", "").lower()
            password = request.form.get("password", "")
            
            logger.debug(f'Login attempt details:')
            logger.debug(f'  Email: {email}')
            logger.debug(f'  Password length: {len(password)}')
            logger.debug(f'  Remember: {request.form.get("remember")}')
            
            try:
                # Try to find user by email
                user = User.query.filter_by(email=email).first()
                
                logger.debug('User lookup results:')
                logger.debug(f'  Found by email: {user is not None}')
                
                if user:
                    logger.debug(f'  User details: id={user.id}, active={user.active}')
                    logger.debug(f'  Password hash: {user.password[:20]}...')
                    # Try password verification
                    is_valid = verify_password(password, user.password)
                    logger.debug(f'  Password verification result: {is_valid}')
            except Exception as e:
                logger.error(f'Error during login attempt logging: {str(e)}')
    
    # Add authentication success/failure logging
    @app.after_request
    def log_auth_result(response):
        if not app.config.get('TESTING') and request.path == '/auth/login' and request.method == 'POST':
            if response.status_code == 302:  # Successful login redirects
                logger.debug('Login successful')
            else:
                logger.debug('Login failed')
                logger.debug(f'Response status: {response.status_code}')
                logger.debug(f'Response headers: {dict(response.headers)}')
                # Log the response body for debugging
                logger.debug(f'Response body: {response.get_data(as_text=True)[:200]}...')
        return response

    # Add post-login handler to redirect admins
    @app.after_request
    def post_login_handler(response):
        if (not app.config.get('TESTING') and 
            request.path == '/auth/login' and 
            request.method == 'POST' and 
            response.status_code == 302 and  # Successful login redirect
            current_user.is_authenticated and 
            current_user.has_role('admin')):
            return redirect(url_for('admin.index'))
        return response

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