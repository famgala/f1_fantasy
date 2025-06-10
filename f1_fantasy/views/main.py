from flask import Blueprint, render_template, redirect, url_for
from flask_security import login_required, roles_required, current_user

bp = Blueprint('main', __name__)

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