from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, current_app
from flask_security import login_required, roles_required, current_user
from flask_security.utils import hash_password
from functools import wraps
from f1_fantasy.forms.settings import SettingsForm
from f1_fantasy.models.settings import Settings
from f1_fantasy.models import db, User, Role, League, Team
from f1_fantasy.security import user_datastore
from datetime import datetime
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from flask_wtf import FlaskForm

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
@login_required
@roles_required('admin')
def before_request():
    """Ensure all admin routes require admin role."""
    pass

@bp.route('/')
@login_required
@roles_required('admin')
def index():
    """Admin dashboard view."""
    # Get statistics for the dashboard
    users = User.query.all() or []
    leagues = League.query.all() or []
    teams = Team.query.all() or []
    
    # Get system status
    maintenance_mode = Settings.get('maintenance_mode', 'false').lower() == 'true'
    smtp_configured = all([
        current_app.config.get('MAIL_SERVER'),
        current_app.config.get('MAIL_PORT'),
        current_app.config.get('MAIL_USERNAME'),
        current_app.config.get('MAIL_PASSWORD')
    ])
    
    return render_template('admin/dashboard.html',
                         users=users,
                         leagues=leagues,
                         teams=teams,
                         maintenance_mode=maintenance_mode,
                         smtp_configured=smtp_configured,
                         now=datetime.now)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def settings():
    """Admin settings management view."""
    form = SettingsForm()
    
    # Get current category from query param or default to general
    category = request.args.get('category', 'general')
    form.category.data = category
    
    if form.validate_on_submit():
        # Update settings based on category
        if category == 'general':
            Settings.set('app_name', form.app_name.data, 
                'Application name displayed in the title and header', 
                'general', current_user.id)
            Settings.set('app_description', form.app_description.data,
                'Application description shown on the homepage',
                'general', current_user.id)
            Settings.set('maintenance_mode', str(form.maintenance_mode.data),
                'Enable maintenance mode to restrict access to admin users only',
                'general', current_user.id)
            Settings.set('allow_registration', str(form.allow_registration.data),
                'Allow new users to register',
                'general', current_user.id)
            Settings.set('require_email_confirmation', str(form.require_email_confirmation.data),
                'Require email confirmation for new registrations',
                'general', current_user.id)
            Settings.set('session_timeout', str(form.session_timeout.data),
                'Session timeout in minutes',
                'general', current_user.id)
            
        elif category == 'league':
            Settings.set('max_leagues_per_user', str(form.max_leagues_per_user.data),
                'Maximum number of leagues a user can join',
                'league', current_user.id)
            Settings.set('max_teams_per_league', str(form.max_teams_per_league.data),
                'Maximum number of teams allowed in a league',
                'league', current_user.id)
            Settings.set('min_teams_per_league', str(form.min_teams_per_league.data),
                'Minimum number of teams required in a league',
                'league', current_user.id)
            Settings.set('max_budget', str(form.max_budget.data),
                'Maximum budget for team creation',
                'league', current_user.id)
            Settings.set('allow_public_leagues', str(form.allow_public_leagues.data),
                'Allow creation of public leagues',
                'league', current_user.id)
        
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('admin.settings', category=category))
    
    # Load current settings into form
    settings = Settings.get_all_by_category(category)
    for setting in settings:
        if hasattr(form, setting.key):
            field = getattr(form, setting.key)
            if isinstance(field, BooleanField):
                field.data = setting.value.lower() == 'true'
            elif isinstance(field, IntegerField):
                field.data = int(setting.value) if setting.value else None
            else:
                field.data = setting.value
    
    # Add SMTP configuration info for display
    smtp_info = {
        'host': current_app.config.get('MAIL_SERVER'),
        'port': current_app.config.get('MAIL_PORT'),
        'use_tls': current_app.config.get('MAIL_USE_TLS'),
        'username': current_app.config.get('MAIL_USERNAME'),
        'from_email': current_app.config.get('MAIL_DEFAULT_SENDER')
    }
    
    return render_template('admin/settings.html', 
                         form=form, 
                         category=category,
                         smtp_info=smtp_info)

@bp.route('/users')
@login_required
@roles_required('admin')
def users():
    """Admin user management view."""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

class UserForm(FlaskForm):
    """Form for creating and editing users."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[EqualTo('password', message='Passwords must match')])
    active = BooleanField('Active')
    roles = SelectMultipleField('Roles', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(role.id, role.name) for role in Role.query.all()]

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_user():
    """Create a new user."""
    form = UserForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Create User')
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Create User')
        
        # Create new user
        user = user_datastore.create_user(
            username=form.username.data,
            email=form.email.data,
            password=hash_password(form.password.data),
            active=form.active.data
        )
        
        # Add roles
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user_datastore.add_role_to_user(user, role)
        
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='Create User')

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_user(user_id):
    """Edit an existing user."""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    # Don't require password for editing
    form.password.validators = [Optional(), Length(min=8)]
    form.confirm_password.validators = [Optional(), EqualTo('password', message='Passwords must match')]
    
    if form.validate_on_submit():
        # Check if username or email is taken by another user
        username_exists = User.query.filter(User.username == form.username.data, User.id != user.id).first()
        if username_exists:
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Edit User')
        
        email_exists = User.query.filter(User.email == form.email.data, User.id != user.id).first()
        if email_exists:
            flash('Email already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Edit User')
        
        # Update user
        user.username = form.username.data
        user.email = form.email.data
        user.active = form.active.data
        
        # Update password if provided
        if form.password.data:
            user.password = hash_password(form.password.data)
        
        # Update roles
        user.roles = []
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user_datastore.add_role_to_user(user, role)
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    # Pre-populate roles
    form.roles.data = [role.id for role in user.roles]
    return render_template('admin/user_form.html', form=form, title='Edit User')

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def delete_user(user_id):
    """Delete a user."""
    if user_id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users')) 