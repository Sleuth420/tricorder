# --- data/system_info.py ---
# Handles system monitoring (CPU, memory, disk)

import logging
import os
import platform
import datetime

# Get a logger for this module
logger = logging.getLogger(__name__)

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
    logger.info("psutil library successfully imported for system monitoring.")
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil library not found. System monitoring will be limited.")

def get_current_time():
    """Get the current time."""
    try:
        now = datetime.datetime.now()
        return now
    except Exception as e:
        logger.error(f"Error getting current time: {e}", exc_info=True)
        return None

def get_cpu_usage():
    """Get CPU usage information."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for CPU monitoring")
        return None, None  # Usage percent, additional info
        
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get CPU temperature if available (Raspberry Pi specific)
        additional_info = None
        try:
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read()) / 1000.0
                additional_info = ("temperature", temp)
                logger.debug(f"CPU temperature: {temp:.1f}°C")
            else:
                cores = psutil.cpu_count()
                additional_info = ("cores", cores)
                logger.debug(f"CPU cores: {cores}")
        except Exception as e:
            logger.warning(f"Could not read CPU temperature: {e}")
            cores = psutil.cpu_count()
            additional_info = ("cores", cores)
            
        logger.debug(f"CPU usage: {cpu_percent:.1f}%")
        return cpu_percent, additional_info
    except Exception as e:
        logger.error(f"Error getting CPU usage: {e}")
        return None, None

def get_memory_usage():
    """Get memory usage information."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for memory monitoring")
        return None, None, None  # Percent, used MB, total MB
        
    try:
        memory = psutil.virtual_memory()
        used_mb = memory.used / (1024 * 1024)
        total_mb = memory.total / (1024 * 1024)
        logger.debug(f"Memory usage: {memory.percent:.1f}% ({used_mb:.0f}MB/{total_mb:.0f}MB)")
        return memory.percent, used_mb, total_mb
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        return None, None, None

def get_disk_usage():
    """Get disk usage information."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for disk monitoring")
        return None, None, None  # Percent, used GB, total GB
        
    try:
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024 * 1024 * 1024)
        total_gb = disk.total / (1024 * 1024 * 1024)
        logger.debug(f"Disk usage: {disk.percent:.1f}% ({used_gb:.1f}GB/{total_gb:.1f}GB)")
        return disk.percent, used_gb, total_gb
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return None, None, None 