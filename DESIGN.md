# Design Document: Raspberry Pi Tricorder Replica

**Version:** 0.0.1 (beta) 

## 1. Introduction

### 1.1. Project Goal

To create a portable device resembling a Star Trek Tricorder using a Raspberry Pi 4 and a Sense HAT. The primary function is to read various environmental sensor data from the Sense HAT and display it clearly on an external screen.

### 1.2. Core Functionality

- Read sensor data: Temperature, Humidity, Barometric Pressure, Orientation (Pitch/Roll/Yaw).
- Display one sensor reading and its mode name at a time.
- Allow cycling through sensor modes using dedicated "Next" and "Previous" inputs.
- Allow freezing/unfreezing the current display reading using a dedicated "Select" input.
- Present the information with a simple, retro-themed graphical user interface.

### 1.3. Scope

This document covers the design for the core software application, including sensor interaction, display logic, and input handling. It assumes initial development and testing using a standard HDMI monitor and keyboard/mouse simulation before migrating to final embedded hardware (LCD screen, physical buttons). Auto-starting the application is considered a later phase.

### 1.4. Target Platform

Raspberry Pi 4 Model B, Raspberry Pi OS (64-bit Bookworm, Debian-based), Python 3.

## 2. System Architecture

### 2.1. Overview

The system comprises the Raspberry Pi acting as the central processing unit, the Sense HAT providing sensor input, an external display for output, and input controls (simulated by keyboard/mouse initially, physical buttons later) for user interaction. The software application orchestrates reading sensor data, processing user input, and rendering the graphical interface.

### 2.2. Architecture Description (Textual)

- **Hardware Layer:** Contains the Raspberry Pi 4, Sense HAT, External Display (HDMI), and Input Device (Keyboard/Mouse/OSK initially, planned Physical Buttons).
- **Software Layer:** Contains the Raspberry Pi OS and the Python 3 Application.
- **User Interaction:** The User interacts with the Input Device.
- **Connections:**
    - Pi controls and reads Sensor Data from Sense HAT.
    - Pi runs the OS, which executes the Python Application.
    - Application reads from Sense HAT (via Pi).
    - Application draws graphics to the External Display (via Pi).
    - Application reads input from the Input Device (via Pi).

*(Note: A visual Mermaid diagram was intended here but removed for formatting simplicity.)*

## 3. Hardware Components

### 3.1. Confirmed

- Raspberry Pi 4 Model B
- Official Raspberry Pi Sense HAT (provides Temperature, Humidity, Pressure, Gyroscope, Accelerometer, Magnetometer sensors)
- HDMI Cable (for connection to display)
- Monitor (for initial development/testing)
- USB Mouse (for OSK interaction during testing)
- Power Supply for Raspberry Pi

### 3.2. Planned/Required

- Small Form Factor LCD Screen (Connection type TBD - HDMI preferred for simplicity, SPI possible). Resolution/size TBD based on case design.
- Three (3) Physical Buttons (Tactile switches preferred).
- Wiring/Connectors (Jumper wires, potentially PCB) to connect buttons to Raspberry Pi GPIO pins.
- Enclosure/Case (To house all components in a "Tricorder" style).

## 4. Software Components & Design Decisions

### 4.1. Operating System

Raspberry Pi OS (64-bit Bookworm) - Standard, well-supported OS for the Raspberry Pi with good hardware compatibility.

### 4.2. Programming Language

Python 3 - Chosen for its readability, extensive libraries, strong community support, and suitability for rapid development on the Raspberry Pi.

### 4.3. Core Libraries

- **`sense-hat`**: Official library provided for easy interaction with the Sense HAT sensors.
  - *Decision:* Use the official library for reliability and simplicity.
- **`pygame`**: Cross-platform library for creating multimedia applications, including graphics, sound, and event handling.
  - *Decision:* Chosen for UI display and input handling because it:
      - Provides straightforward ways to draw shapes, text, and images.
      - Handles fullscreen display modes well.
      - Manages event loops for keyboard/mouse input effectively.
      - Is suitable for the desired simple, retro graphical style without the overhead of a full desktop GUI toolkit (like Tkinter or PyQt).
