# Battery Test Report: Idle Menu (100% → ~20% threshold)

**Test scenario:** Main menu idle  
**Date:** 2026-02-16  
**Device:** Raspberry Pi tricorder (display + Sense HAT + peripherals)  
**Battery range:** 100% to ~20% (run terminated when voltage fell below Pi and screen operating threshold)

---

## 1. Test configuration

### 1.1 Software state
- **Application state:** Main menu only (no navigation; no video, games, or sensor views).
- **Logging:** Admin timer enabled; samples every 30 s to `logs/battery_timer.log` (flush+fsync per write).

### 1.2 Peripherals and services (always on during test)
| Component        | State  | Notes                                              |
|-----------------|--------|----------------------------------------------------|
| Display         | On     | Full UI at normal brightness                      |
| WiFi            | On     | Radio on for the duration                          |
| Bluetooth       | On     | Radio on for the duration                          |
| Sense HAT LEDs  | On     | LED matrix active for display                      |
| Clock motor     | On     | Small motor from clock driving rotating wheel (aesthetic) |

The clock motor runs continuously for the aesthetic wheel display and is powered from the same supply as the Pi and screen.

---

## 2. Results summary

| Metric            | Value / range                          |
|-------------------|----------------------------------------|
| **Total runtime** | ~2 h 15 min (from first to last sample) |
| **Scenario**      | MENU (idle)                            |
| **CPU usage**     | ~28–38% typical; range 13.6–42.9%      |
| **RAM usage**     | 6.5–6.9% (stable)                      |
| **SoC temperature** | 51.6 °C → peak ~77–78 °C → ~66–67 °C at end |
| **Battery % in log** | N/A (not reported by system on this device) |

Runtime is derived from **elapsed_sec** in the CSV log; battery percentage was not available from the platform for this run. End condition is defined as the point where voltage dropped below the operating threshold (Pi + screen), corresponding to roughly “100% down to ~20%” in terms of usable capacity.

---

## 3. Observations

### 3.1 Runtime
- First data row: **839.5 s** (~14 min) after session start.  
- Last data row: **8101.7 s** (~2 h 15 min) after session start.  
- No clean shutdown line (`# SESSION_END`) in the log; session ended when power dropped below threshold, consistent with the 100% → ~20% cutoff.

### 3.2 CPU and RAM
- CPU sits in the low–mid 30% range with occasional spikes, consistent with display refresh, Sense HAT LED updates, WiFi/Bluetooth stack, and the logging process.
- RAM usage is flat at ~6.5–6.9%, indicating no meaningful memory growth over the test.

### 3.3 Thermal
- Temperature rises from ~52 °C to a plateau around **76–78 °C** over roughly 30–40 minutes, then slowly decreases to **~66–67 °C** by the end. This suggests thermal soak followed by either improved airflow, lower ambient temperature, or reduced load (e.g. CPU throttling or lower activity).

### 3.4 Load composition
Under this “idle menu” scenario, power draw includes:
- Pi + display (main load).
- WiFi and Bluetooth radios.
- Sense HAT (sensors + LED matrix).
- Small clock motor for the rotating wheel.
- Application and 30 s interval logging.

---

## 4. Conclusion

Under the conditions above (idle menu, WiFi on, Bluetooth on, Sense HAT LEDs on, clock motor on), the unit ran from **100% to the ~20% voltage threshold** in approximately **2 hours 15 minutes**, at which point voltage fell below the level required for stable Pi and screen operation.

This report can be used as a baseline for the “idle menu” scenario when comparing with other scenarios (e.g. video playback, sensors view, games) or with different peripheral combinations (e.g. motor off, WiFi/Bluetooth off) in future tests.

---

## 5. Data source

- **Log file:** `logs/battery_timer.log`  
- **Format:** CSV with columns `timestamp_utc`, `elapsed_sec`, `scenario`, `cpu_pct`, `ram_pct`, `temp_c`, `battery_pct`, `battery_status`  
- **Sample interval:** 30 s  
- **Session:** 2026-02-16; data from first SESSION_START through last recorded row (no SESSION_END, consistent with power-loss / threshold cutoff).

---

*Report generated from tricorder admin timer log. Test conditions (motor, WiFi, Bluetooth, Sense HAT LEDs) as specified for this run.*
