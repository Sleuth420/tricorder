# --- ui/components/opengl_renderer.py ---
# Handles OpenGL rendering for 3D models using standard PyOpenGL

import pygame
import numpy as np
import math
import logging

# Standard PyOpenGL imports
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("PyOpenGL imported successfully")
except ImportError:
    OPENGL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error("PyOpenGL not available")

class OpenGLRenderer:
    def __init__(self, screen_width, screen_height, config_module):
        """Initialize OpenGL renderer for direct rendering."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config_module
        self.initialized = False
        
        if not OPENGL_AVAILABLE:
            logger.error("PyOpenGL not available")
            return
            
        logger.info("OpenGL renderer created (deferred initialization)")
        
    def _init_opengl(self):
        """Initialize OpenGL settings - called only when in OpenGL context."""
        try:
            # Set viewport to full screen dimensions
            glViewport(0, 0, self.screen_width, self.screen_height)
            
            # Set up projection matrix
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            # Calculate aspect ratio properly
            aspect_ratio = float(self.screen_width) / float(self.screen_height)
            gluPerspective(45.0, aspect_ratio, 0.1, 100.0)
            
            # Set up model-view matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # Enable depth testing
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            
            # Set background color to black
            glClearColor(0.0, 0.0, 0.0, 1.0)
            
            self.initialized = True
            logger.info(f"OpenGL initialized successfully: viewport={self.screen_width}x{self.screen_height}, aspect={aspect_ratio:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenGL: {e}")
            self.initialized = False
    
    def reset_for_new_context(self):
        """Reset the renderer when switching to a new OpenGL context."""
        self.initialized = False
        logger.info("OpenGL renderer reset for new context")
    
    def render(self, pitch, roll, yaw, fonts=None, ship_info=None, pause_menu_active=False, pause_menu_index=0):
        """
        Render a 3D cube with the given rotation and optional text overlay.
        This is called when the display is already in OpenGL mode.
        """
        if not OPENGL_AVAILABLE:
            return False
            
        # Always try to initialize/reinitialize if not done yet or context changed
        # We detect context changes by attempting a simple OpenGL call
        if not self.initialized:
            self._init_opengl()
            if not self.initialized:
                return False
        else:
            # Test if the current context is still valid
            try:
                # Try a simple OpenGL call to detect invalid context
                glGetError()  # Clear any existing errors
                glMatrixMode(GL_MODELVIEW)  # Simple test call
                error = glGetError()
                if error != GL_NO_ERROR:
                    logger.warning(f"OpenGL context appears invalid (error {error}), reinitializing")
                    self.initialized = False
                    self._init_opengl()
                    if not self.initialized:
                        return False
            except Exception as e:
                logger.warning(f"OpenGL context test failed: {e}, reinitializing")
                self.initialized = False
                self._init_opengl()
                if not self.initialized:
                    return False
        
        try:
            # Clear the screen and depth buffer
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Draw pause menu or normal 3D view
            if pause_menu_active and fonts:
                # Full-screen pause menu - don't draw cube
                self._draw_pause_menu_overlay(fonts, pause_menu_index, pitch, roll, yaw)
            else:
                # Normal 3D view - draw cube and overlays
                # Reset the model-view matrix
                glLoadIdentity()
                
                # Move back from the origin
                glTranslatef(0.0, 0.0, -5.0)
                
                # Apply rotation from sensor data
                glRotatef(math.degrees(pitch), 1.0, 0.0, 0.0)
                glRotatef(math.degrees(roll), 0.0, 0.0, 1.0)
                glRotatef(math.degrees(yaw), 0.0, 1.0, 0.0)
                
                # Draw a colored cube
                self._draw_cube()
                
                # Draw text overlay and footer controls
                if fonts:
                    if ship_info:
                        self._draw_text_overlay(fonts, ship_info, pitch, roll, yaw)
                    # Always show footer controls when not in pause menu
                    self._draw_footer_controls(fonts)
            
            # No need to swap buffers - pygame handles this
            return True
            
        except Exception as e:
            logger.error(f"OpenGL rendering error: {e}")
            # Mark as uninitialized so it will try to reinitialize next time
            self.initialized = False
            return False
    
    def _draw_cube(self):
        """Draw a colored cube using immediate mode OpenGL."""
        
        # Define cube vertices
        vertices = [
            # Front face (red)
            (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1),
            # Back face (green)
            (-1, -1, -1), (-1,  1, -1), ( 1,  1, -1), ( 1, -1, -1),
            # Top face (blue)
            (-1,  1, -1), (-1,  1,  1), ( 1,  1,  1), ( 1,  1, -1),
            # Bottom face (yellow)
            (-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1),
            # Right face (magenta)
            ( 1, -1, -1), ( 1,  1, -1), ( 1,  1,  1), ( 1, -1,  1),
            # Left face (cyan)
            (-1, -1, -1), (-1, -1,  1), (-1,  1,  1), (-1,  1, -1)
        ]
        
        # Define face colors
        colors = [
            (1.0, 0.0, 0.0),  # Red
            (0.0, 1.0, 0.0),  # Green  
            (0.0, 0.0, 1.0),  # Blue
            (1.0, 1.0, 0.0),  # Yellow
            (1.0, 0.0, 1.0),  # Magenta
            (0.0, 1.0, 1.0)   # Cyan
        ]
        
        # Draw each face
        glBegin(GL_QUADS)
        for face in range(6):
            glColor3f(*colors[face])
            for vertex in range(4):
                vertex_index = face * 4 + vertex
                glVertex3f(*vertices[vertex_index])
        glEnd()
    
    def _draw_text_overlay(self, fonts, ship_info, pitch, roll, yaw):
        """Draw text overlay on OpenGL surface using 2D projection."""
        # Save current matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # Set up 2D orthographic projection for text (standard OpenGL: bottom-left origin)
        glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing for text overlay
        glDisable(GL_DEPTH_TEST)
        
        try:
            # Create text surfaces using pygame
            info_font = fonts.get('small', fonts.get('medium'))
            
            # Ship info
            name_text = f"Model: {ship_info.get('name', 'Unknown')}"
            desc_text = ship_info.get('description', 'No description')[:50] + "..." if len(ship_info.get('description', '')) > 50 else ship_info.get('description', '')
            
            # Rotation info  
            rotation_text = f"Pitch: {math.degrees(pitch):.1f}° Roll: {math.degrees(roll):.1f}° Yaw: {math.degrees(yaw):.1f}°"
            
            # Render text to surfaces
            name_surface = info_font.render(name_text, True, (0, 255, 70))  # Sickbay green
            desc_surface = info_font.render(desc_text, True, (255, 255, 255))  # White
            rotation_surface = info_font.render(rotation_text, True, (255, 200, 0))  # Engineering gold
            
            # Convert pygame surfaces to OpenGL textures and draw them
            # Note: Y coordinates are from bottom now (OpenGL standard)
            self._draw_text_surface(name_surface, 10, self.screen_height - 30)  # Top of screen
            self._draw_text_surface(desc_surface, 10, self.screen_height - 50)  # Below name
            self._draw_text_surface(rotation_surface, 10, 50)  # Bottom of screen
            
        except Exception as e:
            logger.error(f"Error drawing text overlay: {e}")
        finally:
            # Restore previous state
            glEnable(GL_DEPTH_TEST)
            
            # Restore matrices
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
    
    def _draw_text_surface(self, surface, x, y):
        """Draw a pygame surface as an OpenGL texture."""
        try:
            # Convert surface to string format that OpenGL can use
            # Use False for flipped parameter to fix upside-down text
            text_data = pygame.image.tostring(surface, "RGBA", False)
            
            # Create and bind texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 
                        0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
            
            # Enable blending for text transparency
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_TEXTURE_2D)
            
            # Draw textured quad with corrected texture coordinates
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(x, y)
            glTexCoord2f(1, 1); glVertex2f(x + surface.get_width(), y)
            glTexCoord2f(1, 0); glVertex2f(x + surface.get_width(), y + surface.get_height())
            glTexCoord2f(0, 0); glVertex2f(x, y + surface.get_height())
            glEnd()
            
            # Cleanup
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glDeleteTextures([texture_id])
            
        except Exception as e:
            logger.error(f"Error drawing text surface: {e}")
    
    def _draw_pause_menu_overlay(self, fonts, pause_menu_index, pitch, roll, yaw):
        """Draw pause menu overlay on OpenGL surface using 2D projection."""
        # Save current matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # Set up 2D orthographic projection for text (standard OpenGL: bottom-left origin)
        glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing for menu overlay
        glDisable(GL_DEPTH_TEST)
        
        try:
            # Solid black background (full-screen menu)
            glDisable(GL_BLEND)  # No transparency needed
            glColor3f(0.0, 0.0, 0.0)  # Solid black
            
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(self.screen_width, 0)
            glVertex2f(self.screen_width, self.screen_height)
            glVertex2f(0, self.screen_height)
            glEnd()
            
            # Reset color back to white for text rendering
            glColor3f(1.0, 1.0, 1.0)
            
            # Menu title (convert Y from top-down to bottom-up)
            title_font = fonts.get('large', fonts.get('medium'))
            title_surface = title_font.render("3D VIEWER MENU", True, (255, 200, 0))
            title_x = (self.screen_width - title_surface.get_width()) // 2
            title_y = self.screen_height - 80  # Original was 80 from top
            self._draw_text_surface(title_surface, title_x, title_y)
            
            # Menu options (restore original layout)
            options = ["Toggle Mode", "Back to Ships", "Resume"]
            menu_font = fonts.get('medium', fonts.get('small'))
            start_y = 150  # Original start position from top
            item_height = 40
            
            for i, option in enumerate(options):
                y_pos = self.screen_height - (start_y + i * item_height)  # Convert to bottom-up
                color = (0, 255, 70) if i == pause_menu_index else (255, 255, 255)
                option_surface = menu_font.render(option, True, color)
                option_x = (self.screen_width - option_surface.get_width()) // 2
                self._draw_text_surface(option_surface, option_x, y_pos)
            
            # Current rotation values (restore original position)
            rotation_font = fonts.get('small', fonts.get('medium'))
            rotation_text = f"Pitch: {math.degrees(pitch):.1f}° Roll: {math.degrees(roll):.1f}° Yaw: {math.degrees(yaw):.1f}°"
            rotation_surface = rotation_font.render(rotation_text, True, (255, 200, 0))
            rotation_x = (self.screen_width - rotation_surface.get_width()) // 2
            rotation_y = self.screen_height - (start_y + len(options) * item_height + 20)  # Convert to bottom-up
            self._draw_text_surface(rotation_surface, rotation_x, rotation_y)
            
            # Controls hint (restore original position)
            hint_font = fonts.get('small', fonts.get('medium'))
            hint_text = "A/D: Navigate | Enter: Select | Hold A: Resume"
            hint_surface = hint_font.render(hint_text, True, (255, 255, 255))
            hint_x = (self.screen_width - hint_surface.get_width()) // 2
            hint_y = 40  # Original was 40 from bottom, which is still 40 from bottom
            self._draw_text_surface(hint_surface, hint_x, hint_y)
            
        except Exception as e:
            logger.error(f"Error drawing pause menu overlay: {e}")
        finally:
            # Restore previous state
            glEnable(GL_DEPTH_TEST)
            
            # Restore matrices
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

    def _draw_footer_controls(self, fonts):
        """Draw footer controls for OpenGL mode when pause menu is not active."""
        # Save current matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # Set up 2D orthographic projection for text
        glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing for text overlay
        glDisable(GL_DEPTH_TEST)
        
        try:
            # Footer controls
            hint_font = fonts.get('small', fonts.get('medium'))
            hint_text = "A/D: Rotate | Enter: Menu | Hold A: Back"
            hint_surface = hint_font.render(hint_text, True, (255, 255, 255))
            hint_x = (self.screen_width - hint_surface.get_width()) // 2
            hint_y = 20  # 20 pixels from bottom
            self._draw_text_surface(hint_surface, hint_x, hint_y)
            
        except Exception as e:
            logger.error(f"Error drawing footer controls: {e}")
        finally:
            # Restore previous state
            glEnable(GL_DEPTH_TEST)
            
            # Restore matrices
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

    def cleanup(self):
        """Clean up OpenGL resources."""
        # OpenGL cleanup is handled automatically by pygame
        self.initialized = False
        logger.info("OpenGL resources cleaned up")