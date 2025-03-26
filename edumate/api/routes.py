"""API routes for the EduMate application."""
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

from edumate.api import api_bp
from edumate.models.user import User, Enrollment
from edumate.models.course import Course
from edumate.models.assignment import Assignment
from edumate.models.submission import Submission, CriterionScore
from edumate.models.rubric import Rubric, RubricCriterion
from edumate.services.grading_service import GradingService
from edumate.services.feedback_service import FeedbackService
from edumate.services.plagiarism_service import PlagiarismService
from edumate.utils.file_utils import allowed_file, save_file


# Initialize services
grading_service = GradingService()
feedback_service = FeedbackService()
plagiarism_service = PlagiarismService()


# User routes
@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.get_all()
    return jsonify({'users': [user.to_dict() for user in users]})


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user or (current_user.id != user_id and not current_user.is_admin()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()})


# Course routes
@api_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    """Get all courses."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if current_user.is_admin():
        # Admins can see all courses
        courses = Course.get_all()
    elif current_user.is_teacher():
        # Teachers can see their courses
        courses = current_user.courses_teaching
    else:
        # Students can see enrolled courses
        courses = [enrollment.course for enrollment in current_user.courses_enrolled]
    
    return jsonify({'courses': [course.to_dict() for course in courses]})


@api_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """Get a specific course."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    course = Course.get_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Check if user has access to this course
    if not current_user.is_admin() and not (
        current_user.is_teacher() and course.teacher_id == current_user.id
    ) and not any(e.course_id == course_id for e in current_user.courses_enrolled):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'course': course.to_dict()})


@api_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    """Create a new course."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user or not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['name', 'code']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create course
    course = Course(
        name=data['name'],
        code=data['code'],
        description=data.get('description', ''),
        teacher_id=current_user.id if current_user.is_teacher() else data.get('teacher_id'),
        is_active=data.get('is_active', True),
        start_date=data.get('start_date'),
        end_date=data.get('end_date')
    )
    
    try:
        course.save()
        return jsonify({'course': course.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Assignment routes
@api_bp.route('/courses/<int:course_id>/assignments', methods=['GET'])
@jwt_required()
def get_assignments(course_id):
    """Get all assignments for a course."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    course = Course.get_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Check if user has access to this course
    if not current_user.is_admin() and not (
        current_user.is_teacher() and course.teacher_id == current_user.id
    ) and not any(e.course_id == course_id for e in current_user.courses_enrolled):
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignments = course.assignments
    return jsonify({'assignments': [assignment.to_dict() for assignment in assignments]})


