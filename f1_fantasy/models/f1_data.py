from datetime import datetime
from . import db

class Race(db.Model):
    """Model for F1 races."""
    __tablename__ = 'races'

    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False)
    round = db.Column(db.Integer, nullable=False)  # Race number in the season
    name = db.Column(db.String(100), nullable=False)
    circuit_name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)  # Race start time
    status = db.Column(db.String(20), default='scheduled',  # Options: scheduled, completed, cancelled
                      nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to prevent duplicate races
    __table_args__ = (
        db.UniqueConstraint('season', 'round', name='uix_season_round'),
    )

    def __repr__(self):
        return f'<Race {self.season} Round {self.round}: {self.name}>'

class Driver(db.Model):
    """Model for F1 drivers."""
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False)  # Added season column
    driver_number = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(3), nullable=True)  # Driver's 3-letter code (e.g., HAM, VER)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    constructor = db.Column(db.String(100), nullable=False)  # Current team
    status = db.Column(db.String(20), default='active',  # Options: active, inactive, retired
                      nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to prevent duplicate drivers in the same season
    __table_args__ = (
        db.UniqueConstraint('season', 'driver_number', name='uix_season_driver_number'),
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<Driver {self.season} #{self.driver_number}: {self.full_name}>' 