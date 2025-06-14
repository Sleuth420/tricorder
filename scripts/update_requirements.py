#!/usr/bin/env python3
"""
Script to update package versions in requirements files.
Updates both requirements.txt and requirements-windows.txt while maintaining comments and structure.
"""

import re
from pathlib import Path
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_latest_version(package_name):
    """Get the latest version of a package from PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
        else:
            logger.error(f"Failed to fetch {package_name} info from PyPI (status {response.status_code})")
            return None
    except Exception as e:
        logger.error(f"Error fetching version for {package_name}: {e}")
        return None

def update_requirements_file(file_path):
    """Update package versions in a requirements file while preserving comments and structure."""
    try:
        file_path = Path(file_path).resolve()
        logger.info(f"Processing file: {file_path}")
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return
        with open(file_path, 'r') as f:
            content = f.readlines()
        updated_content = []
        for line in content:
            orig_line = line.rstrip('\n')
            line = line.strip()
            if not line or line.startswith('#'):
                updated_content.append(orig_line)
                continue
            match = re.match(r'([a-zA-Z0-9_\-]+)==(\d+\.\d+\.\d+)', line)
            if match:
                package_name, current_version = match.groups()
                latest_version = get_latest_version(package_name)
                if latest_version and latest_version != current_version:
                    logger.info(f"Updating {package_name} from {current_version} to {latest_version}")
                    updated_content.append(f"{package_name}=={latest_version}")
                elif latest_version:
                    updated_content.append(orig_line)
                else:
                    logger.error(f"Could not update {package_name}, keeping current version {current_version}")
                    updated_content.append(orig_line)
            else:
                updated_content.append(orig_line)
        with open(file_path, 'w') as f:
            f.write('\n'.join(updated_content) + '\n')
        logger.info(f"Successfully updated {file_path}")
    except Exception as e:
        logger.error(f"Error updating {file_path}: {e}")

def main():
    project_root = Path(__file__).parent.parent.resolve()
    logger.info(f"Project root: {project_root}")
    requirements_files = [
        project_root / 'requirements.txt',
        project_root / 'requirements-windows.txt'
    ]
    for req_file in requirements_files:
        if req_file.exists():
            logger.info(f"Updating {req_file.name}...")
            update_requirements_file(req_file)
        else:
            logger.warning(f"File not found: {req_file}")

if __name__ == "__main__":
    main() 