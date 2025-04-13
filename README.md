# Raspberry Pi Tricorder Project

A simple application simulating a Star Trek Tricorder using a Raspberry Pi, Sense HAT, and an external display.

## Features

*   Displays sensor data from the Sense HAT (Temperature, Humidity, Pressure, Orientation).
*   Cycles through sensor modes using input controls.
*   Ability to Freeze/Unfreeze the current display reading.
*   Retro-style UI using Pygame.

## Current Status

*   Designed for testing with an HDMI monitor and keyboard input.
*   GPIO button input needs to be implemented later.

## Files

*   `main.py`: Main application entry point and event loop.
*   `config.py`: Configuration settings (display, colors, fonts, input keys, sensor modes).
*   `sensors.py`: Handles reading data from the Sense HAT.
*   `display.py`: Handles drawing the UI elements on the screen using Pygame.
*   `input_handler.py`: Handles processing user input (currently keyboard).
*   `fonts/`: (Optional) Place custom `.ttf` font files here and update `config.py`.
*   `README.md`: This file.

## Dependencies

*   Python 3
*   `sense-hat` library (`sudo apt install sense-hat`)
*   `pygame` library (`sudo apt install python3-pygame`)

## How to Run

1.  Ensure dependencies are installed.
2.  Navigate to the `tricorder/` directory in the terminal.
3.  Run the main script: `python3 main.py`
4.  Use Left/Right arrow keys to change modes.
5.  Use Enter key to Freeze or Unfreeze the current sensor reading.
6.  Use Esc to quit.

## To DO

1. check input handler for key presses
2. add a logger and a cron job to clean up
3. boot to main.py 
4. splash screen
5. add more sensor data