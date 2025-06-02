# --- ui/components/character_selector.py ---
# Character selection interface for password entry

import pygame
import logging

logger = logging.getLogger(__name__)

class CharacterSelector:
    """A character selection grid for password entry."""
    
    def __init__(self, screen_rect, fonts, config_module):
        """Initialize the character selector."""
        self.screen_rect = screen_rect
        self.config = config_module
        
        # Use fonts
        self._setup_fonts(fonts)
        
        # Caps lock state
        self.caps_lock = False
        
        # Single character grid layout
        self.characters = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '@'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '-', '_'],
            ['SPACE', 'CAPS', 'DELETE', 'SHOW', 'GO', 'CANCEL']
        ]
        
        # Cursor position
        self.cursor_row = 0
        self.cursor_col = 0
        
        # Layout calculations
        self._calculate_layout()
        
        logger.info(f"Character selector initialized for {screen_rect.width}x{screen_rect.height} with cursor at ({self.cursor_row}, {self.cursor_col})")

    def _setup_fonts(self, fonts):
        """Setup fonts."""
        try:
            self.char_font = fonts.get('small', pygame.font.Font(None, 16)) if fonts else pygame.font.Font(None, 16)
            self.title_font = fonts.get('medium', pygame.font.Font(None, 20)) if fonts else pygame.font.Font(None, 20)
            self.footer_font = fonts.get('small', pygame.font.Font(None, 14)) if fonts else pygame.font.Font(None, 14)
            self.fonts = fonts
            logger.info("Character selector fonts loaded")
                
        except Exception as e:
            logger.warning(f"Error setting up fonts, using pygame defaults: {e}")
            self.char_font = pygame.font.Font(None, 16)
            self.title_font = pygame.font.Font(None, 20)
            self.footer_font = pygame.font.Font(None, 14)
            self.fonts = None
        
        # Test font rendering
        try:
            test_surface = self.char_font.render("A", True, (255, 255, 255))
            logger.info(f"Font test successful - rendered 'A' with size {test_surface.get_size()}")
        except Exception as e:
            logger.error(f"Font rendering test failed: {e}")

    def _calculate_layout(self):
        """Calculate the layout dimensions."""
        title_height = 30
        password_field_height = 40
        footer_height = 60
        padding = 20
        
        # Available space for character grid
        available_height = (self.screen_rect.height - 
                          title_height - password_field_height - footer_height - padding * 4)
        available_width = self.screen_rect.width - padding * 2
        
        # Calculate cell dimensions
        max_cols = max(len(row) for row in self.characters)
        num_rows = len(self.characters)
        
        self.cell_width = available_width // max_cols
        self.cell_height = available_height // num_rows
        
        # Ensure minimum cell size
        min_cell_width = 40
        min_cell_height = 25
            
        self.cell_width = max(self.cell_width, min_cell_width)
        self.cell_height = max(self.cell_height, min_cell_height)
        
        # Grid position - center the grid
        total_grid_width = max_cols * self.cell_width
        total_grid_height = num_rows * self.cell_height
        
        self.grid_x = (self.screen_rect.width - total_grid_width) // 2
        self.grid_y = title_height + password_field_height + padding * 2
        
        # Other UI element positions
        self.title_y = padding
        self.password_y = title_height + padding
        self.footer_y = self.screen_rect.height - footer_height
        
        # Store layout values for reference
        self.title_height = title_height
        self.password_field_height = password_field_height
        self.footer_height = footer_height
        self.padding = padding
        
        logger.debug(f"Layout calculated: grid at ({self.grid_x}, {self.grid_y}), cell size ({self.cell_width}, {self.cell_height})")

    def navigate(self, direction):
        """Navigate the cursor in the specified direction."""
        old_pos = (self.cursor_row, self.cursor_col)
        
        if direction == 'UP' and self.cursor_row > 0:
            self.cursor_row -= 1
            # Ensure we don't go beyond the row length
            if self.cursor_col >= len(self.characters[self.cursor_row]):
                self.cursor_col = len(self.characters[self.cursor_row]) - 1
                
        elif direction == 'DOWN' and self.cursor_row < len(self.characters) - 1:
            self.cursor_row += 1
            # Ensure we don't go beyond the row length
            if self.cursor_col >= len(self.characters[self.cursor_row]):
                self.cursor_col = len(self.characters[self.cursor_row]) - 1
                
        elif direction == 'LEFT' and self.cursor_col > 0:
            self.cursor_col -= 1
            
        elif direction == 'RIGHT':
            if self.cursor_col < len(self.characters[self.cursor_row]) - 1:
                self.cursor_col += 1
        
        new_pos = (self.cursor_row, self.cursor_col)
        if old_pos != new_pos:
            selected_char = self.get_selected_character()
            logger.debug(f"Navigation {direction}: moved from {old_pos} to {new_pos}, "
                        f"selected character: '{selected_char}'")
            return True
        else:
            logger.debug(f"Navigation {direction}: no movement from {old_pos}")
            return False

    def get_selected_character(self):
        """Get the currently selected character."""
        if (0 <= self.cursor_row < len(self.characters) and 
            0 <= self.cursor_col < len(self.characters[self.cursor_row])):
            char = self.characters[self.cursor_row][self.cursor_col]
            
            # Apply caps lock to letters
            if char.isalpha() and self.caps_lock:
                char = char.upper()
            
            logger.debug(f"Selected character at ({self.cursor_row}, {self.cursor_col}): '{char}' (caps: {self.caps_lock})")
            return char
        logger.warning(f"Invalid cursor position: ({self.cursor_row}, {self.cursor_col})")
        return None

    def toggle_caps_lock(self):
        """Toggle caps lock state."""
        self.caps_lock = not self.caps_lock
        logger.info(f"Caps lock {'ON' if self.caps_lock else 'OFF'}")
        return True

    def draw(self, screen, title="Enter Password", current_text="", show_password=False):
        """Draw the character selector interface."""
        try:
            # Clear background
            screen.fill(self.config.Theme.BACKGROUND)
            
            # Draw title
            self._draw_title(screen, title)
            
            # Draw password field
            self._draw_password_field(screen, current_text, show_password)
            
            # Draw character grid
            self._draw_character_grid(screen)
            
            # Draw footer
            self._draw_footer(screen)
            
            logger.debug(f"Character selector drawn successfully, cursor at ({self.cursor_row}, {self.cursor_col})")
            
        except Exception as e:
            logger.error(f"Error drawing character selector: {e}", exc_info=True)
            # Draw error message
            error_surface = self.title_font.render(f"Display Error: {str(e)}", True, self.config.Theme.ALERT)
            screen.blit(error_surface, (10, 10))

    def _draw_title(self, screen, title):
        """Draw the title at the top."""
        try:
            title_surface = self.title_font.render(title, True, self.config.Theme.FOREGROUND)
            title_rect = title_surface.get_rect(centerx=self.screen_rect.centerx, y=self.title_y)
            screen.blit(title_surface, title_rect)
            logger.debug(f"Title drawn: '{title}'")
        except Exception as e:
            logger.error(f"Error drawing title: {e}")

    def _draw_password_field(self, screen, text, show_password):
        """Draw the password input field."""
        try:
            field_rect = pygame.Rect(20, self.password_y, self.screen_rect.width - 40, 30)
            pygame.draw.rect(screen, self.config.Theme.MENU_SELECTED_BG, field_rect)
            pygame.draw.rect(screen, self.config.Theme.FOREGROUND, field_rect, 1)
            
            # Display text
            display_text = text if show_password else '*' * len(text)
            
            # Truncate text if too long
            max_chars = 30
            if len(display_text) > max_chars:
                display_text = display_text[-max_chars:]
                
            text_surface = self.char_font.render(display_text, True, self.config.Theme.FOREGROUND)
            text_rect = text_surface.get_rect(centery=field_rect.centery, x=field_rect.x + 3)
            screen.blit(text_surface, text_rect)
            
            # Show character count
            count_text = f"({len(text)}/63)"
            count_surface = self.footer_font.render(count_text, True, self.config.Theme.FOREGROUND)
            count_rect = count_surface.get_rect(centery=field_rect.centery, right=field_rect.right - 5)
            screen.blit(count_surface, count_rect)
            
            logger.debug(f"Password field drawn with {len(text)} characters, show_password={show_password}")
            
        except Exception as e:
            logger.error(f"Error drawing password field: {e}")

    def _draw_character_grid(self, screen):
        """Draw the character selection grid."""
        try:
            chars_drawn = 0
            for row_idx, row in enumerate(self.characters):
                for col_idx, char in enumerate(row):
                    # Calculate cell position
                    x = self.grid_x + col_idx * self.cell_width
                    y = self.grid_y + row_idx * self.cell_height
                    
                    # Cell rectangle
                    cell_padding = 2
                    cell_rect = pygame.Rect(x + cell_padding, y + cell_padding, 
                                          self.cell_width - cell_padding * 2, 
                                          self.cell_height - cell_padding * 2)
                    
                    # Highlight selected cell
                    if row_idx == self.cursor_row and col_idx == self.cursor_col:
                        pygame.draw.rect(screen, self.config.Theme.MENU_SELECTED_BG, cell_rect)
                        text_color = self.config.Theme.MENU_SELECTED_TEXT
                        # Draw thicker border for selected cell
                        pygame.draw.rect(screen, self.config.Theme.FOREGROUND, cell_rect, 2)
                    else:
                        pygame.draw.rect(screen, self.config.Theme.BACKGROUND, cell_rect)
                        text_color = self.config.Theme.FOREGROUND
                        # Draw thin border for unselected cells
                        pygame.draw.rect(screen, self.config.Theme.FOREGROUND, cell_rect, 1)
                    
                    # Character text
                    try:
                        display_char = char
                        
                        # Apply caps lock visual indicator and letter case
                        if char == 'CAPS':
                            if self.caps_lock:
                                display_char = 'CAPS*'  # Show caps lock is on
                                text_color = self.config.Theme.ACCENT  # Highlight when active
                        elif char.isalpha():
                            if self.caps_lock:
                                display_char = char.upper()
                            else:
                                display_char = char.lower()
                            
                        # Use smaller font for action words if needed
                        font_to_use = self.char_font
                        if len(display_char) > 3:
                            # Test if it fits, if not use a smaller font size
                            test_surface = font_to_use.render(display_char, True, text_color)
                            if test_surface.get_width() > cell_rect.width - 4:
                                # Use a smaller font for long action names
                                small_font_size = max(8, int(self.char_font.get_height() * 0.7))
                                font_to_use = pygame.font.Font(None, small_font_size)
                            
                        char_surface = font_to_use.render(display_char, True, text_color)
                        char_rect = char_surface.get_rect(center=cell_rect.center)
                        screen.blit(char_surface, char_rect)
                        chars_drawn += 1
                    except Exception as char_error:
                        logger.error(f"Error rendering character '{char}': {char_error}")
                        # Draw a placeholder
                        placeholder_surface = self.char_font.render("?", True, text_color)
                        placeholder_rect = placeholder_surface.get_rect(center=cell_rect.center)
                        screen.blit(placeholder_surface, placeholder_rect)
            
            logger.debug(f"Character grid drawn with {chars_drawn} characters")
            
        except Exception as e:
            logger.error(f"Error drawing character grid: {e}", exc_info=True)

    def _draw_footer(self, screen):
        """Draw the footer with instructions."""
        try:
            instructions = [
                "A/D: Navigate | Joystick: Move cursor",
                "ENTER: Select character | Hold A: Cancel"
            ]
            
            y_offset = self.footer_y
            for instruction in instructions:
                instruction_surface = self.footer_font.render(instruction, True, self.config.Theme.FOREGROUND)
                instruction_rect = instruction_surface.get_rect(centerx=self.screen_rect.centerx, y=y_offset)
                screen.blit(instruction_surface, instruction_rect)
                y_offset += 20
                
            logger.debug("Footer instructions drawn")
            
        except Exception as e:
            logger.error(f"Error drawing footer: {e}")

    def set_fonts(self, fonts):
        """Update the fonts used by the character selector."""
        if fonts:
            try:
                self._setup_fonts(fonts)
                logger.info("Character selector fonts updated successfully")
            except Exception as e:
                logger.warning(f"Error updating fonts, keeping current: {e}") 