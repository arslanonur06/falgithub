"""
Logging configuration for the Fal Gram Bot.
"""

import logging
import sys
from typing import Dict, Any
from config.settings import settings

def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    
    # Create logger
    logger = logging.getLogger("fal_gram_bot")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Create formatter
    if settings.DEBUG:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler for production
    if not settings.DEBUG:
        try:
            file_handler = logging.FileHandler('logs/fal_gram_bot.log')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except FileNotFoundError:
            # Create logs directory if it doesn't exist
            import os
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler('logs/fal_gram_bot.log')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance."""
    if name:
        return logging.getLogger(f"fal_gram_bot.{name}")
    return logging.getLogger("fal_gram_bot")

# Initialize logging
logger = setup_logging()