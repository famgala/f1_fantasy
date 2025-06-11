from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

class TeamForm(FlaskForm):
    """Form for creating and editing teams."""
    name = StringField('Team Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Team name must be between 3 and 100 characters')
    ])
    submit = SubmitField('Save Team')

    def __init__(self, league=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.league = league

    def validate_name(self, field):
        """Validate that the team name is unique within the league."""
        from f1_fantasy.models import Team
        team = Team.query.filter_by(name=field.data, league_id=self.league.id).first()
        if team and (not hasattr(self, 'team') or team.id != self.team.id):
            raise ValidationError('This team name is already taken in this league. Please choose another.') 