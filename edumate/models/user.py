"""User and Enrollment models for EduMate application."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    """User model representing teachers and students."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    courses_taught = db.relationship('Course', back_populates='teacher')
    enrollments = db.relationship('Enrollment', back_populates='student')
    submissions = db.relationship('Submission', back_populates='student')
    taught_classes = db.relationship('Class', back_populates='teacher')
    class_enrollments = db.relationship('ClassEnrollment', back_populates='user')
    
    def __init__(self, email, password, name, role):
        """Initialize a new user."""
        self.email = email
        self.password = password  # This will use the password.setter
        self.name = name
        self.role = role
    
    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """Return string representation of the user."""
        return f'<User {self.email}>'

class Enrollment(db.Model):
    """Enrollment model representing student enrollment in courses."""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, dropped
    grade = db.Column(db.String(2))  # Final grade (A, B, C, etc.)
    
    # Relationships
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='students_enrolled')
    
    # Ensure a student can only be enrolled once in a course
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),
    )
    
    def to_dict(self):
        """Convert enrollment object to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'student_name': self.student.name,
            'course_name': self.course.name,
            'enrolled_at': self.enrolled_at.isoformat(),
            'status': self.status,
            'grade': self.grade
        }
    
    def __repr__(self):
        """Return string representation of the enrollment."""
        return f'<Enrollment {self.student.name} in {self.course.name}>' 