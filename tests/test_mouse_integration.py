#!/usr/bin/env python3
"""
Test script to verify mouse controls integration with the tricorder application.
This tests the input processing pipeline without running the full application.
"""

import sys
import os
import pygame
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from input.input_handler import process_input
from models.input_manager import InputManager

def test_mouse_input_processing():
    """Test that mouse events are properly processed by the input handler."""
    print("Testing mouse input processing...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    
    # Create input manager
    input_manager = InputManager(config)
    
    # Test mouse button down events
    test_events = [
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=config.MOUSE_LEFT, pos=(50, 50)),
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=config.MOUSE_RIGHT, pos=(50, 50)),
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=config.MOUSE_MIDDLE, pos=(50, 50)),
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=config.MOUSE_LEFT, pos=(50, 50)),
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=config.MOUSE_RIGHT, pos=(50, 50)),
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=config.MOUSE_MIDDLE, pos=(50, 50)),
    ]
    
    # Process events
    results = process_input(test_events, config)
    
    print(f"Processed {len(results)} input events")
    
    # Verify results
    expected_actions = [
        config.INPUT_ACTION_PREV,    # Left down
        config.INPUT_ACTION_NEXT,    # Right down
        config.INPUT_ACTION_SELECT,  # Middle down
        config.INPUT_ACTION_PREV,    # Left up
        config.INPUT_ACTION_NEXT,    # Right up
        config.INPUT_ACTION_SELECT,  # Middle up
    ]
    
    success = True
    for i, result in enumerate(results):
        if result['type'] in ['MOUSEDOWN', 'MOUSEUP']:
            expected_action = expected_actions[i]
            actual_action = result.get('action')
            if actual_action == expected_action:
                print(f"[OK] Event {i+1}: {result['type']} -> {actual_action}")
            else:
                print(f"[FAIL] Event {i+1}: Expected {expected_action}, got {actual_action}")
                success = False
        else:
            print(f"[OK] Event {i+1}: {result['type']} (non-mouse event)")
    
    return success

def test_mouse_long_press():
    """Test mouse long press detection."""
    print("\nTesting mouse long press detection...")
    
    input_manager = InputManager(config)
    
    # Simulate mouse button press
    input_manager.handle_mousedown(config.MOUSE_LEFT)
    
    # Wait for long press duration
    time.sleep(config.INPUT_LONG_PRESS_DURATION + 0.1)
    
    # Check if long press is detected
    is_long_press = input_manager.check_mouse_left_long_press()
    
    if is_long_press:
        print("[OK] Mouse left long press detected correctly")
    else:
        print("[FAIL] Mouse left long press not detected")
        return False
    
    # Reset and test short press
    input_manager.reset_mouse_left_timer()
    input_manager.handle_mousedown(config.MOUSE_LEFT)
    time.sleep(0.5)  # Short press
    input_manager.handle_mouseup(config.MOUSE_LEFT)
    
    is_long_press = input_manager.check_mouse_left_long_press()
    
    if not is_long_press:
        print("[OK] Mouse left short press handled correctly")
    else:
        print("[FAIL] Mouse left short press incorrectly detected as long press")
        return False
    
    return True

def test_mouse_action_mapping():
    """Test that mouse buttons are correctly mapped to actions."""
    print("\nTesting mouse action mapping...")
    
    # Test the mapping from config
    expected_mappings = {
        config.MOUSE_LEFT: config.INPUT_ACTION_PREV,
        config.MOUSE_RIGHT: config.INPUT_ACTION_NEXT,
        config.MOUSE_MIDDLE: config.INPUT_ACTION_SELECT,
    }
    
    success = True
    for button, expected_action in expected_mappings.items():
        actual_action = config.MOUSE_ACTION_MAP.get(button)
        if actual_action == expected_action:
            print(f"[OK] Mouse button {button} -> {actual_action}")
        else:
            print(f"[FAIL] Mouse button {button}: Expected {expected_action}, got {actual_action}")
            success = False
    
    return success

def main():
    """Run all mouse control tests."""
    print("Mouse Controls Integration Test")
    print("=" * 40)
    
    tests = [
        test_mouse_action_mapping,
        test_mouse_input_processing,
        test_mouse_long_press,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("[OK] Test passed")
            else:
                print("[FAIL] Test failed")
        except Exception as e:
            print(f"[FAIL] Test failed with exception: {e}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All mouse control tests passed!")
        return True
    else:
        print("[FAILURE] Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
