# --- models/update_manager.py ---
# Manages system and application updates

import os
import sys
import platform
import subprocess
import logging
import shutil
import json
import time
from pathlib import Path
import config as app_config
from .system_config_manager import SystemConfigManager
from datetime import datetime

logger = logging.getLogger(__name__)

class UpdateManager:
    """Manages system and application updates with comprehensive safety mechanisms."""
    
    def __init__(self, config_module):
        """
        Initialize the UpdateManager.
        
        Args:
            config_module: The configuration module containing update settings
        """
        self.config = config_module
        self.project_root = Path(__file__).parent.parent
        self.platform = platform.system()
        self.is_raspberry_pi = self._is_raspberry_pi()
        
        # Update state tracking
        self.update_menu_index = 0
        self.update_options = self._generate_update_options()
        
        # Status tracking
        self.last_check_result = None
        self.update_available = False
        self.current_version = self._get_current_version()
        self.remote_version = None
        
        # Initialize system config manager
        self.system_config_manager = SystemConfigManager(self.project_root)
        
        # Safety and logging
        self.update_state_file = self.project_root / "logs" / "update_state.json"
        self.os_update_lockfile = self.project_root / "logs" / "os_update.lock"
        
        # Check for interrupted updates on startup
        self._check_interrupted_updates()
        
        logger.info(f"UpdateManager initialized - Platform: {self.platform}, Raspberry Pi: {self.is_raspberry_pi}")
        
    def _check_interrupted_updates(self):
        """Check for interrupted updates and attempt recovery."""
        try:
            # Check for OS update lock file
            if self.os_update_lockfile.exists():
                logger.warning("⚠️  OS update lock file found - previous update may have been interrupted")
                self._recover_from_interrupted_os_update()
            
            # Check for update state file
            if self.update_state_file.exists():
                with open(self.update_state_file, 'r') as f:
                    update_state = json.load(f)
                
                logger.warning(f"⚠️  Update state file found - previous update interrupted at: {update_state.get('stage', 'unknown')}")
                self._recover_from_interrupted_update(update_state)
                
        except Exception as e:
            logger.error(f"Error checking interrupted updates: {e}")
    
    def _recover_from_interrupted_os_update(self):
        """Recover from interrupted OS update."""
        logger.info("🔧 Attempting recovery from interrupted OS update...")
        
        try:
            # Log the recovery attempt
            logger.info("OS update was interrupted - checking system integrity...")
            
            # Check if apt is locked
            if self._is_apt_locked():
                logger.warning("APT is locked - attempting to unlock...")
                self._unlock_apt()
            
            # Run system integrity checks
            integrity_ok = self._check_system_integrity()
            
            if integrity_ok:
                logger.info("✅ System integrity check passed")
                # Complete any pending configuration
                subprocess.run(["sudo", "dpkg", "--configure", "-a"], 
                             capture_output=True, timeout=60)
                logger.info("✅ Package configuration completed")
            else:
                logger.warning("⚠️  System integrity issues detected - manual intervention may be required")
            
            # Remove lock file
            self.os_update_lockfile.unlink()
            logger.info("🔓 OS update lock file removed")
            
        except Exception as e:
            logger.error(f"❌ OS update recovery failed: {e}")
    
    def _recover_from_interrupted_update(self, update_state):
        """Recover from interrupted application update."""
        logger.info(f"🔧 Attempting recovery from interrupted update at stage: {update_state.get('stage', 'unknown')}")
        
        try:
            stage = update_state.get('stage', '')
            timestamp = update_state.get('timestamp', '')
            
            logger.info(f"Update was interrupted at stage '{stage}' on {timestamp}")
            
            if stage in ['git_update', 'dependency_update', 'config_deployment']:
                logger.info("Attempting automatic rollback...")
                self._rollback_update()
                logger.info("✅ Automatic rollback completed")
            else:
                logger.info("✅ Update appears to have completed successfully")
            
            # Remove state file
            self.update_state_file.unlink()
            logger.info("🗑️  Update state file cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Update recovery failed: {e}")
    
    def _is_apt_locked(self):
        """Check if APT is locked."""
        lock_files = [
            "/var/lib/dpkg/lock",
            "/var/lib/dpkg/lock-frontend", 
            "/var/cache/apt/archives/lock",
            "/var/lib/apt/lists/lock"
        ]
        
        for lock_file in lock_files:
            if Path(lock_file).exists():
                try:
                    # Try to get lock info
                    result = subprocess.run(["sudo", "lsof", lock_file], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and result.stdout.strip():
                        return True
                except:
                    continue
        return False
    
    def _unlock_apt(self):
        """Safely unlock APT if no processes are using it."""
        logger.info("🔓 Unlocking APT package manager...")
        
        lock_files = [
            "/var/lib/dpkg/lock",
            "/var/lib/dpkg/lock-frontend",
            "/var/cache/apt/archives/lock", 
            "/var/lib/apt/lists/lock"
        ]
        
        for lock_file in lock_files:
            try:
                subprocess.run(["sudo", "rm", "-f", lock_file], 
                             capture_output=True, timeout=30)
                logger.debug(f"Removed lock file: {lock_file}")
            except Exception as e:
                logger.warning(f"Failed to remove lock file {lock_file}: {e}")
    
    def _check_system_integrity(self):
        """Check basic system integrity after interrupted update."""
        try:
            # Check if essential packages are properly configured
            result = subprocess.run(["dpkg", "--audit"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and not result.stdout.strip():
                return True  # No broken packages
            else:
                logger.warning(f"Package audit found issues: {result.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"System integrity check failed: {e}")
            return False
    
    def _save_update_state(self, stage, **kwargs):
        """Save current update state for recovery purposes."""
        try:
            # Ensure logs directory exists
            self.update_state_file.parent.mkdir(parents=True, exist_ok=True)
            
            state = {
                'stage': stage,
                'timestamp': datetime.now().isoformat(),
                'platform': self.platform,
                'is_raspberry_pi': self.is_raspberry_pi,
                **kwargs
            }
            
            with open(self.update_state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            logger.debug(f"💾 Update state saved: {stage}")
            
        except Exception as e:
            logger.warning(f"Failed to save update state: {e}")
    
    def _clear_update_state(self):
        """Clear update state file after successful completion."""
        try:
            if self.update_state_file.exists():
                self.update_state_file.unlink()
                logger.debug("🗑️  Update state file cleared")
        except Exception as e:
            logger.warning(f"Failed to clear update state: {e}")
    
    def _is_raspberry_pi(self):
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def _get_current_version(self):
        """Get current application version."""
        try:
            from config.version import get_version_info
            return get_version_info()
        except Exception as e:
            logger.error(f"Failed to get current version: {e}")
            return {"build_number": "Unknown", "commit_hash": "unknown"}
    
    def _generate_update_options(self):
        """Generate update menu options based on platform."""
        options = [
            {
                "name": "Quick App Update", 
                "action": "APP_UPDATE",
                "description": "Update application code and dependencies"
            },
            {
                "name": "Check for Updates",
                "action": "CHECK_UPDATES", 
                "description": "Check Git repository for available updates"
            }
        ]
        
        # Add system update option based on platform
        if self.is_raspberry_pi:
            options.insert(-1, {
                "name": "Full System Update",
                "action": "SYSTEM_UPDATE", 
                "description": "Update OS packages and application"
            })
        else:
            # On Windows, show what's NOT available
            options.insert(-1, {
                "name": "System Update (Pi Only)",
                "action": "SYSTEM_UPDATE_UNAVAILABLE", 
                "description": "OS updates only available on Raspberry Pi"
            })
        
        options.append({
            "name": "<- Back",
            "action": "GO_BACK",
            "description": "Return to settings menu"
        })
        
        return options

    def handle_update_input(self, action):
        """Handle input for the update menu."""
        state_changed = False
        
        if action == app_config.INPUT_ACTION_NEXT:
            self.update_menu_index = (self.update_menu_index + 1) % len(self.update_options)
            logger.debug(f"Update Menu NEXT: index={self.update_menu_index}")
            state_changed = True
        elif action == app_config.INPUT_ACTION_PREV:
            self.update_menu_index = (self.update_menu_index - 1 + len(self.update_options)) % len(self.update_options)
            logger.debug(f"Update Menu PREV: index={self.update_menu_index}")
            state_changed = True
        elif action == app_config.INPUT_ACTION_SELECT:
            state_changed = self._execute_selected_action()
            
        return state_changed
    
    def _execute_selected_action(self):
        """Execute the selected update action."""
        selected_option = self.update_options[self.update_menu_index]
        action = selected_option["action"]
        
        logger.info(f"Executing update action: {action}")
        
        if action == "CHECK_UPDATES":
            return self._check_for_updates()
        elif action == "APP_UPDATE":
            return "START_APP_UPDATE"  # Signal to start update process
        elif action == "SYSTEM_UPDATE" and self.is_raspberry_pi:
            return "START_SYSTEM_UPDATE"  # Signal to start system update
        elif action == "SYSTEM_UPDATE_UNAVAILABLE":
            self.last_check_result = "System updates are only available on Raspberry Pi"
            logger.info("System update attempted on non-Pi platform")
            return True
        elif action == "GO_BACK":
            return "GO_BACK"
        
        return False
    
    def _check_for_updates(self):
        """Check for available updates from Git repository."""
        try:
            logger.info("Checking for updates...")
            self.last_check_result = "Checking for updates..."
            
            # Check if we're in a git repository
            if not self._check_git_repository():
                self.last_check_result = "Not a Git repository or Git not available"
                logger.error("Update check failed: Not in a Git repository")
                return True
            
            # Check network connectivity first
            logger.info("Checking network connectivity...")
            if not self._check_network_connectivity():
                self.last_check_result = "No network connection to GitHub"
                logger.warning("Update check failed: No network connection")
                return True
            
            # Check if remote origin exists
            if not self._check_git_remote():
                self.last_check_result = "No Git remote 'origin' configured"
                logger.error("Update check failed: No Git remote configured")
                return True
            
            # Get remote version info
            logger.info("Fetching remote repository information...")
            remote_info = self._get_remote_version()
            if not remote_info:
                self.last_check_result = "Failed to fetch remote repository information"
                logger.error("Update check failed: Could not fetch remote info")
                return True
            
            # Compare versions
            current_hash = self.current_version.get("commit_hash", "unknown")
            remote_hash = remote_info.get("commit_hash", "unknown")
            commits_behind = remote_info.get("commits_behind", 0)
            
            logger.info(f"Version comparison - Current: {current_hash}, Remote: {remote_hash}, Behind: {commits_behind}")
            
            if commits_behind > 0:
                self.update_available = True
                self.remote_version = remote_info
                self.last_check_result = f"Update available: {commits_behind} commit(s) behind ({remote_hash})"
            else:
                self.update_available = False
                self.last_check_result = "Application is up to date"
            
            logger.info(f"Update check result: {self.last_check_result}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}", exc_info=True)
            self.last_check_result = f"Update check failed: {str(e)}"
            return True
    
    def _check_network_connectivity(self):
        """Check if network connection is available."""
        try:
            # Try to reach GitHub
            logger.debug("Testing network connectivity to github.com...")
            result = subprocess.run(
                ["ping", "-c", "1", "github.com"] if self.platform != "Windows" else ["ping", "-n", "1", "github.com"],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.debug("Network connectivity check: SUCCESS")
                return True
            else:
                logger.debug(f"Network connectivity check: FAILED (return code: {result.returncode})")
                if result.stderr:
                    logger.debug(f"Ping error output: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.debug("Network connectivity check: TIMEOUT")
            return False
        except Exception as e:
            logger.debug(f"Network connectivity check: EXCEPTION - {e}")
            return False
    
    def _check_git_repository(self):
        """Check if current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.debug("Git repository check: SUCCESS")
                return True
            else:
                logger.debug("Git repository check: FAILED - Not a git repository")
                return False
        except Exception as e:
            logger.debug(f"Git repository check: EXCEPTION - {e}")
            return False
    
    def _check_git_remote(self):
        """Check if git remote 'origin' is configured."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                remote_url = result.stdout.decode().strip()
                logger.debug(f"Git remote check: SUCCESS - {remote_url}")
                return True
            else:
                logger.debug("Git remote check: FAILED - No origin remote")
                return False
        except Exception as e:
            logger.debug(f"Git remote check: EXCEPTION - {e}")
            return False
    
    def _get_remote_version(self):
        """Get version information from remote repository."""
        try:
            # Fetch from remote repository
            logger.debug("Fetching from remote repository...")
            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"Git fetch failed: {error_msg}")
                return None
            
            logger.debug("Git fetch successful")
            
            # Check if there are differences (commits we're behind)
            logger.debug("Checking commits behind...")
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/master"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Try with 'main' branch as fallback
                logger.debug("Master branch not found, trying main branch...")
                result = subprocess.run(
                    ["git", "rev-list", "--count", "HEAD..origin/main"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    logger.error(f"Failed to check commits behind: {error_msg}")
                    return None
                    
                branch = "main"
            else:
                branch = "master"
            
            commits_behind = int(result.stdout.strip() or "0")
            logger.debug(f"Commits behind: {commits_behind}")
            
            # Get remote commit hash
            logger.debug(f"Getting remote commit hash for origin/{branch}...")
            result = subprocess.run(
                ["git", "rev-parse", "--short", f"origin/{branch}"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                remote_hash = result.stdout.strip()
                logger.debug(f"Remote hash: {remote_hash}")
            else:
                remote_hash = "unknown"
                logger.warning("Could not get remote commit hash")
            
            return {
                "commit_hash": remote_hash,
                "build_number": f"REMOTE {remote_hash}",
                "commits_behind": commits_behind,
                "branch": branch
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Git fetch operation timed out")
            return None
        except Exception as e:
            logger.error(f"Failed to get remote version: {e}", exc_info=True)
            return None
    
    def perform_app_update(self, loading_operation=None):
        """
        Perform application update with comprehensive logging and safety.
        
        Args:
            loading_operation: LoadingOperation instance for progress updates
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("🚀 Starting application update...")
        
        try:
            if loading_operation:
                loading_operation.step("Checking prerequisites...")
            
            self._save_update_state('prerequisites')
            
            if not self._check_network_connectivity():
                raise Exception("No network connection available")
            
            if not self._check_git_repository():
                raise Exception("Not in a Git repository")
            
            # Step 2: Create backup
            if loading_operation:
                loading_operation.step("Creating backup...")
            
            self._save_update_state('backup_creation')
            self._create_backup()
            
            # Step 3: Update git repository
            if loading_operation:
                loading_operation.step("Downloading updates...")
            
            self._save_update_state('git_update')
            self._update_git_repo()
            
            # Step 4: Update Python dependencies
            if loading_operation:
                loading_operation.step("Updating dependencies...")
            
            self._save_update_state('dependency_update')
            self._update_python_dependencies()
            
            # Step 5: Clean up files
            if loading_operation:
                loading_operation.step("Cleaning up...")
            
            self._save_update_state('cleanup')
            self._cleanup_after_update()
            
            # Step 6: Deploy system configuration files (if on Pi)
            if self.is_raspberry_pi:
                if loading_operation:
                    loading_operation.step("Deploying system configurations...")
                
                self._save_update_state('config_deployment')
                config_success = self.system_config_manager.deploy_system_configs(loading_operation)
                if not config_success:
                    logger.warning("System configuration deployment failed, but continuing...")
                    # Don't fail the entire update for config deployment failures
            elif loading_operation:
                # Non-Pi: advance step so progress count stays in sync (step 6 skipped)
                loading_operation.step("Preparing verification...")
            
            # Step 7: Verify update
            if loading_operation:
                loading_operation.step("Verifying update...")
            
            self._save_update_state('verification')
            if not self._verify_update():
                raise Exception("Update verification failed")
            
            # Clear update state on success
            self._clear_update_state()
            
            if loading_operation:
                loading_operation.update_status("Update completed successfully!")
            
            logger.info("✅ Application update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Application update failed: {e}")
            if loading_operation:
                loading_operation.update_status(f"Update failed: {str(e)}")
            
            # Attempt rollback
            try:
                self._save_update_state('rollback')
                self._rollback_update()
                
                # Also rollback system configs if on Pi
                if self.is_raspberry_pi:
                    if loading_operation:
                        loading_operation.update_status("Rolling back system configurations...")
                    self.system_config_manager.rollback_system_configs(loading_operation)
                
                self._clear_update_state()
                if loading_operation:
                    loading_operation.update_status("Rolled back to previous version")
            except Exception as rollback_error:
                logger.error(f"❌ Rollback failed: {rollback_error}")
                if loading_operation:
                                        loading_operation.update_status(f"Rollback failed: {str(rollback_error)}")
            
            return False

    def perform_system_update(self, loading_operation=None):
        """
        Perform full system update with comprehensive safety mechanisms.
        
        Args:
            loading_operation: LoadingOperation instance for progress updates
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_raspberry_pi:
            logger.warning("System update is only available on Raspberry Pi")
            if loading_operation:
                loading_operation.update_status("System update not available on this platform")
            return False
        
        logger.info("🚀 Starting full system update...")
        
        try:
            # Create OS update lock file
            self.os_update_lockfile.parent.mkdir(parents=True, exist_ok=True)
            with open(self.os_update_lockfile, 'w') as f:
                f.write(f"OS update started at: {datetime.now().isoformat()}\n")
            
            if loading_operation:
                loading_operation.step("Checking prerequisites...")
            
            self._save_update_state('os_prerequisites')
            
            if not self._check_network_connectivity():
                raise Exception("No network connection available")
            
            # Step 2: Update package lists
            if loading_operation:
                loading_operation.step("Updating package lists...")
            
            logger.info("📦 Updating package lists...")
            self._save_update_state('package_list_update')
            self._run_system_command(["sudo", "apt", "update"])
            
            # Step 3: Upgrade system packages (most critical step)
            if loading_operation:
                loading_operation.step("Upgrading system packages...")
            
            logger.info("⬆️  Upgrading system packages...")
            self._save_update_state('package_upgrade')
            self._run_system_command(["sudo", "apt", "upgrade", "-y"])
            
            # Step 4: Clean up system packages
            if loading_operation:
                loading_operation.step("Cleaning up packages...")
            
            logger.info("🧹 Cleaning up packages...")
            self._save_update_state('package_cleanup')
            self._run_system_command(["sudo", "apt", "autoremove", "-y"])
            self._run_system_command(["sudo", "apt", "autoclean"])
            
            # Step 5: Update application (don't pass loading_operation - we use 6 steps for system only)
            if loading_operation:
                loading_operation.step("Updating application...")
            
            self._save_update_state('app_update')
            if not self.perform_app_update(None):
                raise Exception("Application update failed during system update")
            
            # Step 6: Deploy system configuration files
            if loading_operation:
                loading_operation.step("Deploying system configurations...")
            
            logger.info("⚙️  Deploying system configurations...")
            self._save_update_state('final_config_deployment')
            config_success = self.system_config_manager.deploy_system_configs(loading_operation)
            if not config_success:
                logger.warning("System configuration deployment failed, but continuing...")
                # Don't fail the entire update for config deployment failures
            
            # Remove OS update lock file
            if self.os_update_lockfile.exists():
                self.os_update_lockfile.unlink()
            
            # Clear update state on success
            self._clear_update_state()
            
            if loading_operation:
                loading_operation.update_status("System update completed!")
            
            logger.info("✅ System update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ System update failed: {e}")
            if loading_operation:
                loading_operation.update_status(f"System update failed: {str(e)}")
            
            # Leave lock file in place for recovery
            logger.warning("🔒 OS update lock file preserved for recovery on next startup")
            return False
    
    def _create_backup(self):
        """Create backup of current application state."""
        logger.info("Creating backup...")
        
        # Create git stash as backup
        try:
            subprocess.run(
                ["git", "stash", "push", "-m", f"Backup before update {self.current_version.get('commit_hash', 'unknown')}"],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            logger.info("Git backup created successfully")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Git backup failed (non-critical): {e}")
    
    def _update_git_repo(self):
        """Update git repository."""
        logger.info("Updating git repository...")
        
        # First fetch from origin
        self._run_system_command(["git", "fetch", "origin"])
        
        # Determine which branch to use (main or master)
        branch = "main"  # Default to main
        try:
            # Check if main branch exists on remote
            result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", "main"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if not result.stdout.strip():
                # main doesn't exist, try master
                logger.debug("main branch not found on remote, trying master...")
                result = subprocess.run(
                    ["git", "ls-remote", "--heads", "origin", "master"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout.strip():
                    branch = "master"
                    logger.debug("Using master branch")
                else:
                    raise Exception("Neither main nor master branch found on remote")
            else:
                logger.debug("Using main branch")
                
        except Exception as e:
            logger.warning(f"Could not determine remote branch, defaulting to main: {e}")
            branch = "main"
        
        # Reset to the determined branch
        logger.info(f"🔄 Resetting to origin/{branch}...")
        self._run_system_command(["git", "reset", "--hard", f"origin/{branch}"])
        
        logger.info("Git repository updated successfully")
    
    def _update_python_dependencies(self):
        """Update Python dependencies."""
        logger.info("Updating Python dependencies...")
        
        # Determine which requirements file to use
        if self.platform == "Windows":
            req_file = self.project_root / "requirements-windows.txt"
        else:
            req_file = self.project_root / "requirements.txt"
        
        if not req_file.exists():
            logger.warning(f"Requirements file not found: {req_file}")
            return
        
        # Get Python executable (handle virtual environment)
        python_exe = sys.executable
        
        # Update pip first
        self._run_system_command([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install/update requirements
        self._run_system_command([python_exe, "-m", "pip", "install", "-r", str(req_file), "--upgrade"])
        
        logger.info("Python dependencies updated successfully")
    
    def _cleanup_after_update(self):
        """Clean up after update."""
        logger.info("Cleaning up after update...")
        
        # Clean Python cache
        self._clean_pycache()
        
        # Clean git
        try:
            subprocess.run(
                ["git", "gc", "--prune=now"],
                cwd=self.project_root,
                capture_output=True
            )
        except:
            pass  # Non-critical
        
        logger.info("Cleanup completed")
    
    def _clean_pycache(self):
        """Clean Python cache files."""
        logger.info("Cleaning Python cache...")
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove __pycache__ directories
            if '__pycache__' in dirs:
                pycache_path = Path(root) / '__pycache__'
                try:
                    shutil.rmtree(pycache_path)
                    logger.debug(f"Removed: {pycache_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove {pycache_path}: {e}")
            
            # Remove .pyc files
            for file in files:
                if file.endswith('.pyc'):
                    pyc_path = Path(root) / file
                    try:
                        pyc_path.unlink()
                        logger.debug(f"Removed: {pyc_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove {pyc_path}: {e}")
    
    def _verify_update(self):
        """Verify that update was successful."""
        try:
            # Try to import main modules
            import config
            
            # Check if git repository is in good state
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Update version info
            self.current_version = self._get_current_version()
            
            logger.info(f"Update verification passed. New version: {self.current_version.get('build_number', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Update verification failed: {e}")
            return False
    
    def _rollback_update(self):
        """Rollback to previous version."""
        logger.info("Rolling back update...")
        
        try:
            # Try to pop the stash we created
            subprocess.run(
                ["git", "stash", "pop"],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            logger.info("Rollback completed successfully")
        except subprocess.CalledProcessError:
            # If stash pop fails, try to reset to HEAD~1
            try:
                subprocess.run(
                    ["git", "reset", "--hard", "HEAD~1"],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True
                )
                logger.info("Rollback to previous commit completed")
            except subprocess.CalledProcessError as e:
                logger.error(f"Rollback failed: {e}")
                raise
    
    def _run_system_command(self, command):
        """Run system command with comprehensive logging and safety."""
        cmd_str = ' '.join(command)
        logger.info(f"🔨 Executing: {cmd_str}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for system operations
            )
            
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            if result.returncode != 0:
                logger.error(f"❌ Command failed after {duration:.1f}ms: {cmd_str}")
                logger.error(f"Return code: {result.returncode}")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr.strip()}")
                if result.stdout:
                    logger.error(f"Standard output: {result.stdout.strip()}")
                raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
            else:
                logger.info(f"✅ Command completed in {duration:.1f}ms: {cmd_str}")
                if result.stdout:
                    # Log first few lines for important output
                    output_lines = result.stdout.strip().split('\n')
                    if len(output_lines) <= 5:
                        logger.debug(f"Output: {result.stdout.strip()}")
                    else:
                        logger.debug(f"Output (first 3 lines): {' | '.join(output_lines[:3])}...")
                        
        except subprocess.TimeoutExpired:
            duration = (time.time() - start_time) * 1000
            logger.error(f"⏰ Command timed out after {duration:.1f}ms: {cmd_str}")
            raise Exception(f"Command timed out: {cmd_str}")
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"💥 Command exception after {duration:.1f}ms: {cmd_str} - {e}")
            raise
    
    def get_update_info(self):
        """Get current update information for UI."""
        # Get system config status
        system_config_status = self.system_config_manager.check_system_config_files()
        
        return {
            'options': self.update_options,
            'selected_index': self.update_menu_index,
            'selected_option': self.update_options[self.update_menu_index],
            'platform': self.platform,
            'is_raspberry_pi': self.is_raspberry_pi,
            'current_version': self.current_version,
            'remote_version': self.remote_version,
            'update_available': self.update_available,
            'last_check_result': self.last_check_result,
            'system_config_status': system_config_status
        }
    
    def restart_application(self):
        """Restart the application after update."""
        logger.info("Restarting application...")
        
        try:
            if self.platform == "Windows":
                # Windows restart
                python_exe = sys.executable
                script_path = str(self.project_root / "main.py")
                subprocess.Popen([python_exe, script_path])
            else:
                # Linux restart
                os.execv(sys.executable, [sys.executable] + sys.argv)
                
        except Exception as e:
            logger.error(f"Failed to restart application: {e}")
            raise 