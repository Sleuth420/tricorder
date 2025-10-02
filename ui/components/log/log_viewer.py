# --- ui/components/log/log_viewer.py ---
# Log viewer component for displaying application logs

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LogViewer:
    """Component for viewing application logs."""
    
    def __init__(self, log_file_path="logs/tricorder.log"):
        """
        Initialize log viewer.
        
        Args:
            log_file_path (str): Path to the log file
        """
        self.log_file_path = log_file_path
        self.max_lines = 20  # Maximum lines to display
        self.scroll_index = 0
        
    def get_log_lines(self):
        """
        Get log lines for display.
        
        Returns:
            list: List of log lines (most recent first)
        """
        try:
            if not os.path.exists(self.log_file_path):
                return ["Log file not found: " + self.log_file_path]
            
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get the last N lines, reverse so most recent is first
            recent_lines = lines[-100:]  # Read last 100 lines from file
            recent_lines.reverse()  # Most recent first
            
            # Format lines for display
            formatted_lines = []
            for line in recent_lines:
                line = line.strip()
                if line:
                    # Clean up log format for better readability
                    # Remove excessive whitespace
                    line = ' '.join(line.split())
                    
                    # Format timestamp if present
                    if '|' in line and ('INFO' in line or 'WARNING' in line or 'ERROR' in line or 'CRITICAL' in line):
                        parts = line.split('|', 2)
                        if len(parts) >= 3:
                            # Format: timestamp | level | message
                            timestamp = parts[0].strip()
                            level = parts[1].strip()
                            message = parts[2].strip()
                            
                            # Shorten timestamp to just time
                            if ' ' in timestamp:
                                time_part = timestamp.split(' ')[1]  # Get time part only
                                # Remove microseconds for cleaner display
                                if '.' in time_part:
                                    time_part = time_part.split('.')[0]
                                line = f"{time_part} {level} {message}"
                            else:
                                line = f"{level} {message}"
                        else:
                            # Fallback: just clean up the line
                            line = ' '.join(line.split())
                    else:
                        # Clean up other lines
                        line = ' '.join(line.split())
                    
                    formatted_lines.append(line)
            
            return formatted_lines
            
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            return [f"Error reading log file: {str(e)}"]
    
    def get_display_lines(self, scroll_index=0):
        """
        Get lines to display based on scroll position.
        
        Args:
            scroll_index (int): Current scroll position
            
        Returns:
            list: Lines to display
        """
        all_lines = self.get_log_lines()
        start_idx = scroll_index
        end_idx = min(start_idx + self.max_lines, len(all_lines))
        
        if start_idx >= len(all_lines):
            return ["End of log file"]
        
        return all_lines[start_idx:end_idx]
