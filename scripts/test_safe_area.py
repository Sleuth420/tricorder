#!/usr/bin/env python3
# --- scripts/test_safe_area.py ---
# Test script for safe area visualization and adjustment

import sys
import os
import pygame
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import display
from utils.ui_scaler import UIScaler
from utils.safe_area_helper import draw_safe_area_overlay, draw_safe_area_info, test_safe_area_settings

def main():
    """Test safe area visualization."""
    print("Safe Area Test Script")
    print("====================")
    
    # Initialize pygame
    pygame.init()
    
    # Create test display
    screen = pygame.display.set_mode((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
    pygame.display.set_caption("Safe Area Test")
    
    # Create UI scaler
    ui_scaler = UIScaler(display.SCREEN_WIDTH, display.SCREEN_HEIGHT, display)
    
    # Load fonts
    try:
        fonts = {
            'small': pygame.font.Font(None, 16),
            'medium': pygame.font.Font(None, 20),
            'large': pygame.font.Font(None, 24)
        }
    except:
        fonts = {
            'small': pygame.font.SysFont(None, 16),
            'medium': pygame.font.SysFont(None, 20),
            'large': pygame.font.SysFont(None, 24)
        }
    
    # Test safe area settings
    print(f"Safe area enabled: {ui_scaler.safe_area_enabled}")
    if ui_scaler.safe_area_enabled:
        safe_rect = ui_scaler.get_safe_area_rect()
        margins = ui_scaler.get_safe_area_margins()
        print(f"Safe area rect: {safe_rect}")
        print(f"Margins: {margins}")
        
        # Test points
        test_results = test_safe_area_settings(ui_scaler)
        print("Test results:")
        for point, in_safe in test_results["test_points"].items():
            print(f"  {point}: {'✓' if in_safe else '✗'}")
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    show_overlay = True
    show_info = True
    
    print("\nControls:")
    print("  SPACE - Toggle safe area overlay")
    print("  I - Toggle info display")
    print("  ESC - Exit")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    show_overlay = not show_overlay
                    print(f"Safe area overlay: {'ON' if show_overlay else 'OFF'}")
                elif event.key == pygame.K_i:
                    show_info = not show_info
                    print(f"Info display: {'ON' if show_info else 'OFF'}")
        
        # Clear screen
        screen.fill((0, 0, 0))  # Black background
        
        # Draw test content
        # Draw border around entire screen
        pygame.draw.rect(screen, (255, 255, 255), (0, 0, display.SCREEN_WIDTH, display.SCREEN_HEIGHT), 2)
        
        # Draw test rectangles in corners
        corner_size = 20
        corners = [
            (0, 0),  # Top-left
            (display.SCREEN_WIDTH - corner_size, 0),  # Top-right
            (0, display.SCREEN_HEIGHT - corner_size),  # Bottom-left
            (display.SCREEN_WIDTH - corner_size, display.SCREEN_HEIGHT - corner_size)  # Bottom-right
        ]
        
        for i, (x, y) in enumerate(corners):
            color = (255, 0, 0) if ui_scaler.is_point_in_safe_area(x + corner_size//2, y + corner_size//2) else (0, 255, 0)
            pygame.draw.rect(screen, color, (x, y, corner_size, corner_size))
        
        # Draw center content
        center_x = display.SCREEN_WIDTH // 2
        center_y = display.SCREEN_HEIGHT // 2
        center_color = (0, 0, 255) if ui_scaler.is_point_in_safe_area(center_x, center_y) else (255, 255, 0)
        pygame.draw.circle(screen, center_color, (center_x, center_y), 15)
        
        # Draw safe area overlay if enabled
        if show_overlay and ui_scaler.safe_area_enabled:
            draw_safe_area_overlay(screen, ui_scaler, display, alpha=80)
        
        # Draw info if enabled
        if show_info and ui_scaler.safe_area_enabled:
            draw_safe_area_info(screen, ui_scaler, fonts, display)
        
        # Draw instructions
        instruction_text = "SPACE: Toggle overlay | I: Toggle info | ESC: Exit"
        text_surface = fonts['small'].render(instruction_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, display.SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print("\nTest completed.")

if __name__ == "__main__":
    main()
