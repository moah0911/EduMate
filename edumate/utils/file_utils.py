"""Utility functions for file handling."""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if a file has an allowed extension."""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_file(file, directory=None):
    """Save a file to the upload directory with a unique name."""
    if not file:
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Generate a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Determine the directory
    if directory is None:
        directory = current_app.config['UPLOAD_FOLDER']
    
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(directory, unique_filename)
    file.save(file_path)
    
    return file_path


def get_file_extension(filename):
    """Get the extension of a file."""
    if not filename or '.' not in filename:
        return None
    return filename.rsplit('.', 1)[1].lower()


def is_image_file(filename):
    """Check if a file is an image."""
    if not filename:
        return False
    return get_file_extension(filename) in {'jpg', 'jpeg', 'png', 'gif'}


def is_document_file(filename):
    """Check if a file is a document."""
    if not filename:
        return False
    return get_file_extension(filename) in {'pdf', 'docx', 'doc', 'txt', 'rtf'}


def is_code_file(filename):
    """Check if a file is a code file."""
    if not filename:
        return False
    return get_file_extension(filename) in {'py', 'java', 'cpp', 'js', 'html', 'css', 'c', 'h', 'php'} 