from datetime import datetime
from f1_fantasy.models import db

class Settings(db.Model):
    """Application-wide settings model."""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(256), nullable=True)
    category = db.Column(db.String(32), nullable=False, default='general')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f'<Settings {self.key}={self.value}>'

    @classmethod
    def get(cls, key, default=None):
        """Get a setting value by key."""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set(cls, key, value, description=None, category='general', user_id=None):
        """Set a setting value by key."""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, category=category)
        setting.value = value
        if description:
            setting.description = description
        if user_id:
            setting.updated_by = user_id
        setting.updated_at = datetime.utcnow()
        db.session.add(setting)
        db.session.commit()
        return setting

    @classmethod
    def get_all_by_category(cls, category=None):
        """Get all settings, optionally filtered by category."""
        query = cls.query
        if category:
            query = query.filter_by(category=category)
        return query.order_by(cls.category, cls.key).all()

    @classmethod
    def get_categories(cls):
        """Get list of all setting categories."""
        return db.session.query(cls.category).distinct().all() 