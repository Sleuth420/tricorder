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
│   └── stargate_304/
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
* Other dependencies listed in `requirements.txt`

## Installation

### Raspberry Pi Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Sleuth420/tricorder.git
   cd tricorder
   ```

2. Install system-level Sense HAT package:
   ```bash
   sudo apt update
   sudo apt install sense-hat
   ```

3. Set up Python virtual environment with system site packages (to allow Sense HAT access):
   ```bash
   # Create virtual environment with system site packages
   python3 -m venv venv --system-site-packages
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

4. Enable I2C interface (required for Sense HAT):
   ```bash
   sudo raspi-config
   ```
   Then navigate to:
   - Interface Options
   - I2C
   - Enable I2C
   - Select "Yes" to reboot when prompted

5. After reboot, verify Sense HAT is detected:
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

**To disable autostart:**
Edit the wayfire.ini file and remove or comment out the tricorder line:
```ini
[autostart]
# tricorder = cd /home/dev/tricorder && source venv/bin/activate && python main.py
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
- **Permission errors**: Ensure virtual environment has system site packages access
- **Display issues**: Verify display configuration and resolution settings

### General
- **Import errors**: Ensure virtual environment is activated and dependencies are installed
- **Performance issues**: Check system resources and close unnecessary applications