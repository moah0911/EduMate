"""Class model for the EduMate application."""

from datetime import datetime
import random
import string
from sqlalchemy.orm import relationship

from edumate import db

class Class(db.Model):
    """Class model for managing courses."""
    
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(50))
    subject = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(50))
    join_code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship('User', back_populates='taught_classes')
    enrollments = relationship('ClassEnrollment', back_populates='class_obj', cascade='all, delete-orphan')
    assignments = relationship('Assignment', back_populates='class_obj', cascade='all, delete-orphan')
    announcements = relationship('Announcement', back_populates='class_obj', cascade='all, delete-orphan')
    
    def __init__(self, name, subject, teacher_id, section=None, room=None, join_code=None, description=None):
        """Initialize a new class."""
        self.name = name
        self.section = section
        self.subject = subject
        self.room = room
        self.join_code = join_code or self.generate_join_code()
        self.description = description
        self.teacher_id = teacher_id
    
    def generate_join_code(self):
        """Generate a unique join code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def add_student(self, user_id):
        """Add a student to the class."""
        enrollment = ClassEnrollment(class_id=self.id, user_id=user_id, role='student')
        db.session.add(enrollment)
        db.session.commit()
        return enrollment
    
    def remove_student(self, user_id):
        """Remove a student from the class."""
        enrollment = ClassEnrollment.query.filter_by(class_id=self.id, user_id=user_id).first()
        if enrollment:
            db.session.delete(enrollment)
            db.session.commit()
    
    def get_students(self):
        """Get all students enrolled in the class."""
        enrollments = ClassEnrollment.query.filter_by(class_id=self.id, role='student').all()
        return [enrollment.user for enrollment in enrollments]
    
    def get_student_count(self):
        """Get the number of students enrolled in the class."""
        return ClassEnrollment.query.filter_by(class_id=self.id, role='student').count()
    
    def get_active_assignments(self):
        """Get all active assignments for the class."""
        from edumate.models.assignment import Assignment
        now = datetime.utcnow()
        return Assignment.query.filter(
            Assignment.class_id == self.id,
            Assignment.due_date >= now
        ).all()
    
    def to_dict(self):
        """Convert class to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'section': self.section,
            'subject': self.subject,
            'room': self.room,
            'join_code': self.join_code,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else None,
            'student_count': self.get_student_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of the class."""
        return f'<Class {self.name}>'


class ClassEnrollment(db.Model):
    """ClassEnrollment model for user-class relationships."""
    
    __tablename__ = 'class_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'teaching_assistant'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    class_obj = relationship('Class', back_populates='enrollments')
    user = relationship('User', back_populates='enrollments')
    
    __table_args__ = (
        db.UniqueConstraint('class_id', 'user_id', name='unique_class_user'),
    )
    
    def __repr__(self):
        """String representation of the enrollment."""
        return f'<ClassEnrollment {self.user_id} in {self.class_id}>'


class Announcement(db.Model):
    """Announcement model for class announcements."""
    
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_obj = relationship('Class', back_populates='announcements')
    user = relationship('User')
    comments = relationship('AnnouncementComment', back_populates='announcement', cascade='all, delete-orphan')
    attachments = relationship('AnnouncementAttachment', back_populates='announcement', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert announcement to dictionary."""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comments': [comment.to_dict() for comment in self.comments],
            'attachments': [attachment.to_dict() for attachment in self.attachments]
        }
    
    def __repr__(self):
        """String representation of the announcement."""
        return f'<Announcement {self.title}>'


class AnnouncementComment(db.Model):
    """AnnouncementComment model for comments on announcements."""
    
    __tablename__ = 'announcement_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    announcement = relationship('Announcement', back_populates='comments')
    user = relationship('User')
    
    def to_dict(self):
        """Convert comment to dictionary."""
        return {
            'id': self.id,
            'announcement_id': self.announcement_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of the comment."""
        return f'<AnnouncementComment {self.id}>'


class AnnouncementAttachment(db.Model):
    """AnnouncementAttachment model for attachments on announcements."""
    
    __tablename__ = 'announcement_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    announcement = relationship('Announcement', back_populates='attachments')
    
    def to_dict(self):
        """Convert attachment to dictionary."""
        return {
            'id': self.id,
            'announcement_id': self.announcement_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    def __repr__(self):
        """String representation of the attachment."""
        return f'<AnnouncementAttachment {self.filename}>' 