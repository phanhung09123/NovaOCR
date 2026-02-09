"""Logging utility for NovaOCR - Single Responsibility Principle"""
import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """
    Centralized logging configuration for the application.
    
    Provides both console and file logging with colored output.
    """
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "NovaOCR", level: str = "INFO", 
                   file_path: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            file_path: Optional file path for logging
            
        Returns:
            Configured logger instance
        """
        if cls._instance is not None:
            return cls._instance
            
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Remove existing handlers
        logger.handlers = []
        
        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Colored format for console
        console_format = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if file_path:
            try:
                log_file = Path(file_path)
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)  # Log everything to file
                
                file_format = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_format)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not create log file: {e}")
        
        cls._instance = logger
        return logger


def get_logger(name: str = "NovaOCR") -> logging.Logger:
    """Convenience function to get logger"""
    return Logger.get_logger(name)
