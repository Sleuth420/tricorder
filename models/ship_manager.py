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
    from ui.components.opengl_model_renderer import OpenGLModelRenderer
    from ui.components.obj_loader import OBJLoader
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
        """Initialize the ship manager."""
        self.config = config_module
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Current rotation values (in degrees)
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        
        # Rotation mode (True = auto/sensor, False = manual)
        self.auto_rotation_mode = True
        self.manual_rotation_speed = 5.0  # Degrees per keypress
        
        # Available ship models
        self.ship_models = {
            'test_cube': self._generate_test_cube(),
            'opengl_test': self._generate_opengl_test(),
            'apollo_1570': self._generate_apollo_model()
        }
        
        # Current active model
        self.current_ship_model = 'test_cube'
        
        # Initialize renderers
        self.wireframe_renderer = Simple3DRenderer(screen_width, screen_height)
        self.opengl_renderer = None  # Created on demand
        self.model_renderer = None   # Created on demand for OBJ models
        
        # Loaded OBJ models cache
        self.loaded_obj_models = {}  # Cache for loaded OBJ models
        
        # Sensor smoothing for noise reduction
        self.smoothing_enabled = True
        self.smoothing_factor = 0.15  # How much new reading affects result (0.1 = very smooth, 0.5 = responsive)
        self.deadzone = 2.0  # Ignore changes smaller than this (degrees)
        self.sensitivity = 0.8  # Overall sensitivity multiplier (0.5 = half sensitivity)
        
        # Smoothed sensor values (moving average)
        self.smoothed_pitch = 0.0
        self.smoothed_roll = 0.0
        self.smoothed_yaw = 0.0
        
        # Previous raw readings for change detection
        self.prev_raw_pitch = None
        self.prev_raw_roll = None  
        self.prev_raw_yaw = None
        
        logger.info(f"Ship manager initialized with sensor smoothing: factor={self.smoothing_factor}, deadzone={self.deadzone}°, sensitivity={self.sensitivity}")
    
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
    
    def _generate_apollo_model(self):
        """Generate Apollo OpenGL model definition."""
        return {
            "name": "Apollo NCC-1570",
            "type": "opengl_model",
            "model_key": "apollo_1570",
            "file_path": "assets/apollo_ncc1570/Apollo_NCC1570.obj",
            "implemented": True,
            "vertices": [],  # Will be loaded from OBJ file
            "edges": [],
            "description": "Apollo-class light cruiser from Star Trek"
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
        """Update rotation values from sensehat tilt sensors with smoothing and filtering."""
        # Only update from sensors if in auto mode
        if not self.auto_rotation_mode:
            return False
            
        try:
            orientation = sensors.get_orientation()
            if orientation:
                # Get raw sensor readings
                raw_pitch = orientation.get('pitch', 0.0)
                raw_roll = orientation.get('roll', 0.0) 
                raw_yaw = orientation.get('yaw', 0.0)
                
                # Apply smoothing filter if enabled
                if self.smoothing_enabled:
                    # Initialize smoothed values on first reading
                    if self.prev_raw_pitch is None:
                        self.smoothed_pitch = raw_pitch
                        self.smoothed_roll = raw_roll
                        self.smoothed_yaw = raw_yaw
                        self.prev_raw_pitch = raw_pitch
                        self.prev_raw_roll = raw_roll
                        self.prev_raw_yaw = raw_yaw
                        logger.debug("Initialized sensor smoothing with first readings")
                    else:
                        # Apply moving average filter (low-pass filter)
                        self.smoothed_pitch = self._smooth_angle(self.smoothed_pitch, raw_pitch)
                        self.smoothed_roll = self._smooth_angle(self.smoothed_roll, raw_roll)
                        self.smoothed_yaw = self._smooth_angle(self.smoothed_yaw, raw_yaw)
                    
                    # Apply deadzone and sensitivity
                    filtered_pitch = self._apply_deadzone_and_sensitivity(self.pitch, self.smoothed_pitch)
                    filtered_roll = self._apply_deadzone_and_sensitivity(self.roll, self.smoothed_roll)
                    filtered_yaw = self._apply_deadzone_and_sensitivity(self.yaw, self.smoothed_yaw)
                    
                    # Update rotation values
                    self.pitch = filtered_pitch
                    self.roll = filtered_roll
                    self.yaw = filtered_yaw
                else:
                    # No smoothing - direct assignment
                    self.pitch = raw_pitch * self.sensitivity
                    self.roll = raw_roll * self.sensitivity
                    self.yaw = raw_yaw * self.sensitivity
                
                # Store previous readings
                self.prev_raw_pitch = raw_pitch
                self.prev_raw_roll = raw_roll
                self.prev_raw_yaw = raw_yaw
                
                return True
        except Exception as e:
            logger.debug(f"Could not read sensor orientation: {e}")
        return False
    
    def _smooth_angle(self, current_smooth, new_raw):
        """Apply exponential moving average to an angle, handling 360-degree wraparound."""
        # Handle angle wraparound (e.g., 359° to 1°)
        diff = new_raw - current_smooth
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        # Apply smoothing factor
        smoothed = current_smooth + (diff * self.smoothing_factor)
        
        # Normalize to 0-360 range
        return smoothed % 360
    
    def _apply_deadzone_and_sensitivity(self, current_value, target_value):
        """Apply deadzone and sensitivity scaling to prevent jitter."""
        # Calculate the change
        change = target_value - current_value
        
        # Handle angle wraparound
        if change > 180:
            change -= 360
        elif change < -180:
            change += 360
        
        # Apply deadzone - ignore small changes
        if abs(change) < self.deadzone:
            return current_value
        
        # Apply sensitivity scaling to the change
        scaled_change = change * self.sensitivity
        
        # Apply the scaled change
        new_value = current_value + scaled_change
        
        # Normalize to 0-360 range
        return new_value % 360
        
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
    
    def render_ship(self, screen, fonts, config_module, pause_menu_active=False, pause_menu_index=0):
        """Render the current ship model to the screen."""
        if self.current_ship_model not in self.ship_models:
            logger.error(f"Cannot render unknown ship model: {self.current_ship_model}")
            return
        
        ship_model = self.ship_models[self.current_ship_model]
        
        # Handle different model types
        if ship_model.get('type') == 'opengl':
            self._render_opengl_model(screen, ship_model, fonts, config_module, pause_menu_active, pause_menu_index)
        elif ship_model.get('type') == 'opengl_model':
            self._render_obj_model(screen, ship_model, fonts, config_module, pause_menu_active, pause_menu_index)
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
    
    def _render_opengl_model(self, screen, ship_model, fonts, config_module, pause_menu_active=False, pause_menu_index=0):
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
            
            # Render the cube with text overlay and pause menu
            success = self.opengl_renderer.render(
                self.pitch, self.roll, self.yaw, fonts, ship_model,
                pause_menu_active, pause_menu_index
            )
            
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
    
    def _render_obj_model(self, screen, ship_model, fonts, config_module, pause_menu_active=False, pause_menu_index=0):
        """Render OBJ model using OpenGL with model renderer."""
        if not OPENGL_AVAILABLE:
            self._render_obj_fallback(screen, ship_model, fonts, config_module)
            return
        
        try:
            # Load OBJ model if not already loaded
            obj_model = self._load_obj_model(ship_model)
            if not obj_model:
                self._render_obj_fallback(screen, ship_model, fonts, config_module)
                return
            
            # Create model renderer if needed  
            if not self.model_renderer:
                self.model_renderer = OpenGLModelRenderer(
                    self.screen_width, self.screen_height, self.config
                )
                logger.info("OpenGL model renderer created")
            
            # Load model into renderer if not already loaded
            if not self.model_renderer.loaded_model:
                success = self.model_renderer.load_model(obj_model)
                if not success:
                    logger.error("Failed to load OBJ model into renderer")
                    self._render_obj_fallback(screen, ship_model, fonts, config_module)
                    return
            
            # Render the model with text overlay and pause menu
            success = self.model_renderer.render(
                self.pitch, self.roll, self.yaw, fonts, ship_model,
                pause_menu_active, pause_menu_index
            )
            
            if not success:
                # Fallback if OpenGL fails
                self._render_obj_fallback(screen, ship_model, fonts, config_module)
        except Exception as e:
            logger.error(f"OBJ model rendering failed: {e}", exc_info=True)
            self._render_obj_fallback(screen, ship_model, fonts, config_module)
    
    def _load_obj_model(self, ship_model):
        """Load an OBJ model from file, with caching."""
        file_path = ship_model.get('file_path')
        if not file_path:
            logger.error("No file path specified for OBJ model")
            return None
        
        # Check cache first
        if file_path in self.loaded_obj_models:
            return self.loaded_obj_models[file_path]
        
        # Load from file
        logger.info(f"Loading OBJ model from: {file_path}")
        obj_model = OBJLoader.load(file_path)
        
        if obj_model:
            # Cache the loaded model
            self.loaded_obj_models[file_path] = obj_model
            logger.info(f"OBJ model loaded and cached: {file_path}")
        else:
            logger.error(f"Failed to load OBJ model: {file_path}")
        
        return obj_model
    
    def _render_obj_fallback(self, screen, ship_model, fonts, config_module):
        """Fallback rendering when OBJ model loading fails."""
        screen.fill(config_module.Theme.BACKGROUND)
        
        font = fonts['medium']
        error_text = f"Failed to Load: {ship_model['name']}"
        error_surface = font.render(error_text, True, config_module.Theme.ALERT)
        error_rect = error_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 30))
        screen.blit(error_surface, error_rect)
        
        # Show file path
        path_font = fonts['small']
        path_text = f"File: {ship_model.get('file_path', 'No path specified')}"
        path_surface = path_font.render(path_text, True, config_module.Theme.FOREGROUND)
        path_rect = path_surface.get_rect(center=(screen.get_width()//2, error_rect.bottom + 20))
        screen.blit(path_surface, path_rect)
        
        # Show suggestions
        suggestion_text = "Check if file exists and PyOpenGL is installed"
        suggestion_surface = path_font.render(suggestion_text, True, config_module.Theme.FOREGROUND)
        suggestion_rect = suggestion_surface.get_rect(center=(screen.get_width()//2, path_rect.bottom + 20))
        screen.blit(suggestion_surface, suggestion_rect)
        
        self._draw_ship_info(screen, ship_model, fonts, config_module)
    
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
    
    def adjust_sensor_sensitivity(self, sensitivity=None, deadzone=None, smoothing_factor=None):
        """Adjust sensor filtering parameters for fine-tuning responsiveness."""
        if sensitivity is not None:
            self.sensitivity = max(0.1, min(2.0, sensitivity))  # Clamp between 0.1 and 2.0
            logger.info(f"Sensor sensitivity adjusted to: {self.sensitivity}")
        
        if deadzone is not None:
            self.deadzone = max(0.0, min(10.0, deadzone))  # Clamp between 0 and 10 degrees
            logger.info(f"Sensor deadzone adjusted to: {self.deadzone}°")
        
        if smoothing_factor is not None:
            self.smoothing_factor = max(0.05, min(1.0, smoothing_factor))  # Clamp between 0.05 and 1.0
            logger.info(f"Sensor smoothing factor adjusted to: {self.smoothing_factor}")
    
    def reset_sensor_smoothing(self):
        """Reset sensor smoothing state (useful when switching modes)."""
        self.prev_raw_pitch = None
        self.prev_raw_roll = None
        self.prev_raw_yaw = None
        self.smoothed_pitch = 0.0
        self.smoothed_roll = 0.0
        self.smoothed_yaw = 0.0
        logger.debug("Sensor smoothing state reset") 