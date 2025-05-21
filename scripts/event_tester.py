import pygame
import sys
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_RELEASED
import config

pygame.init()
screen = pygame.display.set_mode((300, 200))
pygame.display.set_caption("Event Tester")

# Initialize Sense HAT
sense = SenseHat()

print("Event tester running. Press Ctrl+C to exit.")
print("Testing both Pygame events and Sense HAT joystick...")
print("\nKeyboard Controls:")
print("A = Previous")
print("D = Next")
print("Enter = Select")
print("\nJoystick Controls:")
print("UP = Previous")
print("DOWN = Next")
print("MIDDLE = Select")
print("LEFT = Back")
print("RIGHT = Next")

while True:
    # Test Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            print(f"\nKeyboard KEYDOWN: Key={pygame.key.name(event.key)}, Code={event.key}")
            if event.key == config.KEY_PREV:
                print("Action: PREV")
            elif event.key == config.KEY_NEXT:
                print("Action: NEXT")
            elif event.key == config.KEY_SELECT:
                print("Action: SELECT")
        if event.type == pygame.KEYUP:
            print(f"\nKeyboard KEYUP: Key={pygame.key.name(event.key)}, Code={event.key}")
            if event.key == config.KEY_PREV:
                print("Action: PREV")
            elif event.key == config.KEY_NEXT:
                print("Action: NEXT")
            elif event.key == config.KEY_SELECT:
                print("Action: SELECT")

    # Test Sense HAT joystick events
    events = sense.stick.get_events()
    if events:
        for event in events:
            print(f"\nJoystick Event: Direction={event.direction}, Action={event.action}")
            if event.action == ACTION_PRESSED:
                if event.direction == "up":
                    print("Action: PREV")
                elif event.direction == "down":
                    print("Action: NEXT")
                elif event.direction == "middle":
                    print("Action: SELECT")
                elif event.direction == "left":
                    print("Action: BACK")
                elif event.direction == "right":
                    print("Action: NEXT")
            elif event.action == ACTION_RELEASED:
                if event.direction == "up":
                    print("Action: PREV")
                elif event.direction == "down":
                    print("Action: NEXT")
                elif event.direction == "middle":
                    print("Action: SELECT")
                elif event.direction == "left":
                    print("Action: BACK")
                elif event.direction == "right":
                    print("Action: NEXT")

    pygame.time.Clock().tick(30) 