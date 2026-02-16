# --- data/sense_hat_led.py ---
# Sense HAT 8x8 LED matrix display driven by app state and sensor data.
# No-op when Sense HAT is not available (e.g. Windows dev).

import logging
import math
import time

logger = logging.getLogger(__name__)

# Throttle: minimum seconds between LED updates to avoid I2C spam and flicker
LED_UPDATE_INTERVAL = 0.25
_last_led_update_time = 0.0

# Dim RGB values (0-255). Sense HAT low_light is set in sensors.init; keep values modest.
_DIM = 40
_MID = 80
_BRIGHT = 120

# Prebuild 64-pixel buffer: list of [R, G, B]
def _empty_pixels():
    return [[0, 0, 0]] * 64


def _set_pixel(pixels, x, y, r, g, b):
    """Set one pixel in a 64-element list (row-major: row y, col x)."""
    if 0 <= x <= 7 and 0 <= y <= 7:
        pixels[y * 8 + x] = [r, g, b]


def _draw_vertical_bar(pixels, col, height_0_to_8, r, g, b):
    """Fill from bottom (y=7) upward. height_0_to_8 in [0, 8]."""
    h = max(0, min(8, int(round(height_0_to_8))))
    for row in range(7, 7 - h, -1):
        _set_pixel(pixels, col, row, r, g, b)


def _normalize_sensor_value(sensor_key, value, config_module):
    """Return 0.0–1.0 from sensor value using config range_override, or None."""
    if value is None:
        return None
    try:
        props = config_module.SENSOR_DISPLAY_PROPERTIES.get(sensor_key, {})
        rng = props.get("range_override")
        if not rng or len(rng) != 2:
            return None
        lo, hi = rng[0], rng[1]
        if hi == lo:
            return 0.5
        return (float(value) - lo) / (hi - lo)
    except (TypeError, KeyError):
        return None


def _sensor_led_color(sensor_key, config_module, brightness=_MID):
    """Return (r, g, b) for LED from sensor's theme color, scaled to brightness."""
    try:
        props = config_module.SENSOR_DISPLAY_PROPERTIES.get(sensor_key, {})
        color_key = props.get("color_key", "SIDEBAR_SYSTEM")
        color = getattr(config_module.Theme, color_key, config_module.Theme.ACCENT)
    except (TypeError, AttributeError, KeyError):
        color = config_module.Theme.ACCENT
    # Scale to LED brightness (theme colors are 0-255)
    scale = brightness / 255.0
    return tuple(min(255, int(c * scale)) for c in color)


def _pattern_menu(pixels, t=None):
    """Menu: tricorder-style scanning line with trail, plus dim corner beacons."""
    if t is None:
        t = time.time()
    # Scan speed: full 8-row sweep in ~2 seconds at 4 LED updates/sec
    phase = (t * 4) % 8.0
    row_lead = int(phase) % 8
    # Trail behind the scan line (wrap around)
    row_trail1 = (row_lead - 1) % 8
    row_trail2 = (row_lead - 2) % 8
    # Bright lead line (green), dimmer trail, faint trail
    for x in range(8):
        _set_pixel(pixels, x, row_lead, 0, _BRIGHT, 0)
        _set_pixel(pixels, x, row_trail1, 0, _MID, 0)
        _set_pixel(pixels, x, row_trail2, 0, _DIM, 0)
    # Subtle corner beacons (tricorder “listening”)
    c = _DIM // 2
    _set_pixel(pixels, 0, 0, 0, c, 0)
    _set_pixel(pixels, 7, 0, 0, c, 0)
    _set_pixel(pixels, 0, 7, 0, c, 0)
    _set_pixel(pixels, 7, 7, 0, c, 0)


