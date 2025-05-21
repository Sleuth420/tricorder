#!/usr/bin/env python3
import os
import shutil
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_pycache(start_path):
    """
    Recursively find and remove __pycache__ directories.
    
    Args:
        start_path (Path): The root directory to start searching from
    """
    try:
        # Convert to Path object if it's a string
        if isinstance(start_path, str):
            start_path = Path(start_path)
            
        # Walk through all directories
        for root, dirs, files in os.walk(start_path):
            # Check if __pycache__ exists in current directory
            if '__pycache__' in dirs:
                pycache_path = Path(root) / '__pycache__'
                try:
                    shutil.rmtree(pycache_path)
                    logger.info(f"Removed: {pycache_path}")
                except Exception as e:
                    logger.error(f"Error removing {pycache_path}: {e}")
                    
    except Exception as e:
        logger.error(f"An error occurred while cleaning: {e}")

def main():
    parser = argparse.ArgumentParser(description='Clean up __pycache__ directories recursively')
    parser.add_argument('--root', '-r', 
                      help='Root directory to start cleaning from (defaults to current directory)',
                      default=os.getcwd())
    
    args = parser.parse_args()
    root_dir = Path(args.root).resolve()
    
    logger.info(f"Starting cleanup from root directory: {root_dir}")
    clean_pycache(root_dir)
    logger.info("Cleanup completed")

if __name__ == "__main__":
    main() 