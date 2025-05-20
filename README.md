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
├── config.py               # Configuration constants (colors, keys, settings)
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
├── images/
│   └── spork.png           # Game preview images
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
* Pygame (`pip install pygame`)
* Sense Hat library (`sudo apt install sense-hat`)
* psutil for system monitoring (`pip install psutil`)

The complete list of dependencies is in `requirements.txt`.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Sleuth420/tricorder.git
   cd tricorder
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. On Raspberry Pi, install the Sense HAT library:
   ```bash
   sudo apt install sense-hat
   ```

## Usage

Run the application:
```bash
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
    *   **Check the following lines and update them if your username or project path is different:**
        ```ini
        [Service]
        User=dev  # Change 'dev' to your actual username (e.g., 'pi')
        Group=dev # Change 'dev' to your actual username (e.g., 'pi')
        WorkingDirectory=/home/dev/Desktop/tricorder  # Change path if project is elsewhere
        ExecStart=/usr/bin/python3 /home/dev/Desktop/tricorder/main.py # Change path if project is elsewhere
        Environment="DISPLAY=:0"
        # If DISPLAY=:0 is not sufficient, you might need to uncomment and set XAUTHORITY:
        # Environment="XAUTHORITY=/home/your_username/.Xauthority"
        ```
        Save the file and exit the editor (Ctrl+X, then Y, then Enter in nano).

3.  **Copy the Service File to Systemd:**
    You need superuser privileges to copy the file to the systemd directory.
    ```bash
    sudo cp systemd/tricorder.service /etc/systemd/system/
    ```

4.  **Reload Systemd Daemon:**
    This makes systemd aware of the new service file.
    ```bash
    sudo systemctl daemon-reload
    ```

5.  **Enable the Service:**
    This command creates the necessary symlinks for the service to start on boot.
    ```bash
    sudo systemctl enable tricorder.service
    ```

6.  **Start the Service (Optional - for immediate testing):**
    You can start the service immediately to test if it works without a reboot.
    ```bash
    sudo systemctl start tricorder.service
    ```
    Your application's UI should appear on the desktop.

7.  **Check Service Status:**
    To verify the service is running or to check for errors:
    ```bash
    sudo systemctl status tricorder.service
    ```
    Look for `Active: active (running)`. If there are issues, the status output might provide clues.

8.  **Reboot to Test Autorun:**
    Reboot your Raspberry Pi to confirm the application starts automatically after logging into the desktop.
    ```bash
    sudo reboot
    ```

**Troubleshooting:**

*   If the service fails to start or the UI doesn't appear, check the systemd journal for your service:
    ```bash
    journalctl -u tricorder.service -n 50 --no-pager
    ```
    This will show the latest log messages from your service, which can help identify Python errors or other issues.
*   Ensure all paths in the `tricorder.service` file are correct and that the user specified has the necessary permissions to run the application and access the display.
*   Make sure your Python script `main.py` is executable or that the `ExecStart` line correctly invokes the python interpreter. The provided service file uses `/usr/bin/python3`.
*   If you see errors related to display, ensure `Environment="DISPLAY=:0"` is set. If issues persist, you might need to also set `Environment="XAUTHORITY=/home/your_username/.Xauthority"` (making sure to replace `your_username` with the correct user).

---