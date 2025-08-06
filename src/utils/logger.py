"""
Logging utility for the Fal Gram Bot.
Provides centralized logging functionality.
"""

import logging
from config.settings import settings


def setup_logger(name: str = None) -> logging.Logger:
    """
    Set up a logger with the specified name.
    
    Args:
        name: Logger name (defaults to 'fal_gram_bot')
    
    Returns:
        Configured logger instance
    """
    if not name:
        name = 'fal_gram_bot'
    
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger() 