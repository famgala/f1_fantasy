from datetime import datetime
from . import db
from sqlalchemy.ext.associationproxy import association_proxy

class LeagueMember(db.Model):
    __tablename__ = 'league_members'
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='member')  # Options: member, commissioner

    # Co-commissioner permissions (all default to False)
    can_edit_name = db.Column(db.Boolean, default=False)
    can_edit_description = db.Column(db.Boolean, default=False)
    can_edit_is_public = db.Column(db.Boolean, default=False)
    can_edit_max_teams = db.Column(db.Boolean, default=False)
    can_edit_draft_type = db.Column(db.Boolean, default=False)
    can_edit_point_system = db.Column(db.Boolean, default=False)

    league = db.relationship('League', back_populates='member_links')
    user = db.relationship('User', back_populates='leagues')

class League(db.Model):
    """League model for F1 Fantasy leagues."""
    __tablename__ = 'leagues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # League Settings
    max_teams = db.Column(db.Integer, default=10)
    draft_type = db.Column(db.String(20), default='snake',  # Options: snake, auction, random
                          nullable=False)
    point_system = db.Column(db.String(20), default='f1_default',  # Options: f1_default, simple, points_race
                           nullable=False)
    status = db.Column(db.String(20), default='setup',  # Options: setup, active, completed
                      nullable=False)
    
    # Foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    commissioner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], 
                          back_populates='owned_leagues')
    commissioner = db.relationship('User', foreign_keys=[commissioner_id],
                                 back_populates='commissioned_leagues')
    teams = db.relationship('Team', backref='league', lazy='dynamic', cascade='all, delete-orphan')
    member_links = db.relationship('LeagueMember', back_populates='league', cascade='all, delete-orphan')
    members = association_proxy('member_links', 'user')

    def __repr__(self):
        return f'<League {self.name}>'

    def is_commissioner(self, user):
        """Check if a user is the commissioner of this league."""
        return user.id == self.commissioner_id

    def is_owner(self, user):
        """Check if a user is the owner of this league."""
        return user.id == self.owner_id

    def can_manage(self, user):
        """Check if a user can manage this league (owner or commissioner)."""
        return self.is_owner(user) or self.is_commissioner(user)

    @property
    def is_full(self):
        """Check if the league has reached its maximum number of teams."""
        return self.teams.count() >= self.max_teams

    @property
    def is_draftable(self):
        """Check if the league is ready for drafting."""
        return (self.status == 'setup' and 
                self.teams.count() > 1)

    def get_points_for_position(self, position):
        """Get points for a given position based on the league's point system."""
        if position is None or position == 'DNF' or position == 'DNS' or position == 'DSQ':
            return 0
            
        position = int(position)
        
        if self.point_system == 'f1_default':
            # F1 default scoring system
            points = {
                1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
                6: 8, 7: 6, 8: 4, 9: 2, 10: 1
            }
            return points.get(position, 0)
            
        elif self.point_system == 'simple':
            # Simple scoring: 1st = 20, 2nd = 19, ..., 20th = 1
            if 1 <= position <= 20:
                return 21 - position
            return 0
            
        elif self.point_system == 'points_race':
            # Points Race: 10th = 10, 9th/11th = 9, 8th/12th = 8, etc.
            if position == 10:
                return 10
            elif 1 <= position <= 20:
                distance_from_10 = abs(position - 10)
                return max(10 - distance_from_10, 1)
            return 0
            
        return 0