from datetime import datetime, timedelta
import jwt
from flask import current_app
from f1_fantasy.models import League, User

def generate_invite_token(league_id, email, role='member', permissions=None, expires_in=7):
    """Generate a JWT token for a league invite."""
    payload = {
        'league_id': league_id,
        'email': email,
        'role': role,
        'permissions': permissions or {},
        'exp': datetime.utcnow() + timedelta(days=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_invite_token(token):
    """Verify and decode a league invite token."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def process_invite_token(token):
    """Process a league invite token and return league and role info."""
    payload = verify_invite_token(token)
    if not payload:
        return None
    
    league = League.query.get(payload['league_id'])
    if not league:
        return None
    
    return {
        'league': league,
        'role': payload['role'],
        'permissions': payload['permissions'],
        'email': payload['email']
    } 