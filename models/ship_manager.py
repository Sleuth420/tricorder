# --- models/ship_manager.py ---
# Handles ship 3D model management and rendering

import pygame
import math
import logging
import os
from data import sensors

# OpenGL imports (optional - will be checked for availability)
try:
    from ui.components.opengl_renderer import OpenGLRenderer
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False

logger = logging.getLogger(__name__)

class Simple3DRenderer:
    """Basic 3D to 2D projection renderer for wireframe models."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2

    def project_3d_to_2d(self, x, y, z, distance=3.0):
        """Project 3D coordinates to 2D screen coordinates."""
        # Simple perspective projection
        scale = distance / (distance + z)
        screen_x = self.center_x + (x * scale * 100)
        screen_y = self.center_y - (y * scale * 100)  # Invert Y axis
        return int(screen_x), int(screen_y)

    def rotate_point(self, x, y, z, pitch, roll, yaw):
        """Rotate a 3D point using pitch, roll, yaw angles."""
        # Convert degrees to radians
        pitch_rad = math.radians(pitch)
        roll_rad = math.radians(roll)
        yaw_rad = math.radians(yaw)
        
        # Rotation matrices
        # Roll (rotation around Z axis)
        cos_roll = math.cos(roll_rad)
        sin_roll = math.sin(roll_rad)
        x1 = x * cos_roll - y * sin_roll
        y1 = x * sin_roll + y * cos_roll
        z1 = z
        
        # Pitch (rotation around X axis)
        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)
        x2 = x1
        y2 = y1 * cos_pitch - z1 * sin_pitch
        z2 = y1 * sin_pitch + z1 * cos_pitch
        
        # Yaw (rotation around Y axis)
        cos_yaw = math.cos(yaw_rad)
        sin_yaw = math.sin(yaw_rad)
        x3 = x2 * cos_yaw + z2 * sin_yaw
        y3 = y2
        z3 = -x2 * sin_yaw + z2 * cos_yaw
        
        return x3, y3, z3

class ShipManager:
    """Manages 3D ship models and rendering."""
    
    def __init__(self, config_module, screen_width, screen_height):
        self.config = config_module
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 3D rendering
        self.wireframe_renderer = Simple3DRenderer(screen_width, screen_height)
        
        # OpenGL renderer
        self.opengl_renderer = None
        
        # Rotation state
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        
        # Rotation control
        self.auto_rotation_mode = True  # Start with sensor auto-rotation
        self.manual_rotation_speed = 5.0  # Degrees per input
        
        # Available ship models
        self.ship_models = {
            "test_cube": self._generate_test_cube(),
            "opengl_test": self._generate_opengl_test(),
            "stargate_x304": self._generate_stargate_placeholder()
        }
        
        # Current model
        self.current_ship_model = "test_cube"
    
    def _generate_test_cube(self):
        """Generate a simple wireframe cube for testing."""
        return {
            "name": "Test Cube",
            "type": "wireframe",
            "vertices": [
                (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Back face
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)   # Front face
            ],
            "edges": [
                (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
                (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
                (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
            ],
            "description": "Wireframe test cube"
        }
    
    def _generate_opengl_test(self):
        """Generate OpenGL test model definition."""
        return {
            "name": "OpenGL Test",
            "type": "opengl",
            "vertices": [],  # OpenGL renderer handles its own geometry
            "edges": [],
            "description": "GPU-rendered green cube with real OpenGL shaders"
        }
    
    def _generate_stargate_placeholder(self):
        """Generate placeholder for Stargate X-304 model."""
        return {
            "name": "Stargate SG-1 X-304",
            "type": "model_file",
            "file_path": "assets/stargate_304/X304_ship.obj",
            "implemented": False,
            "vertices": [],
            "edges": [],
            "description": "Daedalus-class battlecruiser from Stargate SG-1"
        }
    
    def set_ship_model(self, ship_model_key):
        """Set the current ship model to display."""
        if ship_model_key in self.ship_models:
            self.current_ship_model = ship_model_key
            logger.info(f"Ship model set to: {ship_model_key}")
            return True
        else:
            logger.warning(f"Unknown ship model: {ship_model_key}")
            return False
    
    def update_rotation_from_sensors(self):
        """Update rotation values from sensehat tilt sensors."""
        # Only update from sensors if in auto mode
        if not self.auto_rotation_mode:
            return False
            
        try:
            orientation = sensors.get_orientation()
            if orientation:
                # Map sensehat orientation to our rotation values
                # You may need to adjust these mappings based on how the sensehat is oriented
                self.pitch = orientation.get('pitch', 0.0)
                self.roll = orientation.get('roll', 0.0) 
                self.yaw = orientation.get('yaw', 0.0)
                return True
        except Exception as e:
            logger.debug(f"Could not read sensor orientation: {e}")
        return False
        
    def toggle_rotation_mode(self):
        """Toggle between auto (sensor) and manual rotation modes."""
        self.auto_rotation_mode = not self.auto_rotation_mode
        mode_name = "Auto (Sensor)" if self.auto_rotation_mode else "Manual"
        logger.info(f"Rotation mode switched to: {mode_name}")
        return self.auto_rotation_mode
    
    def apply_manual_rotation(self, direction):
        """Apply manual rotation using keyboard/joystick controls."""
        if direction == 'LEFT':
            self.yaw -= self.manual_rotation_speed
        elif direction == 'RIGHT':
            self.yaw += self.manual_rotation_speed
        elif direction == 'UP':
            self.pitch -= self.manual_rotation_speed
        elif direction == 'DOWN':
            self.pitch += self.manual_rotation_speed
        
        # Keep angles in reasonable range
        self.pitch = self.pitch % 360
        self.roll = self.roll % 360
        self.yaw = self.yaw % 360
    
    def render_ship(self, screen, fonts, config_module):
        """Render the current ship model to the screen."""
        if self.current_ship_model not in self.ship_models:
            logger.error(f"Cannot render unknown ship model: {self.current_ship_model}")
            return
        
        ship_model = self.ship_models[self.current_ship_model]
        
        # Handle different model types
        if ship_model.get('type') == 'opengl':
            self._render_opengl_model(screen, ship_model, fonts, config_module)
        elif ship_model.get('type') == 'model_file':
            if ship_model.get('implemented', False):
                self._render_model_file(screen, ship_model, fonts, config_module)
            else:
                self._render_not_implemented(screen, ship_model, fonts, config_module)
        else:
            # Default wireframe rendering for test_cube
            self._render_wireframe_model(screen, ship_model, fonts, config_module)
    
    def _render_wireframe_model(self, screen, ship_model, fonts, config_module):
        """Render wireframe model (test_cube)."""
        vertices = ship_model['vertices']
        edges = ship_model['edges']
        
        # Clear screen
        screen.fill(config_module.Theme.BACKGROUND)
        
        # Transform and project vertices
        projected_vertices = []
        for vertex in vertices:
            x, y, z = vertex
            # Apply rotation
            rotated_x, rotated_y, rotated_z = self.wireframe_renderer.rotate_point(
                x, y, z, self.pitch, self.roll, self.yaw
            )
            # Project to 2D
            screen_x, screen_y = self.wireframe_renderer.project_3d_to_2d(
                rotated_x, rotated_y, rotated_z
            )
            projected_vertices.append((screen_x, screen_y))
        
        # Draw edges
        line_color = config_module.Theme.FOREGROUND
        for edge in edges:
            start_idx, end_idx = edge
            if 0 <= start_idx < len(projected_vertices) and 0 <= end_idx < len(projected_vertices):
                start_pos = projected_vertices[start_idx]
                end_pos = projected_vertices[end_idx]
                
                # Only draw if both points are on screen
                if (0 <= start_pos[0] < screen.get_width() and 0 <= start_pos[1] < screen.get_height() and
                    0 <= end_pos[0] < screen.get_width() and 0 <= end_pos[1] < screen.get_height()):
                    pygame.draw.line(screen, line_color, start_pos, end_pos, 2)
        
        # Draw vertices as small circles
        vertex_color = config_module.Theme.ACCENT
        for vertex_pos in projected_vertices:
            if 0 <= vertex_pos[0] < screen.get_width() and 0 <= vertex_pos[1] < screen.get_height():
                pygame.draw.circle(screen, vertex_color, vertex_pos, 3)
        
        self._draw_ship_info(screen, ship_model, fonts, config_module)
    
    def _render_opengl_model(self, screen, ship_model, fonts, config_module):
        """Render using actual OpenGL with GPU shaders directly to screen."""
        if not OPENGL_AVAILABLE:
            self._render_opengl_fallback(screen, ship_model, fonts, config_module)
            return
        
        try:
            # Create OpenGL renderer if needed  
            if not self.opengl_renderer:
                self.opengl_renderer = OpenGLRenderer(
                    self.screen_width, self.screen_height, self.config
                )
                logger.info("PyOpenGL renderer created")
            
            # Render the cube
            success = self.opengl_renderer.render(self.pitch, self.roll, self.yaw)
            
            if not success:
                # Fallback if OpenGL fails
                self._render_opengl_fallback(screen, ship_model, fonts, config_module)
        except Exception as e:
            logger.error(f"PyOpenGL rendering failed: {e}")
            self._render_opengl_fallback(screen, ship_model, fonts, config_module)
    

    
    def _render_opengl_fallback(self, screen, ship_model, fonts, config_module):
        """Fallback rendering when OpenGL is not available."""
        screen.fill(config_module.Theme.BACKGROUND)
        
        font = fonts['medium']
        error_text = "OpenGL Not Available"
        error_surface = font.render(error_text, True, config_module.Theme.ALERT)
        error_rect = error_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(error_surface, error_rect)
        
        # Show fallback message
        fallback_font = fonts['small']
        fallback_text = "Install PyOpenGL to enable GPU rendering"
        fallback_surface = fallback_font.render(fallback_text, True, config_module.Theme.FOREGROUND)
        fallback_rect = fallback_surface.get_rect(center=(screen.get_width()//2, error_rect.bottom + 30))
        screen.blit(fallback_surface, fallback_rect)
    
    def _render_model_file(self, screen, ship_model, fonts, config_module):
        """Render a 3D model from file (future implementation for X-304)."""
        screen.fill(config_module.Theme.BACKGROUND)
        
        font = fonts['medium']
        title_text = f"Loading: {ship_model['name']}"
        title_surface = font.render(title_text, True, config_module.Theme.ACCENT)
        title_rect = title_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
        screen.blit(title_surface, title_rect)
        
        # Implementation status
        status_font = fonts['small']
        status_text = "OBJ file loading not yet implemented"
        status_surface = status_font.render(status_text, True, config_module.Theme.FOREGROUND)
        status_rect = status_surface.get_rect(center=(screen.get_width()//2, title_rect.bottom + 30))
        screen.blit(status_surface, status_rect)
        
        self._draw_ship_info(screen, ship_model, fonts, config_module)
    
    def _render_not_implemented(self, screen, ship_model, fonts, config_module):
        """Render placeholder for not-yet-implemented models."""
        screen.fill(config_module.Theme.BACKGROUND)
        
        font = fonts['large']
        title_text = ship_model['name']
        title_surface = font.render(title_text, True, config_module.Theme.ACCENT)
        title_rect = title_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
        screen.blit(title_surface, title_rect)
        
        # Not implemented message
        status_font = fonts['medium']
        status_text = "Not Yet Implemented"
        status_surface = status_font.render(status_text, True, config_module.Theme.ALERT)
        status_rect = status_surface.get_rect(center=(screen.get_width()//2, title_rect.bottom + 20))
        screen.blit(status_surface, status_rect)
        
        self._draw_ship_info(screen, ship_model, fonts, config_module)
    
    def _draw_ship_info(self, screen, ship_model, fonts, config_module):
        """Draw ship information and controls."""
        info_font = fonts['small']
        
        # Ship name and description
        name_text = f"Model: {ship_model['name']}"
        name_surface = info_font.render(name_text, True, config_module.Theme.FOREGROUND)
        screen.blit(name_surface, (10, 10))
        
        desc_text = ship_model.get('description', 'No description')
        desc_surface = info_font.render(desc_text, True, config_module.Theme.FOREGROUND)
        screen.blit(desc_surface, (10, 30))
        
        # Rotation info
        rotation_text = f"Pitch: {self.pitch:.1f}° Roll: {self.roll:.1f}° Yaw: {self.yaw:.1f}°"
        rotation_surface = info_font.render(rotation_text, True, config_module.Theme.FOREGROUND)
        screen.blit(rotation_surface, (10, screen.get_height() - 50))
        
        # Mode info
        mode_text = f"Mode: {'Auto (Sensor)' if self.auto_rotation_mode else 'Manual'}"
        mode_surface = info_font.render(mode_text, True, config_module.Theme.ACCENT)
        screen.blit(mode_surface, (10, screen.get_height() - 30))
    
    def get_current_ship_info(self):
        """Get information about the current ship model."""
        if self.current_ship_model in self.ship_models:
            ship_model = self.ship_models[self.current_ship_model]
            return {
                'model_key': self.current_ship_model,
                'name': ship_model['name'],
                'vertex_count': len(ship_model['vertices']),
                'edge_count': len(ship_model['edges']),
                'description': ship_model.get('description', 'No description')
            }
        return {"name": "Unknown", "description": "No ship model loaded", "model_key": None} 