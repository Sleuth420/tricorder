import os
import logging
import pprint

logger = logging.getLogger(__name__)

def count_python_lines():
    """Count all lines of Python code in the project, excluding unwanted directories and files."""
    exclude_dirs = {'__pycache__', '.venv', '.venv_windows', '.git', 'logs', 'assets', 'venv', 'venv_windows', 'tests'}
    exclude_extensions = {'.txt', '.md', '.png', '.jpg', '.jpeg', '.gif', '.json', '.log', '.gitignore', '.env', '.env.example'}
    exclude_files = {'config_old.py'}  # Specific files to exclude
    
    total_lines = 0
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories from dirs list to prevent os.walk from entering them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Only count .py files, but exclude specific files and extensions
            if file_ext == '.py' and file not in exclude_files and file_ext not in exclude_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        python_files.append((file_path, lines))
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
    
    logger.info(f"Counted {total_lines} lines of Python code across {len(python_files)} files")
    # Log the full list of scanned files at INFO level, formatted nicely.
    logger.info(f"Files scanned:\n{pprint.pformat(python_files)}")
    return total_lines, python_files 