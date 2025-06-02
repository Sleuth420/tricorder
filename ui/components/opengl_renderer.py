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
            # Set up projection matrix
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, self.screen_width / self.screen_height, 0.1, 100.0)
            
            # Set up model-view matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # Enable depth testing
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            
            # Set background color to black
            glClearColor(0.0, 0.0, 0.0, 1.0)
            
            self.initialized = True
            logger.info("OpenGL initialized successfully in proper context")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenGL: {e}")
            self.initialized = False
    
    def reset_for_new_context(self):
        """Reset the renderer when switching to a new OpenGL context."""
        self.initialized = False
        logger.info("OpenGL renderer reset for new context")
    
    def render(self, pitch, roll, yaw):
        """
        Render a 3D cube with the given rotation.
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

    def cleanup(self):
        """Clean up OpenGL resources."""
        # OpenGL cleanup is handled automatically by pygame
        self.initialized = False
        logger.info("OpenGL resources cleaned up")