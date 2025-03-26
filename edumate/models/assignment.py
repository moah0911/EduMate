"""Assignment and Submission models for EduMate application."""

from datetime import datetime
from sqlalchemy.orm import relationship
import json

from edumate import db

class Assignment(db.Model):
    """Assignment model representing course assignments."""
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # homework, quiz, project, exam
    points = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    rubric = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', back_populates='assignments')
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    submissions = db.relationship('Submission', back_populates='assignment', cascade='all, delete-orphan')
    class_obj = db.relationship('Class', back_populates='assignments')
    
    def __init__(self, title, course_id, teacher_id, type, points, due_date, description=None, rubric=None, class_id=None):
        """Initialize a new assignment."""
        self.title = title
        self.course_id = course_id
        self.teacher_id = teacher_id
        self.type = type
        self.points = points
        self.due_date = due_date
        self.description = description
        self.rubric = rubric or {}
        self.class_id = class_id
    
    def get_student_submission(self, student_id):
        """Get a student's submission for this assignment."""
        return next((s for s in self.submissions if s.student_id == student_id), None)
    
    def get_all_submissions(self):
        """Get all submissions for this assignment."""
        return self.submissions
    
    def to_dict(self):
        """Convert assignment object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'course_id': self.course_id,
            'course_name': self.course.name,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'type': self.type,
            'points': self.points,
            'due_date': self.due_date.isoformat(),
            'is_active': self.is_active,
            'rubric': self.rubric,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submission_count': len(self.submissions)
        }
    
    def __repr__(self):
        """Return string representation of the assignment."""
        return f'<Assignment {self.title} for {self.course.code}>'

class Submission(db.Model):
    """Submission model representing student submissions for assignments."""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    status = db.Column(db.String(20), default='submitted')  # draft, submitted, graded
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime)
    
    # Relationships
    assignment = db.relationship('Assignment', back_populates='submissions')
    student = db.relationship('User', back_populates='submissions')
    attachments = db.relationship('SubmissionAttachment', back_populates='submission', cascade='all, delete-orphan')
    
    # Ensure a student can only submit once per assignment
    __table_args__ = (
        db.UniqueConstraint('student_id', 'assignment_id', name='unique_student_assignment'),
    )
    
    def __init__(self, assignment_id, student_id, content=None, file_path=None):
        """Initialize a new submission."""
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.content = content
        self.file_path = file_path
    
    def grade(self, score, feedback=None):
        """Grade the submission."""
        self.score = score
        self.feedback = feedback
        self.status = 'graded'
        self.graded_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert submission object to dictionary."""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'assignment_title': self.assignment.title,
            'student_id': self.student_id,
            'student_name': self.student.name,
            'content': self.content,
            'file_path': self.file_path,
            'score': self.score,
            'feedback': self.feedback,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'attachments': [attachment.to_dict() for attachment in self.attachments]
        }
    
    def __repr__(self):
        """Return string representation of the submission."""
        return f'<Submission by {self.student.name} for {self.assignment.title}>'


class SubmissionAttachment(db.Model):
    """SubmissionAttachment model for attachments on submissions."""
    
    __tablename__ = 'submission_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship('Submission', back_populates='attachments')
    
    def to_dict(self):
        """Convert attachment to dictionary."""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    def __repr__(self):
        """String representation of the attachment."""
        return f'<SubmissionAttachment {self.filename}>'