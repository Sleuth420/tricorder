# --- ui/views/tricorder_schematics.py ---
# Handles the display and logic for the 3D schematics viewer

import pygame
from pygame.locals import *
from OpenGL.GL import *
# from OpenGL.GLU import * # GLU is not used with PyGLM shaders
import glm # PyGLM for matrix operations
import pygltflib
import numpy as np
import logging
from models.app_state import STATE_SCHEMATICS  # Import state constant from app_state

# config_module is passed into draw_schematics_view
# Sensor data will be fetched directly in this module's loop for now.

logger = logging.getLogger(__name__)

# --- Constants ---
MODEL_PATH = "assets/stargate_304/X304_ship.glb" # Path to the 3D model
FOV = 45.0  # Field of view for perspective projection
NEAR_CLIP = 0.1
FAR_CLIP = 100.0
MODEL_SCALE = 0.5  # Scale factor for the model
CAMERA_DISTANCE = 5.0  # Distance from camera to model

# --- Resource Management Class ---
class SchematicViewResources:
    def __init__(self):
        self.vao = None
        self.vbo_vertices = None
        self.vbo_texcoords = None
        self.vbo_normals = None
        self.texture_id = None
        self.shader_program = None
        self.model_matrix_location = None
        self.view_matrix_location = None
        self.projection_matrix_location = None
        self.vertex_count = 0
        self.is_initialized = False
        self.screen_width = 0 # Will be set from the passed screen surface
        self.screen_height = 0
        self.test_vao = None
        self.test_vbo = None

# --- Shader Code ---
VERTEX_SHADER_CODE = """
#version 300 es
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;
layout (location = 2) in vec3 aNormal;

out vec2 TexCoord;
out vec3 Normal;
out vec3 FragPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    TexCoord = aTexCoord;
    Normal = mat3(transpose(inverse(model))) * aNormal;
    FragPos = vec3(model * vec4(aPos, 1.0));
}
"""

FRAGMENT_SHADER_CODE = """
#version 300 es
precision mediump float;
out vec4 FragColor;

in vec2 TexCoord;
in vec3 Normal;
in vec3 FragPos;

uniform sampler2D textureSampler;

void main()
{
    // For test triangle, output a solid color
    if (FragPos.z == 0.0) {
        FragColor = vec4(1.0, 0.0, 0.0, 1.0); // Red color for test triangle
        return;
    }

    // For model, use texture if available
    vec4 texColor = texture(textureSampler, TexCoord);
    if(texColor.a < 0.1)
        discard;
    FragColor = texColor;
}
"""

def _compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        info_log = glGetShaderInfoLog(shader)
        logger.error(f"Shader compilation failed ({shader_type}): {info_log.decode() if isinstance(info_log, bytes) else info_log}")
        return None
    return shader