def _pattern_dashboard_or_sensor(pixels, app_state, sensor_values, config_module):
    """Show a vertical bar for the current sensor (dashboard cycle or sensor view)."""
    sensor_key = app_state.current_sensor
    if not sensor_key:
        # Dashboard may use cycle_index into SENSOR_MODES
        try:
            idx = app_state.cycle_index % len(config_module.SENSOR_MODES)
            sensor_key = config_module.SENSOR_MODES[idx]
        except (AttributeError, TypeError):
            sensor_key = config_module.SENSOR_TEMPERATURE
    data = sensor_values.get(sensor_key)
    if not data or not isinstance(data, dict):
        _pattern_menu(pixels, time.time())
        return
    value = data.get("value")
    norm = _normalize_sensor_value(sensor_key, value, config_module)
    if norm is None:
        _pattern_menu(pixels, time.time())
        return
    # Single column bar in the middle (col 3 or 4), height 0–8
    height = norm * 8
    # Green for normal, amber for high, red for extreme (simple)
    if norm <= 0.5:
        r, g, b = 0, _MID, 0
    elif norm <= 0.85:
        r, g, b = _MID, _MID, 0
    else:
        r, g, b = _MID, 0, 0
    _draw_vertical_bar(pixels, 4, height, r, g, b)


