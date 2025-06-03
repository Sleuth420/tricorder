#!/usr/bin/env python3
"""
Script to create preview images for games in the secret menu
Optimized for 320x240 display with tricorder color scheme
"""

import pygame
import os

def create_game_previews():
    """Create preview images for all games"""
    
    # Initialize pygame
    pygame.init()
    
    # Preview image size (64x48 to maintain 4:3 aspect ratio like 320x240)
    preview_size = (64, 48)
    
    # Tricorder theme colors
    BLACK = (0, 0, 0)
    SICKBAY_GREEN = (0, 255, 70)
    ENGINEERING_GOLD = (255, 200, 0)
    RED_ALERT = (255, 0, 0)
    DARK_GREY = (40, 40, 40)
    WHITE = (255, 255, 255)
    
    # Ensure the assets/images directory exists
    os.makedirs("assets/images", exist_ok=True)
    
    # Create Pong preview
    print("Creating Pong preview...")
    pong_surface = pygame.Surface(preview_size)
    pong_surface.fill(BLACK)
    
    # Draw paddles
    paddle_width = 3
    paddle_height = 16
    left_paddle = pygame.Rect(2, (preview_size[1] - paddle_height) // 2, paddle_width, paddle_height)
    right_paddle = pygame.Rect(preview_size[0] - paddle_width - 2, (preview_size[1] - paddle_height) // 2, paddle_width, paddle_height)
    pygame.draw.rect(pong_surface, SICKBAY_GREEN, left_paddle)
    pygame.draw.rect(pong_surface, SICKBAY_GREEN, right_paddle)
    
    # Draw center line (dashed)
    for y in range(0, preview_size[1], 4):
        pygame.draw.line(pong_surface, SICKBAY_GREEN, (preview_size[0] // 2, y), (preview_size[0] // 2, min(y + 2, preview_size[1])), 1)
    
    # Draw ball
    ball_size = 3
    ball_x = preview_size[0] // 2 + 8
    ball_y = preview_size[1] // 2 - 4
    ball_rect = pygame.Rect(ball_x, ball_y, ball_size, ball_size)
    pygame.draw.rect(pong_surface, ENGINEERING_GOLD, ball_rect)
    
    pygame.image.save(pong_surface, "assets/images/game_pong_preview.png")
    
    # Create Breakout preview
    print("Creating Breakout preview...")
    breakout_surface = pygame.Surface(preview_size)
    breakout_surface.fill(BLACK)
    
    # Draw bricks (multiple colors)
    brick_width = 8
    brick_height = 3
    brick_colors = [RED_ALERT, ENGINEERING_GOLD, SICKBAY_GREEN, WHITE]
    
    for row in range(4):
        for col in range(7):
            if col * brick_width + brick_width <= preview_size[0]:  # Ensure bricks fit
                brick_x = col * brick_width + 2
                brick_y = row * (brick_height + 1) + 4
                brick_rect = pygame.Rect(brick_x, brick_y, brick_width - 1, brick_height)
                pygame.draw.rect(breakout_surface, brick_colors[row % len(brick_colors)], brick_rect)
    
    # Draw paddle
    paddle_width = 12
    paddle_height = 3
    paddle_x = (preview_size[0] - paddle_width) // 2
    paddle_y = preview_size[1] - 8
    paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
    pygame.draw.rect(breakout_surface, SICKBAY_GREEN, paddle_rect)
    
    # Draw ball
    ball_size = 2
    ball_x = preview_size[0] // 2 - 8
    ball_y = preview_size[1] - 16
    ball_rect = pygame.Rect(ball_x, ball_y, ball_size, ball_size)
    pygame.draw.rect(breakout_surface, ENGINEERING_GOLD, ball_rect)
    
    pygame.image.save(breakout_surface, "assets/images/game_breakout_preview.png")
    
    # Create Snake preview
    print("Creating Snake preview...")
    snake_surface = pygame.Surface(preview_size)
    snake_surface.fill(BLACK)
    
    # Draw snake body (L-shaped)
    segment_size = 4
    snake_segments = [
        (20, 24), (24, 24), (28, 24), (32, 24),  # horizontal part
        (32, 20), (32, 16)  # vertical part (head)
    ]
    
    for i, (x, y) in enumerate(snake_segments):
        color = ENGINEERING_GOLD if i == len(snake_segments) - 1 else SICKBAY_GREEN  # Head is gold
        segment_rect = pygame.Rect(x, y, segment_size, segment_size)
        pygame.draw.rect(snake_surface, color, segment_rect)
    
    # Draw food
    food_size = 4
    food_x = 44
    food_y = 32
    food_rect = pygame.Rect(food_x, food_y, food_size, food_size)
    pygame.draw.rect(snake_surface, RED_ALERT, food_rect)
    
    pygame.image.save(snake_surface, "assets/images/game_snake_preview.png")
    
    # Create Tetris preview (placeholder)
    print("Creating Tetris preview...")
    tetris_surface = pygame.Surface(preview_size)
    tetris_surface.fill(BLACK)
    
    # Draw some tetris blocks
    block_size = 3
    tetris_colors = [SICKBAY_GREEN, ENGINEERING_GOLD, RED_ALERT, WHITE]
    
    # Draw some L and T shaped pieces
    tetris_blocks = [
        # L piece
        [(20, 32), (20, 35), (20, 38), (23, 38)],
        # T piece  
        [(30, 32), (27, 35), (30, 35), (33, 35)],
        # Some bottom blocks
        [(15, 41), (18, 41), (21, 41), (24, 41), (27, 41), (30, 41)]
    ]
    
    for piece_idx, piece in enumerate(tetris_blocks):
        color = tetris_colors[piece_idx % len(tetris_colors)]
        for x, y in piece:
            if x + block_size <= preview_size[0] and y + block_size <= preview_size[1]:
                block_rect = pygame.Rect(x, y, block_size, block_size)
                pygame.draw.rect(tetris_surface, color, block_rect)
    
    pygame.image.save(tetris_surface, "assets/images/game_tetris_preview.png")
    
    pygame.quit()
    print("All game preview images created successfully!")

if __name__ == "__main__":
    create_game_previews() 