def _init_gl_resources(resources, screen_width, screen_height, config_module):
    logger.info(f"Initializing OpenGL for Schematics (Screen: {screen_width}x{screen_height})")
    resources.screen_width = screen_width
    resources.screen_height = screen_height

    # Use background color from config
    bg_color = config_module.Theme.BACKGROUND 
    glClearColor(bg_color[0]/255.0, bg_color[1]/255.0, bg_color[2]/255.0, 1.0)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND) # For transparency
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vertex_shader = _compile_shader(VERTEX_SHADER_CODE, GL_VERTEX_SHADER)
    fragment_shader = _compile_shader(FRAGMENT_SHADER_CODE, GL_FRAGMENT_SHADER)

    if not vertex_shader or not fragment_shader:
        return False

    resources.shader_program = glCreateProgram()
    glAttachShader(resources.shader_program, vertex_shader)
    glAttachShader(resources.shader_program, fragment_shader)
    glLinkProgram(resources.shader_program)

    if not glGetProgramiv(resources.shader_program, GL_LINK_STATUS):
        info_log = glGetProgramInfoLog(resources.shader_program)
        logger.error(f"Shader program linking failed: {info_log.decode() if isinstance(info_log, bytes) else info_log}")
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        return False

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    resources.model_matrix_location = glGetUniformLocation(resources.shader_program, "model")
    resources.view_matrix_location = glGetUniformLocation(resources.shader_program, "view")
    resources.projection_matrix_location = glGetUniformLocation(resources.shader_program, "projection")
    
    # Create test triangle VAO/VBO
    resources.test_vao = glGenVertexArrays(1)
    glBindVertexArray(resources.test_vao)
    
    # Test triangle vertices
    test_vertices = np.array([
        -0.5, -0.5, 0.0,  # Bottom left
         0.5, -0.5, 0.0,  # Bottom right
         0.0,  0.5, 0.0   # Top
    ], dtype=np.float32)
    
    resources.test_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, resources.test_vbo)
    glBufferData(GL_ARRAY_BUFFER, test_vertices.nbytes, test_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    logger.info("OpenGL initialized for Schematics.")
    resources.is_initialized = True
    return True

def _load_model_data(resources):
    logger.info(f"Attempting to load GLB model: {MODEL_PATH}")
    try:
        gltf = pygltflib.GLTF2().load(MODEL_PATH)
    except Exception as e:
        logger.error(f"Failed to load/parse GLB '{MODEL_PATH}': {e}", exc_info=True)
        return False

    if not gltf.meshes or not len(gltf.meshes):
        logger.error("GLB model has no meshes.")
        return False
    
    primitive = gltf.meshes[0].primitives[0]
    
    # Get vertex positions
    accessor_vertices = gltf.accessors[primitive.attributes.POSITION]
    resources.vertex_count = accessor_vertices.count
    buffer_view_vertices = gltf.bufferViews[accessor_vertices.bufferView]
    buffer_vertices = gltf.buffers[buffer_view_vertices.buffer]
    
    # Read binary data from buffer
    with open(MODEL_PATH, 'rb') as f:
        f.seek(buffer_vertices.byteOffset if hasattr(buffer_vertices, 'byteOffset') else 0)
        buffer_data = f.read(buffer_vertices.byteLength)
    
    # Extract vertex data
    vertex_data = np.frombuffer(buffer_data[
        buffer_view_vertices.byteOffset + accessor_vertices.byteOffset:
        buffer_view_vertices.byteOffset + accessor_vertices.byteOffset + buffer_view_vertices.byteLength
    ], dtype=np.float32).reshape(-1, 3)

    # Get texture coordinates
    tex_coords_data = np.zeros((resources.vertex_count, 2), dtype=np.float32)
    if primitive.attributes.TEXCOORD_0 is not None:
        accessor_texcoords = gltf.accessors[primitive.attributes.TEXCOORD_0]
        buffer_view_texcoords = gltf.bufferViews[accessor_texcoords.bufferView]
        tex_coords_data = np.frombuffer(buffer_data[
            buffer_view_texcoords.byteOffset + accessor_texcoords.byteOffset:
            buffer_view_texcoords.byteOffset + accessor_texcoords.byteOffset + buffer_view_texcoords.byteLength
        ], dtype=np.float32).reshape(-1, 2)
    else:
        logger.warning("Model has no TEXCOORD_0. Using default (0,0).")

    # Get normals
    normals_data = np.ones((resources.vertex_count, 3), dtype=np.float32) # Default to (1,1,1) if not present
    if primitive.attributes.NORMAL is not None:
        accessor_normals = gltf.accessors[primitive.attributes.NORMAL]
        buffer_view_normals = gltf.bufferViews[accessor_normals.bufferView]
        normals_data = np.frombuffer(buffer_data[
            buffer_view_normals.byteOffset + accessor_normals.byteOffset:
            buffer_view_normals.byteOffset + accessor_normals.byteOffset + buffer_view_normals.byteLength
        ], dtype=np.float32).reshape(-1, 3)
    else:
        logger.warning("Model has no NORMALs. Using default (1,1,1).")

    # Texture loading
    try:
        from PIL import Image
        import io
        
        if primitive.material is not None:
            material = gltf.materials[primitive.material]
            if material.pbrMetallicRoughness and material.pbrMetallicRoughness.baseColorTexture:
                texture_info = material.pbrMetallicRoughness.baseColorTexture
                image_index = gltf.textures[texture_info.index].source
                image_gltf = gltf.images[image_index]
                
                img_bytes = None
                if image_gltf.bufferView is not None:
                    buffer_view_image = gltf.bufferViews[image_gltf.bufferView]
                    img_bytes = buffer_data[
                        buffer_view_image.byteOffset:
                        buffer_view_image.byteOffset + buffer_view_image.byteLength
                    ]
                elif image_gltf.uri and image_gltf.uri.startswith('data:image'):
                    import base64
                    img_bytes = base64.b64decode(image_gltf.uri.split(',',1)[1])

                if img_bytes:
                    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                    img_w, img_h = pil_img.size
                    img_data = pil_img.tobytes("raw", "RGBA", 0, -1)

                    resources.texture_id = glGenTextures(1)
                    glBindTexture(GL_TEXTURE_2D, resources.texture_id)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_w, img_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
                    glGenerateMipmap(GL_TEXTURE_2D)
                    logger.info(f"Texture loaded from GLB (Image {image_index}).")
                else: logger.warning("No texture data found/loaded.")
            else: logger.warning("Material has no baseColorTexture.")
        else: logger.warning("Primitive has no material.")
    except ImportError: logger.error("Pillow not found. Cannot load textures.")
    except Exception as e: logger.error(f"Texture loading error: {e}", exc_info=True)

    # VAO/VBOs
    resources.vao = glGenVertexArrays(1)
    glBindVertexArray(resources.vao)

    resources.vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, resources.vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    resources.vbo_texcoords = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, resources.vbo_texcoords)
    glBufferData(GL_ARRAY_BUFFER, tex_coords_data.nbytes, tex_coords_data, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)

    resources.vbo_normals = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, resources.vbo_normals)
    glBufferData(GL_ARRAY_BUFFER, normals_data.nbytes, normals_data, GL_STATIC_DRAW)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    logger.info("Model VBOs/VAO created.")
    return True

