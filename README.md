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
│   ├── app_state.py        # Manages application state, navigation, menu structures
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

## Dependencies

* Python 3
* Pygame
* Sense Hat library
* psutil for system monitoring
* Other dependencies listed in `requirements.txt`

## Installation

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

## Usage

Run the application:
```bash
# Make sure virtual environment is activated
source venv/bin/activate
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

## Setting up Autorun on Raspberry Pi (systemd)

This project includes a systemd service file to enable the Tricorder application to start automatically when your Raspberry Pi boots into the graphical desktop.

**Prerequisites:**

*   The Tricorder project files should be present on your Raspberry Pi (e.g., in `/home/your_username/Desktop/tricorder`).
*   You are running a Raspberry Pi OS version that uses systemd (most modern versions do).
*   Your Raspberry Pi is configured to boot to the desktop environment.

**Steps:**

1.  **Navigate to the project directory:**
    Open a terminal on your Raspberry Pi and navigate to the Tricorder project directory.
    ```bash
    cd /path/to/your/tricorder
    ```
    For example, if your username is `dev` and the project is on your Desktop:
    ```bash
    cd /home/dev/Desktop/tricorder
    ```

2.  **Verify and Customize the Service File (if needed):**
    The service file is located at `systemd/tricorder.service` within the project. It is pre-configured for a user named `dev` and a project path of `/home/dev/Desktop/tricorder`.

    *   **Open the service file:**
        ```bash
        nano systemd/tricorder.service
        ```