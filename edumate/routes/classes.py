"""Class management routes for the EduMate application."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import string

from edumate import db
from edumate.models.user import User
from edumate.models.class_model import Class, ClassEnrollment, Announcement

bp = Blueprint('classes', __name__, url_prefix='/api/classes')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_classes():
    """Get all classes for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role == 'teacher':
        # Teachers see classes they teach
        classes = Class.query.filter_by(teacher_id=user_id).all()
    else:
        # Students see classes they're enrolled in
        enrollments = ClassEnrollment.query.filter_by(user_id=user_id).all()
        class_ids = [enrollment.class_id for enrollment in enrollments]
        classes = Class.query.filter(Class.id.in_(class_ids)).all()
    
    return jsonify([class_obj.to_dict() for class_obj in classes]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_class():
    """Create a new class."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Only teachers can create classes
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can create classes'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'subject']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Generate a unique join code
    join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Create new class
    class_obj = Class(
        name=data['name'],
        section=data.get('section', ''),
        subject=data['subject'],
        room=data.get('room', ''),
        join_code=join_code,
        description=data.get('description', ''),
        teacher_id=user_id
    )
    
    db.session.add(class_obj)
    db.session.commit()
    
    return jsonify(class_obj.to_dict()), 201

@bp.route('/<int:class_id>', methods=['GET'])
@jwt_required()
def get_class(class_id):
    """Get a specific class by ID."""
    user_id = get_jwt_identity()
    
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check if user is the teacher or enrolled in the class
    if class_obj.teacher_id != user_id:
        enrollment = ClassEnrollment.query.filter_by(
            class_id=class_id, user_id=user_id
        ).first()
        if not enrollment:
            return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(class_obj.to_dict()), 200

@bp.route('/<int:class_id>', methods=['PUT'])
@jwt_required()
def update_class(class_id):
    """Update a class."""
    user_id = get_jwt_identity()
    
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Only the teacher of the class can update it
    if class_obj.teacher_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update class fields
    if 'name' in data:
        class_obj.name = data['name']
    if 'section' in data:
        class_obj.section = data['section']
    if 'subject' in data:
        class_obj.subject = data['subject']
    if 'room' in data:
        class_obj.room = data['room']
    if 'description' in data:
        class_obj.description = data['description']
    
    db.session.commit()
    
    return jsonify(class_obj.to_dict()), 200

@bp.route('/<int:class_id>', methods=['DELETE'])
@jwt_required()
def delete_class(class_id):
    """Delete a class."""
    user_id = get_jwt_identity()
    
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Only the teacher of the class can delete it
    if class_obj.teacher_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(class_obj)
    db.session.commit()
    
    return jsonify({'message': 'Class deleted successfully'}), 200

@bp.route('/join', methods=['POST'])
@jwt_required()
def join_class():
    """Join a class using a join code."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Only students can join classes
    if user.role != 'student':
        return jsonify({'error': 'Only students can join classes'}), 403
    
    data = request.get_json()
    if 'join_code' not in data:
        return jsonify({'error': 'Join code is required'}), 400
    
    # Find class by join code
    class_obj = Class.query.filter_by(join_code=data['join_code']).first()
    if not class_obj:
        return jsonify({'error': 'Invalid join code'}), 404
    
    # Check if already enrolled
    enrollment = ClassEnrollment.query.filter_by(
        class_id=class_obj.id, user_id=user_id
    ).first()
    if enrollment:
        return jsonify({'error': 'Already enrolled in this class'}), 409
    
    # Create enrollment
    enrollment = ClassEnrollment(
        class_id=class_obj.id,
        user_id=user_id,
        role='student'
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify(class_obj.to_dict()), 200

@bp.route('/<int:class_id>/announcements', methods=['GET'])
@jwt_required()
def get_announcements(class_id):
    """Get all announcements for a class."""
    user_id = get_jwt_identity()
    
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check if user is the teacher or enrolled in the class
    if class_obj.teacher_id != user_id:
        enrollment = ClassEnrollment.query.filter_by(
            class_id=class_id, user_id=user_id
        ).first()
        if not enrollment:
            return jsonify({'error': 'Unauthorized'}), 403
    
    announcements = Announcement.query.filter_by(class_id=class_id).all()
    return jsonify([announcement.to_dict() for announcement in announcements]), 200

@bp.route('/<int:class_id>/announcements', methods=['POST'])
@jwt_required()
def create_announcement(class_id):
    """Create a new announcement for a class."""
    user_id = get_jwt_identity()
    
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Only the teacher of the class can create announcements
    if class_obj.teacher_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new announcement
    announcement = Announcement(
        class_id=class_id,
        user_id=user_id,
        title=data['title'],
        content=data['content']
    )
    
    db.session.add(announcement)
    db.session.commit()
    
    return jsonify(announcement.to_dict()), 201 