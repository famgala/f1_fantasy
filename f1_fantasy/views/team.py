from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from f1_fantasy.models import db, Team, League
from f1_fantasy.forms.team import TeamForm

bp = Blueprint('team', __name__, url_prefix='/team')

@bp.route('/create/<int:league_id>', methods=['GET', 'POST'])
@login_required
def create(league_id):
    """Create a new team in a league."""
    league = League.query.get_or_404(league_id)
    
    # Check if user is a member of the league
    if current_user not in league.members:
        flash('You must be a member of the league to create a team.', 'error')
        return redirect(url_for('league.view', league_id=league.id))
    
    # Check if user already has a team in this league
    existing_team = Team.query.filter_by(league_id=league.id, owner_id=current_user.id).first()
    if existing_team:
        flash('You already have a team in this league.', 'error')
        return redirect(url_for('league.view', league_id=league.id))
    
    # Check if league is full
    if league.is_full:
        flash('This league is full.', 'error')
        return redirect(url_for('league.view', league_id=league.id))
    
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            league_id=league.id,
            owner_id=current_user.id
        )
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('team.view', team_id=team.id))
    
    return render_template('team/form.html', form=form, league=league, title='Create Team')

@bp.route('/<int:team_id>')
@login_required
def view(team_id):
    """View team details."""
    team = Team.query.get_or_404(team_id)
    
    # Check if user has permission to view the team
    if not team.league.is_public and current_user not in team.league.members:
        abort(403)
    
    return render_template('team/view.html', team=team) 