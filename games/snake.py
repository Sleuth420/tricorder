# --- games/snake.py ---
# Classic Snake game logic for the tricorder

import pygame
import random
import logging
from enum import Enum

logger = logging.getLogger(__name__)

# --- Game Constants ---
GRID_SIZE = 16  # Size of each grid cell
SNAKE_SPEED = 8  # Frames between moves (lower = faster)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    """Manages the state and logic for the Snake game."""

    def __init__(self, width, height, config):
        """
        Initializes the Snake game.

        Args:
            width (int): Width of the game area.
            height (int): Height of the game area.
            config (module): Application configuration for key bindings, colors.
        """
        self.width = width
        self.height = height
        self.config = config
        self.font = None  # Will be set in draw method from passed fonts

        # Calculate grid dimensions
        self.grid_width = width // GRID_SIZE
        self.grid_height = height // GRID_SIZE
        
        # Initialize snake
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]  # Start in center
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Initialize food
        self.food = self._generate_food()
        
        # Game state
        self.score = 0
        self.game_over = False
        self.winner_message = ""
        self.paused = False
        self.pause_menu_options = ["Resume", "Quit to Menu"]
        self.pause_menu_selected_index = 0
        
        # Movement timing
        self.move_counter = 0

        logger.info(f"Snake game initialized with area {width}x{height}, grid {self.grid_width}x{self.grid_height}")

    def _generate_food(self):
        """Generate food at a random location not occupied by snake."""
        while True:
            food_x = random.randint(0, self.grid_width - 1)
            food_y = random.randint(0, self.grid_height - 1)
            if (food_x, food_y) not in self.snake:
                return (food_x, food_y)

    def turn_left(self):
        """Turn the snake left (counterclockwise)."""
        if not self.game_over and not self.paused:
            current_dir = self.direction
            if current_dir == Direction.UP:
                self.next_direction = Direction.LEFT
            elif current_dir == Direction.LEFT:
                self.next_direction = Direction.DOWN
            elif current_dir == Direction.DOWN:
                self.next_direction = Direction.RIGHT
            elif current_dir == Direction.RIGHT:
                self.next_direction = Direction.UP
            logger.debug(f"Snake turning left: {current_dir} -> {self.next_direction}")

    def turn_right(self):
        """Turn the snake right (clockwise)."""
        if not self.game_over and not self.paused:
            current_dir = self.direction
            if current_dir == Direction.UP:
                self.next_direction = Direction.RIGHT
            elif current_dir == Direction.RIGHT:
                self.next_direction = Direction.DOWN
            elif current_dir == Direction.DOWN:
                self.next_direction = Direction.LEFT
            elif current_dir == Direction.LEFT:
                self.next_direction = Direction.UP
            logger.debug(f"Snake turning right: {current_dir} -> {self.next_direction}")

    def toggle_pause(self):
        """Toggle the paused state of the game."""
        self.paused = not self.paused
        if self.paused:
            self.pause_menu_selected_index = 0
        logger.info(f"Snake game {'paused' if self.paused else 'resumed'}.")

    def navigate_pause_menu_up(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index - 1 + len(self.pause_menu_options)) % len(self.pause_menu_options)
            logger.debug(f"Snake pause menu UP to index {self.pause_menu_selected_index}")

    def navigate_pause_menu_down(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index + 1) % len(self.pause_menu_options)
            logger.debug(f"Snake pause menu DOWN to index {self.pause_menu_selected_index}")

    def select_pause_menu_option(self):
        if self.paused and self.pause_menu_options and self.pause_menu_selected_index < len(self.pause_menu_options):
            selected_action_text = self.pause_menu_options[self.pause_menu_selected_index]
            logger.info(f"Snake pause menu SELECTED: {selected_action_text}")
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

        # Update movement counter
        self.move_counter += 1
        if self.move_counter < SNAKE_SPEED:
            return
        
        self.move_counter = 0

        # Update direction (only change if it's not opposite to current direction)
        if self.next_direction != self.direction:
            # Prevent reversing into itself
            opposite_directions = {
                Direction.UP: Direction.DOWN,
                Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT,
                Direction.RIGHT: Direction.LEFT
            }
            if self.next_direction != opposite_directions[self.direction]:
                self.direction = self.next_direction

        # Move snake
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.game_over = True
            self.winner_message = "GAME OVER! Hit Wall"
            logger.info("Snake game over - hit wall")
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            self.winner_message = "GAME OVER! Hit Self"
            logger.info("Snake game over - hit self")
            return

        # Add new head
        self.snake.insert(0, new_head)

        # Check food collision
        if new_head == self.food:
            self.score += 10
            self.food = self._generate_food()
            logger.debug(f"Snake ate food, score: {self.score}")
            
            # Check win condition (snake fills most of the screen)
            max_length = (self.grid_width * self.grid_height) - 10  # Leave some space
            if len(self.snake) >= max_length:
                self.game_over = True
                self.winner_message = "YOU WIN! Perfect Snake!"
                logger.info("Snake game won - maximum length reached")
        else:
            # Remove tail if no food eaten
            self.snake.pop()

    def draw(self, screen, fonts, config_module):
        """Draw the current state of the Snake game."""
        if not self.font:
            self.font = fonts.get('medium', fonts.get('default'))

        # Draw grid background (optional)
        # for x in range(0, self.width, GRID_SIZE):
        #     pygame.draw.line(screen, config_module.COLOR_GRAPH_BORDER, (x, 0), (x, self.height))
        # for y in range(0, self.height, GRID_SIZE):
        #     pygame.draw.line(screen, config_module.COLOR_GRAPH_BORDER, (0, y), (self.width, y))

        # Draw food
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE,
            self.food[1] * GRID_SIZE,
            GRID_SIZE - 1,  # Small gap between cells
            GRID_SIZE - 1
        )
        pygame.draw.rect(screen, config_module.COLOR_ACCENT, food_rect)

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            snake_rect = pygame.Rect(
                x * GRID_SIZE,
                y * GRID_SIZE,
                GRID_SIZE - 1,
                GRID_SIZE - 1
            )
            # Head is brighter than body
            if i == 0:  # Head
                pygame.draw.rect(screen, config_module.COLOR_FOREGROUND, snake_rect)
            else:  # Body
                # Use a dimmer color for body
                body_color = tuple(int(c * 0.7) for c in config_module.COLOR_FOREGROUND)
                pygame.draw.rect(screen, body_color, snake_rect)

        # Draw score
        score_text = f"Score: {self.score}"
        score_surf = self.font.render(score_text, True, config_module.COLOR_ACCENT)
        screen.blit(score_surf, (10, 10))

        # Draw level/length (compact)
        length_text = f"Length: {len(self.snake)}"
        length_surf = self.font.render(length_text, True, config_module.COLOR_FOREGROUND)
        screen.blit(length_surf, (10, 30))

        # Draw controls hint (OS-adaptive: Left/Right on Pi, A/D on dev)
        if len(self.snake) < 5:  # Show hint for first few moves
            labels = config_module.get_control_labels()
            hint_text = f"{labels['prev']}=Turn Left, {labels['next']}=Turn Right"
            hint_surf = self.font.render(hint_text, True, config_module.COLOR_FOREGROUND)
            hint_x = self.width // 2 - hint_surf.get_width() // 2
            screen.blit(hint_surf, (hint_x, self.height - 30))

        # Draw game over message
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(128)
            overlay.fill(config_module.COLOR_BACKGROUND)
            screen.blit(overlay, (0, 0))

            game_over_text = self.font.render(self.winner_message, True, config_module.COLOR_ACCENT)
            game_over_pos = (self.width // 2 - game_over_text.get_width() // 2,
                             self.height // 2 - game_over_text.get_height() // 2 - 20)
            screen.blit(game_over_text, game_over_pos)
            try:
                labels = config_module.get_control_labels()
                quit_hint = f"Press {labels['prev']} to quit"
            except Exception:
                quit_hint = "Press A to quit"
            hint_surf = self.font.render(quit_hint, True, config_module.COLOR_FOREGROUND)
            hint_pos = (self.width // 2 - hint_surf.get_width() // 2, self.height // 2 + 15)
            screen.blit(hint_surf, hint_pos)

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