"""Authentication routes for the EduMate application."""
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash

from edumate.auth import auth_bp
from edumate.models.user import User


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate role
    valid_roles = ['student', 'teacher', 'admin']
    if data['role'] not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
    
    # Create user
    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role'],
        is_active=True
    )
    user.password = data['password']  # This will hash the password
    
    try:
        user.save()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 401
    
    # Verify password
    if not user.verify_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    
    # Check if user exists and is active
    user = User.get_by_id(current_user_id)
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    # Generate new access token
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token
    })


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    current_user_id = get_jwt_identity()
    
    user = User.get_by_id(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()})


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user information."""
    current_user_id = get_jwt_identity()
    
    user = User.get_by_id(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update user fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    if 'password' in data:
        user.password = data['password']
    
    try:
        user.save()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    current_user_id = get_jwt_identity()
    
    user = User.get_by_id(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['current_password', 'new_password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Verify current password
    if not user.verify_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    user.password = data['new_password']
    
    try:
        user.save()
        return jsonify({
            'message': 'Password changed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 