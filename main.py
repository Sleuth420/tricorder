# --- main.py ---
# Main application file for the Raspberry Pi tricorder
# Now with menu-based navigation and modular structure

import sys
import pygame
import logging
import time
import platform
import os
import threading

# Force SDL to use x11 video driver BEFORE pygame.init() - but only on Linux
if platform.system() == "Linux":
    os.environ["SDL_VIDEODRIVER"] = "x11"

# Import configuration and logging modules
import config
import logging_config

# Import application components from the new modular structure
from models.app_state import AppState, STATE_MENU, STATE_PONG_ACTIVE
from models.reading_history import ReadingHistory
from data import sensors
from data import system_info
# Import the new data updater function
from data.data_updater import update_all_data
from ui.display_manager import init_display, update_display
from input.input_handler import process_input, init_joystick

# Get a logger for this module
logger = logging.getLogger(__name__)

def count_python_lines():
    """Count all lines of Python code in the project, excluding unwanted directories and files."""
    exclude_dirs = {'__pycache__', 'venv', 'venv_windows', '.git', 'logs', 'assets'}
    exclude_extensions = {'.txt', '.md', '.png', '.jpg', '.jpeg', '.gif', '.json', '.log', '.gitignore'}
    exclude_files = {'config_old.py'}  # Specific files to exclude
    
    total_lines = 0
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories from dirs list to prevent os.walk from entering them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Only count .py files, but exclude specific files
            if file_ext == '.py' and file not in exclude_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        python_files.append((file_path, lines))
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
    
    logger.info(f"Counted {total_lines} lines of Python code across {len(python_files)} files")
    return total_lines, python_files

def draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage_text):
    """Draw the loading screen with splash logo, progress bar, and line count."""
    screen.fill(config.Theme.BACKGROUND)
    
    # Draw the splash logo
    screen.blit(logo_splash, logo_rect)
    
    # Loading bar dimensions
    bar_width = int(screen.get_width() * 0.6)
    bar_height = 20
    bar_x = (screen.get_width() - bar_width) // 2
    bar_y = logo_rect.bottom + 40
    
    # Draw loading bar background
    bar_bg_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
    pygame.draw.rect(screen, config.Theme.FOREGROUND, bar_bg_rect)
    pygame.draw.rect(screen, config.Theme.BACKGROUND, pygame.Rect(bar_x, bar_y, bar_width, bar_height))
    
    # Draw loading bar fill
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(screen, config.Theme.ACCENT, fill_rect)
    
    # Draw progress percentage
    try:
        progress_font = fonts.get('medium', pygame.font.Font(None, config.FONT_SIZE_MEDIUM))
    except:
        progress_font = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
    
    progress_text = f"{int(progress * 100)}%"
    progress_surface = progress_font.render(progress_text, True, config.Theme.FOREGROUND)
    progress_rect = progress_surface.get_rect(center=(screen.get_width() // 2, bar_y + bar_height + 25))
    screen.blit(progress_surface, progress_rect)
    
    # Draw current stage text
    stage_surface = progress_font.render(stage_text, True, config.Theme.FOREGROUND)
    stage_rect = stage_surface.get_rect(center=(screen.get_width() // 2, progress_rect.bottom + 20))
    screen.blit(stage_surface, stage_rect)
    
    # Draw line count if available
    if total_lines > 0:
        lines_text = f"Python Lines: {current_lines:,} / {total_lines:,}"
        lines_surface = progress_font.render(lines_text, True, config.Theme.ACCENT)
        lines_rect = lines_surface.get_rect(center=(screen.get_width() // 2, stage_rect.bottom + 20))
        screen.blit(lines_surface, lines_rect)
    
    pygame.display.flip()

class LoadingProgress:
    """Thread-safe loading progress tracker."""
    def __init__(self):
        self.current_lines = 0
        self.total_lines = 0
        self.stage = "Initializing..."
        self.complete = False
        self.lock = threading.Lock()
    
    def update(self, current_lines=None, total_lines=None, stage=None, complete=None):
        with self.lock:
            if current_lines is not None:
                self.current_lines = current_lines
            if total_lines is not None:
                self.total_lines = total_lines
            if stage is not None:
                self.stage = stage
            if complete is not None:
                self.complete = complete
    
    def get_status(self):
        with self.lock:
            return self.current_lines, self.total_lines, self.stage, self.complete

def loading_worker(progress_tracker):
    """Background worker that performs the actual loading tasks."""
    try:
        # Stage 1: Count Python lines
        progress_tracker.update(stage="Counting Python files...")
        time.sleep(0.5)  # Small delay to show the stage
        
        total_lines, python_files = count_python_lines()
        progress_tracker.update(total_lines=total_lines, current_lines=total_lines)
        
        # Stage 2: Initialize sensors (if not already done)
        progress_tracker.update(stage="Initializing sensors...")
        time.sleep(0.5)
        
        # Stage 3: Preparing system
        progress_tracker.update(stage="Preparing system...")
        time.sleep(0.5)
        
        # Stage 4: Loading complete
        progress_tracker.update(stage="Loading complete!", complete=True)
        
    except Exception as e:
        logger.error(f"Error in loading worker: {e}", exc_info=True)
        progress_tracker.update(stage="Loading completed with errors", complete=True)

def display_critical_error_on_screen(screen, fonts, config_module, messages):
    """Helper function to display critical error messages if possible."""
    if screen and fonts and config_module and pygame.get_init() and pygame.display.get_active():
        try:
            screen.fill(config_module.Theme.BACKGROUND)
            error_font_size = config_module.FONT_SIZE_MEDIUM
            try:
                # Try to use a pre-loaded font if available, otherwise default system font
                error_font = fonts.get('medium', pygame.font.Font(None, error_font_size))
            except Exception: 
                error_font = pygame.font.Font(None, config_module.FONT_SIZE_LARGE) # Absolute fallback

            current_y = screen.get_height() // 4 # Start a bit higher
            center_x = screen.get_width() // 2

            for i, msg_text in enumerate(messages):
                msg_sf = error_font.render(msg_text, True, config_module.Theme.ALERT)
                msg_pos = (center_x - msg_sf.get_width() // 2, current_y)
                screen.blit(msg_sf, msg_pos)
                current_y += msg_sf.get_height() + 5
                if i == 0: # Add extra space after the first line (typically the error type)
                    current_y += 5
            
            pygame.display.flip()
            pygame.time.wait(5000) # Show error for 5 seconds
        except Exception as display_e:
            logger.error(f"Failed to display critical error message on screen: {display_e}", exc_info=True)
    else:
        logger.warning("Screen, fonts, or Pygame not available/active for displaying critical error message.")

def main():
    """Main function to run the tricorder application."""
    logging_config.setup_logging()
    logger.info("Starting tricorder Application...")
    
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Display size: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}, Fullscreen: {config.FULLSCREEN}")
    logger.info(f"Available sensor modes: {', '.join(config.SENSOR_MODES)}")

    # Critical Initialization: Display
    screen, clock, fonts = init_display()
    if not screen:
        logger.critical("Fatal Error: Could not initialize display. Application cannot continue.")
        sys.exit(1) # Exit if display fails - app is unusable
    logger.info("Display initialized successfully.")

    # Get actual screen dimensions after display initialization
    actual_screen_width = screen.get_width()
    actual_screen_height = screen.get_height()
    logger.info(f"Actual screen dimensions: {actual_screen_width}x{actual_screen_height}")

    # Initialize Models using the new modular architecture
    app_state = AppState(config, actual_screen_width, actual_screen_height)
    reading_history = ReadingHistory(config.SENSOR_MODES, config.GRAPH_HISTORY_SIZE)
    logger.info("Application state and reading history initialized.")

    exit_code = 0
    try:
        # Non-critical Initializations (loading screen with splash, sensors)
        try:
            logo_splash = pygame.image.load(config.SPLASH_LOGO_PATH).convert_alpha()
            # Scale the logo to be 60% of screen width while maintaining aspect ratio (reduced to make room for loading elements)
            screen_width = screen.get_width()
            target_width = int(screen_width * 0.6)
            aspect_ratio = logo_splash.get_height() / logo_splash.get_width()
            target_height = int(target_width * aspect_ratio)
            logo_splash = pygame.transform.smoothscale(logo_splash, (target_width, target_height))
            # Position logo higher to make room for loading elements
            logo_center_y = screen.get_height() // 3
            logo_rect = logo_splash.get_rect(center=(screen.get_width() // 2, logo_center_y))
            
            logger.info("Starting loading screen...")
            
            # Create progress tracker and start loading worker
            progress_tracker = LoadingProgress()
            loading_thread = threading.Thread(target=loading_worker, args=(progress_tracker,))
            loading_thread.daemon = True
            loading_thread.start()
            
            # Loading screen loop - minimum 5 seconds
            loading_start_time = time.time()
            minimum_loading_time = 5.0  # 5 seconds minimum
            
            while True:
                current_time = time.time()
                elapsed_time = current_time - loading_start_time
                
                # Get current loading status
                current_lines, total_lines, stage, complete = progress_tracker.get_status()
                
                # Calculate progress (combination of time and completion)
                time_progress = min(elapsed_time / minimum_loading_time, 1.0)
                
                # If loading is complete and minimum time has passed
                if complete and elapsed_time >= minimum_loading_time:
                    progress = 1.0
                    draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage)
                    time.sleep(0.5)  # Brief pause to show 100%
                    break
                elif complete:
                    # Loading done but minimum time not reached - show time-based progress
                    progress = time_progress
                else:
                    # Loading not done - show partial progress based on time
                    progress = time_progress * 0.9  # Max 90% until actually complete
                
                # Draw the loading screen
                draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage)
                
                # Handle quit events during loading
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        logger.info("pygame.QUIT event received during loading. Exiting.")
                        pygame.quit()
                        sys.exit(0)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
            
            logger.info("Loading screen finished.")
            
        except Exception as e_splash:
            logger.warning(f"Could not load or display loading screen: {e_splash}", exc_info=True)

        try:
            sensors_active = sensors.init_sensors()
            if not sensors_active:
                logger.warning("Could not initialize Sense HAT. Sensor readings will show errors.")
            else:
                logger.info("Sensors initialized successfully.")
                # Initialize joystick after sensors are initialized
                if init_joystick():
                    logger.info("Joystick initialized successfully")
                else:
                    logger.warning("Could not initialize joystick")
        except Exception as e_sensors:
            logger.error(f"Error initializing sensors: {e_sensors}", exc_info=True)
            sensors_active = False # Assume sensors are not active if init fails

        sensor_values = {}
        running = True
        logger.info("Entering main event loop...")

        # Main Application Loop
        while running:
            try: # Inner try-except for runtime errors to keep the application alive
                # 1. Handle Input
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        logger.info("pygame.QUIT event received. Exiting loop.")
                        running = False
                        break
                if not running: # If QUIT received, skip rest of this iteration and exit loop
                    continue

                input_results = process_input(events, config)
                app_state.handle_input(input_results)

                # 2. Update App State
                current_time = time.time()
                app_state.auto_cycle_dashboard(current_time)
                app_state.update()

                if app_state.current_state == STATE_PONG_ACTIVE and app_state.active_pong_game:
                    app_state.game_manager.update_pong(app_state.keys_held)

                # 3. Read Sensor Data
                if app_state.current_state != STATE_PONG_ACTIVE:
                    should_read_sensors = (not app_state.is_frozen or
                                          (current_time - app_state.last_reading_time >= 1.0))
                    if should_read_sensors:
                        app_state.last_reading_time = current_time
                        update_all_data(sensor_values, reading_history, config)
                
                # 4. Update Display
                update_display(screen, app_state, sensor_values, reading_history, fonts, config)
                
                # 5. Control Frame Rate
                clock.tick(config.FPS)

            except Exception as e_runtime: # Catch runtime errors within the main loop
                logger.critical(f"Runtime error in main loop: {e_runtime}", exc_info=True)
                error_messages = [
                    "Runtime Error Occurred:",
                    str(e_runtime)[:100], # Show first 100 chars of error
                    "Returning to main menu.",
                    "Check logs for full details."
                ]
                display_critical_error_on_screen(screen, fonts, config, error_messages)
                
                # Reset to a safe state (main menu) and continue running
                app_state.state_manager.transition_to(STATE_MENU)
                logger.info("Reset state to MENU due to runtime error. Application continues.")
                time.sleep(1) # Brief pause to ensure error message is seen if rapidly re-triggering

        # --- End of 'while running' loop ---
        logger.info("Exiting main loop.")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting application gracefully.")
        # exit_code remains 0 for a clean, developer-initiated exit
    except Exception as e_catastrophic:
        # This catches unhandled exceptions from the initialization phase (post-display)
        # or if something truly unexpected breaks out of the main loop's structure.
        logger.critical(f"Catastrophic application error: {e_catastrophic}", exc_info=True)
        error_messages = [
            "Catastrophic System Error:", 
            str(e_catastrophic)[:100],
            "Application will now exit.",
            "Check logs for details."
        ]
        display_critical_error_on_screen(screen, fonts, config, error_messages)
        exit_code = 1 # Indicate an error exit
    finally:
        logger.info("Performing application cleanup...")
        try:
            # Only cleanup sensors if the module was loaded and init attempted
            if 'sensors' in sys.modules and 'sensors_active' in locals(): 
                sensors.cleanup_sensors()
                logger.info("Sensors cleanup called.")
        except Exception as e_cleanup_sensors:
            logger.error(f"Error during sensor cleanup: {e_cleanup_sensors}", exc_info=True)
        
        try:
            if pygame.get_init(): # Check if Pygame is initialized before quitting
                pygame.quit()
                logger.info("Pygame quit called.")
        except Exception as e_cleanup_pygame:
            logger.error(f"Error during pygame.quit(): {e_cleanup_pygame}", exc_info=True)
            
        logger.info(f"Tricorder Application Closed. Exit code: {exit_code}")

    sys.exit(exit_code)

# Ensure the main function runs only when the script is executed directly
if __name__ == '__main__':
    main()
