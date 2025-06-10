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

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles) 