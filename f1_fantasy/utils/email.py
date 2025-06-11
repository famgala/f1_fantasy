from flask import current_app, render_template
from flask_mail import Message
from ..extensions import mail

def send_invite_email(email, league_name, invite_url):
    """Send a league invitation email."""
    msg = Message(
        subject=f'Invitation to join {league_name}',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email]
    )
    
    msg.html = render_template(
        'email/league_invite.html',
        league_name=league_name,
        invite_url=invite_url
    )
    
    mail.send(msg) 