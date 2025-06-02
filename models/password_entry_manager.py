# --- models/password_entry_manager.py ---
# Manages password entry state and character selection

import logging
from ui.components.character_selector import CharacterSelector
import config as app_config

logger = logging.getLogger(__name__)

class PasswordEntryManager:
    """Manages password entry using the character selector."""
    
    def __init__(self, config_module, screen_rect, fonts):
        """
        Initialize the password entry manager.
        
        Args:
            config_module: Configuration module
            screen_rect (pygame.Rect): Available screen area
            fonts (dict): Dictionary of loaded fonts
        """
        self.config = config_module
        self.character_selector = CharacterSelector(screen_rect, fonts, config_module)
        
        # Password entry state
        self.current_password = ""
        self.show_password = False
        self.target_network = None
        
        logger.info(f"Password entry manager initialized with screen rect {screen_rect}")
        
    def set_target_network(self, network):
        """Set the network to connect to."""
        self.target_network = network
        self.current_password = ""  # Reset password for new network
        ssid = network.get('ssid', 'Unknown') if network else 'None'
        logger.info(f"Password entry started for network: {ssid}")
        
    def handle_input(self, action_from_app_state):
        """
        Handle input for password entry.
        
        Args:
            action_from_app_state (str): Input action
            
        Returns:
            str or bool: Action string or boolean for navigation
        """
        logger.debug(f"Password entry received action: '{action_from_app_state}'")
        
        if action_from_app_state == app_config.INPUT_ACTION_NEXT:
            # D key cycles to next character in reading order
            logger.debug("Processing NEXT action for sequential navigation")
            result = self._navigate_sequential(1)
            logger.debug(f"Sequential navigation NEXT result: {result}")
            return result
        elif action_from_app_state == app_config.INPUT_ACTION_PREV:
            # A key cycles to previous character in reading order
            logger.debug("Processing PREV action for sequential navigation")
            result = self._navigate_sequential(-1)
            logger.debug(f"Sequential navigation PREV result: {result}")
            return result
        elif action_from_app_state == app_config.INPUT_ACTION_SELECT:
            logger.info("Processing SELECT action for character selection")
            result = self._handle_character_selection()
            logger.info(f"Character selection result: {result}")
            return result
        elif action_from_app_state == app_config.INPUT_ACTION_BACK:
            logger.info("Processing BACK action - cancelling password entry")
            return 'CANCEL_PASSWORD_ENTRY'
        else:
            logger.warning(f"Unknown action received in password entry: '{action_from_app_state}'")
            
        return False
        
    def handle_joystick_input(self, direction):
        """
        Handle joystick navigation.
        
        Args:
            direction (str): Direction ('UP', 'DOWN', 'LEFT', 'RIGHT')
            
        Returns:
            bool: True if navigation occurred
        """
        logger.debug(f"Password entry received joystick direction: '{direction}'")
        result = self.character_selector.navigate(direction)
        logger.debug(f"Joystick navigation result: {result}")
        return result
        
    def _navigate_sequential(self, direction):
        """Navigate through characters in reading order (left-to-right, top-to-bottom)."""
        chars = self.character_selector.characters
        current_row = self.character_selector.cursor_row
        current_col = self.character_selector.cursor_col
        
        logger.debug(f"Sequential navigation: current position ({current_row}, {current_col}), direction {direction}")
        
        # Convert 2D position to 1D index
        current_index = 0
        for r in range(current_row):
            current_index += len(chars[r])
        current_index += current_col
        
        # Calculate total characters
        total_chars = sum(len(row) for row in chars)
        
        # Move in direction
        new_index = (current_index + direction) % total_chars
        
        logger.debug(f"Sequential navigation: index {current_index} -> {new_index} (total: {total_chars})")
        
        # Convert back to 2D position
        char_count = 0
        for row_idx, row in enumerate(chars):
            if char_count + len(row) > new_index:
                old_row, old_col = self.character_selector.cursor_row, self.character_selector.cursor_col
                self.character_selector.cursor_row = row_idx
                self.character_selector.cursor_col = new_index - char_count
                
                selected_char = self.character_selector.get_selected_character()
                logger.debug(f"Sequential navigation complete: ({old_row}, {old_col}) -> "
                           f"({row_idx}, {new_index - char_count}), selected: '{selected_char}'")
                return True
            char_count += len(row)
        
        logger.warning("Sequential navigation failed to find valid position")
        return False
        
    def _handle_character_selection(self):
        """Handle selection of a character from the grid."""
        selected = self.character_selector.get_selected_character()
        
        logger.info(f"Character selection: selected '{selected}', current password length: {len(self.current_password)}")
        
        if selected == 'DELETE':
            if self.current_password:
                removed_char = self.current_password[-1]
                self.current_password = self.current_password[:-1]
                logger.info(f"Delete: removed '{removed_char}', new length: {len(self.current_password)}")
            else:
                logger.debug("Delete pressed but password is empty")
            return True
            
        elif selected == 'CAPS':
            # Toggle caps lock
            return self.character_selector.toggle_caps_lock()
            
        elif selected == 'SHOW':
            self.show_password = not self.show_password
            logger.info(f"Password visibility toggled: {self.show_password}")
            return True
            
        elif selected == 'GO':
            if self.current_password or self._is_open_network():
                ssid = self.target_network.get('ssid', 'Unknown') if self.target_network else 'Unknown'
                logger.info(f"Connect requested for '{ssid}' with password length: {len(self.current_password)}")
                return 'ATTEMPT_CONNECTION'
            else:
                logger.warning("Cannot connect: no password entered for secured network")
                return False
                
        elif selected == 'CANCEL':
            logger.info("Password entry cancelled by user selection")
            return 'CANCEL_PASSWORD_ENTRY'
            
        elif selected == 'SPACE':
            if len(self.current_password) < 63:
                self.current_password += ' '
                logger.info(f"Space added, password length: {len(self.current_password)}")
            else:
                logger.warning("Cannot add space: password at maximum length")
            return True
            
        elif selected and len(selected) == 1 and len(self.current_password) < 63:  # WiFi password max length
            self.current_password += selected
            logger.info(f"Character '{selected}' added, password length: {len(self.current_password)}")
            return True
        
        elif selected and len(selected) == 1:
            logger.warning(f"Cannot add character '{selected}': password at maximum length (63)")
            return False
            
        else:
            logger.warning(f"Unhandled character selection: '{selected}' (type: {type(selected)})")
            return False
        
    def _is_open_network(self):
        """Check if the target network is open (no password required)."""
        if self.target_network:
            security = self.target_network.get('security', 'Unknown')
            is_open = security in ['Open', 'None', '']
            logger.debug(f"Network security check: '{security}' -> open: {is_open}")
            return is_open
        logger.debug("No target network set, assuming secured")
        return False
        
    def get_current_password(self):
        """Get the current password."""
        logger.debug(f"Password requested, length: {len(self.current_password)}")
        return self.current_password
        
    def get_target_network(self):
        """Get the target network."""
        ssid = self.target_network.get('ssid', 'Unknown') if self.target_network else 'None'
        logger.debug(f"Target network requested: {ssid}")
        return self.target_network
        
    def draw(self, screen):
        """
        Draw the password entry interface.
        
        Args:
            screen (pygame.Surface): Surface to draw on
        """
        try:
            if self.target_network:
                ssid = self.target_network.get('ssid', 'Unknown')
                title = f"Enter Password for '{ssid}'"
            else:
                title = "Enter Password"
                
            logger.debug(f"Drawing password entry interface with title: '{title}'")
            
            self.character_selector.draw(
                screen,
                title=title,
                current_text=self.current_password,
                show_password=self.show_password
            )
            
        except Exception as e:
            logger.error(f"Error drawing password entry interface: {e}", exc_info=True) 