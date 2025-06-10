from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_security import login_required, roles_required, current_user
from f1_fantasy.models import db, User
from f1_fantasy.security import user_datastore
from flask_security.utils import hash_password
from wtforms import StringField, PasswordField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
import os
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

class ProfileForm(FlaskForm):
    """Form for editing user profile."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', 
                                   validators=[EqualTo('password', message='Passwords must match')])
    avatar = FileField('Avatar', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

    def validate_avatar(self, field):
        if field.data:
            # Check file size (max 2MB)
            if len(field.data.read()) > 2 * 1024 * 1024:
                raise ValidationError('File size must be less than 2MB')
            field.data.seek(0)  # Reset file pointer after reading

@bp.route('/')
def index():
    """Public landing page."""
    if current_user.is_authenticated:
        if current_user.has_role('admin'):
            return redirect(url_for('admin.index'))
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard view for authenticated users."""
    if current_user.has_role('admin'):
        return redirect(url_for('admin.index'))
    return render_template('dashboard.html')

@bp.route('/admin')
@login_required
@roles_required('admin')
def admin_dashboard():
    """Admin dashboard view - only accessible by admin users."""
    return render_template('admin/dashboard.html')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile view and edit."""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if username or email is taken by another user
        username_exists = User.query.filter(User.username == form.username.data, User.id != current_user.id).first()
        if username_exists:
            flash('Username already exists.', 'danger')
            return render_template('profile.html', form=form)
        
        email_exists = User.query.filter(User.email == form.email.data, User.id != current_user.id).first()
        if email_exists:
            flash('Email already exists.', 'danger')
            return render_template('profile.html', form=form)
        
        # Handle avatar upload
        if form.avatar.data:
            # Create avatars directory if it doesn't exist
            avatar_dir = os.path.join(current_app.static_folder, 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            
            # Delete old avatar if it exists
            if current_user.avatar:
                old_avatar_path = os.path.join(avatar_dir, current_user.avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            
            # Save new avatar
            filename = secure_filename(f"{current_user.id}_{form.avatar.data.filename}")
            form.avatar.data.save(os.path.join(avatar_dir, filename))
            current_user.avatar = filename
        
        # Update user
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        # Update password if provided
        if form.password.data:
            current_user.password = hash_password(form.password.data)
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html', form=form) 