from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_security import login_required, logout_user, roles_required
from flask_login import login_user, logout_user, login_required
from ..models import db, User, League, LeagueMember
from ..forms.auth import LoginForm, RegistrationForm
from ..utils.tokens import verify_invite_token, process_invite_token

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    return redirect(url_for('security.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check for invite token
    invite_token = request.args.get('token')
    invite_data = None
    if invite_token:
        invite_data = process_invite_token(invite_token)
        if not invite_data:
            flash('Invalid or expired invitation link.', 'error')
            return redirect(url_for('auth.register'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create user
        user = User(
            username=form.username.data,
            email=form.email.data,
            visibility='public'  # Default to public visibility
        )
        user.set_password(form.password.data)
        db.session.add(user)
        
        # Process league invite if present
        if invite_data:
            league = League.query.get(invite_data['league_id'])
            if league and not league.is_member(user):
                league_member = LeagueMember(
                    league_id=league.id,
                    user_id=user.id,
                    role=invite_data['role'],
                    **invite_data['permissions']
                )
                db.session.add(league_member)
        
        db.session.commit()
        
        # Log the user in
        login_user(user)
        flash('Registration successful!', 'success')
        
        # Redirect to league if invited, otherwise to index
        if invite_data:
            return redirect(url_for('league.view', league_id=invite_data['league_id']))
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html', form=form, invite_data=invite_data) 