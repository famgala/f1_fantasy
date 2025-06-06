from flask import Blueprint, redirect, url_for
from flask_security import login_required, logout_user, roles_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    return redirect(url_for('security.login')) 