from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import models after db is initialized to avoid circular imports
from .user import User, Role
from .settings import Settings
from .league import League, league_members
from .team import Team

# Re-export models for convenience
__all__ = ['db', 'User', 'Role', 'Settings', 'League', 'Team', 'league_members'] 