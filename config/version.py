"""
Version information for the tricorder application.
Handles automatic version generation based on git commits.
"""

import subprocess
import logging
import os

logger = logging.getLogger(__name__)

# Version configuration - update these manually when needed
RELEASE_STAGE = "BETA"
MAJOR_VERSION = 0
MINOR_VERSION = 1

def get_git_commit_count():
    """
    Get the number of git commits in the current repository.
    
    Returns:
        int: Number of commits, or 1 as fallback
    """
    try:
        # Get total commit count (go up one directory since we're in config/)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_root
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        logger.warning(f"Could not get git commit count: {e}")
        return 1  # Fallback to 1 if git is unavailable

def get_git_commit_hash():
    """
    Get the current git commit hash (short version).
    
    Returns:
        str: Short commit hash, or 'unknown' as fallback
    """
    try:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_root
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.warning(f"Could not get git commit hash: {e}")
        return 'unknown'

def get_build_number():
    """
    Generate the build number string for display (short form to fit menu footer).
    Format: STAGE MAJOR.MINOR (one decimal place)
    
    Returns:
        str: Build number string
    """
    return f"{RELEASE_STAGE} {MAJOR_VERSION}.{MINOR_VERSION}"


def get_build_number_full():
    """
    Full build string including patch (for Settings/update screen, logging).
    Format: STAGE MAJOR.MINOR.PATCH
    """
    patch_version = get_git_commit_count()
    return f"{RELEASE_STAGE} {MAJOR_VERSION}.{MINOR_VERSION}.{patch_version}"

def get_version_info():
    """
    Get complete version information.
    
    Returns:
        dict: Dictionary containing version info
    """
    return {
        'stage': RELEASE_STAGE,
        'major': MAJOR_VERSION,
        'minor': MINOR_VERSION,
        'patch': get_git_commit_count(),
        'commit_hash': get_git_commit_hash(),
        'build_number': get_build_number_full()
    }

# For backward compatibility (short form used in menu footer)
BUILD_NUMBER = get_build_number() 