def _render_scene_3d(resources, pitch, roll, yaw, config_module):
    if not resources.is_initialized or not resources.shader_program:
        logger.warning("Render called but not initialized.")
        return

    # Use config dimensions instead of actual screen dimensions
    screen_width = config_module.SCREEN_WIDTH
    screen_height = config_module.SCREEN_HEIGHT

    bg_color = config_module.Theme.BACKGROUND # Get BG color from config
    glClearColor(bg_color[0]/255.0, bg_color[1]/255.0, bg_color[2]/255.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glUseProgram(resources.shader_program)

    # Calculate aspect ratio using config dimensions
    aspect_ratio = screen_width / screen_height if screen_height > 0 else 1.0
    proj_matrix = glm.perspective(glm.radians(FOV), aspect_ratio, NEAR_CLIP, FAR_CLIP)
    glUniformMatrix4fv(resources.projection_matrix_location, 1, GL_FALSE, glm.value_ptr(proj_matrix))

    # Adjust camera position
    view_matrix = glm.lookAt(
        glm.vec3(0, 0, 2.0),  # Camera position
        glm.vec3(0, 0, 0),    # Look at center
        glm.vec3(0, 1, 0)     # Up vector
    )
    glUniformMatrix4fv(resources.view_matrix_location, 1, GL_FALSE, glm.value_ptr(view_matrix))

    # First render the test triangle
    model_matrix = glm.mat4(1.0)
    glUniformMatrix4fv(resources.model_matrix_location, 1, GL_FALSE, glm.value_ptr(model_matrix))
    
    glBindVertexArray(resources.test_vao)
    glDrawArrays(GL_TRIANGLES, 0, 3)  # Draw test triangle
    glBindVertexArray(0)

    # Then render the model if available
    if resources.vao and resources.vertex_count > 0:
        model_matrix = glm.mat4(1.0)
        # Scale the model
        model_matrix = glm.scale(model_matrix, glm.vec3(0.1))  # Scale down the model
        # Apply rotations
        model_matrix = glm.rotate(model_matrix, glm.radians(yaw), glm.vec3(0, 1, 0))
        model_matrix = glm.rotate(model_matrix, glm.radians(pitch), glm.vec3(1, 0, 0))
        model_matrix = glm.rotate(model_matrix, glm.radians(roll), glm.vec3(0, 0, 1))
        
        glUniformMatrix4fv(resources.model_matrix_location, 1, GL_FALSE, glm.value_ptr(model_matrix))

        if resources.texture_id:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, resources.texture_id)
            tex_loc = glGetUniformLocation(resources.shader_program, "textureSampler")
            if tex_loc != -1: glUniform1i(tex_loc, 0)
        
        glBindVertexArray(resources.vao)
        glDrawArrays(GL_TRIANGLES, 0, resources.vertex_count)
        glBindVertexArray(0)

