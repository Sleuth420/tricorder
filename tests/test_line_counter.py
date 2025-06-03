#!/usr/bin/env python3
"""
Simple test script to verify the Python line counting functionality.
Run this to see what the loading screen will display.
"""

import os
import time

def count_python_lines():
    """Count all lines of Python code in the project, excluding unwanted directories."""
    exclude_dirs = {'__pycache__', 'venv', 'venv_windows', '.git', 'logs', 'assets'}
    exclude_extensions = {'.txt', '.md', '.png', '.jpg', '.jpeg', '.gif', '.json', '.log', '.gitignore'}
    
    total_lines = 0
    python_files = []
    
    print("Scanning for Python files...")
    print(f"Excluding directories: {', '.join(sorted(exclude_dirs))}")
    print()
    
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories from dirs list to prevent os.walk from entering them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Only count .py files
            if file_ext == '.py':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        python_files.append((file_path, lines))
                        print(f"  {file_path}: {lines:,} lines")
                except Exception as e:
                    print(f"  ERROR reading {file_path}: {e}")
    
    print()
    print(f"TOTAL: {total_lines:,} lines of Python code across {len(python_files)} files")
    return total_lines, python_files

if __name__ == "__main__":
    start_time = time.time()
    total_lines, files = count_python_lines()
    end_time = time.time()
    
    print(f"\nScan completed in {end_time - start_time:.2f} seconds")
    print(f"\nTop 5 largest files:")
    files.sort(key=lambda x: x[1], reverse=True)
    for i, (filepath, lines) in enumerate(files[:5]):
        print(f"  {i+1}. {filepath}: {lines:,} lines") 