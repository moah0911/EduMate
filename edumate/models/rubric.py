"""Rubric model for managing grading rubrics."""
from edumate.extensions import db
from edumate.models.base import BaseModel


class Rubric(BaseModel):
    """Rubric model for managing grading rubrics."""
    
    __tablename__ = 'rubrics'
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False, unique=True)
    
    # Relationships
    criteria = db.relationship('RubricCriterion', backref='rubric', lazy=True,
                              cascade='all, delete-orphan')
    
    @property
    def total_points(self):
        """Get the total points for the rubric."""
        return sum(criterion.max_score for criterion in self.criteria)
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        data = super().to_dict()
        data['criteria'] = [criterion.to_dict() for criterion in self.criteria]
        data['total_points'] = self.total_points
        return data
    
    def __repr__(self):
        """String representation of the rubric."""
        return f"<Rubric {self.id}: {self.name}>"


class RubricCriterion(BaseModel):
    """RubricCriterion model for managing rubric criteria."""
    
    __tablename__ = 'rubric_criteria'
    
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_score = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, default=1.0)
    order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        data = super().to_dict()
        return data
    
    def __repr__(self):
        """String representation of the rubric criterion."""
        return f"<RubricCriterion {self.id}: {self.name}>" 