def _cleanup_gl_resources(resources):
    logger.info("Cleaning up Schematics GL resources.")
    if resources.vbo_vertices: glDeleteBuffers(1, [resources.vbo_vertices])
    if resources.vbo_texcoords: glDeleteBuffers(1, [resources.vbo_texcoords])
    if resources.vbo_normals: glDeleteBuffers(1, [resources.vbo_normals])
    if resources.texture_id: glDeleteTextures(1, [resources.texture_id])
    if resources.vao: glDeleteVertexArrays(1, [resources.vao])
    if resources.test_vbo: glDeleteBuffers(1, [resources.test_vbo])
    if resources.test_vao: glDeleteVertexArrays(1, [resources.test_vao])
    if resources.shader_program: glDeleteProgram(resources.shader_program)
    resources.is_initialized = False

# Main function called by display_manager.py
def draw_schematics_view(screen, app_state, fonts, config_module):
    logger.info("Entering Schematics Viewer.")
    
    res = SchematicViewResources()
    
    # Use config dimensions instead of actual screen dimensions
    screen_width = config_module.SCREEN_WIDTH
    screen_height = config_module.SCREEN_HEIGHT

    if not _init_gl_resources(res, screen_width, screen_height, config_module):
        logger.error("Failed to initialize OpenGL for Schematics.")
        # Display error on the Pygame screen
        screen.fill(config_module.Theme.BACKGROUND)
        err_surf = fonts['medium'].render("Schematics: OpenGL Error", True, config_module.Theme.ALERT)
        screen.blit(err_surf, ( (screen_width - err_surf.get_width()) // 2, (screen_height - err_surf.get_height()) // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        return # Exit this view

    if not _load_model_data(res):
        logger.error("Failed to load model for Schematics.")
        screen.fill(config_module.Theme.BACKGROUND)
        err_surf = fonts['medium'].render("Schematics: Model Load Error", True, config_module.Theme.ALERT)
        screen.blit(err_surf, ( (screen_width - err_surf.get_width()) // 2, (screen_height - err_surf.get_height()) // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        _cleanup_gl_resources(res)
        return

    # Import get_orientation here to keep it local to this view's loop
    try:
        from data.sensors import get_orientation
        sense_hat_ok = True
    except ImportError:
        logger.warning("Schematics: data.sensors.get_orientation not found.")
        sense_hat_ok = False
        def get_orientation(): return None # Dummy

    running_schematics = True
    clock = pygame.time.Clock()
    pitch, roll, yaw = 0.0, 0.0, 0.0

    while running_schematics:
        # Check if main app state has changed away from schematics
        if app_state.current_state != STATE_SCHEMATICS:
            logger.info("Main app state changed. Exiting schematics viewer loop.")
            running_schematics = False
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_schematics = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running_schematics = False
                    if hasattr(app_state, '_process_action') and hasattr(config_module, 'INPUT_ACTION_BACK'):
                         app_state._process_action(config_module.INPUT_ACTION_BACK)
                    break
        if not running_schematics: break

        if sense_hat_ok:
            orientation = get_orientation()
            if orientation:
                pitch = orientation.get('pitch', pitch)
                roll = orientation.get('roll', roll)
                yaw = orientation.get('yaw', yaw)
        else: # Simulate rotation if no Sense HAT for testing
             yaw = (yaw + 0.5) % 360

        _render_scene_3d(res, pitch, roll, yaw, config_module)
        pygame.display.flip()
        clock.tick(config_module.FPS)

    logger.info("Exiting Schematics Viewer rendering loop.")
    _cleanup_gl_resources(res)
    # The app_state should have been changed to STATE_MENU by input_handler in main.py
    # if the user initiated a "BACK" action.