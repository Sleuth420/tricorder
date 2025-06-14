import pygame
import logging

logger = logging.getLogger(__name__)

def display_critical_error_on_screen(screen, fonts, config_module, messages):
    """Helper function to display critical error messages if possible."""
    if screen and fonts and config_module and pygame.get_init() and pygame.display.get_active():
        try:
            screen.fill(config_module.Theme.BACKGROUND)
            error_font_size = config_module.FONT_SIZE_MEDIUM
            try:
                # Try to use a pre-loaded font if available, otherwise default system font
                error_font = fonts.get('medium', pygame.font.Font(None, error_font_size))
            except Exception: 
                error_font = pygame.font.Font(None, config_module.FONT_SIZE_LARGE) # Absolute fallback

            current_y = screen.get_height() // 4 # Start a bit higher
            center_x = screen.get_width() // 2

            for i, msg_text in enumerate(messages):
                msg_sf = error_font.render(msg_text, True, config_module.Theme.ALERT)
                msg_pos = (center_x - msg_sf.get_width() // 2, current_y)
                screen.blit(msg_sf, msg_pos)
                current_y += msg_sf.get_height() + 5
                if i == 0: # Add extra space after the first line (typically the error type)
                    current_y += 5
            
            pygame.display.flip()
            pygame.time.wait(5000) # Show error for 5 seconds
        except Exception as display_e:
            logger.error(f"Failed to display critical error message on screen: {display_e}", exc_info=True)
    else:
        logger.warning("Screen, fonts, or Pygame not available/active for displaying critical error message.") 