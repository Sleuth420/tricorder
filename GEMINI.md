# GEMINI.md

This document provides a comprehensive overview of the Raspberry Pi Tricorder project, designed to give context for AI-assisted development.

## Project Overview

This is a Python-based application that simulates a Star Trek-style tricorder on a Raspberry Pi with a Sense HAT and an external display. It also supports a mock-data mode for development on Windows.

The application features a retro, menu-based user interface for displaying various data points:
-   **System Monitoring:** CPU, Memory, Disk usage.
-   **Environmental Sensing:** Temperature, Humidity, Pressure (from Sense HAT).
-   **Motion Sensing:** Orientation, Acceleration (from Sense HAT).
-   **Schematics Viewer:** Renders 3D models using OpenGL.
-   **Media Player:** Plays audio and video files.
-   **Games:** Includes classic games like Pong, Snake, and Breakout.

### Architecture

The project follows a modular and stateful architecture, primarily using `pygame` for rendering and event handling.

-   **Entry Point:** `main.py` initializes the application, manages the main loop, and handles high-level state.
-   **State Management:** The `models/state_manager.py` and `models/app_state.py` are central to the application's flow, controlling transitions between different views (e.g., Menu, Sensor View, Game).
-   **Configuration:** A comprehensive, modular configuration system resides in the `config/` directory. Key files like `ui.py`, `display.py`, and `sensors.py` define the application's appearance and behavior.
-   **UI Layer:** The `ui/` directory is responsible for all rendering.
    -   `ui/display_manager.py` acts as a router, deciding which view to render based on the current application state.
    -   `ui/views/` contains the rendering logic for each specific screen.
    -   `ui/components/` holds reusable UI elements like graphs and text boxes.
-   **Data Acquisition:** The `data/` directory contains modules for reading real sensor data from the Sense HAT (`sensors.py`) and system information (`system_info.py`). It provides mock data when running on a non-Pi environment.
-   **Dependencies:** Key libraries include `pygame`, `sense-hat`, `psutil`, `PyOpenGL`, and `python-vlc`. Dependencies are listed in `requirements.txt`.

## Building and Running

### Installation

1.  **Create a virtual environment:**
    -   On Windows: `python -m venv venv_windows`
    -   On Linux/Pi: `python3 -m venv venv`
2.  **Activate the virtual environment:**
    -   On Windows: `venv_windows\Scripts\activate`
    -   On Linux/Pi: `source venv/bin/activate`
3.  **Install dependencies:**
    -   `pip install -r requirements.txt`
    -   (Note: For Raspberry Pi, the `README.md` details additional steps for linking system-level Sense HAT libraries).

### Running the Application

Once dependencies are installed and the virtual environment is active, run the application with:

```bash
python main.py
```

The application will automatically detect the platform (Windows vs. Linux) and use mock sensor data if the Sense HAT is not available.

## Development Conventions

-   **State-Driven Logic:** All application flow is controlled by a state machine. To add a new screen or feature, you will likely need to:
    1.  Define a new state constant in `models/app_state.py`.
    2.  Add a new view module in the `ui/views/` directory.
    3.  Update `ui/display_manager.py` to route your new state to your new view.
    4.  Trigger the state transition from an input handler or another part of the application logic in `models/app_state.py`.
-   **Configuration-Driven UI:** UI elements, colors, fonts, and layout parameters are defined in the `config/` directory. Avoid hardcoding values in the UI rendering code.
-   **Logging:** The application uses Python's `logging` module. `logging_config.py` sets up the configuration. Use `logging.getLogger(__name__)` at the top of each module to get a logger instance.
-   **UI Scaling:** The `utils/ui_scaler.py` module provides a `UIScaler` class to handle adjustments for different screen resolutions. UI components should use this scaler to remain resolution-independent.
-   **Error Handling:** The main loop in `main.py` includes `try...except` blocks to catch and log runtime errors, preventing the application from crashing and attempting to return to a safe state (the main menu).
-   **File Structure:** The project is organized by feature/concern (e.g., `ui`, `data`, `models`, `games`). New files should be placed in the appropriate directory.
