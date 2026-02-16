# --- utils/admin_timer.py ---
# Battery-life / scenario logging for admin testing.
# When ADMIN_TIMER is enabled, logs elapsed time, scenario, CPU%, RAM%, temp, battery
# to a separate file. Each write is flushed and fsync'd so data survives power loss.

import logging
import os
import time
from datetime import datetime

from data import system_info

logger = logging.getLogger(__name__)

# CSV header for the battery timer log (one line per session start, then data rows)
HEADER = "timestamp_utc,elapsed_sec,scenario,cpu_pct,ram_pct,temp_c,battery_pct,battery_status"


def _get_temp_c():
    """Get CPU/SoC temperature in °C if available (e.g. Pi thermal_zone0)."""
    try:
        cpu_pct, extra = system_info.get_cpu_usage()
        if extra and extra[0] == "temperature":
            return round(extra[1], 1)
    except Exception:
        pass
    try:
        path = "/sys/class/thermal/thermal_zone0/temp"
        if os.path.exists(path):
            with open(path, "r") as f:
                return round(int(f.read().strip()) / 1000.0, 1)
    except Exception:
        pass
    return None


def _safe_float(value, default=None):
    if value is None:
        return "" if default is None else default
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return "" if default is None else default


def _safe_str(value, default=""):
    if value is None:
        return default
    s = str(value).strip()
    if "," in s or "\n" in s or '"' in s:
        s = '"' + s.replace('"', '""') + '"'
    return s or default


class AdminTimer:
    """
    Logs battery-life test samples to a dedicated file: elapsed time, scenario (state),
    CPU%, RAM%, temp °C, battery% and status. Flush + fsync after each write so the
    log survives power loss when the Pi dies.
    """

    def __init__(self, config_module):
        self.config = config_module
        self.start_time = None
        self._file = None
        self._last_log_time = 0.0
        self._path = None

    def start(self):
        """Start the timer and open the log file (append). Write session header."""
        self.start_time = time.time()
        self._last_log_time = self.start_time
        log_dir = getattr(self.config, "ADMIN_TIMER_LOG_DIR", "logs")
        log_name = getattr(self.config, "ADMIN_TIMER_LOG_FILENAME", "battery_timer.log")
        self._path = os.path.join(log_dir, log_name)
        try:
            os.makedirs(log_dir, exist_ok=True)
            self._file = open(self._path, "a", encoding="utf-8")
            # Ensure file has header (if new or empty)
            try:
                self._file.seek(0)
                first = self._file.read(len(HEADER) + 20)
                if HEADER not in first:
                    self._file.seek(0, os.SEEK_END)
                    self._file.write(HEADER + "\n")
                    self._flush_sync()
            except Exception:
                pass
            self._file.seek(0, os.SEEK_END)
            # Session start line (comment-style so parsers can skip or use)
            utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            self._file.write(f"# SESSION_START {utc}\n")
            self._flush_sync()
            logger.info("Admin timer started; log file: %s", os.path.abspath(self._path))
        except OSError as e:
            logger.error("Admin timer: could not open log file %s: %s", self._path, e)
            self._file = None

    def _flush_sync(self):
        if self._file is None:
            return
        try:
            self._file.flush()
            if hasattr(os, "fsync"):
                os.fsync(self._file.fileno())
        except OSError as e:
            logger.warning("Admin timer flush/fsync failed: %s", e)

    def log_sample(self, app_state):
        """If interval has elapsed, append one CSV row and flush+fsync."""
        if self._file is None or self.start_time is None:
            return
        now = time.time()
        interval = getattr(self.config, "ADMIN_TIMER_LOG_INTERVAL_SEC", 30)
        if now - self._last_log_time < interval:
            return
        self._last_log_time = now
        scenario = str(getattr(app_state, "current_state", "") or "")

        cpu_pct, _ = system_info.get_cpu_usage()
        ram_result = system_info.get_memory_usage()
        ram_pct = ram_result[0] if ram_result else None
        temp_c = _get_temp_c()
        battery_pct, battery_status = system_info.get_battery_info() or (None, None)

        elapsed = round(now - self.start_time, 1)
        utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        cpu_s = _safe_float(cpu_pct, "")
        ram_s = _safe_float(ram_pct, "")
        temp_s = _safe_float(temp_c, "") if temp_c is not None else ""
        bat_s = _safe_float(battery_pct, "") if battery_pct is not None else ""
        line = f"{utc},{elapsed},{_safe_str(scenario)},{cpu_s},{ram_s},{temp_s},{bat_s},{_safe_str(battery_status)}\n"
        try:
            self._file.write(line)
            self._flush_sync()
        except OSError as e:
            logger.warning("Admin timer write failed: %s", e)

    def stop(self):
        """Write a few safety lines (SESSION_END + summary), flush+fsync, then close the log file."""
        if self._file is not None:
            try:
                utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                elapsed = round((time.time() - self.start_time), 1) if self.start_time else 0
                self._file.write(f"# SESSION_END {utc} elapsed_sec={elapsed}\n")
                self._file.write("# Log saved safely before stop.\n")
                self._flush_sync()
                self._file.write("# End of session.\n")
                self._flush_sync()
                self._file.close()
                logger.info("Admin timer stopped; log saved to %s", self._path)
            except OSError as e:
                logger.warning("Admin timer close failed: %s", e)
            self._file = None
        self.start_time = None