def _pattern_sensors_menu(pixels, app_state, sensor_values, config_module):
    """Sensors submenu: selector strip (which sensor) + value bar for selected sensor."""
    try:
        menu_items = app_state.get_current_menu_items()
        selected_index = app_state.get_current_menu_index()
    except (AttributeError, TypeError):
        _pattern_menu(pixels, time.time())
        return
    if not menu_items:
        _pattern_menu(pixels, time.time())
        return
    n = len(menu_items)
    # Left: selector strip – one row per item, selected row bright
    selector_col = 0
    for i in range(min(5, n)):
        row = 1 + (i * 5 // max(1, n))  # Spread 1..5
        if row <= 5:
            if i == selected_index % n:
                _set_pixel(pixels, selector_col, row, 0, _BRIGHT, 0)
            else:
                _set_pixel(pixels, selector_col, row, 0, _DIM, 0)
    # Right: value bar for selected sensor
    selected_item = menu_items[selected_index % n]
    sensor_key = None
    if getattr(selected_item, "data", None) and isinstance(selected_item.data, dict):
        sensor_key = selected_item.data.get("sensor_type")
    if sensor_key and sensor_key in config_module.SENSOR_MODES:
        data = sensor_values.get(sensor_key)
        if data and isinstance(data, dict):
            value = data.get("value")
            norm = _normalize_sensor_value(sensor_key, value, config_module)
            if norm is not None:
                height = norm * 8
                r, g, b = _sensor_led_color(sensor_key, config_module)
                _draw_vertical_bar(pixels, 5, height, r, g, b)
                # Optional: also show on col 6 slightly dimmer for thickness
                r2, g2, b2 = tuple(min(255, c * 3 // 4) for c in (r, g, b))
                _draw_vertical_bar(pixels, 6, height, r2, g2, b2)
    else:
        # No sensor data: show dim bar at 50%
        _draw_vertical_bar(pixels, 5, 4, _DIM, _DIM, 0)


def _pattern_sensor_view(pixels, app_state, sensor_values, config_module):
    """Individual sensor view: one value bar in sensor-specific color + live indicator."""
    sensor_key = app_state.current_sensor
    if not sensor_key:
        sensor_key = config_module.SENSOR_TEMPERATURE
    data = sensor_values.get(sensor_key)
    if not data or not isinstance(data, dict):
        _pattern_menu(pixels, time.time())
        return
    value = data.get("value")
    norm = _normalize_sensor_value(sensor_key, value, config_module)
    if norm is None:
        _pattern_menu(pixels, time.time())
        return
    height = norm * 8
    r, g, b = _sensor_led_color(sensor_key, config_module)
    _draw_vertical_bar(pixels, 4, height, r, g, b)
    # Live indicator: top-right pixel pulses
    t = time.time()
    pulse = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 2.0))
    live = tuple(min(255, int(c * pulse)) for c in (0, _DIM, 0))
    _set_pixel(pixels, 7, 0, *live)


def _pattern_settings(pixels):
    """Settings: horizontal line in the middle."""
    c = _DIM
    for x in range(8):
        _set_pixel(pixels, x, 3, c, c, 0)
        _set_pixel(pixels, x, 4, c, c, 0)


def _pattern_media_player(pixels, app_state):
    """Media player: play (triangle) or pause (two bars) indicator."""
    try:
        is_playing = app_state.media_player_manager.is_playing()
    except Exception:
        is_playing = False
    c = _MID
    if is_playing:
        # Play triangle (right-pointing) centered
        _set_pixel(pixels, 4, 2, 0, c, 0)
        _set_pixel(pixels, 4, 3, 0, c, 0)
        _set_pixel(pixels, 4, 4, 0, c, 0)
        _set_pixel(pixels, 4, 5, 0, c, 0)
        _set_pixel(pixels, 5, 2, 0, c, 0)
        _set_pixel(pixels, 5, 3, 0, c, 0)
        _set_pixel(pixels, 5, 4, 0, c, 0)
        _set_pixel(pixels, 5, 5, 0, c, 0)
        _set_pixel(pixels, 6, 3, 0, c, 0)
        _set_pixel(pixels, 6, 4, 0, c, 0)
    else:
        # Pause: two vertical bars
        for y in range(2, 6):
            _set_pixel(pixels, 3, y, c, c, 0)
            _set_pixel(pixels, 5, y, c, c, 0)


def _pattern_schematics(pixels):
    """Schematics / 3D viewer: small “frame” outline."""
    c = _DIM
    for i in range(8):
        _set_pixel(pixels, i, 0, 0, 0, c)
        _set_pixel(pixels, i, 7, 0, 0, c)
        _set_pixel(pixels, 0, i, 0, 0, c)
        _set_pixel(pixels, 7, i, 0, 0, c)


def _pattern_games(pixels):
    """Secret games: simple smiley or dots."""
    c = _MID
    _set_pixel(pixels, 2, 2, c, c, 0)
    _set_pixel(pixels, 5, 2, c, c, 0)
    _set_pixel(pixels, 1, 4, c, c, 0)
    _set_pixel(pixels, 2, 5, c, c, 0)
    _set_pixel(pixels, 3, 5, c, c, 0)
    _set_pixel(pixels, 4, 5, c, c, 0)
    _set_pixel(pixels, 5, 5, c, c, 0)
    _set_pixel(pixels, 6, 4, c, c, 0)


def _usage_to_color(usage_pct):
    """Return (r, g, b) for usage 0-100: green <=60, yellow 60-85, red >85."""
    if usage_pct is None:
        return _DIM, _DIM, _DIM
    if usage_pct <= 60:
        return 0, _MID, 0
    if usage_pct <= 85:
        return _MID, _MID, 0
    return _MID, 0, 0


def _pattern_system(pixels, app_state, sensor_values, config_module):
    """System view: three vertical bars (CPU, RAM, Disk) + WiFi/Bluetooth corner indicators."""
    # Three bars at columns 1, 3, 5 (CPU, RAM, Disk). Height from 0-100% -> 0-8 rows.
    def get_usage(key):
        data = sensor_values.get(key, {})
        if not isinstance(data, dict):
            return None
        return data.get("value")

    cpu = get_usage(config_module.SENSOR_CPU_USAGE)
    ram = get_usage(config_module.SENSOR_MEMORY_USAGE)
    disk = get_usage(config_module.SENSOR_DISK_USAGE)

    for col, usage in [(1, cpu), (3, ram), (5, disk)]:
        height = (usage * 8 / 100) if usage is not None else 0
        height = max(0, min(8, height))
        r, g, b = _usage_to_color(usage)
        _draw_vertical_bar(pixels, col, height, r, g, b)

    # WiFi (bottom-left) and Bluetooth (bottom-right): green = connected, red = not
    wifi_data = sensor_values.get(getattr(config_module, "INFO_WIFI_STATUS", "WIFI_STATUS"), {})
    wifi_ok = (wifi_data.get("text") or "").lower() in ("connected", "online")
    bt_data = sensor_values.get(getattr(config_module, "INFO_BLUETOOTH_STATUS", "BLUETOOTH_STATUS"), {})
    bt_ok = (bt_data.get("text") or "").lower() in ("connected",)

    w, b = (0, _DIM, 0) if wifi_ok else (_DIM, 0, 0), (0, _DIM, 0) if bt_ok else (_DIM, 0, 0)
    _set_pixel(pixels, 0, 7, *w)
    _set_pixel(pixels, 7, 7, *b)

    # Frozen state: dim red border so hardware reflects freeze
    if getattr(app_state, "is_frozen", False):
        c = _DIM // 2
        for i in range(8):
            _set_pixel(pixels, i, 0, c, 0, 0)
            _set_pixel(pixels, i, 7, c, 0, 0)
            _set_pixel(pixels, 0, i, c, 0, 0)
            _set_pixel(pixels, 7, i, c, 0, 0)


def _pattern_wifi(pixels, app_state):
    """WiFi screens: show signal-style bars if connected, else single bar."""
    try:
        state = app_state.current_state
        if state == "SETTINGS_WIFI_NETWORKS" or state == "WIFI_PASSWORD_ENTRY":
            # Scanning/connecting: two bars
            _draw_vertical_bar(pixels, 2, 4, _DIM, _DIM, 0)
            _draw_vertical_bar(pixels, 4, 6, _DIM, _DIM, 0)
            return
        wm = getattr(app_state, 'wifi_manager', None)
        enabled = wm and getattr(wm, 'last_known_enabled_state', False)
    except Exception:
        enabled = False
    if enabled:
        _draw_vertical_bar(pixels, 2, 3, 0, _DIM, 0)
        _draw_vertical_bar(pixels, 4, 5, 0, _DIM, 0)
        _draw_vertical_bar(pixels, 6, 7, 0, _DIM, 0)
    else:
        _draw_vertical_bar(pixels, 4, 2, _DIM, 0, 0)


def _choose_and_build_pattern(app_state, sensor_values, config_module):
    """Pick pattern by state and fill the 64-pixel list."""
    state = app_state.current_state
    pixels = _empty_pixels()

    if state == "SYSTEM":
        _pattern_system(pixels, app_state, sensor_values, config_module)
    elif state == "SENSORS_MENU":
        _pattern_sensors_menu(pixels, app_state, sensor_values, config_module)
    elif state == "SENSOR":
        _pattern_sensor_view(pixels, app_state, sensor_values, config_module)
    elif state == "DASHBOARD":
        _pattern_dashboard_or_sensor(pixels, app_state, sensor_values, config_module)
    elif state == "MENU":
        _pattern_menu(pixels, time.time())
    elif state == "MEDIA_PLAYER":
        _pattern_media_player(pixels, app_state)
    elif state in ("SCHEMATICS", "SCHEMATICS_MENU", "SCHEMATICS_CATEGORY"):
        _pattern_schematics(pixels)
    elif state in ("PONG_ACTIVE", "BREAKOUT_ACTIVE", "SNAKE_ACTIVE"):
        _pattern_games(pixels)
    elif state in ("SETTINGS_WIFI", "SETTINGS_WIFI_NETWORKS", "WIFI_PASSWORD_ENTRY"):
        _pattern_wifi(pixels, app_state)
    elif "SETTINGS" in state or "CONFIRM" in state or "SELECT_COMBO" in state:
        _pattern_settings(pixels)
    else:
        _pattern_menu(pixels, time.time())

    return pixels


def update_led_display(app_state, sensor_values, config_module):
    """
    Update the Sense HAT 8x8 LED matrix based on app state and sensor data.
    Safe to call every frame; updates are throttled. No-op if Sense HAT is not available.
    """
    global _last_led_update_time
    if not getattr(config_module, "SENSE_HAT_LED_ENABLED", True):
        return
    try:
        from data.sensors import sense
    except ImportError:
        return
    if sense is None:
        return
    now = time.time()
    if now - _last_led_update_time < LED_UPDATE_INTERVAL:
        return
    _last_led_update_time = now
    try:
        pixels = _choose_and_build_pattern(app_state, sensor_values, config_module)
        # sense.set_pixels expects list of 64 [R,G,B]
        sense.set_pixels(pixels)
    except Exception as e:
        logger.debug("Sense HAT LED update skipped: %s", e)
