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
        self.paused = False # Add paused state
        self.pause_menu_options = ["Resume", "Quit to Menu"]
        self.pause_menu_selected_index = 0

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

    def move_paddle_up(self):
        """Moves the player paddle up."""
        if not self.game_over and not self.paused:
            self.paddle_y -= PADDLE_SPEED
            if self.paddle_y < 0:
                self.paddle_y = 0

    def move_paddle_down(self):
        """Moves the player paddle down."""
        if not self.game_over and not self.paused:
            self.paddle_y += PADDLE_SPEED
            if self.paddle_y > self.height - PADDLE_HEIGHT:
                self.paddle_y = self.height - PADDLE_HEIGHT

    def toggle_pause(self):
        """Toggles the paused state of the game."""
        self.paused = not self.paused
        if self.paused:
            self.pause_menu_selected_index = 0 
        logger.info(f"Pong game {'paused' if self.paused else 'resumed'}.")

    def navigate_pause_menu_up(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index - 1 + len(self.pause_menu_options)) % len(self.pause_menu_options)
            logger.debug(f"Pong pause menu UP to index {self.pause_menu_selected_index}: '{self.pause_menu_options[self.pause_menu_selected_index]}'")

    def navigate_pause_menu_down(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index + 1) % len(self.pause_menu_options)
            logger.debug(f"Pong pause menu DOWN to index {self.pause_menu_selected_index}: '{self.pause_menu_options[self.pause_menu_selected_index]}'")

    def select_pause_menu_option(self):
        if self.paused and self.pause_menu_options and self.pause_menu_selected_index < len(self.pause_menu_options):
            selected_action_text = self.pause_menu_options[self.pause_menu_selected_index]
            logger.info(f"Pong pause menu SELECTED: {selected_action_text}")
            if selected_action_text == "Resume":
                self.toggle_pause() 
                return "RESUME_GAME"
            elif selected_action_text == "Quit to Menu":
                return "QUIT_TO_MENU"
        return None

    def update(self, keys_held):
        """Updates the game state (ball movement, collisions, paddle movement)."""
        if self.game_over or self.paused: # Check for pause state here
            return

        # Paddle movement is now handled by explicit move_paddle_up/down() calls from app_state

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

        # Draw PAUSED message and controls if paused (and not game over)
        if self.paused and not self.game_over:
            medium_font = fonts.get('medium', self.font)
            small_font = fonts.get('small', self.font)
            
            overlay_alpha = 180
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            screen.blit(overlay, (0, 0))

            paused_title_surf = medium_font.render("PAUSED", True, config.COLOR_ALERT)
            paused_title_rect = paused_title_surf.get_rect(center=(self.width // 2, self.height // 3))
            screen.blit(paused_title_surf, paused_title_rect)

            menu_item_y_start = paused_title_rect.bottom + 40
            for i, option_text in enumerate(self.pause_menu_options):
                color = config.COLOR_ACCENT if i == self.pause_menu_selected_index else config.COLOR_FOREGROUND
                option_surf = small_font.render(option_text, True, color)
                option_rect = option_surf.get_rect(center=(self.width // 2, menu_item_y_start + i * (small_font.get_height() + 15)))
                screen.blit(option_surf, option_rect)

        # Draw Game Over / Winner message
        elif self.game_over: # Use elif to avoid drawing over pause message
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