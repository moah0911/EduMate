"""Assignment routes for EduMate application."""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

from edumate import db
from edumate.models.user import User
from edumate.models.class_model import Class, ClassEnrollment
from edumate.models.assignment import Assignment, Submission, SubmissionAttachment
from edumate.services.ai_grading import AIGradingService

bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/', methods=['GET'])
@jwt_required()
def list_assignments():
    """List assignments for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role == 'teacher':
        # Get assignments created by the teacher
        assignments = Assignment.query.filter_by(teacher_id=user.id).all()
    else:
        # Get assignments from enrolled courses
        assignments = []
        for enrollment in user.enrollments:
            assignments.extend(enrollment.course.assignments)
    
    return jsonify([assignment.to_dict() for assignment in assignments]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_assignment():
    """Create a new assignment."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Only teachers can create assignments
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can create assignments'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'course_id', 'type', 'points', 'due_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user is the teacher of the course
    course = Class.query.get_or_404(data['course_id'])
    if course.teacher_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Create new assignment
    assignment = Assignment(
        title=data['title'],
        course_id=data['course_id'],
        teacher_id=user.id,
        type=data['type'],
        points=data['points'],
        due_date=data['due_date'],
        description=data.get('description'),
        rubric=data.get('rubric', {})
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify(assignment.to_dict()), 201

@bp.route('/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    """Get assignment details."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Check if user has access to the assignment
    if user.role == 'teacher' and assignment.teacher_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    elif user.role == 'student' and not any(e.class_id == assignment.class_id for e in user.enrollments):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(assignment.to_dict()), 200

@bp.route('/<int:assignment_id>', methods=['PUT'])
@jwt_required()
def update_assignment(assignment_id):
    """Update assignment details."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Only the teacher who created the assignment can update it
    if user.role != 'teacher' or assignment.teacher_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['title', 'description', 'type', 'points', 'due_date', 'is_active', 'rubric']
    for field in allowed_fields:
        if field in data:
            setattr(assignment, field, data[field])
    
    db.session.commit()
    return jsonify(assignment.to_dict()), 200

@bp.route('/<int:assignment_id>/submit', methods=['POST'])
@jwt_required()
def submit_assignment(assignment_id):
    """Submit an assignment."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Only students can submit assignments
    if user.role != 'student':
        return jsonify({'error': 'Only students can submit assignments'}), 403
    
    # Check if student is enrolled in the course
    if not any(e.class_id == assignment.class_id for e in user.enrollments):
        return jsonify({'error': 'Access denied'}), 403
    
    # Handle file upload if present
    file = request.files.get('file')
    file_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
    
    # Get content from form data
    content = request.form.get('content')
    
    # Create or update submission
    submission = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=user.id
    ).first()
    
    if submission:
        submission.content = content
        submission.file_path = file_path
        submission.status = 'submitted'
    else:
        submission = Submission(
            assignment_id=assignment_id,
            student_id=user.id,
            content=content,
            file_path=file_path
        )
        db.session.add(submission)
    
    db.session.commit()
    return jsonify(submission.to_dict()), 200

@bp.route('/<int:assignment_id>/submissions', methods=['GET'])
@jwt_required()
def list_submissions(assignment_id):
    """List all submissions for an assignment."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Teachers can view all submissions, students can only view their own
    if user.role == 'teacher':
        if assignment.teacher_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        submissions = assignment.submissions
    else:
        if not any(e.class_id == assignment.class_id for e in user.enrollments):
            return jsonify({'error': 'Access denied'}), 403
        submissions = [s for s in assignment.submissions if s.student_id == user.id]
    
    return jsonify([submission.to_dict() for submission in submissions]), 200

@bp.route('/<int:assignment_id>/submissions/<int:submission_id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(assignment_id, submission_id):
    """Grade a submission."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    submission = Submission.query.get_or_404(submission_id)
    
    # Only the teacher who created the assignment can grade submissions
    if user.role != 'teacher' or assignment.teacher_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Validate submission belongs to the assignment
    if submission.assignment_id != assignment_id:
        return jsonify({'error': 'Invalid submission'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    if 'score' not in data:
        return jsonify({'error': 'Score is required'}), 400
    
    # Update submission grade
    submission.grade(data['score'], data.get('feedback'))
    db.session.commit()
    
    return jsonify(submission.to_dict()), 200

@bp.route('/<int:assignment_id>/attachment/<int:attachment_id>', methods=['GET'])
@jwt_required()
def get_attachment(assignment_id, attachment_id):
    """Get a submission attachment."""
    user_id = get_jwt_identity()
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    attachment = SubmissionAttachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'error': 'Attachment not found'}), 404
    
    submission = Submission.query.get(attachment.submission_id)
    if not submission or submission.assignment_id != assignment_id:
        return jsonify({'error': 'Attachment not found'}), 404
    
    # Check if user is authorized to access this attachment
    if assignment.teacher_id != user_id and submission.student_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return send_file(attachment.file_path, as_attachment=True, download_name=attachment.filename) 