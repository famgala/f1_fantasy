from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_security import roles_required
from f1_fantasy.models import db, League, User, Team, LeagueMember
from f1_fantasy.forms.league import LeagueForm, LeagueInviteForm
from sqlalchemy.exc import IntegrityError

bp = Blueprint('league', __name__, url_prefix='/league')

@bp.route('/')
@login_required
def index():
    """List all leagues the user is a member of."""
    if current_user.has_role('admin'):
        # Admin user can view all leagues regardless of ownership.
        user_leagues = League.query.all()
        owned_leagues = []
        commissioned_leagues = []
        public_leagues = League.query.filter_by(is_public=True).all()
        # Redirect to admin dashboard by default
        return redirect(url_for('admin.index'))
    else:
        # Regular users only see their leagues and public leagues
        user_leagues = current_user.leagues.all()
        owned_leagues = current_user.owned_leagues.all()
        commissioned_leagues = current_user.commissioned_leagues.all()
        public_leagues = League.query.filter_by(is_public=True).all()
    
    return render_template('league/index.html',
                         user_leagues=user_leagues,
                         owned_leagues=owned_leagues,
                         commissioned_leagues=commissioned_leagues,
                         public_leagues=public_leagues)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new league."""
    form = LeagueForm()
    if form.validate_on_submit():
        try:
            league = League(
                name=form.name.data,
                description=form.description.data,
                is_public=form.is_public.data,
                max_teams=form.max_teams.data,
                draft_type=form.draft_type.data,
                point_system=form.point_system.data,
                status=form.status.data,
                owner_id=current_user.id,
                commissioner_id=current_user.id
            )
            db.session.add(league)
            db.session.flush()  # flush so that league.id is available
            league_member = LeagueMember(league_id=league.id, user_id=current_user.id, role='commissioner',
                                        can_edit_name=True, can_edit_description=True, can_edit_is_public=True,
                                        can_edit_max_teams=True, can_edit_draft_type=True, can_edit_point_system=True,
                                        can_edit_draft_date=True)
            db.session.add(league_member)
            db.session.commit()
            flash('League created successfully!', 'success')
            return redirect(url_for('league.view', league_id=league.id))
        except IntegrityError:
            db.session.rollback()
            flash('A league with this name already exists.', 'error')
    
    return render_template('league/form.html', form=form, title='Create League')

@bp.route('/<int:league_id>')
@login_required
def view(league_id):
    """View league details."""
    league = League.query.get_or_404(league_id)
    if not league.is_public and current_user not in league.members:
        abort(403)
    
    teams = league.teams.all()
    members = league.members.all()
    is_commissioner = league.is_commissioner(current_user)
    is_owner = league.is_owner(current_user)
    
    return render_template('league/view.html',
                         league=league,
                         teams=teams,
                         members=members,
                         is_commissioner=is_commissioner,
                         is_owner=is_owner)

@bp.route('/<int:league_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(league_id):
    """Edit league settings."""
    league = League.query.get_or_404(league_id)
    league_member = LeagueMember.query.filter_by(league_id=league.id, user_id=current_user.id).first()
    is_owner = league.is_owner(current_user)
    is_commissioner = league.is_commissioner(current_user)
    can_edit = lambda field: is_owner or (is_commissioner and getattr(league_member, f'can_edit_{field}', False))

    form = LeagueForm(obj=league)
    if form.validate_on_submit():
        try:
            if can_edit('name'):
                league.name = form.name.data
            if can_edit('description'):
                league.description = form.description.data
            if can_edit('is_public'):
                league.is_public = form.is_public.data
            if can_edit('max_teams'):
                league.max_teams = form.max_teams.data
            if can_edit('draft_type'):
                league.draft_type = form.draft_type.data
            if can_edit('point_system'):
                league.point_system = form.point_system.data
            db.session.commit()
            flash('League settings updated successfully!', 'success')
            return redirect(url_for('league.view', league_id=league.id))
        except IntegrityError:
            db.session.rollback()
            flash('A league with this name already exists.', 'error')
    return render_template('league/form.html', form=form, league=league, title='Edit League', can_edit=can_edit)

@bp.route('/<int:league_id>/delete', methods=['POST'])
@login_required
def delete(league_id):
    """Delete a league."""
    league = League.query.get_or_404(league_id)
    if not league.is_owner(current_user):
        abort(403)
    
    if request.form.get('confirm') != league.name:
        flash('Please type the league name to confirm deletion.', 'error')
        return redirect(url_for('league.view', league_id=league.id))
    
    db.session.delete(league)
    db.session.commit()
    flash('League deleted successfully.', 'success')
    return redirect(url_for('league.index'))

@bp.route('/<int:league_id>/invite', methods=['GET', 'POST'])
@login_required
def invite(league_id):
    """Invite a user to join the league."""
    league = League.query.get_or_404(league_id)
    if not league.can_manage(current_user):
        abort(403)
    
    if league.is_full:
        flash('League is full.', 'error')
        return redirect(url_for('league.view', league_id=league.id))
    
    form = LeagueInviteForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('User not found.', 'error')
        elif user in league.members:
            flash('User is already a member.', 'error')
        else:
            league_member = LeagueMember(league_id=league.id, user_id=user.id, role=form.role.data)
            if form.role.data == 'commissioner':
                league_member.can_edit_name = form.can_edit_name.data
                league_member.can_edit_description = form.can_edit_description.data
                league_member.can_edit_is_public = form.can_edit_is_public.data
                league_member.can_edit_max_teams = form.can_edit_max_teams.data
                league_member.can_edit_draft_type = form.can_edit_draft_type.data
                league_member.can_edit_point_system = form.can_edit_point_system.data
            db.session.add(league_member)
            db.session.commit()
            flash('User invited successfully!', 'success')
            return redirect(url_for('league.view', league_id=league.id))
    
    return render_template('league/invite.html',
                         form=form,
                         league=league)

@bp.route('/<int:league_id>/members/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_member(league_id, user_id):
    """Remove a member from the league."""
    league = League.query.get_or_404(league_id)
    if not league.can_manage(current_user):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot remove yourself from the league.', 'error')
    elif user == league.owner:
        flash('You cannot remove the league owner.', 'error')
    else:
        league_member = LeagueMember.query.filter_by(league_id=league.id, user_id=user.id).first()
        if league_member:
            db.session.delete(league_member)
            db.session.commit()
            flash('Member removed successfully.', 'success')
    
    return redirect(url_for('league.view', league_id=league.id))

@bp.route('/<int:league_id>/members/<int:user_id>/role', methods=['POST'])
@login_required
def update_member_role(league_id, user_id):
    """Update a member's role in the league."""
    league = League.query.get_or_404(league_id)
    if not league.is_owner(current_user):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role not in ['member', 'commissioner']:
        abort(400)
    
    if user == current_user:
        flash('You cannot change your own role.', 'error')
    elif user == league.owner:
        flash('You cannot change the owner\'s role.', 'error')
    else:
        league_member = LeagueMember.query.filter_by(league_id=league.id, user_id=user.id).first()
        if league_member:
            league_member.role = new_role
            db.session.commit()
            flash('Member role updated successfully.', 'success')
    
    return redirect(url_for('league.view', league_id=league.id))

@bp.route('/<int:league_id>/join', methods=['POST'])
@login_required
def join(league_id):
    """Join a public league."""
    league = League.query.get_or_404(league_id)
    if not league.is_public:
        abort(403)
    
    existing = LeagueMember.query.filter_by(league_id=league.id, user_id=current_user.id).first()
    if existing:
        flash('You are already a member of this league.', 'error')
    elif league.is_full:
        flash('League is full.', 'error')
    else:
        league_member = LeagueMember(league_id=league.id, user_id=current_user.id, role='member')
        db.session.add(league_member)
        db.session.commit()
        flash('You have joined the league!', 'success')
    
    return redirect(url_for('league.view', league_id=league.id))

@bp.route('/<int:league_id>/leave', methods=['POST'])
@login_required
def leave(league_id):
    """Leave a league."""
    league = League.query.get_or_404(league_id)
    if current_user == league.owner:
        flash('League owner cannot leave the league.', 'error')
    else:
        league_member = LeagueMember.query.filter_by(league_id=league.id, user_id=current_user.id).first()
        if league_member:
            db.session.delete(league_member)
            db.session.commit()
            flash('You have left the league.', 'success')
    
    return redirect(url_for('league.index')) 