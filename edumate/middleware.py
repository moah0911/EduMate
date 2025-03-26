"""Middleware for the EduMate Flask application.

This module provides middleware components for:
- Request tracking and logging
- Performance monitoring
- Security headers
- Rate limiting
- Error handling
"""

import time
import uuid
from functools import wraps
from flask import request, g, jsonify, current_app
from werkzeug.exceptions import HTTPException
import traceback

from edumate.utils.advanced_logger import get_logger

logger = get_logger()

class RequestMiddleware:
    """Middleware for tracking and logging HTTP requests."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with a Flask application."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """Process request before it's handled by a view function."""
        # Generate a unique request ID
        g.request_id = str(uuid.uuid4())
        
        # Store request start time for performance tracking
        g.start_time = time.time()
        
        # Log request start
        logger.debug(f"Request started: {request.method} {request.path}",
                    request_id=g.request_id,
                    method=request.method,
                    path=request.path,
                    remote_addr=request.remote_addr,
                    user_agent=request.user_agent.string)
    
    def after_request(self, response):
        """Process response before it's sent to the client."""
        # Calculate request duration
        duration = time.time() - g.start_time
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
        
        # Log request completion
        user_id = g.get('user_id', 'anonymous')
        logger.log_access(
            user=user_id,
            method=request.method,
            path=request.path,
            status=response.status_code,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            response_time=duration * 1000  # Convert to milliseconds
        )
        
        return response
    
    def teardown_request(self, exception):
        """Clean up after request is processed, regardless of whether an exception occurred."""
        if exception:
            logger.error(
                f"Request failed: {request.method} {request.path}",
                exc_info=exception,
                user=g.get('user_id', 'anonymous'),
                request_id=g.get('request_id', 'unknown'),
                method=request.method,
                path=request.path
            )


class RateLimiter:
    """Rate limiting middleware to prevent abuse."""
    
    def __init__(self, app=None, default_limits=None, key_func=None):
        self.app = app
        self.default_limits = default_limits or ["100 per minute"]
        self.key_func = key_func or (lambda: request.remote_addr)
        self.limiter = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the rate limiter with a Flask application."""
        try:
            from flask_limiter import Limiter
            from flask_limiter.util import get_remote_address
            
            self.limiter = Limiter(
                app=app,
                key_func=self.key_func or get_remote_address,
                default_limits=self.default_limits
            )
            
            logger.info("Rate limiter initialized", 
                       default_limits=self.default_limits)
        except ImportError:
            logger.warning("Flask-Limiter not installed, rate limiting disabled")
    
    def limit(self, limit_value):
        """Decorator to apply rate limiting to a route."""
        if self.limiter:
            return self.limiter.limit(limit_value)
        
        # If limiter is not available, return a no-op decorator
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapped
        return decorator


class ErrorHandler:
    """Middleware for handling and logging errors."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the error handler with a Flask application."""
        app.register_error_handler(Exception, self.handle_exception)
        app.register_error_handler(404, self.handle_404)
        app.register_error_handler(500, self.handle_500)
    
    def handle_exception(self, e):
        """Handle uncaught exceptions."""
        # Log the error
        logger.error(
            f"Unhandled exception: {str(e)}",
            exc_info=e,
            user=g.get('user_id', 'anonymous'),
            request_id=g.get('request_id', 'unknown'),
            path=request.path
        )
        
        # Determine if this is an HTTP exception
        if isinstance(e, HTTPException):
            return self.handle_http_exception(e)
        
        # For other exceptions, return a 500 error
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'request_id': g.get('request_id', 'unknown')
        }), 500
    
    def handle_http_exception(self, e):
        """Handle HTTP exceptions."""
        response = e.get_response()
        
        # Add JSON body with error details
        response.data = jsonify({
            'error': e.name,
            'message': e.description,
            'code': e.code,
            'request_id': g.get('request_id', 'unknown')
        }).data
        
        response.content_type = 'application/json'
        return response
    
    def handle_404(self, e):
        """Handle 404 Not Found errors."""
        logger.info(
            f"404 Not Found: {request.path}",
            user=g.get('user_id', 'anonymous'),
            path=request.path
        )
        
        return jsonify({
            'error': 'Not Found',
            'message': f"The requested URL {request.path} was not found on the server",
            'request_id': g.get('request_id', 'unknown')
        }), 404
    
    def handle_500(self, e):
        """Handle 500 Internal Server Error."""
        logger.error(
            f"500 Internal Server Error: {str(e)}",
            exc_info=e,
            user=g.get('user_id', 'anonymous'),
            request_id=g.get('request_id', 'unknown'),
            path=request.path
        )
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'The server encountered an internal error and was unable to complete your request',
            'request_id': g.get('request_id', 'unknown')
        }), 500


class PerformanceMonitor:
    """Middleware for monitoring application performance."""
    
    def __init__(self, app=None, slow_threshold_ms=500):
        self.app = app
        self.slow_threshold_ms = slow_threshold_ms
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the performance monitor with a Flask application."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Store start time before processing request."""
        g.start_time = time.time()
    
    def after_request(self, response):
        """Monitor request duration and log slow requests."""
        duration = time.time() - g.start_time
        duration_ms = duration * 1000
        
        # Log performance data
        logger.log_performance(
            operation=f"{request.method} {request.path}",
            duration=duration,
            success=response.status_code < 400,
            details=f"Status: {response.status_code}"
        )
        
        # Log warning for slow requests
        if duration_ms > self.slow_threshold_ms:
            logger.warning(
                f"Slow request: {request.method} {request.path} took {duration_ms:.2f}ms",
                method=request.method,
                path=request.path,
                duration_ms=duration_ms,
                status_code=response.status_code
            )
        
        return response


def setup_middleware(app):
    """Set up all middleware components for the Flask application."""
    # Initialize request middleware
    request_middleware = RequestMiddleware(app)
    
    # Initialize rate limiter
    rate_limiter = RateLimiter(
        app,
        default_limits=["200 per minute", "10000 per day"],
        key_func=lambda: request.remote_addr
    )
    
    # Initialize error handler
    error_handler = ErrorHandler(app)
    
    # Initialize performance monitor
    performance_monitor = PerformanceMonitor(app, slow_threshold_ms=500)
    
    logger.info("All middleware components initialized")
    
    return {
        'request_middleware': request_middleware,
        'rate_limiter': rate_limiter,
        'error_handler': error_handler,
        'performance_monitor': performance_monitor
    } 