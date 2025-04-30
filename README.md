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