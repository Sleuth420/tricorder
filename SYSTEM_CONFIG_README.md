# System Configuration Management

The tricorder update system now includes **System Configuration Management** for Raspberry Pi deployments. This feature automatically manages and deploys system configuration files during updates.

## Overview

When running system updates on Raspberry Pi, the system will:

1. **Backup existing system configs** (with `.bak` extension)
2. **Deploy new configs** from the repository 
3. **Handle proper permissions** (sudo for boot files)
4. **Provide rollback capability** if needed

## Managed Configuration Files

The system manages these configuration files:

### Boot Configuration Files (require sudo)
- **`config.txt`** → `/boot/firmware/config.txt`
  - Raspberry Pi boot configuration (GPU, display, overclocking, etc.)
  - Critical for display settings, underscan adjustments

- **`cmdline.txt`** → `/boot/firmware/cmdline.txt`  
  - Kernel command line parameters
  - Boot options and system behavior

### User Configuration Files
- **`wayfire.ini`** → `~/.config/wayfire.ini`
  - Wayfire compositor configuration
  - Window manager settings for the desktop environment

## Directory Structure

```
tricorder/
├── system_config/           # Repository configuration files
│   ├── config.txt          # Pi boot config
│   ├── cmdline.txt         # Kernel command line
│   └── wayfire.ini         # Wayfire compositor config
└── models/
    └── system_config_manager.py  # Management logic
```

## How It Works

### During Updates

1. **App Update**: Deploys system configs after code update
2. **System Update**: Deploys system configs after OS package updates
3. **Backup Creation**: Creates `.bak` files of existing configs
4. **Permission Handling**: Uses `sudo` for `/boot/firmware/` files
5. **Validation**: Basic syntax checking for config files

### Update Process

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Git Update    │───▶│  Deploy Configs  │───▶│   Restart App   │
│  (Code/Deps)    │    │ (system_config/) │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Backup & Copy   │
                       │ /boot/firmware/  │
                       │   ~/.config/     │
                       └──────────────────┘
```

### Rollback Support

If an update fails:
1. **Code rollback** (git stash pop)
2. **Config rollback** (restore from `.bak` files)
3. **Dependency rollback** (pip install from requirements)

## File Mappings

| Repository File | Target Location | Permissions | Description |
|-----------------|-----------------|-------------|-------------|
| `system_config/config.txt` | `/boot/firmware/config.txt` | sudo | Pi boot config |
| `system_config/cmdline.txt` | `/boot/firmware/cmdline.txt` | sudo | Kernel parameters |
| `system_config/wayfire.ini` | `~/.config/wayfire.ini` | user | Compositor config |

## Platform Behavior

### Raspberry Pi
- ✅ Full system config management
- ✅ Automatic backup and deployment
- ✅ Sudo permission handling
- ✅ File validation

### Windows/Other Platforms  
- ❌ System config deployment disabled
- ✅ Config file status display (for development)
- ✅ Validation and checking (non-destructive)

## Configuration Examples

### `config.txt` - Display & Performance
```ini
# Display configuration
hdmi_force_hotplug=1
hdmi_group=1  
hdmi_mode=16
disable_overscan=1

# GPU memory
gpu_mem=128

# Enable hardware acceleration
dtoverlay=vc4-kms-v3d
```

### `cmdline.txt` - Boot Parameters
```
console=serial0,115200 console=tty1 root=PARTUUID=12345678-02 rootfstype=ext4 elevator=deadline fsck.repair=yes quiet splash plymouth.ignore-serial-consoles
```

### `wayfire.ini` - Window Manager
```ini
[autostart]
tricorder = python3 /home/pi/tricorder/main.py

[output:HDMI-A-1]
mode = 1920x1080@60.000000
```

## Using the System

### Update Process
1. Navigate to **Settings** → **System Updates**
2. Choose update type:
   - **Check for Updates** (status only)
   - **Quick App Update** (code + configs)  
   - **Full System Update** (OS + code + configs)

### Status Display
The update screen shows:
- Current version information
- System config status: `3/3 available` 
- Platform information
- Last update check results

### Troubleshooting

#### Config Files Missing
```
System Configs: 0/3 available
```
**Solution**: Add config files to `system_config/` directory

#### Permission Errors
```
ERROR: Sudo copy failed: Permission denied
```
**Solution**: Ensure user has sudo access, run update from terminal if needed

#### Validation Warnings
```
Warning: No GPU memory split overlay found
```
**Solution**: Review config file contents, warnings don't prevent deployment

## Development

### Testing
```bash
# Test system config management
python test_system_config.py

# Check file status
python -c "
from models.system_config_manager import SystemConfigManager
from pathlib import Path
scm = SystemConfigManager(Path('.'))
print(scm.check_system_config_files())
"
```

### Adding New Config Files

1. Add file to `system_config/` directory
2. Update `_get_config_mappings()` in `SystemConfigManager`
3. Add validation logic if needed
4. Test on target platform

## Safety Features

- ✅ **Automatic backups** before deployment
- ✅ **Rollback capability** on update failure  
- ✅ **Permission validation** for system files
- ✅ **Syntax checking** where applicable
- ✅ **Non-destructive** on non-Pi platforms
- ✅ **Graceful failure** (continues if config deployment fails)

## Why This Matters

System configuration management ensures that:

1. **Display settings survive OS updates** (no more black screens!)
2. **Underscan/overscan adjustments persist** across reboots
3. **Boot parameters remain consistent** after kernel updates
4. **Desktop environment stays configured** properly
5. **Version control** for system-level changes
6. **Easy deployment** to multiple Pi devices
7. **Rollback capability** if configs cause issues

This makes the tricorder much more robust and maintainable in kiosk/production environments! 