# --- models/game_manager.py ---
# Manages game state and game instances

import logging
from games.pong import PongGame
from games.breakout import BreakoutGame
from games.snake import SnakeGame
# State constants - defined locally to avoid circular imports
STATE_PONG_ACTIVE = "PONG_ACTIVE"
STATE_BREAKOUT_ACTIVE = "BREAKOUT_ACTIVE"
STATE_SNAKE_ACTIVE = "SNAKE_ACTIVE"
STATE_MENU = "MENU"
import config as app_config

logger = logging.getLogger(__name__)

class GameManager:
    """Manages game instances and game-related state."""
    
    def __init__(self, config_module, screen_width, screen_height):
        """
        Initialize the game manager.
        
        Args:
            config_module: The configuration module
            screen_width (int): Screen width for games
            screen_height (int): Screen height for games
        """
        self.config = config_module
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Game instances
        self.active_pong_game = None
        self.active_breakout_game = None
        self.active_snake_game = None
        
    def launch_pong(self):
        """
        Launch a new Pong game.
        
        Returns:
            bool: True if game was launched successfully
        """
        try:
            self.active_pong_game = PongGame(
                self.screen_width, 
                self.screen_height, 
                self.config
            )
            logger.info("Pong game launched successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to launch Pong game: {e}")
            return False
            
    def launch_breakout(self):
        """
        Launch a new Breakout game.
        
        Returns:
            bool: True if game was launched successfully
        """
        try:
            self.active_breakout_game = BreakoutGame(
                self.screen_width, 
                self.screen_height, 
                self.config
            )
            logger.info("Breakout game launched successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to launch Breakout game: {e}")
            return False
            
    def launch_snake(self):
        """
        Launch a new Snake game.
        
        Returns:
            bool: True if game was launched successfully
        """
        try:
            self.active_snake_game = SnakeGame(
                self.screen_width, 
                self.screen_height, 
                self.config
            )
            logger.info("Snake game launched successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to launch Snake game: {e}")
            return False
            
    def launch_tetris(self):
        """
        Launch a new Tetris game (placeholder).
        
        Returns:
            bool: True if game was launched successfully
        """
        logger.warning("Tetris game not yet implemented")
        return False
        
    def close_current_game(self):
        """Close the currently active game."""
        if self.active_pong_game:
            logger.info("Closing Pong game")
            self.active_pong_game = None
        if self.active_breakout_game:
            logger.info("Closing Breakout game")
            self.active_breakout_game = None
        if self.active_snake_game:
            logger.info("Closing Snake game")
            self.active_snake_game = None
            
    def handle_pong_input(self, action_name, event_type=None):
        """
        Handle input for the active Pong game.
        
        Args:
            action_name (str): The input action name
            event_type (str, optional): The event type for special handling
            
        Returns:
            str: Game action result (e.g., "RESUME_GAME", "QUIT_TO_MENU")
        """
        if not self.active_pong_game:
            return None
            
        # Handle different game states
        if not self.active_pong_game.paused and not self.active_pong_game.game_over:
            # Active game state
            if action_name == app_config.INPUT_ACTION_PREV:
                logger.debug("Pong: Moving paddle up")
                self.active_pong_game.move_paddle_up()
            elif action_name == app_config.INPUT_ACTION_NEXT:
                logger.debug("Pong: Moving paddle down")
                self.active_pong_game.move_paddle_down()
            elif action_name == app_config.INPUT_ACTION_SELECT:
                logger.info("Pong: Pausing game")
                self.active_pong_game.toggle_pause()
                return "GAME_PAUSED"
                
        elif self.active_pong_game.paused:
            # Paused game state - handle pause menu
            if action_name == app_config.INPUT_ACTION_PREV:
                logger.debug("Pong: Navigating pause menu up")
                self.active_pong_game.navigate_pause_menu_up()
            elif action_name == app_config.INPUT_ACTION_NEXT:
                logger.debug("Pong: Navigating pause menu down")
                self.active_pong_game.navigate_pause_menu_down()
            elif action_name == app_config.INPUT_ACTION_SELECT:
                logger.debug("Pong: Selecting pause menu option")
                menu_action = self.active_pong_game.select_pause_menu_option()
                if menu_action == "RESUME_GAME":
                    logger.info("Pong: Resuming game from pause menu")
                    return "RESUME_GAME"
                elif menu_action == "QUIT_TO_MENU":
                    logger.info("Pong: Quitting to menu from pause menu")
                    return "QUIT_TO_MENU"
                    
        elif self.active_pong_game.game_over:
            # Game over state
            if action_name == app_config.INPUT_ACTION_BACK:
                logger.info("Pong: Quitting from game over screen")
                return "QUIT_TO_MENU"
                
        return None
        
    def update_pong(self, keys_held):
        """
        Update the Pong game state.
        
        Args:
            keys_held (set): Set of currently held keys
        """
        if self.active_pong_game:
            self.active_pong_game.update(keys_held)
            
    def handle_continuous_pong_input(self, keys_held):
        """
        Handle continuous input for Pong (held keys).
        
        Args:
            keys_held (set): Set of currently held keys
        """
        if (self.active_pong_game and 
            not self.active_pong_game.paused and 
            not self.active_pong_game.game_over):
            
            if self.config.KEY_PREV in keys_held:
                self.active_pong_game.move_paddle_up()
            if self.config.KEY_NEXT in keys_held:
                self.active_pong_game.move_paddle_down()
                
    def is_pong_active(self):
        """Check if Pong game is currently active."""
        return self.active_pong_game is not None
        
    def handle_breakout_input(self, action_name, event_type=None):
        """
        Handle input for the active Breakout game.
        
        Args:
            action_name (str): The input action name
            event_type (str, optional): The event type for special handling
            
        Returns:
            str: Game action result (e.g., "RESUME_GAME", "QUIT_TO_MENU")
        """
        if not self.active_breakout_game:
            return None
            
        # Handle different game states
        if not self.active_breakout_game.paused and not self.active_breakout_game.game_over:
            # Active game state
            if action_name == app_config.INPUT_ACTION_PREV:
                logger.debug("Breakout: Moving paddle left")
                self.active_breakout_game.move_paddle_left()
            elif action_name == app_config.INPUT_ACTION_NEXT:
                logger.debug("Breakout: Moving paddle right")
                self.active_breakout_game.move_paddle_right()
            elif action_name == app_config.INPUT_ACTION_SELECT:
                if self.active_breakout_game.ball_on_paddle:
                    logger.info("Breakout: Launching ball")
                    self.active_breakout_game.launch_ball()
                else:
                    logger.info("Breakout: Pausing game")
                    self.active_breakout_game.toggle_pause()
                    return "GAME_PAUSED"
                
        elif self.active_breakout_game.paused:
            # Paused game state - handle pause menu
            if action_name == app_config.INPUT_ACTION_PREV:
                logger.debug("Breakout: Navigating pause menu up")
                self.active_breakout_game.navigate_pause_menu_up()
            elif action_name == app_config.INPUT_ACTION_NEXT:
                logger.debug("Breakout: Navigating pause menu down")
                self.active_breakout_game.navigate_pause_menu_down()
            elif action_name == app_config.INPUT_ACTION_SELECT:
                logger.debug("Breakout: Selecting pause menu option")
                menu_action = self.active_breakout_game.select_pause_menu_option()
                if menu_action == "RESUME_GAME":
                    logger.info("Breakout: Resuming game from pause menu")
                    return "RESUME_GAME"
                elif menu_action == "QUIT_TO_MENU":
                    logger.info("Breakout: Quitting to menu from pause menu")
                    return "QUIT_TO_MENU"
                    
        elif self.active_breakout_game.game_over:
            # Game over state
            if action_name == app_config.INPUT_ACTION_BACK:
                logger.info("Breakout: Quitting from game over screen")
                return "QUIT_TO_MENU"
                
        return None
        
    def handle_snake_input(self, action_name, event_type=None):
        """
        Handle input for the active Snake game.
        
        Args:
            action_name (str): The input action name
            event_type (str, optional): The event type for special handling
            
        Returns:
            str: Game action result (e.g., "RESUME_GAME", "QUIT_TO_MENU")
        """
        if not self.active_snake_game:
            return None
            
        # Handle different game states
        if not self.active_snake_game.paused and not self.active_snake_game.game_over:
            # Active game state
            if action_name == app_config.INPUT_ACTION_PREV:
                logger.debug("Snake: Turning left")
                self.active_snake_game.turn_left()
            elif action_name == app_config.INPUT_ACTION_NEXT:
                logger.debug("Snake: Turning right")
                self.active_snake_game.turn_right()
            elif action_name == app_config.INPUT_ACTION_SELECT:
                logger.info("Snake: Pausing game")
                self.active_snake_game.toggle_pause()
                return "GAME_PAUSED"
                
        elif self.active_snake_game.paused:
            # Paused game state - handle pause menu
            if action_name == app_config.INPUT_ACTION_PREV:
                logger.debug("Snake: Navigating pause menu up")
                self.active_snake_game.navigate_pause_menu_up()
            elif action_name == app_config.INPUT_ACTION_NEXT:
                logger.debug("Snake: Navigating pause menu down")
                self.active_snake_game.navigate_pause_menu_down()
            elif action_name == app_config.INPUT_ACTION_SELECT:
                logger.debug("Snake: Selecting pause menu option")
                menu_action = self.active_snake_game.select_pause_menu_option()
                if menu_action == "RESUME_GAME":
                    logger.info("Snake: Resuming game from pause menu")
                    return "RESUME_GAME"
                elif menu_action == "QUIT_TO_MENU":
                    logger.info("Snake: Quitting to menu from pause menu")
                    return "QUIT_TO_MENU"
                    
        elif self.active_snake_game.game_over:
            # Game over state
            if action_name == app_config.INPUT_ACTION_BACK:
                logger.info("Snake: Quitting from game over screen")
                return "QUIT_TO_MENU"
                
        return None

    def update_breakout(self, keys_held):
        """
        Update the Breakout game state.
        
        Args:
            keys_held (set): Set of currently held keys
        """
        if self.active_breakout_game:
            self.active_breakout_game.update(keys_held)
            
    def update_snake(self, keys_held):
        """
        Update the Snake game state.
        
        Args:
            keys_held (set): Set of currently held keys
        """
        if self.active_snake_game:
            self.active_snake_game.update(keys_held)

    def handle_continuous_breakout_input(self, keys_held):
        """
        Handle continuous input for Breakout (held keys).
        
        Args:
            keys_held (set): Set of currently held keys
        """
        if (self.active_breakout_game and 
            not self.active_breakout_game.paused and 
            not self.active_breakout_game.game_over):
            
            if self.config.KEY_PREV in keys_held:
                self.active_breakout_game.move_paddle_left()
            if self.config.KEY_NEXT in keys_held:
                self.active_breakout_game.move_paddle_right()

    def is_breakout_active(self):
        """Check if Breakout game is currently active."""
        return self.active_breakout_game is not None
        
    def is_snake_active(self):
        """Check if Snake game is currently active."""
        return self.active_snake_game is not None

    def get_pong_game(self):
        """Get the active Pong game instance."""
        return self.active_pong_game
        
    def get_breakout_game(self):
        """Get the active Breakout game instance."""
        return self.active_breakout_game
        
    def get_snake_game(self):
        """Get the active Snake game instance."""
        return self.active_snake_game 