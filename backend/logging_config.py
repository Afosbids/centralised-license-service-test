import logging
import os
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime

def setup_logging():
    """Configure structured logging with JSON formatting."""
    
    # Get log level from environment (default: INFO)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json").lower()
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    if log_format == "json":
        # JSON formatter for production
        formatter = jsonlogger.JsonFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s',
            rename_fields={
                'levelname': 'level',
                'name': 'logger',
                'asctime': 'timestamp'
            }
        )
    else:
        # Plain text formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)

# Custom filter to add timestamp in ISO format
class ISOTimestampFilter(logging.Filter):
    def filter(self, record):
        record.timestamp = datetime.utcnow().isoformat() + 'Z'
        return True

# Add the filter to root logger
logging.getLogger().addFilter(ISOTimestampFilter())
