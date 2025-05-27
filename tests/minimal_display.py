import pygame
import time
import os
import sys # Added for sys.exit()

# Crucial for Pygame on headless/framebuffer when using Xorg
os.environ["SDL_VIDEODRIVER"] = "x11"

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
FPS = 10 # Keep it low for debugging

print("Minimal Pygame Test Starting...")
print(f"User: {os.getenv('USER', 'Not Set')}")
print(f"Display: {os.getenv('DISPLAY')}")
print(f"XAuthority: {os.getenv('XAUTHORITY', 'Not Set')}")
print(f"SDL_VIDEODRIVER: {os.getenv('SDL_VIDEODRIVER')}")

try:
    print("Initializing Pygame...")
    pygame.init()
    print("Pygame initialized.")

    print("Pygame Display Info (Before set_mode):")
    try:
        # On some minimal systems, display.Info() might not be fully populated before set_mode
        # or if no X server is properly detected yet by Pygame's SDL.
        info = pygame.display.Info()
        print(f"  Hardware acceleration available: {info.hw}")
        print(f"  Window manager available: {info.wm}")
        print(f"  Video driver in use by SDL: {pygame.display.get_driver()}")
        print(f"  Current display bitsize: {info.bitsize}")
        print(f"  Current display size from info: {info.current_w}x{info.current_h}")
    except pygame.error as e:
        print(f"  Could not get pygame.display.Info() before set_mode: {e}")


    print(f"Requesting display mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT} FULLSCREEN")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    print("Display mode set.")

    actual_w = screen.get_width()
    actual_h = screen.get_height()
    print(f"Actual screen dimensions from surface: {actual_w}x{actual_h}")

    if actual_w != SCREEN_WIDTH or actual_h != SCREEN_HEIGHT:
        print(f"WARNING: Actual dimensions ({actual_w}x{actual_h}) differ from requested ({SCREEN_WIDTH}x{SCREEN_HEIGHT})")
    
    print("Pygame Display Info (After set_mode):")
    info = pygame.display.Info() # Get info again after mode set
    print(f"  Hardware acceleration available: {info.hw}")
    print(f"  Window manager available: {info.wm}")
    print(f"  Video driver in use by SDL: {pygame.display.get_driver()}")
    print(f"  Current display bitsize: {info.bitsize}")
    print(f"  Current display size from info: {info.current_w}x{info.current_h}")


    pygame.mouse.set_visible(False)
    print("Mouse set to invisible.")

    clock = pygame.time.Clock()
    print("Clock created.")

    colors = {
        "RED": (255, 0, 0),
        "GREEN": (0, 255, 0),
        "BLUE": (0, 0, 255),
        "YELLOW": (255, 255, 0)
    }
    color_names = list(colors.keys())
    color_index = 0
    
    running = True
    loop_counter = 0

    print("Entering main loop...")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("QUIT event received.")
                running = False
            if event.type == pygame.KEYDOWN:
                print(f"KEYDOWN event: {event.key}")
                if event.key == pygame.K_ESCAPE:
                    print("ESCAPE key pressed. Exiting.")
                    running = False
                if event.key == pygame.K_SPACE: # Add a way to cycle colors
                    color_index = (color_index + 1) % len(color_names)
                    print(f"Space pressed. Changed color to {color_names[color_index]}.")


        current_color_name = color_names[color_index]
        current_color_rgb = colors[current_color_name]
        screen.fill(current_color_rgb)
        
        try:
            # Attempt to load a system font, more likely to be available
            font = pygame.font.Font(None, 28) # Default system font, size 28
            text_surface = font.render(f"Test {loop_counter} - {current_color_name}", True, (0,0,0)) # Black text
            screen.blit(text_surface, (10, 10))
        except Exception as e:
            print(f"Error rendering font: {e}")


        pygame.display.flip()
        
        loop_counter += 1
        if loop_counter % (FPS * 5) == 0: # Change color automatically every 5 seconds
            color_index = (color_index + 1) % len(color_names)
            print(f"Automatic color change to {color_names[color_index]}. Screen filled.")
        
        clock.tick(FPS)

except Exception as e:
    print(f"Minimal Pygame Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    # Keep process alive to see error in journal if service auto-restarts
    # This will only happen if the exception is outside the main loop or if running is false
    # If inside the loop, it would just quit pygame and exit.
    # time.sleep(60) 
finally:
    print("Quitting Pygame.")
    pygame.quit()
    print("Exiting script.")
    sys.exit(0)