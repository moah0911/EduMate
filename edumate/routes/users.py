"""User management routes for the EduMate application."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

from edumate import db
from edumate.models.user import User

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users."""
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role
    } for user in users]), 200

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user by ID."""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role
    }), 200

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user's information."""
    current_user_id = get_jwt_identity()
    
    # Only allow users to update their own information or admin users
    if current_user_id != user_id:
        current_user = User.query.get(current_user_id)
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update user fields
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        # Check if email is already taken
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email already in use'}), 409
        user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])
    if 'role' in data:
        # Only admin can change roles
        current_user = User.query.get(current_user_id)
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized to change role'}), 403
        user.role = data['role']
    
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role
    }), 200

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Only admin can delete users
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200 