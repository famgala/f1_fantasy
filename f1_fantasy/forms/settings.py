from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length

class SMTPForm(FlaskForm):
    """SMTP server settings form."""
    smtp_host = StringField('SMTP Host', validators=[DataRequired(), Length(max=256)])
    smtp_port = IntegerField('SMTP Port', validators=[DataRequired(), NumberRange(min=1, max=65535)])
    smtp_username = StringField('SMTP Username', validators=[DataRequired(), Length(max=256)])
    smtp_password = StringField('SMTP Password', validators=[DataRequired(), Length(max=256)])
    smtp_use_tls = BooleanField('Use TLS')
    smtp_from_email = StringField('From Email', validators=[DataRequired(), Email(), Length(max=256)])
    smtp_from_name = StringField('From Name', validators=[DataRequired(), Length(max=256)])

class LeagueForm(FlaskForm):
    """League settings form."""
    max_leagues_per_user = IntegerField('Max Leagues per User', 
        validators=[DataRequired(), NumberRange(min=1, max=100)])
    max_teams_per_league = IntegerField('Max Teams per League', 
        validators=[DataRequired(), NumberRange(min=2, max=100)])
    min_teams_per_league = IntegerField('Min Teams per League', 
        validators=[DataRequired(), NumberRange(min=2, max=100)])
    max_budget = IntegerField('Max Team Budget', 
        validators=[DataRequired(), NumberRange(min=1000000, max=100000000)])
    allow_public_leagues = BooleanField('Allow Public Leagues')
    require_league_approval = BooleanField('Require League Approval')

class GeneralForm(FlaskForm):
    """General application settings form."""
    app_name = StringField('Application Name', validators=[DataRequired(), Length(max=64)])
    app_description = TextAreaField('Application Description', validators=[Optional(), Length(max=512)])
    maintenance_mode = BooleanField('Maintenance Mode')
    allow_registration = BooleanField('Allow New Registrations')
    require_email_confirmation = BooleanField('Require Email Confirmation')
    session_timeout = IntegerField('Session Timeout (minutes)', 
        validators=[DataRequired(), NumberRange(min=5, max=1440)])

class SettingsForm(FlaskForm):
    """Combined settings form."""
    category = SelectField('Category', choices=[
        ('general', 'General Settings'),
        ('league', 'League Settings')
    ])
    
    # General settings
    app_name = StringField('Application Name', validators=[DataRequired(), Length(max=64)])
    app_description = TextAreaField('Application Description', validators=[Optional(), Length(max=512)])
    maintenance_mode = BooleanField('Maintenance Mode')
    allow_registration = BooleanField('Allow New Registrations')
    require_email_confirmation = BooleanField('Require Email Confirmation')
    session_timeout = IntegerField('Session Timeout (minutes)', 
        validators=[DataRequired(), NumberRange(min=5, max=1440)])
    
    # League settings
    max_leagues_per_user = IntegerField('Max Leagues per User', 
        validators=[Optional(), NumberRange(min=1, max=100)])
    max_teams_per_league = IntegerField('Max Teams per League', 
        validators=[Optional(), NumberRange(min=2, max=100)])
    min_teams_per_league = IntegerField('Min Teams per League', 
        validators=[Optional(), NumberRange(min=2, max=100)])
    max_budget = IntegerField('Max Team Budget', 
        validators=[Optional(), NumberRange(min=1000000, max=100000000)])
    allow_public_leagues = BooleanField('Allow Public Leagues')
    require_league_approval = BooleanField('Require League Approval') 