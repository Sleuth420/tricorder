# --- models/ship_manager.py ---
# Manages 3D ship models and rendering for the schematics viewer

import pygame
import logging
import math
import time
from data import sensors

logger = logging.getLogger(__name__)

class Simple3DRenderer:
    """Simple software-based 3D renderer using pygame for maximum compatibility."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        
    def project_3d_to_2d(self, x, y, z, distance=3.0):
        """Project 3D coordinates to 2D screen coordinates with perspective."""
        if z + distance <= 0:
            z = -distance + 0.1  # Avoid division by zero
        factor = distance / (z + distance)
        screen_x = int(self.center_x + x * factor * 100)
        screen_y = int(self.center_y - y * factor * 100)  # Negative because screen Y is inverted
        return screen_x, screen_y
    
    def rotate_point(self, x, y, z, pitch, roll, yaw):
        """Rotate a 3D point by the given angles (in degrees)."""
        # Convert to radians
        pitch_rad = math.radians(pitch)
        roll_rad = math.radians(roll)
        yaw_rad = math.radians(yaw)
        
        # Rotation around X-axis (pitch)
        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)
        y1 = y * cos_pitch - z * sin_pitch
        z1 = y * sin_pitch + z * cos_pitch
        y, z = y1, z1
        
        # Rotation around Y-axis (yaw)
        cos_yaw = math.cos(yaw_rad)
        sin_yaw = math.sin(yaw_rad)
        x1 = x * cos_yaw + z * sin_yaw
        z1 = -x * sin_yaw + z * cos_yaw
        x, z = x1, z1
        
        # Rotation around Z-axis (roll)
        cos_roll = math.cos(roll_rad)
        sin_roll = math.sin(roll_rad)
        x1 = x * cos_roll - y * sin_roll
        y1 = x * sin_roll + y * cos_roll
        x, y = x1, y1
        
        return x, y, z

class ShipManager:
    """Manages ship models and 3D rendering for the schematics viewer."""
    
    def __init__(self, config_module, screen_width, screen_height):
        self.config = config_module
        self.renderer = Simple3DRenderer(screen_width, screen_height)
        
        # Current rotation values
        self.pitch = 0.0
        self.roll = 0.0  
        self.yaw = 0.0
        
        # Rotation mode control
        self.auto_rotation_mode = True  # True = use sensors, False = manual only
        self.manual_rotation_speed = 2.0  # degrees per frame when using keys
        
        # Ship models
        self.ship_models = {
            'test_cube': self._generate_test_cube(),
            'enterprise_nx01': self._generate_test_ship()
        }
        
        self.current_ship_model = 'test_cube'
        logger.info("ShipManager initialized with simple 3D renderer")
    
    def _generate_test_cube(self):
        """Generate vertices and edges for a simple test cube."""
        # Cube vertices
        vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Back face
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Front face
        ]
        
        # Cube edges (vertex index pairs)
        edges = [
            # Back face
            (0, 1), (1, 2), (2, 3), (3, 0),
            # Front face  
            (4, 5), (5, 6), (6, 7), (7, 4),
            # Connecting edges
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        return {'vertices': vertices, 'edges': edges, 'name': 'Test Cube'}
    
    def _generate_test_ship(self):
        """Generate vertices and edges for a simple ship-like shape."""
        # Simple ship shape - like a triangular prism
        vertices = [
            # Nose
            [0, 0, 2],
            # Body section
            [-1, -0.5, 0], [1, -0.5, 0], [1, 0.5, 0], [-1, 0.5, 0],
            # Tail section
            [-0.5, -0.3, -2], [0.5, -0.3, -2], [0.5, 0.3, -2], [-0.5, 0.3, -2]
        ]
        
        edges = [
            # Nose to body
            (0, 1), (0, 2), (0, 3), (0, 4),
            # Body rectangle
            (1, 2), (2, 3), (3, 4), (4, 1),
            # Body to tail
            (1, 5), (2, 6), (3, 7), (4, 8),
            # Tail rectangle
            (5, 6), (6, 7), (7, 8), (8, 5)
        ]
        
        return {'vertices': vertices, 'edges': edges, 'name': 'Enterprise NX-01'}
    
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
        vertices = ship_model['vertices']
        edges = ship_model['edges']
        
        # Clear screen
        screen.fill(config_module.Theme.BACKGROUND)
        
        # Transform and project vertices
        projected_vertices = []
        for vertex in vertices:
            x, y, z = vertex
            # Apply rotation
            rotated_x, rotated_y, rotated_z = self.renderer.rotate_point(
                x, y, z, self.pitch, self.roll, self.yaw
            )
            # Project to 2D
            screen_x, screen_y = self.renderer.project_3d_to_2d(
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
        
        # Draw ship info
        info_font = fonts.get('small', fonts.get('medium'))
        ship_name = ship_model['name']
        
        # Ship name
        name_surface = info_font.render(f"Ship: {ship_name}", True, config_module.Theme.FOREGROUND)
        screen.blit(name_surface, (10, 10))
        
        # Rotation values
        rotation_text = f"P:{self.pitch:.1f}° R:{self.roll:.1f}° Y:{self.yaw:.1f}°"
        rotation_surface = info_font.render(rotation_text, True, config_module.Theme.FOREGROUND)
        screen.blit(rotation_surface, (10, 30))
        
        # Rotation mode indicator
        mode_text = f"Mode: {'Auto (Sensor)' if self.auto_rotation_mode else 'Manual'}"
        mode_surface = info_font.render(mode_text, True, config_module.Theme.ACCENT)
        screen.blit(mode_surface, (10, 50))
        
        # Controls help
        help_text = "Hold D or Middle Press = Menu"
        help_surface = info_font.render(help_text, True, config_module.Theme.FOREGROUND)
        help_rect = help_surface.get_rect(centerx=screen.get_width()//2, bottom=screen.get_height()-10)
        screen.blit(help_surface, help_rect)
    
    def get_current_ship_info(self):
        """Get information about the currently selected ship."""
        if self.current_ship_model in self.ship_models:
            ship_model = self.ship_models[self.current_ship_model]
            return {
                'model_key': self.current_ship_model,
                'name': ship_model['name'],
                'vertex_count': len(ship_model['vertices']),
                'edge_count': len(ship_model['edges'])
            }
        return None 