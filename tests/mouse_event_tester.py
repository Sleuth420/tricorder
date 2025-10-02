import pygame
import sys
import config

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Mouse Event Tester")

print("Mouse event tester running. Press Ctrl+C to exit.")
print("Testing mouse button events...")
print("\nMouse Controls:")
print("Left Click = Previous (like A key)")
print("Right Click = Next (like D key)")
print("Middle Click = Select (like Enter key)")
print("Long Left Click = Back to Menu")
print("Long Right Click = Pause Menu (in schematics)")
print("Long Middle Click = Secret Menu (on Settings item)")

# Track mouse button states for long press detection
mouse_buttons_held = {
    config.MOUSE_LEFT: False,
    config.MOUSE_RIGHT: False,
    config.MOUSE_MIDDLE: False
}

mouse_press_start_times = {
    config.MOUSE_LEFT: None,
    config.MOUSE_RIGHT: None,
    config.MOUSE_MIDDLE: None
}

import time

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button
            print(f"\nMouse BUTTONDOWN: Button={button}, Pos={event.pos}")
            
            # Check if it's one of our mapped buttons
            if button in [config.MOUSE_LEFT, config.MOUSE_RIGHT, config.MOUSE_MIDDLE]:
                mouse_buttons_held[button] = True
                mouse_press_start_times[button] = time.time()
                
                # Map to actions
                if button == config.MOUSE_LEFT:
                    print("Action: PREV (Previous/Left)")
                elif button == config.MOUSE_RIGHT:
                    print("Action: NEXT (Next/Right)")
                elif button == config.MOUSE_MIDDLE:
                    print("Action: SELECT")
            else:
                print(f"Unmapped button: {button}")
                
        elif event.type == pygame.MOUSEBUTTONUP:
            button = event.button
            print(f"\nMouse BUTTONUP: Button={button}, Pos={event.pos}")
            
            # Check if it's one of our mapped buttons
            if button in [config.MOUSE_LEFT, config.MOUSE_RIGHT, config.MOUSE_MIDDLE]:
                mouse_buttons_held[button] = False
                
                # Calculate press duration
                if mouse_press_start_times[button] is not None:
                    press_duration = time.time() - mouse_press_start_times[button]
                    print(f"Press duration: {press_duration:.2f} seconds")
                    
                    # Check for long press
                    if press_duration >= config.INPUT_LONG_PRESS_DURATION:
                        if button == config.MOUSE_LEFT:
                            print("Action: BACK (Long press)")
                        elif button == config.MOUSE_RIGHT:
                            print("Action: PAUSE MENU (Long press)")
                        elif button == config.MOUSE_MIDDLE:
                            print("Action: SECRET MENU (Long press)")
                    else:
                        # Short press actions
                        if button == config.MOUSE_LEFT:
                            print("Action: PREV (Short press)")
                        elif button == config.MOUSE_RIGHT:
                            print("Action: NEXT (Short press)")
                        elif button == config.MOUSE_MIDDLE:
                            print("Action: SELECT (Short press)")
                
                mouse_press_start_times[button] = None
            else:
                print(f"Unmapped button: {button}")

    # Check for long press while buttons are held
    current_time = time.time()
    for button, is_held in mouse_buttons_held.items():
        if is_held and mouse_press_start_times[button] is not None:
            hold_duration = current_time - mouse_press_start_times[button]
            if hold_duration >= config.INPUT_LONG_PRESS_DURATION:
                if button == config.MOUSE_LEFT:
                    print(f"\nLong press detected: Mouse Left held for {hold_duration:.1f}s - BACK action")
                elif button == config.MOUSE_RIGHT:
                    print(f"\nLong press detected: Mouse Right held for {hold_duration:.1f}s - PAUSE MENU action")
                elif button == config.MOUSE_MIDDLE:
                    print(f"\nLong press detected: Mouse Middle held for {hold_duration:.1f}s - SECRET MENU action")
                # Reset to avoid spam
                mouse_press_start_times[button] = None

    pygame.time.Clock().tick(30)