- **`gpiozero` (Planned)**: High-level library for interacting with GPIO pins.
  - *Decision:* Will be used for reading physical button presses due to its ease of use compared to lower-level GPIO libraries.

### 4.4. Modules (Python Files)

The application is structured into separate modules for better organization, maintainability, and separation of concerns.

- **`main.py`**:
  - *Responsibility:* Main application entry point. Initializes other modules (display, sensors). Contains the main application loop. Manages application state (current mode, frozen status). Orchestrates input handling, data retrieval, and screen updates. Handles application startup and cleanup.
  - *Justification:* Centralizes control flow and state management.
- **`config/` (Modular Configuration System)**:
  - *Responsibility:* Stores all configuration constants organized into logical modules:
    - `__init__.py`: Main config module that imports and exposes all sub-configurations
    - `colors.py`: Color palettes and themes (Palette, Theme classes)
    - `display.py`: Display and graphics settings (screen dimensions, FPS, graph settings)
    - `ui.py`: UI layout constants (fonts, arrow indicators, layout dimensions)
    - `input.py`: Input mappings and controls (key mappings, GPIO pins, action constants)
    - `sensors.py`: Sensor configurations and display properties
  - *Justification:* Separates configuration from logic and organizes settings by category, making it easy to find and modify specific types of settings. Maintains backward compatibility through the main `__init__.py` module.
- **`sensors.py`**:
  - *Responsibility:* Initializes the Sense HAT. Provides functions to read and format data for specific sensor modes requested by `main.py`. Handles potential errors during sensor communication. Includes sensor cleanup logic.
  - *Justification:* Encapsulates all direct interaction with the Sense HAT hardware/library, isolating sensor-specific code.
- **`display.py`**:
  - *Responsibility:* Initializes Pygame display and loads fonts. Provides functions (`draw_ui`) to render the entire user interface (background, text elements, hints) onto the Pygame screen surface based on data provided by `main.py`.
  - *Justification:* Encapsulates all Pygame drawing logic, keeping UI rendering separate from application state and sensor logic.
- **`input_handler.py`**:
  - *Responsibility:* Processes Pygame events related to user input (currently keyboard, potentially mouse later, planned GPIO). Translates low-level events (e.g., `KEYDOWN` for Left Arrow) into application-level actions ("PREV", "NEXT", "SELECT", "QUIT").
  - *Justification:* Isolates input processing logic, making it easier to switch between input methods (keyboard -> GPIO) later by modifying primarily this file.

## 5. File Structure

tricorder/
├── main.py # Main application logic, event loop
├── config/ # Modular configuration system
│   ├── __init__.py # Main config module (imports all sub-configs)
│   ├── colors.py # Color palettes and themes
│   ├── display.py # Display and graphics settings
│   ├── ui.py # UI layout, fonts, and arrow indicators
│   ├── input.py # Input mappings and controls
│   └── sensors.py # Sensor configurations and display properties
├── config_old.py # DEPRECATED - old monolithic config (with warnings)
├── sensors.py # Functions to interact with the Sense HAT
├── display.py # Functions to draw the UI using Pygame
├── input_handler.py # Functions to handle input (keyboard now, GPIO later)
├── fonts/ # Optional: Directory to store custom font files (.ttf)
│ └── (put font files here later)
└── README.md # Project description and usage instructions


*Justification:* This flat structure within the `tricorder` directory is simple and sufficient for the current number of modules. Logically groups related functionality into separate files as described in section 4.4. Provides an optional dedicated folder for assets like fonts.

## 6. User Interface (UI) Design

### 6.1. Layout

The screen is divided into logical sections:

- **Top Area:** Displays the name of the current sensor mode (e.g., "TEMPERATURE"). Indicates "[FROZEN]" status if applicable. Uses accent color.
- **Middle Area:** Displays the primary sensor reading (value and unit) in a large font. Uses foreground color.
- **Bottom Area:** Displays hints for the main interactions ("< PREV | FREEZE | NEXT >" or similar, potentially changing based on frozen state). Uses foreground color and a small font.

