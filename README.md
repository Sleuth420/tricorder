# Raspberry Pi Tricorder Project

A Star Trek inspired tricorder simulation using a Raspberry Pi, Sense HAT, and an external display. Displays environmental and system data with a retro-style interface.

## Features

* Menu-based navigation system
* Dashboard with auto-cycling through sensors (integrated into Sensor View)
* Individual sensor views with real-time graphs
* System monitoring (CPU, Memory, Disk usage)
* Environmental monitoring (Temperature, Humidity, Pressure)
* Motion sensing (Orientation, Acceleration)
* Clock display
* Configurable controls (supports 3-button operation: Up/Back, Down, Select/Action)
* Secret Games Menu (Pong implemented)
* Media Player (Main menu → Schematics → Media Player): audio (.mp3, .wav, .ogg) and video (.mp4) via VLC in a separate window
* Cross-platform development support (Windows with mock sensor data)

## Project Structure

```
tricorder/
├── main.py                 # Entry point, main application loop
├── config/                 # Modular configuration system
│   ├── __init__.py         # Main config module (imports all sub-configs)
│   ├── colors.py           # Color palettes and themes
│   ├── display.py          # Display and graphics settings
│   ├── ui.py               # UI layout, fonts, and arrow indicators
│   ├── input.py            # Input mappings and controls
│   └── sensors.py          # Sensor configurations and display properties
├── config_old.py           # DEPRECATED - old monolithic config (with warnings)
├── logging_config.py       # Logging setup
├── requirements.txt        # Python dependencies
├── data/
│   ├── __init__.py
│   ├── sensors.py          # Raw Sense HAT sensor reading functions
│   ├── system_info.py      # Raw system metric reading functions
│   └── data_updater.py     # Centralized data fetching and formatting
├── games/
│   ├── __init__.py
│   └── pong.py             # Pong game logic
├── assets/
│   ├── images/
│   └── apollo_ncc1570/
├── input/
│   ├── __init__.py
│   └── input_handler.py    # Processes Pygame events into detailed input results
├── logs/
│   └── tricorder.log       # Log file output
├── models/
│   ├── __init__.py
│   ├── app_state.py        # Main application state coordinator
│   ├── app_state_old.py    # DEPRECATED - old monolithic state manager (with warnings)
│   ├── state_manager.py    # Manages state transitions
│   ├── input_manager.py    # Handles input processing and combos
│   ├── menu_manager.py     # Manages menu navigation and generation
│   ├── game_manager.py     # Manages game lifecycle
│   ├── menu_item.py        # Menu item data structure
│   └── reading_history.py  # Stores time-series data for graphs
└── ui/
    ├── __init__.py
    ├── display_manager.py  # Initializes display, routes state to view functions
    ├── menu.py             # Draws the main menu screen layout (sidebar + content)
    ├── components/
    │   ├── __init__.py
    │   ├── graph.py        # Reusable graph drawing component
    │   ├── text_display.py # Reusable text rendering components
    │   └── ui_elements.py  # Reusable UI elements (panels, menu items)
    └── views/
        ├── __init__.py
        ├── sensor_view.py      # Draws view for single sensor OR dashboard
        ├── settings_view.py    # Draws the settings screen
        ├── system_info_view.py # Draws the system info screen
        └── secret_games_view.py # Draws the secret games menu screen
```

## Architecture

The application follows a modular architecture with clear separation of concerns:

### Component Managers (models/)
- **AppState**: Main coordinator that orchestrates between component managers
- **StateManager**: Handles state transitions and navigation flow
- **InputManager**: Processes input events, manages key combinations and timing
- **MenuManager**: Generates and manages menu structures and navigation
- **GameManager**: Manages game lifecycle (launching, updating, closing games)

### Benefits of Refactored Architecture
- **Single Responsibility Principle**: Each manager handles one specific concern
- **Improved Testability**: Components can be tested independently
- **Better Maintainability**: Changes to input handling don't affect menu logic, etc.
- **Cleaner Code**: Smaller, focused classes instead of one monolithic state manager

## Dependencies

