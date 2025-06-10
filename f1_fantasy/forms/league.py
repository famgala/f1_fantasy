from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, IntegerField, FloatField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError

class LeagueForm(FlaskForm):
    """Form for creating and editing leagues."""
    name = StringField('League Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='League name must be between 3 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description cannot exceed 500 characters')
    ])
    is_public = BooleanField('Public League', default=True)
    
    # League Settings
    max_teams = IntegerField('Maximum Teams', validators=[
        DataRequired(),
        NumberRange(min=2, max=20, message='League must have between 2 and 20 teams')
    ], default=10)
    
    draft_type = SelectField('Draft Type', choices=[('snake', 'Snake'), ('random', 'Random')], default='snake', validators=[DataRequired()])
    
    point_system = SelectField('Point System', choices=[
        ('f1_default', 'F1 Default Scoring'),
        ('simple', 'Simple Scoring (1st = 20, 2nd = 19, etc.)'),
        ('points_race', 'Points Race (10th = 10, 9th/11th = 9, etc.)')
    ], validators=[DataRequired()])
    
    draft_date = DateTimeField('Draft Date',
                             format='%Y-%m-%d %H:%M',
                             validators=[Optional()],
                             description="When the draft will be held")

    submit = SubmitField('Save League')

    def validate_name(self, field):
        """Validate that the league name is unique."""
        from f1_fantasy.models import League
        league = League.query.filter_by(name=field.data).first()
        if league and (not hasattr(self, 'league') or league.id != self.league.id):
            raise ValidationError('This league name is already taken. Please choose another.')

    def validate_draft_date(self, field):
        """Validate that draft date is in the future."""
        if field.data and field.data < datetime.now():
            raise ValidationError('Draft date must be in the future')

class LeagueInviteForm(FlaskForm):
    """Form for inviting users to a league."""
    email = StringField('Email', validators=[
        DataRequired(),
        Length(max=120, message='Email cannot exceed 120 characters')
    ])
    role = SelectField('Role', choices=[
        ('member', 'Member'),
        ('commissioner', 'Commissioner')
    ], validators=[DataRequired()])
    can_edit_name = BooleanField('Can Edit Name')
    can_edit_description = BooleanField('Can Edit Description')
    can_edit_is_public = BooleanField('Can Edit Public/Private')
    can_edit_max_teams = BooleanField('Can Edit Max Teams')
    can_edit_draft_type = BooleanField('Can Edit Draft Type')
    can_edit_point_system = BooleanField('Can Edit Point System')
    submit = SubmitField('Send Invite') 