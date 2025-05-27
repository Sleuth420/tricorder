# --- test_logging.py ---
# Simple script to test the logging configuration

import logging
import logging_config
import os
import sys

# Get a logger for this module
logger = logging.getLogger(__name__)

def main():
    """Test the logging configuration by logging messages at different levels."""
    print("Testing logging configuration...")
    
    # Setup logging with DEBUG level to show all messages
    logging_config.setup_logging(log_level=logging.DEBUG)
    
    # Log messages at different levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Test changing log level at runtime
    print("\nChanging log level to WARNING...")
    logging_config.set_log_level(logging.WARNING)
    
    # These should be filtered out
    logger.debug("This DEBUG message should not appear")
    logger.info("This INFO message should not appear")
    
    # These should still show
    logger.warning("This WARNING message should appear")
    logger.error("This ERROR message should appear")
    logger.critical("This CRITICAL message should appear")
    
    # Show log file location
    log_file_path = os.path.join(logging_config.LOG_DIRECTORY, logging_config.LOG_FILENAME)
    print(f"\nLog file should be at: {os.path.abspath(log_file_path)}")
    print("Check both console output above and log file contents to verify configuration")

if __name__ == "__main__":
    main() 