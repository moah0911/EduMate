"""Course model for EduMate application."""

from datetime import datetime
from .. import db

class Course(db.Model):
    """Course model representing academic courses."""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', back_populates='courses_taught')
    students_enrolled = db.relationship('Enrollment', back_populates='course')
    assignments = db.relationship('Assignment', back_populates='course', cascade='all, delete-orphan')
    
    def __init__(self, name, code, teacher_id, description=None, start_date=None, end_date=None):
        """Initialize a new course."""
        self.name = name
        self.code = code
        self.teacher_id = teacher_id
        self.description = description
        self.start_date = start_date or datetime.utcnow()
        self.end_date = end_date or datetime.utcnow()
    
    def get_active_assignments(self):
        """Get all active assignments for this course."""
        return [a for a in self.assignments if a.is_active]
    
    def get_enrolled_students(self):
        """Get all students enrolled in this course."""
        return [enrollment.student for enrollment in self.students_enrolled]
    
    def to_dict(self):
        """Convert course object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name,
            'is_active': self.is_active,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'enrolled_students_count': len(self.students_enrolled),
            'assignments_count': len(self.assignments)
        }
    
    def __repr__(self):
        """Return string representation of the course."""
        return f'<Course {self.code}: {self.name}>' 