@api_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    """Get a specific assignment."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    course = assignment.course
    
    # Check if user has access to this assignment
    if not current_user.is_admin() and not (
        current_user.is_teacher() and course.teacher_id == current_user.id
    ) and not any(e.course_id == course.id for e in current_user.courses_enrolled):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'assignment': assignment.to_dict()})


@api_bp.route('/courses/<int:course_id>/assignments', methods=['POST'])
@jwt_required()
def create_assignment(course_id):
    """Create a new assignment."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user or not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    course = Course.get_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Check if user is the teacher of this course
    if not current_user.is_admin() and course.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['title', 'assignment_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create assignment
    assignment = Assignment(
        title=data['title'],
        description=data.get('description', ''),
        course_id=course_id,
        due_date=data.get('due_date'),
        points=data.get('points', 100),
        is_active=data.get('is_active', True),
        assignment_type=data['assignment_type'],
        instructions=data.get('instructions', ''),
        allow_attachments=data.get('allow_attachments', True),
        allow_late_submissions=data.get('allow_late_submissions', True),
        late_submission_penalty=data.get('late_submission_penalty', 0.1)
    )
    
    try:
        assignment.save()
        
        # Create rubric if provided
        if 'rubric' in data:
            rubric_data = data['rubric']
            rubric = Rubric(
                name=rubric_data.get('name', f'Rubric for {assignment.title}'),
                description=rubric_data.get('description', ''),
                assignment_id=assignment.id
            )
            rubric.save()
            
            # Create criteria
            for criterion_data in rubric_data.get('criteria', []):
                criterion = RubricCriterion(
                    rubric_id=rubric.id,
                    name=criterion_data.get('name', ''),
                    description=criterion_data.get('description', ''),
                    max_score=criterion_data.get('max_score', 10),
                    weight=criterion_data.get('weight', 1.0),
                    order=criterion_data.get('order', 0)
                )
                criterion.save()
        
        return jsonify({'assignment': assignment.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Submission routes
@api_bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@jwt_required()
def get_submissions(assignment_id):
    """Get all submissions for an assignment."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    course = assignment.course
    
    # Check if user has access to view submissions
    if not current_user.is_admin() and not (current_user.is_teacher() and course.teacher_id == current_user.id):
        # Students can only see their own submissions
        if current_user.is_student():
            submission = assignment.get_submission_for_student(current_user.id)
            if submission:
                return jsonify({'submissions': [submission.to_dict()]})
            else:
                return jsonify({'submissions': []})
        else:
            return jsonify({'error': 'Unauthorized'}), 403
    
    submissions = assignment.submissions
    return jsonify({'submissions': [submission.to_dict() for submission in submissions]})


@api_bp.route('/assignments/<int:assignment_id>/submissions', methods=['POST'])
@jwt_required()
def create_submission(assignment_id):
    """Create a new submission."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    course = assignment.course
    
    # Check if user is enrolled in this course
    if not current_user.is_admin() and not (
        current_user.is_teacher() and course.teacher_id == current_user.id
    ) and not any(e.course_id == course.id for e in current_user.courses_enrolled):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if assignment is active
    if not assignment.is_active:
        return jsonify({'error': 'Assignment is not active'}), 400
    
    # Check if submission already exists
    existing_submission = assignment.get_submission_for_student(current_user.id)
    if existing_submission:
        return jsonify({'error': 'Submission already exists', 'submission': existing_submission.to_dict()}), 400
    
    # Handle file upload if present
    file_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename and allowed_file(file.filename):
            file_path = save_file(file)
    
    # Get content from form data or JSON
    content = None
    if request.form and 'content' in request.form:
        content = request.form['content']
    elif request.is_json:
        data = request.get_json()
        content = data.get('content')
    
    if not content and not file_path:
        return jsonify({'error': 'No content or file provided'}), 400
    
    # Create submission
    submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=content,
        file_path=file_path
    )
    
    try:
        submission.save()
        return jsonify({'submission': submission.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/submissions/<int:submission_id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(submission_id):
    """Grade a submission."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user or not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    submission = Submission.get_by_id(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    assignment = submission.assignment
    course = assignment.course
    
    # Check if user is the teacher of this course
    if not current_user.is_admin() and course.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if manual grading is requested
    manual_grading = False
    if request.is_json:
        data = request.get_json()
        manual_grading = data.get('manual_grading', False)
        
        if manual_grading:
            # Update submission with manual grade
            submission.score = data.get('score')
            submission.feedback = data.get('feedback')
            submission.is_graded = True
            
            # Update criterion scores if provided
            if 'criterion_scores' in data and assignment.rubric:
                from edumate.models.submission import CriterionScore
                
                # Clear existing criterion scores
                for cs in submission.criterion_scores:
                    cs.delete()
                
                # Add new criterion scores
                for cs_data in data['criterion_scores']:
                    criterion_score = CriterionScore(
                        submission_id=submission.id,
                        criterion_id=cs_data['criterion_id'],
                        score=cs_data['score'],
                        feedback=cs_data.get('feedback')
                    )
                    criterion_score.save()
            
            submission.save()
            return jsonify({'submission': submission.to_dict()})
    
    # Use grading service for automated grading
    try:
        graded_submission = grading_service.grade_submission(submission)
        if graded_submission:
            graded_submission.save()
            return jsonify({'submission': graded_submission.to_dict()})
        else:
            return jsonify({'error': 'Failed to grade submission'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/submissions/<int:submission_id>/feedback', methods=['GET'])
@jwt_required()
def get_feedback(submission_id):
    """Get feedback for a submission."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    submission = Submission.get_by_id(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    assignment = submission.assignment
    course = assignment.course
    
    # Check if user has access to this submission
    if not current_user.is_admin() and not (
        current_user.is_teacher() and course.teacher_id == current_user.id
    ) and current_user.id != submission.student_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get feedback tone from query parameters
    tone = request.args.get('tone', 'constructive')
    
    # Generate feedback if not already graded
    if not submission.is_graded:
        return jsonify({'error': 'Submission has not been graded yet'}), 400
    
    # Get personalized feedback
    feedback = feedback_service.generate_feedback(submission, tone)
    
    return jsonify({'feedback': feedback})


@api_bp.route('/submissions/<int:submission_id>/plagiarism', methods=['GET'])
@jwt_required()
def check_plagiarism(submission_id):
    """Check a submission for plagiarism."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user or not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    submission = Submission.get_by_id(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    assignment = submission.assignment
    course = assignment.course
    
    # Check if user is the teacher of this course
    if not current_user.is_admin() and course.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check for internet plagiarism if requested
    check_internet = request.args.get('internet', 'false').lower() == 'true'
    
    if check_internet:
        result = plagiarism_service.check_internet_plagiarism(submission)
    else:
        result = plagiarism_service.check_plagiarism(submission)
    
    return jsonify(result)


# Rubric routes
@api_bp.route('/assignments/<int:assignment_id>/rubric', methods=['GET'])
@jwt_required()
def get_rubric(assignment_id):
    """Get the rubric for an assignment."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    course = assignment.course
    
    # Check if user has access to this assignment
    if not current_user.is_admin() and not (
        current_user.is_teacher() and course.teacher_id == current_user.id
    ) and not any(e.course_id == course.id for e in current_user.courses_enrolled):
        return jsonify({'error': 'Unauthorized'}), 403
    
    rubric = assignment.rubric
    if not rubric:
        return jsonify({'error': 'Rubric not found'}), 404
    
    return jsonify({'rubric': rubric.to_dict()})


@api_bp.route('/assignments/<int:assignment_id>/rubric', methods=['POST'])
@jwt_required()
def create_rubric(assignment_id):
    """Create a rubric for an assignment."""
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user or not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    course = assignment.course
    
    # Check if user is the teacher of this course
    if not current_user.is_admin() and course.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if rubric already exists
    if assignment.rubric:
        return jsonify({'error': 'Rubric already exists', 'rubric': assignment.rubric.to_dict()}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Create rubric
    rubric = Rubric(
        name=data.get('name', f'Rubric for {assignment.title}'),
        description=data.get('description', ''),
        assignment_id=assignment_id
    )
    
    try:
        rubric.save()
        
        # Create criteria
        for criterion_data in data.get('criteria', []):
            criterion = RubricCriterion(
                rubric_id=rubric.id,
                name=criterion_data.get('name', ''),
                description=criterion_data.get('description', ''),
                max_score=criterion_data.get('max_score', 10),
                weight=criterion_data.get('weight', 1.0),
                order=criterion_data.get('order', 0)
            )
            criterion.save()
        
        return jsonify({'rubric': rubric.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500 