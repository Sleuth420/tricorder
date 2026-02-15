# --- models/network_manager.py ---
# Simple network status caching to reduce polling frequency

import time
import logging
from data import system_info

logger = logging.getLogger(__name__)

class NetworkManager:
    """Simple network status manager with caching to reduce polling frequency."""
    
    def __init__(self, cache_interval=5.0):
        """
        Initialize network manager.
        
        Args:
            cache_interval (float): How often to refresh network status (seconds)
        """
        self.cache_interval = cache_interval
        self.last_wifi_check = 0
        self.last_bluetooth_check = 0
        self.last_ip_check = 0
        self.cached_wifi_status = "Unknown", "Unknown"
        self.cached_bluetooth_status = "Unknown", "Unknown"
        self.cached_ip = None

    def get_ip_cached(self):
        """Get local IP with caching (e.g. for WiFi). Returns None if not connected."""
        current_time = time.time()
        if (current_time - self.last_ip_check) >= self.cache_interval:
            try:
                self.cached_ip = system_info.get_local_ip()
                self.last_ip_check = current_time
            except Exception as e:
                logger.debug(f"Error updating IP cache: {e}")
        return self.cached_ip
    
    def get_wifi_info_cached(self):
        """Get WiFi status with caching."""
        current_time = time.time()
        
        # Check if cache is stale
        if (current_time - self.last_wifi_check) >= self.cache_interval:
            try:
                self.cached_wifi_status = system_info.get_wifi_info()
                self.last_wifi_check = current_time
                logger.debug(f"WiFi status updated: {self.cached_wifi_status}")
            except Exception as e:
                logger.error(f"Error updating WiFi status: {e}")
                # Keep cached value on error
        
        return self.cached_wifi_status
    
    def get_bluetooth_info_cached(self):
        """Get Bluetooth status with caching."""
        current_time = time.time()
        
        # Check if cache is stale
        if (current_time - self.last_bluetooth_check) >= self.cache_interval:
            try:
                self.cached_bluetooth_status = system_info.get_bluetooth_info()
                self.last_bluetooth_check = current_time
                logger.debug(f"Bluetooth status updated: {self.cached_bluetooth_status}")
            except Exception as e:
                logger.error(f"Error updating Bluetooth status: {e}")
                # Keep cached value on error
        
        return self.cached_bluetooth_status
