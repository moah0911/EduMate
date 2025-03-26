import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logger
def setup_logger(name, log_file, level=logging.INFO):
    """Create and configure a logger"""
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s - {%(pathname)s:%(lineno)d}'
    )

    # Create a rotating file handler
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    handler.setFormatter(formatter)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Create different loggers for different purposes
system_logger = setup_logger('system', 'system.log')
access_logger = setup_logger('access', 'access.log')
error_logger = setup_logger('error', 'error.log')
audit_logger = setup_logger('audit', 'audit.log')

def log_system_event(message):
    """Log system events"""
    system_logger.info(message)

def log_access(user_id, action):
    """Log user access and actions"""
    access_logger.info(f"User {user_id}: {action}")

def log_error(error, context=None):
    """Log errors with context"""
    if context:
        error_logger.error(f"{error} - Context: {context}")
    else:
        error_logger.error(str(error))

def log_audit(user_id, action, details):
    """Log audit trail entries"""
    audit_logger.info(f"USER:{user_id} ACTION:{action} DETAILS:{details}")
