# --- games/breakout.py ---
# Classic Breakout game logic for the tricorder

import pygame
import random
import logging

logger = logging.getLogger(__name__)

# --- Game Constants ---
PADDLE_WIDTH = 60  # Wider paddle for Breakout
PADDLE_HEIGHT = 8  # Thinner paddle
BALL_SIZE = 6
PADDLE_SPEED = 6
INITIAL_BALL_SPEED_X = 3
INITIAL_BALL_SPEED_Y = -3  # Start moving up
PADDLE_Y_OFFSET = 20  # Distance from bottom

# Brick constants
BRICK_ROWS = 6
BRICKS_PER_ROW = 8
BRICK_WIDTH = 35
BRICK_HEIGHT = 12
BRICK_SPACING = 4
BRICK_TOP_MARGIN = 30

class BreakoutGame:
    """Manages the state and logic for the Breakout game."""

    def __init__(self, width, height, config):
        """
        Initializes the Breakout game.

        Args:
            width (int): Width of the game area.
            height (int): Height of the game area.
            config (module): Application configuration for key bindings, colors.
        """
        self.width = width
        self.height = height
        self.config = config
        self.font = None  # Will be set in draw method from passed fonts

        # Game objects
        self.paddle_x = self.width // 2 - PADDLE_WIDTH // 2
        self.paddle_y = self.height - PADDLE_Y_OFFSET
        
        self.ball_x = self.width // 2 - BALL_SIZE // 2
        self.ball_y = self.height // 2
        self.ball_vel_x = INITIAL_BALL_SPEED_X * random.choice((1, -1))
        self.ball_vel_y = INITIAL_BALL_SPEED_Y

        # Initialize bricks
        self.bricks = self._create_bricks()
        
        # Game state
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.winner_message = ""
        self.paused = False
        self.pause_menu_options = ["Resume", "Quit to Menu"]
        self.pause_menu_selected_index = 0
        
        # Ball release state
        self.ball_on_paddle = True  # Start with ball on paddle

        logger.info(f"Breakout game initialized with area {width}x{height}")

    def _create_bricks(self):
        """Create the brick layout."""
        bricks = []
        
        # Calculate starting position to center the bricks
        total_width = BRICKS_PER_ROW * BRICK_WIDTH + (BRICKS_PER_ROW - 1) * BRICK_SPACING
        start_x = (self.width - total_width) // 2
        
        for row in range(BRICK_ROWS):
            for col in range(BRICKS_PER_ROW):
                x = start_x + col * (BRICK_WIDTH + BRICK_SPACING)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_SPACING)
                
                # Different colors for different rows (optional enhancement)
                color_index = row % 3  # 3 different colors
                bricks.append({
                    'x': x,
                    'y': y,
                    'width': BRICK_WIDTH,
                    'height': BRICK_HEIGHT,
                    'color_index': color_index,
                    'active': True
                })
        
        return bricks

    def reset_ball(self):
        """Reset ball to paddle position."""
        self.ball_x = self.paddle_x + PADDLE_WIDTH // 2 - BALL_SIZE // 2
        self.ball_y = self.paddle_y - BALL_SIZE - 2
        self.ball_vel_x = INITIAL_BALL_SPEED_X * random.choice((1, -1))
        self.ball_vel_y = INITIAL_BALL_SPEED_Y
        self.ball_on_paddle = True
        logger.debug("Breakout ball reset to paddle")

    def move_paddle_left(self):
        """Move the paddle left."""
        if not self.game_over and not self.paused:
            self.paddle_x -= PADDLE_SPEED
            if self.paddle_x < 0:
                self.paddle_x = 0
            
            # Move ball with paddle if attached
            if self.ball_on_paddle:
                self.ball_x = self.paddle_x + PADDLE_WIDTH // 2 - BALL_SIZE // 2

    def move_paddle_right(self):
        """Move the paddle right."""
        if not self.game_over and not self.paused:
            self.paddle_x += PADDLE_SPEED
            if self.paddle_x > self.width - PADDLE_WIDTH:
                self.paddle_x = self.width - PADDLE_WIDTH
            
            # Move ball with paddle if attached
            if self.ball_on_paddle:
                self.ball_x = self.paddle_x + PADDLE_WIDTH // 2 - BALL_SIZE // 2

    def launch_ball(self):
        """Launch the ball from the paddle."""
        if self.ball_on_paddle and not self.paused and not self.game_over:
            self.ball_on_paddle = False
            logger.debug("Breakout ball launched")

    def toggle_pause(self):
        """Toggle the paused state of the game."""
        self.paused = not self.paused
        if self.paused:
            self.pause_menu_selected_index = 0
        logger.info(f"Breakout game {'paused' if self.paused else 'resumed'}.")

    def navigate_pause_menu_up(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index - 1 + len(self.pause_menu_options)) % len(self.pause_menu_options)
            logger.debug(f"Breakout pause menu UP to index {self.pause_menu_selected_index}")

    def navigate_pause_menu_down(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index + 1) % len(self.pause_menu_options)
            logger.debug(f"Breakout pause menu DOWN to index {self.pause_menu_selected_index}")

    def select_pause_menu_option(self):
        if self.paused and self.pause_menu_options and self.pause_menu_selected_index < len(self.pause_menu_options):
            selected_action_text = self.pause_menu_options[self.pause_menu_selected_index]
            logger.info(f"Breakout pause menu SELECTED: {selected_action_text}")
            if selected_action_text == "Resume":
                self.toggle_pause()
                return "RESUME_GAME"
            elif selected_action_text == "Quit to Menu":
                return "QUIT_TO_MENU"
        return None

    def update(self, keys_held):
        """Update the game state."""
        if self.game_over or self.paused:
            return

        # Don't move ball if it's on paddle
        if self.ball_on_paddle:
            return

        # Ball movement
        self.ball_x += self.ball_vel_x
        self.ball_y += self.ball_vel_y

        # Ball collision with walls
        if self.ball_x <= 0 or self.ball_x >= self.width - BALL_SIZE:
            self.ball_vel_x *= -1
            self.ball_x = max(0, min(self.ball_x, self.width - BALL_SIZE))

        if self.ball_y <= 0:
            self.ball_vel_y *= -1
            self.ball_y = 0

        # Ball collision with bottom (lose life)
        if self.ball_y >= self.height:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.winner_message = "GAME OVER!"
                logger.info("Breakout game over - no lives left")
            else:
                self.reset_ball()
            return

        # Ball collision with paddle
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE)

        if ball_rect.colliderect(paddle_rect) and self.ball_vel_y > 0:
            # Calculate hit position for angle variation
            hit_pos = (self.ball_x + BALL_SIZE/2) - (self.paddle_x + PADDLE_WIDTH/2)
            hit_pos_normalized = hit_pos / (PADDLE_WIDTH/2)  # -1 to 1
            
            self.ball_vel_y = -abs(self.ball_vel_y)
            self.ball_vel_x += hit_pos_normalized * 2  # Add angle variation
            
            # Limit ball speed
            max_speed = 6
            if abs(self.ball_vel_x) > max_speed:
                self.ball_vel_x = max_speed if self.ball_vel_x > 0 else -max_speed
                
            self.ball_y = self.paddle_y - BALL_SIZE
            logger.debug("Breakout ball hit paddle")

        # Ball collision with bricks
        for brick in self.bricks:
            if not brick['active']:
                continue
                
            brick_rect = pygame.Rect(brick['x'], brick['y'], brick['width'], brick['height'])
            if ball_rect.colliderect(brick_rect):
                brick['active'] = False
                self.score += 10
                
                # Simple bounce logic - reverse Y direction
                self.ball_vel_y *= -1
                
                logger.debug(f"Breakout brick destroyed, score: {self.score}")
                break

        # Check win condition
        active_bricks = sum(1 for brick in self.bricks if brick['active'])
        if active_bricks == 0:
            self.game_over = True
            self.winner_message = "YOU WIN!"
            logger.info("Breakout game won - all bricks destroyed")

    def draw(self, screen, fonts, config_module):
        """Draw the current state of the Breakout game."""
        if not self.font:
            self.font = fonts.get('medium', fonts.get('default'))

        # Draw bricks
        brick_colors = [
            config_module.COLOR_ACCENT,     # Row color 1
            config_module.COLOR_FOREGROUND, # Row color 2  
            config_module.COLOR_GRAPH_BORDER # Row color 3
        ]
        
        for brick in self.bricks:
            if brick['active']:
                color = brick_colors[brick['color_index']]
                brick_rect = pygame.Rect(brick['x'], brick['y'], brick['width'], brick['height'])
                pygame.draw.rect(screen, color, brick_rect)
                pygame.draw.rect(screen, config_module.COLOR_BACKGROUND, brick_rect, 1)

        # Draw paddle
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, config_module.COLOR_FOREGROUND, paddle_rect)

        # Draw ball
        ball_rect = pygame.Rect(int(self.ball_x), int(self.ball_y), BALL_SIZE, BALL_SIZE)
        pygame.draw.rect(screen, config_module.COLOR_ACCENT, ball_rect)

        # Draw score and lives
        score_text = f"Score: {self.score}  Lives: {self.lives}"
        score_surf = self.font.render(score_text, True, config_module.COLOR_ACCENT)
        screen.blit(score_surf, (10, 10))

        # Show launch instruction if ball is on paddle
        if self.ball_on_paddle and not self.paused and not self.game_over:
            launch_text = "Press ENTER to launch ball"
            launch_surf = self.font.render(launch_text, True, config_module.COLOR_FOREGROUND)
            text_x = self.width // 2 - launch_surf.get_width() // 2
            text_y = self.height - 50
            screen.blit(launch_surf, (text_x, text_y))

        # Draw game over message
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(128)
            overlay.fill(config_module.COLOR_BACKGROUND)
            screen.blit(overlay, (0, 0))

            game_over_text = self.font.render(self.winner_message, True, config_module.COLOR_ACCENT)
            game_over_pos = (self.width // 2 - game_over_text.get_width() // 2, 
                           self.height // 2 - game_over_text.get_height() // 2)
            screen.blit(game_over_text, game_over_pos)

        # Draw pause menu
        if self.paused:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(128)
            overlay.fill(config_module.COLOR_BACKGROUND)
            screen.blit(overlay, (0, 0))

            menu_y = self.height // 2 - (len(self.pause_menu_options) * 30) // 2
            for i, option in enumerate(self.pause_menu_options):
                color = config_module.COLOR_ACCENT if i == self.pause_menu_selected_index else config_module.COLOR_FOREGROUND
                text = self.font.render(option, True, color)
                text_pos = (self.width // 2 - text.get_width() // 2, menu_y + i * 30)
                screen.blit(text, text_pos) 