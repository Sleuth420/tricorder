# --- games/pong.py ---
# Simple 1-Player Pong game logic

import pygame
import random
import logging

logger = logging.getLogger(__name__)

# --- Game Constants ---
# Note: These are relative to the game screen/surface, not the main app screen
PADDLE_WIDTH = 8  # Increased paddle width for better visibility
PADDLE_HEIGHT = 60  # Increased paddle height for better gameplay
BALL_SIZE = 8  # Increased ball size for better visibility
PADDLE_SPEED = 9  # Faster paddle for better responsiveness
INITIAL_BALL_SPEED_X = 4  # Slightly increased for better gameplay
INITIAL_BALL_SPEED_Y = 4  # Slightly increased for better gameplay
SCORE_LIMIT = 7 # Set score limit to 7
AI_PADDLE_SPEED = 4 # Increased AI speed to match player

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
        self.paddle_y = self.height // 2 - PADDLE_HEIGHT // 2 # Player paddle (left)
        self.paddle_ai_y = self.height // 2 - PADDLE_HEIGHT // 2 # AI paddle (right)
        
        self.ball_x = self.width // 2 - BALL_SIZE // 2
        self.ball_y = self.height // 2 - BALL_SIZE // 2
        self.ball_vel_x = INITIAL_BALL_SPEED_X * random.choice((1, -1))
        self.ball_vel_y = INITIAL_BALL_SPEED_Y * random.choice((1, -1))

        # Game state
        self.score_player = 0
        self.score_ai = 0
        self.game_over = False
        self.winner_message = ""
        self.paused = False # Add paused state
        self.pause_menu_options = ["Resume", "Quit to Menu"]
        self.pause_menu_selected_index = 0

        logger.info(f"Pong game initialized with area {width}x{height}")

    def reset_ball(self, served_by_player=True):
        """Resets the ball to the center, optionally towards player or AI."""
        self.ball_x = self.width // 2 - BALL_SIZE // 2
        self.ball_y = self.height // 2 - BALL_SIZE // 2
        
        # Determine ball direction based on who scored or who is serving
        if served_by_player: # If player just scored or starts game
            self.ball_vel_x = INITIAL_BALL_SPEED_X 
        else: # If AI just scored
            self.ball_vel_x = -INITIAL_BALL_SPEED_X
            
        self.ball_vel_y = INITIAL_BALL_SPEED_Y * random.choice((1, -1))
        logger.debug(f"Pong ball reset, vel_x: {self.ball_vel_x}")

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

        # --- AI Paddle Movement ---
        ai_paddle_center = self.paddle_ai_y + PADDLE_HEIGHT / 2
        if self.ball_y + BALL_SIZE / 2 < ai_paddle_center - PADDLE_HEIGHT / 4: # Add some margin to reduce jitter
            self.paddle_ai_y -= AI_PADDLE_SPEED
        elif self.ball_y + BALL_SIZE / 2 > ai_paddle_center + PADDLE_HEIGHT / 4:
            self.paddle_ai_y += AI_PADDLE_SPEED
        
        # Clamp AI paddle to screen
        if self.paddle_ai_y < 0:
            self.paddle_ai_y = 0
        elif self.paddle_ai_y > self.height - PADDLE_HEIGHT:
            self.paddle_ai_y = self.height - PADDLE_HEIGHT


        # --- Ball Movement --- #
        self.ball_x += self.ball_vel_x
        self.ball_y += self.ball_vel_y

        # Ball collision with top/bottom walls
        if self.ball_y <= 0 or self.ball_y >= self.height - BALL_SIZE:
            self.ball_vel_y *= -1
            self.ball_y = max(0, min(self.ball_y, self.height - BALL_SIZE)) # Clamp position
            logger.debug("Pong ball hit top/bottom wall")

        # Ball collision with right wall (Player scores)
        if self.ball_x >= self.width - BALL_SIZE:
            logger.debug("Pong ball missed by AI - Player scores!")
            self.score_player += 1 
            if self.score_player >= SCORE_LIMIT:
                self.game_over = True
                self.winner_message = "PLAYER WINS!"
                logger.info("Pong game over - Player wins!")
            else:
                self.reset_ball(served_by_player=False) # AI serves next

        # Ball collision with left wall (AI scores)
        if self.ball_x <= 0:
            logger.debug("Pong ball missed by Player - AI scores!")
            self.score_ai += 1
            if self.score_ai >= SCORE_LIMIT:
                self.game_over = True
                self.winner_message = "AI WINS!"
                logger.info("Pong game over - AI wins!")
            else:
                self.reset_ball(served_by_player=True) # Player serves next
            return # Stop processing on score/game over for this side

        # Ball collision with player paddle (left)
        player_paddle_rect = pygame.Rect(0, self.paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE)

        if ball_rect.colliderect(player_paddle_rect):
            if self.ball_vel_x < 0: # Only bounce if moving towards paddle
                self.ball_vel_x *= -1.1 
                hit_pos = (self.ball_y + BALL_SIZE/2) - (self.paddle_y + PADDLE_HEIGHT/2)
                self.ball_vel_y += hit_pos * 0.1 
                self.ball_x = PADDLE_WIDTH 
                logger.debug("Pong ball hit player paddle")

        # Ball collision with AI paddle (right)
        ai_paddle_rect = pygame.Rect(self.width - PADDLE_WIDTH, self.paddle_ai_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        # Re-evaluate ball_rect in case its position was clamped or changed
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE) 

        if ball_rect.colliderect(ai_paddle_rect):
            if self.ball_vel_x > 0: # Only bounce if moving towards AI paddle
                self.ball_vel_x *= -1.1
                hit_pos = (self.ball_y + BALL_SIZE/2) - (self.paddle_ai_y + PADDLE_HEIGHT/2)
                self.ball_vel_y += hit_pos * 0.1
                self.ball_x = self.width - PADDLE_WIDTH - BALL_SIZE # Prevent sticking
                logger.debug("Pong ball hit AI paddle")

    def draw(self, screen, fonts, config_module):
        """Draws the current state of the Pong game."""
        # Use a font passed from the main app
        if not self.font:
            self.font = fonts.get('medium', fonts.get('default'))

        # Draw center line (dashed)
        line_color = config_module.COLOR_GRAPH_BORDER
        dash_length = 10
        gap_length = 5
        for y in range(0, self.height, dash_length + gap_length):
            pygame.draw.line(screen, line_color, 
                           (self.width // 2, y), 
                           (self.width // 2, min(y + dash_length, self.height)), 
                           2)  # Increased line width

        # Draw player paddle (left)
        paddle_rect = pygame.Rect(0, int(self.paddle_y), PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, config_module.COLOR_FOREGROUND, paddle_rect)

        # Draw AI paddle (right)
        ai_paddle_rect = pygame.Rect(self.width - PADDLE_WIDTH, int(self.paddle_ai_y), PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, config_module.COLOR_FOREGROUND, ai_paddle_rect)

        # Draw ball
        ball_rect = pygame.Rect(int(self.ball_x), int(self.ball_y), BALL_SIZE, BALL_SIZE)
        pygame.draw.rect(screen, config_module.COLOR_ACCENT, ball_rect)  # Use accent color for ball

        # Draw score with larger font
        score_text = f"Player: {self.score_player}  AI: {self.score_ai}"
        score_surf = self.font.render(score_text, True, config_module.COLOR_ACCENT)
        # Position score near the top-center
        score_pos = (self.width // 2 - score_surf.get_width() // 2, 10)
        screen.blit(score_surf, score_pos)

        # Draw game over message if game is over
        if self.game_over:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(128)  # Semi-transparent
            overlay.fill(config_module.COLOR_BACKGROUND)
            screen.blit(overlay, (0, 0))

            # Draw game over message
            game_over_text = self.font.render(self.winner_message, True, config_module.COLOR_ACCENT)
            game_over_pos = (self.width // 2 - game_over_text.get_width() // 2,
                            self.height // 2 - game_over_text.get_height() // 2 - 20)
            screen.blit(game_over_text, game_over_pos)
            # Quit hint (OS-adaptive)
            try:
                labels = config_module.get_control_labels()
                quit_hint = f"Press {labels['prev']} to quit"
            except Exception:
                quit_hint = "Press A to quit"
            hint_surf = self.font.render(quit_hint, True, config_module.COLOR_FOREGROUND)
            hint_pos = (self.width // 2 - hint_surf.get_width() // 2, self.height // 2 + 15)
            screen.blit(hint_surf, hint_pos)

        # Draw pause menu if paused
        if self.paused:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(128)  # Semi-transparent
            overlay.fill(config_module.COLOR_BACKGROUND)
            screen.blit(overlay, (0, 0))

            # Draw pause menu options
            menu_y = self.height // 2 - (len(self.pause_menu_options) * 30) // 2
            for i, option in enumerate(self.pause_menu_options):
                color = config_module.COLOR_ACCENT if i == self.pause_menu_selected_index else config_module.COLOR_FOREGROUND
                text = self.font.render(option, True, color)
                text_pos = (self.width // 2 - text.get_width() // 2, menu_y + i * 30)
                screen.blit(text, text_pos) 