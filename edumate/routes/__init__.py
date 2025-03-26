"""Routes package for EduMate application."""

from .auth import bp as auth_bp
from .courses import bp as courses_bp
from .assignments import bp as assignments_bp

__all__ = [
    'auth_bp',
    'courses_bp',
    'assignments_bp'
] 