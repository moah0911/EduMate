"""Base model for all database models."""
from datetime import datetime
from edumate.extensions import db


class BaseModel(db.Model):
    """Base model with common fields and methods."""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Save the model to the database."""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the model from the database."""
        db.session.delete(self)
        db.session.commit()
        return self
    
    @classmethod
    def get_by_id(cls, id):
        """Get a model by its ID."""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Get all models."""
        return cls.query.all()
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 