"""Logging Configuration."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "geostudio",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Configure logger."""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


logger = setup_logger()


def set_log_level(level: int) -> None:
    """Change logging level."""
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
