"""Authentication routes for EduMate application."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import User
from .. import db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate role
    if data['role'] not in ['teacher', 'student']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    user = User(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        role=data['role']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    """Log in a user."""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    # Verify user and password
    if not user or not user.verify_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user information."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['name']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # Update password if provided
    if 'password' in data:
        user.password = data['password']
    
    db.session.commit()
    return jsonify(user.to_dict()), 200 