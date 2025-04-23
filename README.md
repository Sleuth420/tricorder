# Raspberry Pi Tricorder Project

A Star Trek inspired tricorder simulation using a Raspberry Pi, Sense HAT, and an external display. Displays environmental and system data with a retro-style interface.

## Features

* Menu-based navigation system
* Dashboard with auto-cycling through sensors
* Individual sensor views with real-time graphs
* System monitoring (CPU, Memory, Disk usage)
* Environmental monitoring (Temperature, Humidity, Pressure)
* Motion sensing (Orientation, Acceleration)
* Easy navigation with only 3 buttons

## Project Structure

```
tricorder/
├── main.py                 # Entry point, application orchestration
├── config.py               # Configuration and constants
├── logging_config.py       # Logging setup
├── data/                   # Data acquisition layer
│   ├── sensors.py          # Raw sensor data acquisition
│   └── system_info.py      # System monitoring (CPU, memory, disk)
├── models/                 # Application state and data models
│   ├── app_state.py        # Manages application state and navigation
│   └── reading_history.py  # Stores and manages sensor history
├── ui/                     # User interface layer
│   ├── display_manager.py  # Coordinates which view to show
│   ├── menu.py             # Menu rendering and navigation
│   ├── dashboard.py        # Multi-sensor view
│   ├── sensor_view.py      # Individual sensor view
│   └── components/         # Reusable UI elements
│       ├── graph.py        # Graph rendering component
│       ├── text_display.py # Text rendering helpers 
│       └── ui_elements.py  # Buttons, borders, etc.
└── input/                  # Input handling
    └── input_handler.py    # Input processing
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
   git clone https://github.com/yourusername/tricorder.git
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
* Press `A` (or Left Arrow) to navigate to previous item or sensor
* Press `D` (or Right Arrow) to navigate to next item or sensor
* Press `Enter` to select menu items or freeze/unfreeze sensor readings

## To Do

1. Add GPIO button support for physical buttons
2. Add more comprehensive data visualization
3. Boot to application on startup
4. Add splash screen
5. Add data logging capabilities