# --- logging_config.py ---
# Handles the logging configuration for the tricorder application.

import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime

LOG_DIRECTORY = "logs"
LOG_FILENAME = "tricorder.log"
LOG_MAX_BYTES = 1024 * 1024 * 5 # 5 MB limit per file (adjust as needed)
LOG_BACKUP_COUNT = 7 # Keep 7 backup files

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output with emoji indicators."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green  
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    # Emoji indicators for different log levels
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '💬', 
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    def format(self, record):
        # Add color and emoji to levelname
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        emoji = self.EMOJIS.get(levelname, '')
        
        # Create colored levelname with emoji
        colored_levelname = f"{color}{emoji} {levelname}{self.COLORS['RESET']}"
        
        # Temporarily replace levelname for formatting
        original_levelname = record.levelname
        record.levelname = colored_levelname
        
        # Format the record
        formatted = super().format(record)
        
        # Restore original levelname
        record.levelname = original_levelname
        
        return formatted

class StructuredFormatter(logging.Formatter):
    """Enhanced formatter with structured information and better readability."""
    
    def format(self, record):
        # Add extra context
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Get module path for better context
        module_parts = record.name.split('.')
        if len(module_parts) > 2:
            # Show last 2 parts for deeply nested modules
            short_name = f"...{'.'.join(module_parts[-2:])}"
        else:
            short_name = record.name
            
        # Format: [TIMESTAMP] LEVEL | MODULE | MESSAGE
        formatted = f"[{timestamp}] {record.levelname:8} | {short_name:25} | {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
            
        return formatted

def setup_logging(log_level=logging.INFO, enable_colors=True, enable_structured=True):
    """
    Configures enhanced logging to write to both a rotating file and console.
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
        enable_colors: Whether to use colored console output (default: True)
        enable_structured: Whether to use structured formatting (default: True)
    """
    # Create log directory if it doesn't exist
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
    
    log_file_path = os.path.join(LOG_DIRECTORY, LOG_FILENAME)
    
    # Create formatters
    if enable_structured:
        file_formatter = StructuredFormatter()
        if enable_colors and sys.stdout.isatty():  # Only use colors if terminal supports it
            console_formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        else:
            console_formatter = StructuredFormatter()
    else:
        # Fallback to original format
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

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
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
        
        logging.debug(f"File logging initialized: {log_file_path}")
    except Exception as e:
        print(f"Warning: Unable to create log file at {log_file_path}: {e}")
        # Continue without file logging, but still use console
    
    # 2. Setup console handler for stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    logging.info("🚀 Enhanced logging initialized: console + file output enabled")
    logging.info(f"📁 Log file location: {os.path.abspath(log_file_path)}")

    # Log system info for debugging
    logging.debug(f"🐍 Python version: {sys.version}")
    logging.debug(f"📊 Log level: {logging.getLevelName(log_level)}")
    logging.debug(f"🎨 Colors enabled: {enable_colors and sys.stdout.isatty()}")
    logging.debug(f"📋 Structured format: {enable_structured}")

def log_performance(func_name, duration_ms, **kwargs):
    """Helper function for performance logging."""
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    logging.info(f"⏱️  PERF | {func_name} completed in {duration_ms:.2f}ms{' | ' + extra_info if extra_info else ''}")

def log_user_action(action, details=None):
    """Helper function for user action logging."""
    detail_str = f" | {details}" if details else ""
    logging.info(f"👤 USER | {action}{detail_str}")

def log_system_event(event, component=None, status="SUCCESS"):
    """Helper function for system event logging."""
    comp_str = f" | {component}" if component else ""
    logging.info(f"⚙️  SYS | {event} | {status}{comp_str}")

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
    
    logging.warning(f"🔧 Log level changed to: {logging.getLevelName(level)}")

# --- Optional: Log cleanup (can be added if TimedRotatingFileHandler isn't sufficient) ---
# Although TimedRotatingFileHandler manages backups, you could add
# more complex cleanup logic here if needed, e.g., based on total size.
# For now, the handler's backupCount handles the retention period. 