# --- logging_config.py ---
# Handles the logging configuration for the tricorder application.

import logging
import logging.handlers
import os
import sys
from datetime import datetime

LOG_DIRECTORY = "logs"
LOG_FILENAME = "tricorder.log"
LOG_MAX_BYTES = 1024 * 1024 * 5 # 5 MB limit per file (adjust as needed)
LOG_BACKUP_COUNT = 7 # Keep 7 backup files

def setup_logging(log_level=logging.INFO):
    """
    Configures logging to write to both a rotating file and console.
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
    """
    # Create log directory if it doesn't exist
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)
    
    log_file_path = os.path.join(LOG_DIRECTORY, LOG_FILENAME)
    
    # Create a formatter that includes timestamp, level, and module name
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers (to avoid duplicates if setup_logging is called multiple times)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 1. Setup file handler with rotation
    try:
        # Use TimedRotatingFileHandler for daily rotation
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file_path,
            when='midnight', # Rotate daily
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
        
        logging.debug(f"File logging initialized: {log_file_path}")
    except Exception as e:
        print(f"Warning: Unable to create log file at {log_file_path}: {e}")
        # Continue without file logging, but still use console
    
    # 2. Setup console handler for stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    logging.info("Logging initialized: sending logs to both console and file.")
    logging.info(f"Log file location: {os.path.abspath(log_file_path)}")

    # Log system info for debugging
    logging.debug(f"Python version: {sys.version}")
    logging.debug(f"Log level: {logging.getLevelName(log_level)}")

# Helper function to change log level at runtime if needed
def set_log_level(level):
    """
    Change the logging level at runtime.
    
    Args:
        level: A logging level (e.g., logging.DEBUG, logging.INFO)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Update all handlers to the same level
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    logging.warning(f"Log level changed to: {logging.getLevelName(level)}")

# --- Optional: Log cleanup (can be added if TimedRotatingFileHandler isn't sufficient) ---
# Although TimedRotatingFileHandler manages backups, you could add
# more complex cleanup logic here if needed, e.g., based on total size.
# For now, the handler's backupCount handles the retention period. 