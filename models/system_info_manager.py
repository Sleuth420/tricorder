# --- models/system_info_manager.py ---
# System information caching to reduce expensive operations

import time
import logging
import os
from data import system_info

logger = logging.getLogger(__name__)

class SystemInfoManager:
    """Manages system information with caching to reduce expensive operations."""
    
    def __init__(self, cache_interval=2.0):
        """
        Initialize system info manager.
        
        Args:
            cache_interval (float): How often to refresh system info (seconds)
        """
        self.cache_interval = cache_interval
        self.last_cpu_check = 0
        self.last_memory_check = 0
        self.last_disk_check = 0
        self.last_voltage_check = 0
        self.last_battery_check = 0
        self.last_temp_check = 0
        
        # Cached values
        self.cached_cpu_info = None
        self.cached_memory_info = None
        self.cached_disk_info = None
        self.cached_voltage_info = None
        self.cached_battery_info = None
        self.cached_temp_info = None
    
    def get_cpu_info_cached(self):
        """Get CPU info with caching."""
        current_time = time.time()
        
        if (current_time - self.last_cpu_check) >= self.cache_interval:
            try:
                self.cached_cpu_info = system_info.get_cpu_usage()
                self.last_cpu_check = current_time
                logger.debug("CPU info updated from cache")
            except Exception as e:
                logger.error(f"Error updating CPU info: {e}")
                # Keep cached value on error
        
        return self.cached_cpu_info
    
    def get_memory_info_cached(self):
        """Get memory info with caching."""
        current_time = time.time()
        
        if (current_time - self.last_memory_check) >= self.cache_interval:
            try:
                self.cached_memory_info = system_info.get_memory_usage()
                self.last_memory_check = current_time
                logger.debug("Memory info updated from cache")
            except Exception as e:
                logger.error(f"Error updating memory info: {e}")
                # Keep cached value on error
        
        return self.cached_memory_info
    
    def get_disk_info_cached(self):
        """Get disk info with caching."""
        current_time = time.time()
        
        if (current_time - self.last_disk_check) >= self.cache_interval:
            try:
                self.cached_disk_info = system_info.get_disk_usage()
                self.last_disk_check = current_time
                logger.debug("Disk info updated from cache")
            except Exception as e:
                logger.error(f"Error updating disk info: {e}")
                # Keep cached value on error
        
        return self.cached_disk_info
    
    def get_voltage_info_cached(self):
        """Get voltage info with caching."""
        current_time = time.time()
        
        if (current_time - self.last_voltage_check) >= self.cache_interval:
            try:
                self.cached_voltage_info = system_info.get_voltage_info()
                self.last_voltage_check = current_time
                logger.debug("Voltage info updated from cache")
            except Exception as e:
                logger.error(f"Error updating voltage info: {e}")
                # Keep cached value on error
        
        return self.cached_voltage_info
    
    def get_battery_info_cached(self):
        """Get battery info with caching."""
        current_time = time.time()
        
        if (current_time - self.last_battery_check) >= self.cache_interval:
            try:
                self.cached_battery_info = system_info.get_battery_info()
                self.last_battery_check = current_time
                logger.debug("Battery info updated from cache")
            except Exception as e:
                logger.error(f"Error updating battery info: {e}")
                # Keep cached value on error
        
        return self.cached_battery_info
    
    def get_cpu_temperature_cached(self):
        """Get CPU temperature with caching (5-second interval for file reads)."""
        current_time = time.time()
        
        # Use longer cache interval for file reads (5 seconds)
        if (current_time - self.last_temp_check) >= 5.0:
            try:
                if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = float(f.read()) / 1000.0
                    self.cached_temp_info = temp
                    self.last_temp_check = current_time
                    logger.debug(f"CPU temperature updated from cache: {temp:.1f}°C")
            except Exception as e:
                logger.error(f"Error updating CPU temperature: {e}")
                # Keep cached value on error
        
        return self.cached_temp_info
