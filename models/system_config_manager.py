# --- models/system_config_manager.py ---
# Manages system configuration files deployment and rollback

import os
import shutil
import subprocess
import logging
from pathlib import Path
import platform

logger = logging.getLogger(__name__)

class SystemConfigManager:
    """Manages deployment and rollback of system configuration files."""
    
    def __init__(self, project_root):
        """
        Initialize the system configuration manager.
        
        Args:
            project_root (Path): Root directory of the project
        """
        self.project_root = Path(project_root)
        self.system_config_dir = self.project_root / "system_config"
        self.is_raspberry_pi = self._is_raspberry_pi()
        
        # Define system configuration file mappings
        self.config_mappings = self._get_config_mappings()
        
        logger.info(f"SystemConfigManager initialized - Raspberry Pi: {self.is_raspberry_pi}")
        logger.debug(f"System config directory: {self.system_config_dir}")
    
    def _is_raspberry_pi(self):
        """Check if running on Raspberry Pi."""
        try:
            if platform.system() != "Linux":
                return False
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def _get_config_mappings(self):
        """Get the mapping of config files to their system locations."""
        if not self.is_raspberry_pi:
            # On non-Pi systems, return empty mappings
            return {}
        
        # Get the current user's home directory
        home_dir = Path.home()
        
        return {
            # Boot configuration files (require sudo)
            "config.txt": {
                "source": self.system_config_dir / "config.txt",
                "target": Path("/boot/firmware/config.txt"),
                "backup": Path("/boot/firmware/config.txt.bak"),
                "requires_sudo": True,
                "description": "Raspberry Pi boot configuration"
            },
            "cmdline.txt": {
                "source": self.system_config_dir / "cmdline.txt", 
                "target": Path("/boot/firmware/cmdline.txt"),
                "backup": Path("/boot/firmware/cmdline.txt.bak"),
                "requires_sudo": True,
                "description": "Raspberry Pi boot command line"
            },
            # User configuration files
            "wayfire.ini": {
                "source": self.system_config_dir / "wayfire.ini",
                "target": home_dir / ".config" / "wayfire.ini",
                "backup": home_dir / ".config" / "wayfire.ini.bak",
                "requires_sudo": False,
                "description": "Wayfire compositor configuration"
            }
        }
    
    def check_system_config_files(self):
        """Check which system config files are available and their status."""
        if not self.is_raspberry_pi:
            return {"available": [], "missing": [], "status": "Not on Raspberry Pi"}
        
        if not self.system_config_dir.exists():
            return {"available": [], "missing": [], "status": "No system_config directory"}
        
        available = []
        missing = []
        
        for config_name, config_info in self.config_mappings.items():
            source_file = config_info["source"]
            target_file = config_info["target"]
            
            source_exists = source_file.exists()
            target_exists = target_file.exists()
            
            status = {
                "name": config_name,
                "description": config_info["description"],
                "source_exists": source_exists,
                "target_exists": target_exists,
                "requires_sudo": config_info["requires_sudo"],
                "source_path": str(source_file),
                "target_path": str(target_file)
            }
            
            if source_exists:
                available.append(status)
            else:
                missing.append(status)
        
        return {
            "available": available,
            "missing": missing,
            "status": f"Found {len(available)} config files, {len(missing)} missing"
        }
    
    def deploy_system_configs(self, loading_operation=None):
        """
        Deploy system configuration files to their proper locations.
        
        Args:
            loading_operation: LoadingOperation instance for progress updates
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_raspberry_pi:
            logger.warning("System config deployment only available on Raspberry Pi")
            return False
        
        if not self.system_config_dir.exists():
            logger.warning(f"System config directory not found: {self.system_config_dir}")
            return False
        
        deployed_files = []
        failed_files = []
        
        try:
            config_status = self.check_system_config_files()
            available_configs = config_status["available"]
            
            if not available_configs:
                logger.info("No system config files to deploy")
                return True
            
            logger.info(f"Deploying {len(available_configs)} system configuration files...")
            
            for i, config in enumerate(available_configs):
                config_name = config["name"]
                config_info = self.config_mappings[config_name]
                
                if loading_operation:
                    progress_msg = f"Deploying {config_name}... ({i+1}/{len(available_configs)})"
                    loading_operation.update_status(progress_msg)
                
                logger.info(f"Deploying {config_name}: {config_info['description']}")
                
                try:
                    # Create backup of existing file
                    if config_info["target"].exists():
                        self._create_system_file_backup(config_info)
                    
                    # Deploy the new file
                    success = self._deploy_single_config(config_info)
                    
                    if success:
                        deployed_files.append(config_name)
                        logger.info(f"Successfully deployed {config_name}")
                    else:
                        failed_files.append(config_name)
                        logger.error(f"Failed to deploy {config_name}")
                        
                except Exception as e:
                    logger.error(f"Error deploying {config_name}: {e}")
                    failed_files.append(config_name)
            
            # Summary
            total_files = len(available_configs)
            success_count = len(deployed_files)
            
            if failed_files:
                logger.warning(f"Deployed {success_count}/{total_files} config files. Failed: {failed_files}")
                return False
            else:
                logger.info(f"Successfully deployed all {success_count} system configuration files")
                return True
                
        except Exception as e:
            logger.error(f"System config deployment failed: {e}")
            return False
    
    def _create_system_file_backup(self, config_info):
        """Create backup of existing system file."""
        source_file = config_info["target"]
        backup_file = config_info["backup"]
        requires_sudo = config_info["requires_sudo"]
        
        logger.debug(f"Creating backup: {source_file} -> {backup_file}")
        
        try:
            if requires_sudo:
                # Use sudo to copy the file
                result = subprocess.run(
                    ["sudo", "cp", str(source_file), str(backup_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    logger.error(f"Sudo backup failed: {result.stderr}")
                    raise Exception(f"Failed to create backup with sudo: {result.stderr}")
            else:
                # Regular file copy
                shutil.copy2(source_file, backup_file)
                
            logger.debug(f"Backup created successfully: {backup_file}")
            
        except Exception as e:
            logger.error(f"Failed to create backup for {source_file}: {e}")
            raise
    
    def _deploy_single_config(self, config_info):
        """Deploy a single configuration file."""
        source_file = config_info["source"]
        target_file = config_info["target"]
        requires_sudo = config_info["requires_sudo"]
        
        try:
            # Ensure target directory exists
            target_dir = target_file.parent
            if requires_sudo and not target_dir.exists():
                result = subprocess.run(
                    ["sudo", "mkdir", "-p", str(target_dir)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    logger.error(f"Failed to create directory with sudo: {result.stderr}")
                    return False
            elif not requires_sudo:
                target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            if requires_sudo:
                result = subprocess.run(
                    ["sudo", "cp", str(source_file), str(target_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    logger.error(f"Sudo copy failed: {result.stderr}")
                    return False
                    
                # Set proper permissions
                result = subprocess.run(
                    ["sudo", "chmod", "644", str(target_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    logger.warning(f"Failed to set permissions: {result.stderr}")
            else:
                shutil.copy2(source_file, target_file)
                os.chmod(target_file, 0o644)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy {source_file} to {target_file}: {e}")
            return False
    
    def rollback_system_configs(self, loading_operation=None):
        """
        Rollback system configuration files from backups.
        
        Args:
            loading_operation: LoadingOperation instance for progress updates
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_raspberry_pi:
            logger.warning("System config rollback only available on Raspberry Pi")
            return False
        
        restored_files = []
        failed_files = []
        
        try:
            logger.info("Rolling back system configuration files...")
            
            for config_name, config_info in self.config_mappings.items():
                backup_file = config_info["backup"]
                target_file = config_info["target"]
                requires_sudo = config_info["requires_sudo"]
                
                if not backup_file.exists():
                    logger.debug(f"No backup found for {config_name}, skipping")
                    continue
                
                if loading_operation:
                    loading_operation.update_status(f"Restoring {config_name}...")
                
                logger.info(f"Restoring {config_name} from backup")
                
                try:
                    if requires_sudo:
                        result = subprocess.run(
                            ["sudo", "cp", str(backup_file), str(target_file)],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode != 0:
                            logger.error(f"Sudo restore failed: {result.stderr}")
                            failed_files.append(config_name)
                            continue
                    else:
                        shutil.copy2(backup_file, target_file)
                    
                    restored_files.append(config_name)
                    logger.info(f"Successfully restored {config_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to restore {config_name}: {e}")
                    failed_files.append(config_name)
            
            # Summary
            if failed_files:
                logger.warning(f"Restored {len(restored_files)} files, failed: {failed_files}")
                return False
            else:
                logger.info(f"Successfully restored {len(restored_files)} system configuration files")
                return True
                
        except Exception as e:
            logger.error(f"System config rollback failed: {e}")
            return False
    
    def validate_config_files(self):
        """
        Validate system configuration files for basic syntax/format issues.
        
        Returns:
            dict: Validation results
        """
        if not self.is_raspberry_pi:
            return {"status": "Not on Raspberry Pi", "files": []}
        
        validation_results = []
        
        for config_name, config_info in self.config_mappings.items():
            source_file = config_info["source"]
            
            if not source_file.exists():
                continue
            
            result = {
                "name": config_name,
                "valid": True,
                "warnings": [],
                "errors": []
            }
            
            try:
                # Basic validation based on file type
                if config_name == "config.txt":
                    result = self._validate_config_txt(source_file, result)
                elif config_name == "cmdline.txt":
                    result = self._validate_cmdline_txt(source_file, result)
                elif config_name == "wayfire.ini":
                    result = self._validate_wayfire_ini(source_file, result)
                    
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"Validation error: {e}")
            
            validation_results.append(result)
        
        return {
            "status": "Validation complete",
            "files": validation_results
        }
    
    def _validate_config_txt(self, file_path, result):
        """Validate config.txt file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for common issues
        if "dtoverlay=vc4-fkms-v3d" not in content and "dtoverlay=vc4-kms-v3d" not in content:
            result["warnings"].append("No GPU memory split overlay found")
        
        if "enable_tvout=1" in content and "hdmi_force_hotplug=1" in content:
            result["warnings"].append("Both TV out and HDMI force enabled - may cause conflicts")
        
        return result
    
    def _validate_cmdline_txt(self, file_path, result):
        """Validate cmdline.txt file."""
        with open(file_path, 'r') as f:
            content = f.read().strip()
        
        # Should be a single line
        if '\n' in content:
            result["errors"].append("cmdline.txt should be a single line")
            result["valid"] = False
        
        # Check for required parameters
        required_params = ["root=", "rootfstype="]
        for param in required_params:
            if param not in content:
                result["errors"].append(f"Missing required parameter: {param}")
                result["valid"] = False
        
        return result
    
    def _validate_wayfire_ini(self, file_path, result):
        """Validate wayfire.ini file."""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(file_path)
            
            # Check for required sections
            required_sections = ["autostart"]
            for section in required_sections:
                if section not in config:
                    result["warnings"].append(f"Missing recommended section: [{section}]")
                    
        except Exception as e:
            result["errors"].append(f"INI file format error: {e}")
            result["valid"] = False
        
        return result 