### 6.2. Visual Style

Aims for a simple, retro "computer terminal" aesthetic.

- **Colors:** Limited palette (Black background, Green foreground, Amber/Gold accent) defined in `config/colors.py`. A distinct color indicates the frozen state.
- **Fonts:** Monospaced or simple pixelated font preferred (currently uses Pygame default, configurable via `config/ui.py`). Multiple sizes for hierarchy (Large for value, Medium for title, Small for hints).

### 6.3. Interaction Flow / State Diagram Description (Textual)

- The application starts showing the first sensor mode (e.g., TEMPERATURE) in a 'Live' state.
- Pressing NEXT cycles forward through the defined sensor modes (TEMPERATURE -> HUMIDITY -> PRESSURE -> ORIENTATION -> TEMPERATURE...).
- Pressing PREV cycles backward through the defined sensor modes (...ORIENTATION -> PRESSURE -> HUMIDITY -> TEMPERATURE -> ORIENTATION...).
- Pressing SELECT while in the 'Live' state transitions the application to the 'Frozen' state, displaying the last captured reading for the current mode.
- Pressing SELECT while in the 'Frozen' state transitions the application back to the 'Live' state for the current mode, resuming live sensor reads.
- Pressing NEXT or PREV while in the 'Frozen' state changes to the appropriate next/previous sensor mode AND transitions the application back to the 'Live' state.

*(Note: A visual Mermaid diagram was intended here but removed for formatting simplicity.)*

## 7. Data Flow

1.  **Input:** User presses a key (e.g., Right Arrow) on the keyboard/OSK.
2.  **Event Detection:** Pygame detects the `KEYDOWN` event.
3.  **Input Processing (`input_handler.py`):** Receives the Pygame event list, identifies the Right Arrow key press, returns the action string "NEXT".
4.  **State Update (`main.py`):** Receives "NEXT", updates `current_mode_index`, sets `is_frozen` to `False`, sets `mode_changed` flag.
5.  **Data Request (`main.py`):** Checks `is_frozen` (False) and `mode_changed` (True). Determines the new `current_mode_name` (e.g., "HUMIDITY"). Calls `sensors.get_sensor_data("HUMIDITY")`.
6.  **Sensor Reading (`sensors.py`):** Receives "HUMIDITY", calls the appropriate `sense_hat` library function (e.g., `sense.get_humidity()`). Formats the value (e.g., "65.2") and unit ("%"). Returns ("65.2", "%", "").
7.  **Display Preparation (`main.py`):** Receives the data ("65.2", "%", ""). Stores it in `last_value`, `last_unit`, `last_note`. Calls `display.draw_ui` passing the screen surface, "HUMIDITY", "65.2", "%", "", and `is_frozen` (False).
8.  **Rendering (`display.py`):** Receives data. Clears the screen buffer. Renders text elements ("HUMIDITY", "65.2 %", hints) using loaded fonts and configured colors onto the Pygame screen surface. Checks `is_frozen` to decide whether to add "[FROZEN]" text or use frozen colors.
9.  **Screen Update (`main.py`):** Calls `pygame.display.flip()` to make the updated screen buffer visible on the actual monitor.
10. **Loop:** Waits briefly (`clock.tick()`) and repeats from Step 1/2. (If frozen and mode not changed, Step 5 would skip to Step 7 using `last_value` etc.).

## 8. Future Enhancements (Potential)

- Sound effects for button presses or mode changes.
- Additional display modes (e.g., showing multiple sensors, simple graphs).
- Logging sensor data to a file.
- Implementation of GPIO button input using `gpiozero`.
- Configuration as a systemd service for auto-start on boot.
- Simple temperature calibration/offset configuration.
- Integration of other I2C/SPI sensors if desired.
- Adding Compass heading (Yaw) stabilization logic if needed.