* Python 3
* Pygame
* Sense Hat library (Raspberry Pi only)
* psutil for system monitoring
* **Media Player**: `python-vlc` and the **VLC application** must be installed (for audio and video playback). Install VLC from [videolan.org](https://www.videolan.org/); on Raspberry Pi: `sudo apt install vlc`. Place media files in `assets/media/` (.mp3, .wav, .ogg, .mp4).
* Other dependencies listed in `requirements.txt`

## Installation

### Raspberry Pi Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Sleuth420/tricorder.git
   cd tricorder
   ```

2. Install system-level dependencies:
   ```bash
   sudo apt update
   sudo apt install sense-hat python3-rtimu python3-dev build-essential
   sudo pip3 install sense-hat
   ```

3. Set up Python virtual environment:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install Python dependencies (excluding PyOpenGL-accelerate which causes build issues)
   pip install -r requirements.txt
   ```

4. Link system-level Sense HAT libraries to virtual environment:
   ```bash
   # Remove any existing sense_hat installations in venv
   rm -rf ~/Desktop/tricorder/venv/lib/python3.11/site-packages/sense_hat*
   
   # Create symbolic links to system packages
   ln -s /usr/lib/python3/dist-packages/sense_hat ~/Desktop/tricorder/venv/lib/python3.11/site-packages/
   ln -s /usr/lib/python3/dist-packages/sense_hat-2.6.0.dist-info ~/Desktop/tricorder/venv/lib/python3.11/site-packages/
   ln -s /usr/lib/python3/dist-packages/RTIMU* ~/Desktop/tricorder/venv/lib/python3.11/site-packages/
   ```

5. Verify Sense HAT installation:
   ```bash
   # Test that Sense HAT can be imported
   python3 -c "import sense_hat; print('Sense HAT library is working')"
   ```

6. Enable I2C interface (required for Sense HAT):
   ```bash
   sudo raspi-config
   ```
   Then navigate to:
   - Interface Options
   - I2C
   - Enable I2C
   - Select "Yes" to reboot when prompted

7. After reboot, verify Sense HAT is detected:
   ```bash
   sudo i2cdetect -y 1
   ```
   You should see the Sense HAT's I2C address (typically 0x46) in the output.

### Windows Development Setup

For development and testing on Windows without a Raspberry Pi:

1. Clone this repository:
   ```bash
   git clone https://github.com/Sleuth420/tricorder.git
   cd tricorder
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv_windows
   
   # Activate virtual environment (Windows)
   venv_windows\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

**Windows Development Features:**
- Automatically detects Windows platform and uses mock sensor data
- Runs in windowed mode (800x600) instead of fullscreen
- Simulates realistic sensor readings:
  - Temperature: ~22°C with natural variations
  - Humidity: ~45% with fluctuations
  - Pressure: ~1013 hPa with atmospheric changes
  - Orientation: Slow drift simulation
  - Acceleration: Gravity simulation with minor variations
- No Sense HAT hardware required

## Usage

### Raspberry Pi
```bash
# Make sure virtual environment is activated
source venv/bin/activate
python main.py
```

### Windows Development
```bash
# Make sure virtual environment is activated
venv_windows\Scripts\activate
python main.py
```

### Controls
* Keyboard (Development/Testing):
    * `A`: Navigate Up (Menus) / Move Paddle Up (Pong) / Hold for Back (Views/Games)
    * `D`: Navigate Down (Menus) / Move Paddle Down (Pong)
    * `Enter`: Select (Menus) / Freeze/Unfreeze (Views) / Launch Game (Secret Menu)
    * `ESC`: Quit Application
* 3-Button Mapping (Intended Hardware):
    * Button 1 (`A`): Short Press = Up (Menus); Long Press = Back (Views/Games)
    * Button 2 (`D`): Short Press = Down (Menus)
    * Button 3 (`Enter`): Short Press = Select/Action

On Raspberry Pi (physical left/middle/right + joystick), in-app footers and the Controls menu show **Left**, **Right**, **Middle**, and **Back (hold Left)** instead of key names. On Windows they show **A**, **D**, **Enter**, and **Back (hold A)**. To force one style everywhere, set `CONTROL_DISPLAY_STYLE` in `config/input.py` to `"buttons"` or `"keys"`.

## To Do

1. Add GPIO button support for physical buttons
2. Add more comprehensive data visualization
3. Boot to application on startup
4. Add splash screen
5. Add data logging capabilities

## Setting up Autorun on Raspberry Pi (Wayfire)

The Tricorder application can be configured to start automatically when your Raspberry Pi boots into the desktop environment using Wayfire's autostart configuration.

**Prerequisites:**

*   The Tricorder project files should be present on your Raspberry Pi (e.g., in `/home/your_username/tricorder`).
*   You are running Raspberry Pi OS with Wayfire compositor (default in recent versions).
*   Your Raspberry Pi is configured to boot to the desktop environment.

**Steps:**

1.  **Navigate to the Wayfire configuration directory:**
    ```bash
    mkdir -p ~/.config/wayfire
    ```

2.  **Create or edit the Wayfire configuration file:**
    ```bash
    nano ~/.config/wayfire/wayfire.ini
    ```

3.  **Add the autostart configuration:**
    Add the following section to the file (replace `/home/dev/tricorder` with your actual project path):
    ```ini
    [autostart]
    tricorder = cd /home/dev/tricorder && source venv/bin/activate && python main.py
    ```

4.  **Save and exit the editor** (Ctrl+X, then Y, then Enter in nano).

5.  **Reboot your Raspberry Pi:**
    ```bash
    sudo reboot
    ```

The Tricorder application will now start automatically when the desktop loads.

### Booting faster and (almost) straight to the app

To reduce the time until the app is on screen:

1. **Autologin** – Skip the login screen so the desktop (and then the app) starts without user input.
   - Run `sudo raspi-config` → **System Options** → **Boot / Auto Login** → choose **Desktop Autologin** (or **Console Autologin** if you later switch to console-only boot).
   - Reboot to apply.

2. **Disable the early rainbow splash** – Removes the first splash before the boot loader.
   - Edit the Pi boot config (on the Pi):
     ```bash
     sudo nano /boot/firmware/config.txt
     ```
     (Use `/boot/config.txt` on older Pi OS if that’s what you have.)
   - In the `[all]` section (or at the top), add:
     ```ini
     disable_splash=1
     ```
   - Save and exit.

3. **Shorten or disable the Plymouth splash** – The “Raspberry Pi” graphic during boot is Plymouth. To hide it and see console text (or a black screen) until the app runs:
   - Edit the kernel command line:
     ```bash
     sudo nano /boot/firmware/cmdline.txt
     ```
     (Or `/boot/cmdline.txt` on older Pi OS.)
   - In the single line, **remove** the word `splash` (and optionally add `plymouth.enable=0` to fully disable Plymouth).
   - Example before: `... quiet splash plymouth.ignore-serial-consoles ...`
   - Example after: `... quiet plymouth.enable=0 plymouth.ignore-serial-consoles ...`
   - Save (keep the rest of the line unchanged) and reboot.

4. **Keep Wayfire autostart** – The app is started by the `[autostart]` entry in `~/.config/wayfire/wayfire.ini` (see above). With autologin, the sequence is: boot → (optional splash) → desktop → Tricorder starts automatically.

Result: the Pi boots, optionally shows a short or no splash, logs in automatically, loads the desktop, and then starts the Tricorder app. For a true “console-only” boot (no desktop, app on framebuffer) you’d need a custom setup (e.g. start only the app in a minimal X session); the steps above are the standard way to get “boot and go straight to the app” with the desktop still available in the background.

**To disable autostart:**
Edit the wayfire.ini file and remove or comment out the tricorder line:
```ini
[autostart]
# tricorder = cd /home/dev/tricorder && source venv/bin/activate && python main.py
```

**Hiding the mouse cursor for kiosk mode:**
For a clean kiosk experience, hide the mouse cursor:

1. Install unclutter:
   ```bash
   sudo apt install unclutter
   ```

2. Add cursor hiding to your wayfire.ini autostart section:
   ```ini
   [autostart]
   tricorder = cd /home/dev/tricorder && source venv/bin/activate && python main.py
   hide_cursor = unclutter -idle 0.1 -root
   ```

**Alternative: Manual startup script**
You can also create a desktop shortcut or startup script:

1. Create a startup script:
   ```bash
   nano ~/start_tricorder.sh
   ```

2. Add the following content:
   ```bash
   #!/bin/bash
   cd /home/dev/tricorder
   source venv/bin/activate
   python main.py
   ```

3. Make it executable:
   ```bash
   chmod +x ~/start_tricorder.sh
   ```

4. Add to Wayfire autostart:
   ```ini
   [autostart]
   tricorder = /home/dev/start_tricorder.sh
   ```

## Display tuning on Raspberry Pi

If the app doesn’t quite fit the physical screen (black top margin, bottom or sides cut off, or the app’s curved mask not matching the display), it can be either **Pi overscan** (framebuffer scaling) or **app safe area** (in-app margins and curve). Try both.

### 1. Pi display margins (cmdline.txt or config.txt)

This project uses **composite video** with margins set in the kernel command line. The reference copy is in the repo:

- **`system_config/cmdline.txt`** – Contains the `video=Composite-1:320x240M@60,margin_left=...,margin_right=...,margin_top=...,margin_bottom=...` parameters. These margins add black borders (shrink the visible image). **Smaller values** = less border, image closer to edges; **larger values** = more border. Copy this file to `/boot/firmware/cmdline.txt` (or `/boot/cmdline.txt` on older Pi OS) on the Pi and edit the `margin_*` values to match your display, then reboot.

  If the **sides are too tight** or you have **black top margin**, try reducing `margin_left`, `margin_right`, and `margin_top`. If the **bottom is cut off**, reduce `margin_bottom` or increase the others so the image is centered. Keep the rest of the cmdline (console=, root=, etc.) intact.

- **`system_config/config.txt`** – Reference for `/boot/firmware/config.txt`. Overscan is disabled there so the **cmdline.txt** `video=` and margins are in control. For **HDMI** (non-composite) you’d use `overscan_left`, `overscan_right`, etc. in config.txt instead.

### 2. App safe area and curve (config/display.py)

The app draws a **safe area** (margins) and an optional **rounded-corner mask** to match a curved screen/cover. If your cover or bezel is different, adjust:

- **`config/display.py`**
  - **`SAFE_AREA_TOP` / `BOTTOM` / `LEFT` / `RIGHT`** – Insets in pixels. Increase if content is still cut off by the bezel; decrease if you see unnecessary black (e.g. a large black top margin).
  - **`SAFE_AREA_CORNER_RADIUS`** – Radius of the rounded mask. Change so the app’s curve matches your screen/cover (e.g. try 8–20). Set to `0` for a rectangular mask (no curve).
  - **`SAFE_AREA_ENABLED`** – Set to `False` to disable the safe area and mask entirely (full 320×240 with no blackening).

Typical combo: fix **overscan** first so the Pi output fits the panel, then tweak **safe area** and **corner radius** so the app’s visible area and curve match your hardware.

### UI scaling best practices

When adding or changing UI code, keep layout consistent across resolutions and safe areas:

- **Use `UIScaler` everywhere** – Layout and sizing should go through `utils/ui_scaler.py`: `scale()`, `margin()`, `padding()` for dimensions; `screen_width` / `screen_height` for logical size.
- **Pass `ui_scaler` into draw paths** – Views and components should receive `ui_scaler` (from `app_state.ui_scaler` or the display layer) and use it instead of raw `screen.get_width()` / `get_height()` or magic numbers.
- **Prefer content rects** – Use the main content rect (e.g. from the menu layout) or `ui_scaler.get_safe_area_rect()` when drawing into a restricted area so content and games stay inside the safe area.
- **Avoid raw pixels in views** – Replace hardcoded values (e.g. `80`, `40`, `20`) with `ui_scaler.scale(...)` or `ui_scaler.margin(...)` so the UI scales correctly on different resolutions and on Pi with safe area enabled.

## Development Workflow

### Cross-Platform Development
1. **Windows Development**: Make changes and test using mock sensor data
2. **Raspberry Pi Deployment**: Transfer files and test with real hardware
3. **Version Control**: Use git to sync changes between platforms

### File Transfer to Raspberry Pi
- Use FileZilla, SCP, or git to transfer files
- Ensure virtual environment is activated before running
- Test with real Sense HAT hardware for final validation

## Troubleshooting

### Windows Development
- **"x11 not available" error**: This is automatically handled by platform detection
- **Mock sensor warnings**: These are normal in development mode and indicate mock data is being used
- **Window size issues**: Windows uses 800x600 windowed mode vs Pi's 320x240 fullscreen

### Raspberry Pi
- **Sense HAT not detected**: Check I2C is enabled and Sense HAT is properly connected
- **"No module named 'sense_hat'" error**: Ensure symbolic links are created correctly (step 4 in setup)
- **"No module named 'RTIMU'" error**: Install python3-rtimu and create RTIMU symbolic links
- **PyOpenGL-accelerate build errors**: This package is optional and has been removed from requirements.txt due to compilation issues on ARM64
- **Permission errors**: Ensure you have proper permissions for creating symbolic links
- **Display issues (fit, black margin, bottom/sides cut off)**: See [Display tuning on Raspberry Pi](#display-tuning-on-raspberry-pi) for overscan (`config.txt`) and app safe area (`config/display.py`).

#### Common Sense HAT Issues:
If you encounter Sense HAT import errors after following the setup:

1. **Check if system packages are installed**:
   ```bash
   python3 -c "import sys; sys.path.append('/usr/lib/python3/dist-packages'); import sense_hat; print('System sense_hat works')"
   ```

2. **Recreate symbolic links if needed**:
   ```bash
   rm -rf ~/Desktop/tricorder/venv/lib/python3.11/site-packages/sense_hat*
   rm -rf ~/Desktop/tricorder/venv/lib/python3.11/site-packages/RTIMU*
   ln -s /usr/lib/python3/dist-packages/sense_hat ~/Desktop/tricorder/venv/lib/python3.11/site-packages/
   ln -s /usr/lib/python3/dist-packages/sense_hat-2.6.0.dist-info ~/Desktop/tricorder/venv/lib/python3.11/site-packages/
   ln -s /usr/lib/python3/dist-packages/RTIMU* ~/Desktop/tricorder/venv/lib/python3.11/site-packages/
   ```

### General
- **Import errors**: Ensure virtual environment is activated and dependencies are installed
- **Performance issues**: Check system resources and close unnecessary applications

### Licenses
All licenses and attributions are in the LICENSE.txt file.