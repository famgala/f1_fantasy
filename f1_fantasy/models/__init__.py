from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import models after db is initialized to avoid circular imports
from .user import User, Role
from .settings import Settings
from .league import League, LeagueMember
from .team import Team
from .f1_data import Race, Driver

# Re-export models for convenience
__all__ = ['db', 'User', 'Role', 'Settings', 'League', 'LeagueMember', 'Team', 'Race', 'Driver'] 