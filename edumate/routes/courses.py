"""Course routes for EduMate application."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Course, Enrollment
from .. import db

bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@bp.route('/', methods=['GET'])
@jwt_required()
def list_courses():
    """List all courses for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role == 'teacher':
        # Get courses taught by the teacher
        courses = Course.query.filter_by(teacher_id=user.id).all()
    else:
        # Get courses enrolled in by the student
        courses = [enrollment.course for enrollment in user.enrollments]
    
    return jsonify([course.to_dict() for course in courses]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    """Create a new course."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Only teachers can create courses
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can create courses'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'code', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if course code already exists
    if Course.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Course code already exists'}), 409
    
    # Create new course
    course = Course(
        name=data['name'],
        code=data['code'],
        teacher_id=user.id,
        description=data.get('description'),
        start_date=data['start_date'],
        end_date=data['end_date']
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify(course.to_dict()), 201

@bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """Get course details."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    
    # Check if user has access to the course
    if user.role == 'teacher' and course.teacher_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    elif user.role == 'student' and not any(e.course_id == course.id for e in user.enrollments):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(course.to_dict()), 200

@bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    """Update course details."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    
    # Only the teacher of the course can update it
    if user.role != 'teacher' or course.teacher_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
    for field in allowed_fields:
        if field in data:
            setattr(course, field, data[field])
    
    db.session.commit()
    return jsonify(course.to_dict()), 200

@bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course(course_id):
    """Enroll a student in a course."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    
    # Only students can enroll in courses
    if user.role != 'student':
        return jsonify({'error': 'Only students can enroll in courses'}), 403
    
    # Check if student is already enrolled
    if any(e.course_id == course.id for e in user.enrollments):
        return jsonify({'error': 'Already enrolled in this course'}), 409
    
    # Create enrollment
    enrollment = Enrollment(student_id=user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify(enrollment.to_dict()), 201

@bp.route('/<int:course_id>/students', methods=['GET'])
@jwt_required()
def list_enrolled_students(course_id):
    """List all students enrolled in a course."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    
    # Only the teacher of the course can view enrolled students
    if user.role != 'teacher' or course.teacher_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    return jsonify([enrollment.to_dict() for enrollment in enrollments]), 200 