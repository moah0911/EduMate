"""Submission model for managing student submissions."""
import os
from edumate.extensions import db
from edumate.models.base import BaseModel


class Submission(BaseModel):
    """Submission model for managing student submissions."""
    
    __tablename__ = 'submissions'
    
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    is_late = db.Column(db.Boolean, default=False)
    is_graded = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    plagiarism_score = db.Column(db.Float, nullable=True)
    
    # Relationships
    criterion_scores = db.relationship('CriterionScore', backref='submission', lazy=True,
                                      cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='uq_submission'),
    )
    
    @property
    def file_name(self):
        """Get the file name from the file path."""
        if self.file_path:
            return os.path.basename(self.file_path)
        return None
    
    @property
    def percentage_score(self):
        """Get the percentage score."""
        if self.score is None or self.assignment.points == 0:
            return 0
        return (self.score / self.assignment.points) * 100
    
    def get_criterion_score(self, criterion_id):
        """Get score for a specific criterion."""
        for cs in self.criterion_scores:
            if cs.criterion_id == criterion_id:
                return cs.score
        return None
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        data = super().to_dict()
        data['student_name'] = self.student.get_full_name() if self.student else None
        data['assignment_title'] = self.assignment.title if self.assignment else None
        data['percentage_score'] = self.percentage_score
        data['file_name'] = self.file_name
        data['criterion_scores'] = [cs.to_dict() for cs in self.criterion_scores]
        return data
    
    def __repr__(self):
        """String representation of the submission."""
        return f"<Submission {self.id}: {self.student_id} for {self.assignment_id}>"


class CriterionScore(BaseModel):
    """CriterionScore model for storing scores for each rubric criterion."""
    
    __tablename__ = 'criterion_scores'
    
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('rubric_criteria.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    
    # Relationship
    criterion = db.relationship('RubricCriterion', backref='scores', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('submission_id', 'criterion_id', name='uq_criterion_score'),
    )
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        data = super().to_dict()
        data['criterion_name'] = self.criterion.name if self.criterion else None
        data['max_score'] = self.criterion.max_score if self.criterion else None
        data['percentage'] = (self.score / self.criterion.max_score * 100) if self.criterion and self.criterion.max_score else 0
        return data
    
    def __repr__(self):
        """String representation of the criterion score."""
        return f"<CriterionScore {self.submission_id}/{self.criterion_id}: {self.score}>" 