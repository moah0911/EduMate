"""Advanced logging utility for EduMate application.

This module provides enhanced logging capabilities including:
- Structured logging with JSON format
- Log rotation based on file size and time
- Multiple log levels with color coding
- Context-aware logging with user and session information
- Performance metrics logging
"""

import os
import json
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import threading
from functools import wraps
import traceback
import uuid
import socket
from pathlib import Path

# Configure logging constants
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# ANSI color codes for terminal output
COLORS = {
    'DEBUG': '\033[36m',  # Cyan
    'INFO': '\033[32m',   # Green
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',  # Red
    'CRITICAL': '\033[41m\033[37m',  # White on Red background
    'RESET': '\033[0m'    # Reset color
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to log level names in terminal output"""
    
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)

class StructuredLogRecord(logging.LogRecord):
    """Extended LogRecord that supports structured data"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structured_data = {}

class AdvancedLogger:
    """Advanced logger with structured logging and performance tracking"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, app_name="edumate", log_dir="logs", log_level="INFO", 
                 max_bytes=10485760, backup_count=10, when='midnight', 
                 console_output=True, json_format=True):
        """Initialize the advanced logger.
        
        Args:
            app_name (str): Name of the application
            log_dir (str): Directory to store log files
            log_level (str): Minimum log level to record
            max_bytes (int): Maximum size of log file before rotation
            backup_count (int): Number of backup files to keep
            when (str): Time-based rotation interval
            console_output (bool): Whether to output logs to console
            json_format (bool): Whether to format logs as JSON
        """
        if self._initialized:
            return
            
        self.app_name = app_name
        self.log_dir = log_dir
        self.log_level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.when = when
        self.console_output = console_output
        self.json_format = json_format
        self.hostname = socket.gethostname()
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up loggers
        self._setup_app_logger()
        self._setup_access_logger()
        self._setup_error_logger()
        self._setup_audit_logger()
        self._setup_performance_logger()
        
        self._initialized = True
    
    def _setup_app_logger(self):
        """Set up the main application logger"""
        self.app_logger = logging.getLogger(f"{self.app_name}.app")
        self.app_logger.setLevel(self.log_level)
        self.app_logger.propagate = False
        
        # Add file handler with rotation
        app_log_path = os.path.join(self.log_dir, f"{self.app_name}.log")
        file_handler = RotatingFileHandler(
            app_log_path, 
            maxBytes=self.max_bytes, 
            backupCount=self.backup_count
        )
        
        if self.json_format:
            file_formatter = logging.Formatter(
                '{"timestamp":"%(asctime)s", "level":"%(levelname)s", "module":"%(module)s", '
                '"function":"%(funcName)s", "line":%(lineno)d, "message":"%(message)s", '
                '"structured_data":%(structured_data)s}'
            )
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        self.app_logger.addHandler(file_handler)
        
        # Add console handler if enabled
        if self.console_output:
            console_handler = logging.StreamHandler()
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.app_logger.addHandler(console_handler)
    
    def _setup_access_logger(self):
        """Set up logger for access logs"""
        self.access_logger = logging.getLogger(f"{self.app_name}.access")
        self.access_logger.setLevel(self.log_level)
        self.access_logger.propagate = False
        
        # Add file handler with time-based rotation
        access_log_path = os.path.join(self.log_dir, f"{self.app_name}_access.log")
        file_handler = TimedRotatingFileHandler(
            access_log_path,
            when=self.when,
            backupCount=self.backup_count
        )
        
        if self.json_format:
            file_formatter = logging.Formatter(
                '{"timestamp":"%(asctime)s", "user":"%(user)s", "method":"%(method)s", '
                '"path":"%(path)s", "status":%(status)d, "ip":"%(ip)s", '
                '"user_agent":"%(user_agent)s", "response_time":%(response_time).2f}'
            )
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(user)s - %(method)s %(path)s - %(status)d - %(ip)s - '
                '%(user_agent)s - %(response_time).2fms'
            )
        
        file_handler.setFormatter(file_formatter)
        self.access_logger.addHandler(file_handler)
    
    def _setup_error_logger(self):
        """Set up logger for error logs"""
        self.error_logger = logging.getLogger(f"{self.app_name}.error")
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.propagate = False
        
        # Add file handler with rotation
        error_log_path = os.path.join(self.log_dir, f"{self.app_name}_error.log")
        file_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        
        if self.json_format:
            file_formatter = logging.Formatter(
                '{"timestamp":"%(asctime)s", "level":"%(levelname)s", "module":"%(module)s", '
                '"function":"%(funcName)s", "line":%(lineno)d, "message":"%(message)s", '
                '"exception":"%(exc_info)s", "user":"%(user)s", "trace":"%(trace)s"}'
            )
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s\n'
                'User: %(user)s\nException: %(exc_info)s\nTrace:\n%(trace)s'
            )
        
        file_handler.setFormatter(file_formatter)
        self.error_logger.addHandler(file_handler)
        
        # Add console handler if enabled
        if self.console_output:
            console_handler = logging.StreamHandler()
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(logging.ERROR)
            self.error_logger.addHandler(console_handler)
    
    def _setup_audit_logger(self):
        """Set up logger for audit logs"""
        self.audit_logger = logging.getLogger(f"{self.app_name}.audit")
        self.audit_logger.setLevel(self.log_level)
        self.audit_logger.propagate = False
        
        # Add file handler with rotation
        audit_log_path = os.path.join(self.log_dir, f"{self.app_name}_audit.log")
        file_handler = RotatingFileHandler(
            audit_log_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        
        if self.json_format:
            file_formatter = logging.Formatter(
                '{"timestamp":"%(asctime)s", "user":"%(user)s", "action":"%(action)s", '
                '"resource":"%(resource)s", "resource_id":"%(resource_id)s", '
                '"details":"%(details)s", "ip":"%(ip)s", "success":%(success)s}'
            )
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - AUDIT - User: %(user)s - Action: %(action)s - '
                'Resource: %(resource)s - ID: %(resource_id)s - Success: %(success)s - '
                'Details: %(details)s - IP: %(ip)s'
            )
        
        file_handler.setFormatter(file_formatter)
        self.audit_logger.addHandler(file_handler)
    
    def _setup_performance_logger(self):
        """Set up logger for performance metrics"""
        self.perf_logger = logging.getLogger(f"{self.app_name}.performance")
        self.perf_logger.setLevel(self.log_level)
        self.perf_logger.propagate = False
        
        # Add file handler with rotation
        perf_log_path = os.path.join(self.log_dir, f"{self.app_name}_performance.log")
        file_handler = RotatingFileHandler(
            perf_log_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        
        if self.json_format:
            file_formatter = logging.Formatter(
                '{"timestamp":"%(asctime)s", "operation":"%(operation)s", '
                '"duration":%(duration).4f, "success":%(success)s, "details":"%(details)s"}'
            )
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - PERFORMANCE - Operation: %(operation)s - '
                'Duration: %(duration).4fs - Success: %(success)s - Details: %(details)s'
            )
        
        file_handler.setFormatter(file_formatter)
        self.perf_logger.addHandler(file_handler)
    
    def log(self, level, message, **kwargs):
        """Log a message with the specified level and additional context.
        
        Args:
            level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message (str): Log message
            **kwargs: Additional context to include in the log
        """
        level_num = LOG_LEVELS.get(level.upper(), logging.INFO)
        
        # Create extra dict for structured data
        extra = {'structured_data': json.dumps(kwargs) if kwargs else '{}'}
        
        # Log the message
        self.app_logger.log(level_num, message, extra=extra)
    
    def debug(self, message, **kwargs):
        """Log a debug message."""
        self.log('DEBUG', message, **kwargs)
    
    def info(self, message, **kwargs):
        """Log an info message."""
        self.log('INFO', message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log a warning message."""
        self.log('WARNING', message, **kwargs)
    
    def error(self, message, exc_info=None, **kwargs):
        """Log an error message with exception information."""
        user = kwargs.get('user', 'anonymous')
        
        # Get exception details
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_type = type(exc_info).__name__
                exc_message = str(exc_info)
                exc_traceback = ''.join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))
            else:
                exc_type = 'Unknown'
                exc_message = 'No exception details available'
                exc_traceback = ''
        else:
            exc_type = 'None'
            exc_message = 'No exception provided'
            exc_traceback = ''
        
        # Log to error logger
        extra = {
            'user': user,
            'exc_info': f"{exc_type}: {exc_message}",
            'trace': exc_traceback
        }
        
        self.error_logger.error(message, extra=extra)
        
        # Also log to app logger
        self.log('ERROR', message, exception=f"{exc_type}: {exc_message}", **kwargs)
    
    def critical(self, message, exc_info=None, **kwargs):
        """Log a critical message with exception information."""
        user = kwargs.get('user', 'anonymous')
        
        # Get exception details
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_type = type(exc_info).__name__
                exc_message = str(exc_info)
                exc_traceback = ''.join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))
            else:
                exc_type = 'Unknown'
                exc_message = 'No exception details available'
                exc_traceback = ''
        else:
            exc_type = 'None'
            exc_message = 'No exception provided'
            exc_traceback = ''
        
        # Log to error logger
        extra = {
            'user': user,
            'exc_info': f"{exc_type}: {exc_message}",
            'trace': exc_traceback
        }
        
        self.error_logger.critical(message, extra=extra)
        
        # Also log to app logger
        self.log('CRITICAL', message, exception=f"{exc_type}: {exc_message}", **kwargs)
    
    def log_access(self, user, method, path, status, ip, user_agent, response_time):
        """Log an API or page access.
        
        Args:
            user (str): User identifier
            method (str): HTTP method
            path (str): Request path
            status (int): HTTP status code
            ip (str): Client IP address
            user_agent (str): User agent string
            response_time (float): Response time in milliseconds
        """
        extra = {
            'user': user,
            'method': method,
            'path': path,
            'status': status,
            'ip': ip,
            'user_agent': user_agent,
            'response_time': response_time
        }
        
        self.access_logger.info('', extra=extra)
    
    def log_audit(self, user, action, resource, resource_id, success, details=None, ip=None):
        """Log an audit event.
        
        Args:
            user (str): User identifier
            action (str): Action performed (create, read, update, delete)
            resource (str): Resource type (user, course, assignment)
            resource_id (str): Resource identifier
            success (bool): Whether the action was successful
            details (str): Additional details
            ip (str): Client IP address
        """
        extra = {
            'user': user,
            'action': action,
            'resource': resource,
            'resource_id': str(resource_id),
            'success': success,
            'details': details or '',
            'ip': ip or '0.0.0.0'
        }
        
        self.audit_logger.info('', extra=extra)
    
    def log_performance(self, operation, duration, success=True, details=None):
        """Log a performance metric.
        
        Args:
            operation (str): Operation name
            duration (float): Duration in seconds
            success (bool): Whether the operation was successful
            details (str): Additional details
        """
        extra = {
            'operation': operation,
            'duration': duration,
            'success': success,
            'details': details or ''
        }
        
        self.perf_logger.info('', extra=extra)
    
    def performance_tracker(self, operation_name=None):
        """Decorator to track function performance.
        
        Args:
            operation_name (str): Name of the operation (defaults to function name)
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                operation = operation_name or f"{func.__module__}.{func.__name__}"
                success = True
                details = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    details = str(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    self.log_performance(operation, duration, success, details)
            
            return wrapper
        
        return decorator

# Create a singleton instance
logger = AdvancedLogger()

def get_logger():
    """Get the singleton logger instance."""
    return logger 