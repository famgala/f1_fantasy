from datetime import datetime
from . import db

class League(db.Model):
    """League model for F1 Fantasy leagues."""
    __tablename__ = 'leagues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    owner = db.relationship('User', backref=db.backref('owned_leagues', lazy='dynamic'))
    teams = db.relationship('Team', backref='league', lazy='dynamic', cascade='all, delete-orphan')
    members = db.relationship('User', 
                            secondary='league_members',
                            backref=db.backref('leagues', lazy='dynamic'),
                            lazy='dynamic')

    def __repr__(self):
        return f'<League {self.name}>'

# Association table for league members
league_members = db.Table('league_members',
    db.Column('league_id', db.Integer, db.ForeignKey('leagues.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
) 