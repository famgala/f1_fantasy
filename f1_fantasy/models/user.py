from datetime import datetime
from flask_security import UserMixin, RoleMixin
from f1_fantasy.models import db

# Association table for user-role many-to-many relationship
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    avatar = db.Column(db.String(255), nullable=True)  # Store the filename of the avatar
    visibility = db.Column(db.String(20), default='public')  # Options: public, hidden
    pending_invites = db.Column(db.JSON, default=list)  # Store pending league invites
    
    # Flask-Security tracking fields
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer())
    
    roles = db.relationship('Role', secondary=user_roles,
                          backref=db.backref('users', lazy='dynamic')) 
    # Relationship to LeagueMember for user's leagues
    leagues = db.relationship('LeagueMember', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    owned_leagues = db.relationship('League', foreign_keys='League.owner_id',
                                  back_populates='owner', lazy='dynamic')
    commissioned_leagues = db.relationship('League', foreign_keys='League.commissioner_id',
                                        back_populates='commissioner', lazy='dynamic')

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def is_searchable(self):
        """Check if the user should appear in search results."""
        return self.visibility == 'public' and self.active

    def add_pending_invite(self, league_id, inviter_id, role='member', permissions=None):
        """Add a pending league invite."""
        if not self.pending_invites:
            self.pending_invites = []
        
        invite = {
            'league_id': league_id,
            'inviter_id': inviter_id,
            'role': role,
            'permissions': permissions or {},
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Check if invite already exists
        for existing in self.pending_invites:
            if existing['league_id'] == league_id:
                return False
        
        self.pending_invites.append(invite)
        return True

    def remove_pending_invite(self, league_id):
        """Remove a pending league invite."""
        if not self.pending_invites:
            return False
        
        initial_length = len(self.pending_invites)
        self.pending_invites = [invite for invite in self.pending_invites 
                              if invite['league_id'] != league_id]
        
        return len(self.pending_invites) < initial_length

    def get_pending_invites(self):
        """Get all pending league invites."""
        if not self.pending_invites:
            return []
        
        from .league import League, User as Inviter
        invites = []
        for invite in self.pending_invites:
            league = League.query.get(invite['league_id'])
            inviter = Inviter.query.get(invite['inviter_id'])
            if league and inviter:
                invites.append({
                    'league': league,
                    'inviter': inviter,
                    'role': invite['role'],
                    'permissions': invite['permissions'],
                    'created_at': datetime.fromisoformat(invite['created_at'])
                })
        return invites

    def __repr__(self):
        return f'<User {self.username}>' 