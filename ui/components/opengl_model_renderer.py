# --- ui/components/opengl_model_renderer.py ---
# OpenGL renderer specifically for OBJ models

import pygame
import math
import logging
from typing import Optional, Dict, Any
import os

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False

from .obj_loader import OBJModel

logger = logging.getLogger(__name__)

class OpenGLModelRenderer:
    """OpenGL renderer for OBJ models that extends the basic OpenGL renderer functionality."""
    
    def __init__(self, screen_width, screen_height, config_module):
        """Initialize the model renderer."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config_module
        self.initialized = False
        
        # Model data
        self.loaded_model = None
        self.display_list = None  # OpenGL display list for performance
        self.model_scale = 1.0
        self.model_center = (0.0, 0.0, 0.0)
        
        # Texture management
        self.loaded_textures = {}  # Cache for loaded textures {material_name: texture_id}
        self.current_texture = None
        
        if not OPENGL_AVAILABLE:
            logger.error("PyOpenGL not available for model rendering")
            return
            
        logger.info("OpenGL model renderer created")
        
    def load_model(self, model: OBJModel) -> bool:
        """
        Load an OBJ model for rendering.
        
        Args:
            model (OBJModel): The loaded OBJ model
            
        Returns:
            bool: True if successful
        """
        if not model or not OPENGL_AVAILABLE:
            return False
            
        self.loaded_model = model
        
        # Calculate model scaling and centering
        self.model_center = model.get_center()
        self.model_scale = model.get_scale_factor(target_size=3.5)  # Larger for better visibility on small screens
        
        logger.info(f"Model loaded: center={self.model_center}, scale={self.model_scale}")
        
        # Clear any existing display list and textures
        self._cleanup_resources()
        
        # Don't load textures here - defer until OpenGL context is active
        # Textures will be loaded on first render
        logger.info(f"Model loaded with {len(model.materials)} materials (textures will load on first render)")
        
        return True
    
    def _load_model_textures(self, model: OBJModel):
        """Load textures for the model materials."""
        if not model.materials:
            logger.info("No materials found in model, using default material")
            return
        
        for material_name, material_data in model.materials.items():
            texture_id = self._load_material_texture(material_name, material_data)
            if texture_id:
                self.loaded_textures[material_name] = texture_id
                logger.info(f"Loaded texture for material: {material_name}")
    
    def _load_material_texture(self, material_name: str, material_data: Dict) -> Optional[int]:
        """Load texture for a specific material."""
        # Look for texture map in material data
        texture_path = None
        
        # Check for various texture map types
        if 'map_Kd' in material_data:  # Diffuse map
            texture_path = material_data['map_Kd']
        elif 'map_Ka' in material_data:  # Ambient map
            texture_path = material_data['map_Ka']
        
        if not texture_path:
            logger.debug(f"No texture map found for material: {material_name}")
            return None
        
        logger.info(f"Attempting to load texture for material '{material_name}': {texture_path}")
        
        # Convert relative path to absolute if needed
        if not os.path.isabs(texture_path):
            # Assume texture is relative to the model directory
            model_dir = os.path.dirname(self.loaded_model.file_path) if hasattr(self.loaded_model, 'file_path') else 'assets/apollo_ncc1570'
            texture_path = os.path.join(model_dir, texture_path)
            logger.info(f"Resolved texture path: {texture_path}")
        
        if not os.path.exists(texture_path):
            logger.warning(f"Texture file not found: {texture_path}")
            return None
        
        try:
            # Load texture using pygame
            logger.info(f"Loading texture file: {texture_path}")
            texture_surface = pygame.image.load(texture_path)
            
            # Convert to RGB format - pygame surfaces don't have get_format() method
            # Just convert to RGB directly
            texture_surface = texture_surface.convert()
            logger.debug("Converted texture to RGB format")
            
            texture_data = pygame.image.tostring(texture_surface, "RGB", False)
            
            width = texture_surface.get_width()
            height = texture_surface.get_height()
            
            logger.info(f"Texture loaded: {width}x{height} pixels")
            
            # Generate OpenGL texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
            
            logger.info(f"Texture uploaded to OpenGL successfully: {texture_path} (ID: {texture_id})")
            return texture_id
            
        except Exception as e:
            logger.error(f"Failed to load texture {texture_path}: {e}", exc_info=True)
            return None
        
    def _init_opengl(self):
        """Initialize OpenGL settings - called when in OpenGL context."""
        try:
            # Set viewport
            glViewport(0, 0, self.screen_width, self.screen_height)
            
            # Set up projection matrix
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            aspect_ratio = float(self.screen_width) / float(self.screen_height)
            gluPerspective(45.0, aspect_ratio, 0.1, 100.0)
            
            # Set up model-view matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # Enable depth testing
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            
            # Enable back-face culling for performance
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
            
            # Set background color
            glClearColor(0.0, 0.0, 0.0, 1.0)
            
            # Enable lighting for better model appearance
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            
            # Set up light
            light_pos = [5.0, 5.0, 5.0, 1.0]  # Positional light
            light_ambient = [0.2, 0.2, 0.2, 1.0]
            light_diffuse = [0.8, 0.8, 0.8, 1.0]
            light_specular = [1.0, 1.0, 1.0, 1.0]
            
            glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
            glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
            glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
            
            # Enable color material
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
            
            # Enable texturing
            glEnable(GL_TEXTURE_2D)
            
            self.initialized = True
            logger.info("OpenGL model renderer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenGL model renderer: {e}")
            self.initialized = False
    
    def reset_for_new_context(self):
        """Reset renderer for new OpenGL context."""
        self.initialized = False
        # Clear cached resources since they're invalid in new context
        self._cleanup_resources()
        logger.info("OpenGL model renderer reset for new context")
    
    def _cleanup_resources(self):
        """Clean up OpenGL resources."""
        if self.display_list:
            try:
                glDeleteLists(self.display_list, 1)
            except:
                pass
            self.display_list = None
        
        # Clean up textures
        for texture_id in self.loaded_textures.values():
            try:
                glDeleteTextures([texture_id])
            except:
                pass
        self.loaded_textures.clear()
    
    def render(self, pitch, roll, yaw, fonts=None, schematics_info=None, pause_menu_active=False, pause_menu_index=0, auto_rotation_mode=True):
        """
        Render the loaded model with given rotation.
        
        Args:
            pitch, roll, yaw: Rotation angles in degrees
            fonts: Font dictionary for text overlay
            schematics_info: Schematics information dictionary
            pause_menu_active: Whether pause menu is shown
            pause_menu_index: Selected pause menu index
            auto_rotation_mode: Whether in auto or manual rotation mode
            
        Returns:
            bool: True if rendering successful
        """
        if not OPENGL_AVAILABLE or not self.loaded_model:
            return False
            
        # Initialize if needed
        if not self.initialized:
            self._init_opengl()
            if not self.initialized:
                return False
        
        try:
            # Clear buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            if pause_menu_active and fonts:
                # Draw pause menu
                self._draw_pause_menu_overlay(fonts, pause_menu_index, pitch, roll, yaw, auto_rotation_mode)
            else:
                # Draw the 3D model
                self._render_model(pitch, roll, yaw)
                
                # Draw overlays
                if fonts:
                    if schematics_info:
                        self._draw_text_overlay(fonts, schematics_info, pitch, roll, yaw)
                    self._draw_footer_controls(fonts)
            
            return True
            
        except Exception as e:
            logger.error(f"Model rendering error: {e}")
            self.initialized = False
            return False
    
    def _render_model(self, pitch, roll, yaw):
        """Render the actual 3D model."""
        if not self.loaded_model:
            return
            
        # Create display list if not exists (for performance)
        if not self.display_list:
            self._create_display_list()
        
        # Set up model-view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Move camera back
        glTranslatef(0.0, 0.0, -5.0)
        
        # Apply rotations (pitch, roll, yaw are already in degrees)
        glRotatef(pitch, 1.0, 0.0, 0.0)
        glRotatef(roll, 0.0, 0.0, 1.0)
        glRotatef(yaw, 0.0, 1.0, 0.0)
        
        # Scale and center the model
        glScalef(self.model_scale, self.model_scale, self.model_scale)
        center_x, center_y, center_z = self.model_center
        glTranslatef(-center_x, -center_y, -center_z)
        
        # Render the model
        if self.display_list:
            glCallList(self.display_list)
        else:
            self._render_immediate_mode()
    
    def _create_display_list(self):
        """Create an OpenGL display list for efficient rendering."""
        if not self.loaded_model:
            return
            
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        
        self._render_immediate_mode()
        
        glEndList()
        logger.info("Display list created for model")
    
    def _render_immediate_mode(self):
        """Render model using immediate mode OpenGL."""
        if not self.loaded_model:
            return
            
        # Default material if no materials are defined
        default_material = {
            'diffuse': (0.7, 0.7, 0.7),
            'ambient': (0.2, 0.2, 0.2),
            'specular': (0.5, 0.5, 0.5),
            'shininess': 32.0
        }
        
        current_material = None
        current_texture_id = None
        
        # Track texture loading for progress (only on first render)
        materials_to_load = []
        if hasattr(self.loaded_model, 'materials'):
            for face in self.loaded_model.faces:
                face_material = face.get('material')
                if (face_material and 
                    face_material in self.loaded_model.materials and
                    face_material not in self.loaded_textures and
                    face_material not in materials_to_load):
                    materials_to_load.append(face_material)
        
        texture_load_count = 0
        total_materials = len(materials_to_load)
        
        logger.debug(f"Rendering {len(self.loaded_model.faces)} faces with {len(self.loaded_textures)} textures available")
        if total_materials > 0:
            logger.info(f"First render: will load {total_materials} textures on-demand")
        
        for face in self.loaded_model.faces:
            # Set material if it changed
            face_material = face.get('material')
            if face_material != current_material:
                current_material = face_material
                
                if face_material and face_material in self.loaded_model.materials:
                    mat = self.loaded_model.materials[face_material]
                    logger.debug(f"Applying material: {face_material}")
                else:
                    mat = default_material
                    logger.debug(f"Using default material for face material: {face_material}")
                
                self._apply_material(mat)
                
                # Load and bind texture if available (on-demand loading during render)
                new_texture_id = None
                if face_material:
                    # Check if texture is already loaded
                    if face_material in self.loaded_textures:
                        new_texture_id = self.loaded_textures[face_material]
                    else:
                        # Try to load texture now (OpenGL context is active)
                        logger.info(f"Loading texture for material: {face_material}")
                        new_texture_id = self._load_material_texture(face_material, mat)
                        if new_texture_id:
                            self.loaded_textures[face_material] = new_texture_id
                            texture_load_count += 1
                            logger.info(f"Texture loaded ({texture_load_count}/{total_materials}): {face_material}")
                
                if new_texture_id != current_texture_id:
                    current_texture_id = new_texture_id
                    if current_texture_id:
                        glEnable(GL_TEXTURE_2D)
                        glBindTexture(GL_TEXTURE_2D, current_texture_id)
                        logger.debug(f"Bound texture {current_texture_id} for material {face_material}")
                    else:
                        glDisable(GL_TEXTURE_2D)
                        if face_material:
                            logger.debug(f"No texture available for material: {face_material}")
            
            # Render face
            face_vertices = face['vertices']
            
            if len(face_vertices) == 3:
                glBegin(GL_TRIANGLES)
            elif len(face_vertices) == 4:
                glBegin(GL_QUADS)
            else:
                # Handle n-gons by triangulation (basic fan triangulation)
                glBegin(GL_TRIANGLE_FAN)
            
            for v_idx, t_idx, n_idx in face_vertices:
                # Set normal if available
                if n_idx is not None and n_idx < len(self.loaded_model.normals):
                    nx, ny, nz = self.loaded_model.normals[n_idx]
                    glNormal3f(nx, ny, nz)
                
                # Set texture coordinate if available
                if t_idx is not None and t_idx < len(self.loaded_model.tex_coords):
                    u, v = self.loaded_model.tex_coords[t_idx]
                    glTexCoord2f(u, v)
                
                # Set vertex
                if v_idx < len(self.loaded_model.vertices):
                    x, y, z = self.loaded_model.vertices[v_idx]
                    glVertex3f(x, y, z)
            
            glEnd()
            
        if total_materials > 0 and texture_load_count > 0:
            logger.info(f"First render complete: loaded {texture_load_count} textures")
    
    def _apply_material(self, material: Dict[str, Any]):
        """Apply material properties to OpenGL."""
        # Set material colors
        if 'diffuse' in material:
            diffuse = list(material['diffuse']) + [1.0]  # Add alpha
            glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        
        if 'ambient' in material:
            ambient = list(material['ambient']) + [1.0]
            glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        
        if 'specular' in material:
            specular = list(material['specular']) + [1.0]
            glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        
        if 'shininess' in material:
            glMaterialf(GL_FRONT, GL_SHININESS, material['shininess'])
    
    def _draw_text_overlay(self, fonts, schematics_info, pitch, roll, yaw):
        """Draw text overlay (reusing implementation from base renderer)."""
        # Save matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable lighting for text
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        try:
            info_font = fonts.get('small', fonts.get('medium'))
            
            # Schematics info
            name_text = f"Model: {schematics_info.get('name', 'Unknown')}"
            desc_text = schematics_info.get('description', 'No description')
            if len(desc_text) > 50:
                desc_text = desc_text[:50] + "..."
            
            # Rotation info (pitch, roll, yaw are already in degrees)
            rotation_text = f"Pitch: {pitch:.1f}° Roll: {roll:.1f}° Yaw: {yaw:.1f}°"
            
            # Render surfaces
            name_surface = info_font.render(name_text, True, (0, 255, 70))
            desc_surface = info_font.render(desc_text, True, (255, 255, 255))
            rotation_surface = info_font.render(rotation_text, True, (255, 200, 0))
            
            # Draw them
            self._draw_text_surface(name_surface, 10, self.screen_height - 30)
            self._draw_text_surface(desc_surface, 10, self.screen_height - 50)
            self._draw_text_surface(rotation_surface, 10, 50)
            
        except Exception as e:
            logger.error(f"Error drawing text overlay: {e}")
        finally:
            # Restore state
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
    
    def _draw_text_surface(self, surface, x, y):
        """Draw pygame surface as OpenGL texture."""
        try:
            text_data = pygame.image.tostring(surface, "RGBA", False)
            
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 
                        0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
            
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_TEXTURE_2D)
            
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(x, y)
            glTexCoord2f(1, 1); glVertex2f(x + surface.get_width(), y)
            glTexCoord2f(1, 0); glVertex2f(x + surface.get_width(), y + surface.get_height())
            glTexCoord2f(0, 0); glVertex2f(x, y + surface.get_height())
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glDeleteTextures([texture_id])
            
        except Exception as e:
            logger.error(f"Error drawing text surface: {e}")
    
    def _draw_pause_menu_overlay(self, fonts, pause_menu_index, pitch, roll, yaw, auto_rotation_mode):
        """Draw pause menu (reuse from base implementation)."""
        # Save matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        try:
            # Black background
            glDisable(GL_BLEND)
            glColor3f(0.0, 0.0, 0.0)
            
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(self.screen_width, 0)
            glVertex2f(self.screen_width, self.screen_height)
            glVertex2f(0, self.screen_height)
            glEnd()
            
            glColor3f(1.0, 1.0, 1.0)
            
            # Menu title
            title_font = fonts.get('large', fonts.get('medium'))
            title_surface = title_font.render("3D VIEWER MENU", True, (255, 200, 0))
            title_x = (self.screen_width - title_surface.get_width()) // 2
            title_y = self.screen_height - 80
            self._draw_text_surface(title_surface, title_x, title_y)
            
            # Menu options
            current_mode = "Auto" if auto_rotation_mode else "Manual"
            options = [f"Toggle Mode ({current_mode})", "Back to Schematics", "Resume"]
            menu_font = fonts.get('medium', fonts.get('small'))
            start_y = 150
            item_height = 40
            
            for i, option in enumerate(options):
                y_pos = self.screen_height - (start_y + i * item_height)
                color = (0, 255, 70) if i == pause_menu_index else (255, 255, 255)
                option_surface = menu_font.render(option, True, color)
                option_x = (self.screen_width - option_surface.get_width()) // 2
                self._draw_text_surface(option_surface, option_x, y_pos)
            
            # Rotation values (pitch, roll, yaw are already in degrees)
            rotation_font = fonts.get('small', fonts.get('medium'))
            rotation_text = f"Pitch: {pitch:.1f}° Roll: {roll:.1f}° Yaw: {yaw:.1f}°"
            rotation_surface = rotation_font.render(rotation_text, True, (255, 200, 0))
            rotation_x = (self.screen_width - rotation_surface.get_width()) // 2
            rotation_y = self.screen_height - (start_y + len(options) * item_height + 20)
            self._draw_text_surface(rotation_surface, rotation_x, rotation_y)
            
            # Controls hint
            hint_font = fonts.get('small', fonts.get('medium'))
            hint_text = "A/D: Navigate | Enter: Select | Hold A: Resume"
            hint_surface = hint_font.render(hint_text, True, (255, 255, 255))
            hint_x = (self.screen_width - hint_surface.get_width()) // 2
            hint_y = 40
            self._draw_text_surface(hint_surface, hint_x, hint_y)
            
        except Exception as e:
            logger.error(f"Error drawing pause menu: {e}")
        finally:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

    def _draw_footer_controls(self, fonts):
        """Draw footer controls."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        try:
            hint_font = fonts.get('small', fonts.get('medium'))
            hint_text = "A/D: Rotate | Enter: Menu | Hold A: Back"
            hint_surface = hint_font.render(hint_text, True, (255, 255, 255))
            hint_x = (self.screen_width - hint_surface.get_width()) // 2
            hint_y = 20
            self._draw_text_surface(hint_surface, hint_x, hint_y)
            
        except Exception as e:
            logger.error(f"Error drawing footer: {e}")
        finally:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
    
    def cleanup(self):
        """Clean up resources."""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
            self.display_list = None
        self.initialized = False
        logger.info("OpenGL model renderer cleaned up") 