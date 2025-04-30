# --- games/pong.py ---
# Simple 1-Player Pong game logic

import pygame
import random
import logging

logger = logging.getLogger(__name__)

# --- Game Constants ---
# Note: These are relative to the game screen/surface, not the main app screen
PADDLE_WIDTH = 5
PADDLE_HEIGHT = 40
BALL_SIZE = 5
PADDLE_SPEED = 4
INITIAL_BALL_SPEED_X = 3
INITIAL_BALL_SPEED_Y = 3
SCORE_LIMIT = 7 # Set score limit to 7

class PongGame:
    """Manages the state and logic for the 1-player Pong game."""

    def __init__(self, width, height, config):
        """
        Initializes the Pong game.

        Args:
            width (int): Width of the game area.
            height (int): Height of the game area.
            config (module): Application configuration for key bindings, colors.
        """
        self.width = width
        self.height = height
        self.config = config
        self.font = None # Will be set in draw method from passed fonts

        # Game objects
        self.paddle_y = self.height // 2 - PADDLE_HEIGHT // 2
        self.ball_x = self.width // 2 - BALL_SIZE // 2
        self.ball_y = self.height // 2 - BALL_SIZE // 2
        self.ball_vel_x = INITIAL_BALL_SPEED_X * random.choice((1, -1))
        self.ball_vel_y = INITIAL_BALL_SPEED_Y * random.choice((1, -1))

        # Game state
        self.score = 0
        self.game_over = False
        self.winner_message = ""

        logger.info(f"Pong game initialized with area {width}x{height}")

    def reset_ball(self):
        """Resets the ball to the center with a random direction."""
        self.ball_x = self.width // 2 - BALL_SIZE // 2
        self.ball_y = self.height // 2 - BALL_SIZE // 2
        self.ball_vel_x = INITIAL_BALL_SPEED_X * random.choice((1, -1))
        self.ball_vel_y = INITIAL_BALL_SPEED_Y * random.choice((1, -1))
        logger.debug("Pong ball reset")

    def handle_input(self, key_code):
        """
        Processes player input (raw key codes).
        Currently does nothing for Pong as movement is handled in update.

        Args:
            key_code (int): The pygame key code (e.g., pygame.K_a, pygame.K_d).
        """
        if self.game_over:
            return # No input if game over

        # Example: Could use KEY_SELECT to restart game after game over
        # if self.game_over and key_code == self.config.KEY_SELECT:
        #     self.game_over = False
        #     self.score = 0
        #     self.reset_ball()
        #     logger.info("Pong game restarted")

        # Paddle movement is now handled in the update method based on keys_held
        pass

        # if key_code == self.config.KEY_PREV: # Check against configured key for UP
        #    ...
        # elif key_code == self.config.KEY_NEXT: # Check against configured key for DOWN
        #    ...

    def update(self, keys_held):
        """Updates the game state (ball movement, collisions, paddle movement)."""
        if self.game_over:
            return

        # --- Paddle Movement based on keys_held --- #
        if self.config.KEY_PREV in keys_held:
            self.paddle_y -= PADDLE_SPEED
            if self.paddle_y < 0:
                self.paddle_y = 0
            # logger.debug(f"Pong paddle moving Up to {self.paddle_y}") # Too spammy
        elif self.config.KEY_NEXT in keys_held:
            self.paddle_y += PADDLE_SPEED
            if self.paddle_y > self.height - PADDLE_HEIGHT:
                self.paddle_y = self.height - PADDLE_HEIGHT
            # logger.debug(f"Pong paddle moving Down to {self.paddle_y}") # Too spammy

        # --- Ball Movement --- #
        self.ball_x += self.ball_vel_x
        self.ball_y += self.ball_vel_y

        # Ball collision with top/bottom walls
        if self.ball_y <= 0 or self.ball_y >= self.height - BALL_SIZE:
            self.ball_vel_y *= -1
            self.ball_y = max(0, min(self.ball_y, self.height - BALL_SIZE)) # Clamp position
            logger.debug("Pong ball hit top/bottom wall")

        # Ball collision with right wall (opponent side - for score)
        if self.ball_x >= self.width - BALL_SIZE:
            logger.debug("Pong ball hit right wall - Player scores!")
            self.score += 1 # Increment score
            if self.score >= SCORE_LIMIT:
                self.game_over = True
                self.winner_message = "YOU WIN!"
                logger.info("Pong game over - Player wins!")
            else:
                self.reset_ball() # Reset ball after scoring
                # Optionally add a small delay here before ball moves again

        # Ball collision with left wall (player side - game over)
        if self.ball_x <= 0:
             self.game_over = True
             self.winner_message = "GAME OVER"
             logger.info("Pong game over - Ball missed!")
             return # Stop processing on game over

        # Ball collision with paddle
        paddle_rect = pygame.Rect(0, self.paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE)

        if ball_rect.colliderect(paddle_rect):
            if self.ball_vel_x < 0: # Only bounce if moving towards paddle
                self.ball_vel_x *= -1.1 # Increase speed slightly on bounce
                # Adjust Y velocity based on where it hit the paddle
                hit_pos = (self.ball_y + BALL_SIZE/2) - (self.paddle_y + PADDLE_HEIGHT/2)
                self.ball_vel_y += hit_pos * 0.1 # Add some vertical deflection
                # Prevent ball from getting stuck inside paddle
                self.ball_x = PADDLE_WIDTH
                logger.debug("Pong ball hit player paddle")

    def draw(self, screen, fonts, config):
        """Draws the current state of the Pong game."""
        # Use a font passed from the main app
        if not self.font:
            self.font = fonts.get('medium', fonts.get('default'))

        # Clear screen (the display manager should handle overall clearing)
        # screen.fill(config.COLOR_BACKGROUND)

        # Draw center line (optional)
        line_color = config.COLOR_GRAPH_BORDER
        for y in range(0, self.height, 10):
            pygame.draw.line(screen, line_color, (self.width // 2, y), (self.width // 2, y + 5), 1)

        # Draw paddle
        paddle_rect = pygame.Rect(0, int(self.paddle_y), PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, config.COLOR_FOREGROUND, paddle_rect)

        # Draw ball
        ball_rect = pygame.Rect(int(self.ball_x), int(self.ball_y), BALL_SIZE, BALL_SIZE)
        pygame.draw.rect(screen, config.COLOR_FOREGROUND, ball_rect)

        # Draw score
        score_text = f"Score: {self.score}"
        score_surf = self.font.render(score_text, True, config.COLOR_ACCENT)
        # Position score near the top-right, adjusting for text width
        score_pos = (self.width - score_surf.get_width() - 10, 10)
        screen.blit(score_surf, score_pos)

        # Draw Game Over / Winner message
        if self.game_over:
            large_font = fonts.get('large', self.font)
            msg_surf = large_font.render(self.winner_message, True, config.COLOR_ALERT)
            msg_rect = msg_surf.get_rect(center=(self.width // 2, self.height // 2))
            screen.blit(msg_surf, msg_rect)

            # Add hint to go back
            key_prev_name = pygame.key.name(config.KEY_PREV).upper()
            hint = f"(Hold {key_prev_name}=Back)"
            small_font = fonts.get('small', self.font)
            hint_surf = small_font.render(hint, True, config.COLOR_FOREGROUND)
            hint_rect = hint_surf.get_rect(center=(self.width // 2, msg_rect.bottom + 20))
            screen.blit(hint_surf, hint_rect) 