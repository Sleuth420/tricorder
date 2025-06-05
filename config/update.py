# --- config/update.py ---
# Update system configuration

# GitHub Repository Configuration
# Update these values for your specific repository
GITHUB_REPO_OWNER = "Sleuth420"          # Your GitHub username
GITHUB_REPO_NAME = "tricorder"           # Your repository name  
GITHUB_BRANCH = "main"                   # Branch to update from (main is your default)

# Full repository URL for reference
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}.git"

# Update System Settings
UPDATE_TIMEOUT_SECONDS = 300             # 5 minutes timeout for update operations
NETWORK_CHECK_TIMEOUT = 10               # 10 seconds for network connectivity check
MAX_RETRY_ATTEMPTS = 3                   # Maximum retry attempts for failed operations

# Platform-specific settings
ENABLE_SYSTEM_UPDATES_ON_WINDOWS = False # Set to True to enable OS updates on Windows (not recommended)
REQUIRE_SUDO_CONFIRMATION = True         # Require explicit confirmation for sudo operations

# Update verification settings
VERIFY_IMPORTS_AFTER_UPDATE = True       # Test import of key modules after update
CLEANUP_ON_SUCCESS = True               # Clean up temporary files after successful update
BACKUP_RETENTION_DAYS = 7               # How long to keep backup stashes (git)

# Logging settings for updates
LOG_UPDATE_COMMANDS = True               # Log all update commands for debugging
LOG_COMMAND_OUTPUT = False               # Log stdout/stderr of update commands (verbose)
LOG_NETWORK_CHECKS = True                # Log network connectivity checks

# Error handling
ROLLBACK_ON_IMPORT_FAILURE = True        # Rollback if post-update imports fail
ROLLBACK_ON_DEPENDENCY_FAILURE = True    # Rollback if pip install fails
SHOW_DETAILED_ERROR_MESSAGES = True      # Show detailed error messages to user 