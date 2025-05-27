# tricorder_schematics.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import * # Or use PyGLM for projection/view matrices
import pygltflib
import numpy as np
import logging

# Assuming your existing config.py and sensors.py are accessible
from config import SCREEN_WIDTH, SCREEN_HEIGHT # Use the defined 320x240
from data.sensors import get_orientation # Or a more advanced filtered orientation

logger = logging.getLogger(__name__)

# --- Constants ---
MODEL_PATH = "assets/stargate_304/X304_ship.glb" # Correct path to your model
FOV = 45  # Field of view for perspective projection
NEAR_CLIP = 0.1
FAR_CLIP = 100.0

# --- Global Variables (or a class structure) ---
vao = None
vbo_vertices = None
vbo_texcoords = None # If your model has them and you use them
vbo_normals = None   # For lighting
texture_id = None
shader_program = None
model_matrix_location = None
view_matrix_location = None
projection_matrix_location = None
vertex_count_for_drawing = 0 # Store vertex count here


# --- Shader Code ---
VERTEX_SHADER_CODE = '''
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord; // If you have texture coordinates
layout (location = 2) in vec3 aNormal;   // If you have normals for lighting

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
    Normal = mat3(transpose(inverse(model))) * aNormal; // Transform normals correctly
    FragPos = vec3(model * vec4(aPos, 1.0));
}
'''

FRAGMENT_SHADER_CODE = '''
#version 330 core
out vec4 FragColor;

in vec2 TexCoord;
in vec3 Normal;
in vec3 FragPos; // Position of the fragment in world space

uniform sampler2D textureSampler;
// uniform vec3 lightPos; // Example: for a light source
// uniform vec3 viewPos;  // Example: for specular lighting
// uniform vec3 lightColor;

void main()
{
    // Basic texturing
    FragColor = texture(textureSampler, TexCoord);

    // Basic diffuse lighting (example)
    // vec3 norm = normalize(Normal);
    // vec3 lightDir = normalize(lightPos - FragPos);
    // float diff = max(dot(norm, lightDir), 0.0);
    // vec3 diffuse = diff * lightColor;
    // FragColor = vec4(diffuse, 1.0) * texture(textureSampler, TexCoord);
}
'''

# --- OpenGL Initialization and Model Loading ---
def init_gl():
    """Initialize OpenGL settings."""
    global shader_program, model_matrix_location, view_matrix_location, projection_matrix_location

    glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue background
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_TEXTURE_2D) # Not needed for modern GL if shaders handle texturing

    # Compile shaders
    vertex_shader = compile_shader(VERTEX_SHADER_CODE, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(FRAGMENT_SHADER_CODE, GL_FRAGMENT_SHADER)
    if not vertex_shader or not fragment_shader:
        logger.error("Shader compilation failed.")
        return False
        
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    if not glGetProgramiv(shader_program, GL_LINK_STATUS):
        info_log = glGetProgramInfoLog(shader_program)
        logger.error(f"Shader program linking failed: {info_log}")
        return False

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    # Get uniform locations
    model_matrix_location = glGetUniformLocation(shader_program, "model")
    view_matrix_location = glGetUniformLocation(shader_program, "view")
    projection_matrix_location = glGetUniformLocation(shader_program, "projection")
    
    logger.info("OpenGL initialized and shaders compiled.")
    return True


def compile_shader(source, shader_type):
    """Compile a single shader."""
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        info_log = glGetShaderInfoLog(shader)
        logger.error(f"Shader compilation failed ({shader_type}): {info_log.decode() if isinstance(info_log, bytes) else info_log}")
        return None
    return shader

def load_model_glb(path):
    """Loads a GLB model and prepares it for OpenGL."""
    global vao, vbo_vertices, vbo_texcoords, vbo_normals, texture_id, vertex_count_for_drawing
    
    logger.info(f"Attempting to load GLB model from: {path}")
    try:
        gltf = pygltflib.GLTF2().load(path)
    except Exception as e:
        logger.error(f"Failed to load or parse GLB file '{path}': {e}", exc_info=True)
        return False

    if not gltf.meshes or not gltf.meshes[0].primitives:
        logger.error("GLB model does not contain any meshes or primitives.")
        return False
        
    primitive = gltf.meshes[0].primitives[0]
    
    # --- Vertices ---
    accessor_vertices = gltf.accessors[primitive.attributes.POSITION]
    vertex_count_for_drawing = accessor_vertices.count # Store vertex count
    buffer_view_vertices = gltf.bufferViews[accessor_vertices.bufferView]
    vertex_data_blob = gltf.buffers[buffer_view_vertices.buffer].data # Get the whole blob
    # Slice the specific part for vertices
    vertex_data = vertex_data_blob[
                  buffer_view_vertices.byteOffset + accessor_vertices.byteOffset :
                  buffer_view_vertices.byteOffset + accessor_vertices.byteOffset + buffer_view_vertices.byteLength
                  ]
    vertices = np.frombuffer(vertex_data, dtype=np.float32).reshape(-1, 3)

    tex_coords = np.zeros((vertex_count_for_drawing, 2), dtype=np.float32) # Default
    if primitive.attributes.TEXCOORD_0 is not None:
        accessor_texcoords = gltf.accessors[primitive.attributes.TEXCOORD_0]
        buffer_view_texcoords = gltf.bufferViews[accessor_texcoords.bufferView]
        texcoord_data = vertex_data_blob[ # Use the same blob
                       buffer_view_texcoords.byteOffset + accessor_texcoords.byteOffset :
                       buffer_view_texcoords.byteOffset + accessor_texcoords.byteOffset + buffer_view_texcoords.byteLength
                       ]
        tex_coords = np.frombuffer(texcoord_data, dtype=np.float32).reshape(-1, 2)
    else:
        logger.warning("Model does not have texture coordinates (TEXCOORD_0). Using default.")

    normals = np.zeros((vertex_count_for_drawing, 3), dtype=np.float32) # Default
    if primitive.attributes.NORMAL is not None:
        accessor_normals = gltf.accessors[primitive.attributes.NORMAL]
        buffer_view_normals = gltf.bufferViews[accessor_normals.bufferView]
        normal_data = vertex_data_blob[ # Use the same blob
                      buffer_view_normals.byteOffset + accessor_normals.byteOffset :
                      buffer_view_normals.byteOffset + accessor_normals.byteOffset + buffer_view_normals.byteLength
                      ]
        normals = np.frombuffer(normal_data, dtype=np.float32).reshape(-1, 3)
    else:
        logger.warning("Model does not have normals. Using default. Lighting will be basic.")

    if primitive.material is not None:
        material = gltf.materials[primitive.material]
        if material.pbrMetallicRoughness and material.pbrMetallicRoughness.baseColorTexture:
            texture_info = material.pbrMetallicRoughness.baseColorTexture
            image_index = gltf.textures[texture_info.index].source
            image = gltf.images[image_index]
            
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            try:
                from PIL import Image
                import io

                img_data_source_bytes = None
                if image.bufferView is not None: # Embedded data in bufferView
                    img_buffer_view = gltf.bufferViews[image.bufferView]
                    img_data_source_bytes = vertex_data_blob[ # Use the main data blob
                                     img_buffer_view.byteOffset :
                                     img_buffer_view.byteOffset + img_buffer_view.byteLength
                                     ]
                elif image.uri and image.uri.startswith('data:image'): # Embedded data as URI
                    import base64
                    header, encoded = image.uri.split(',', 1)
                    img_data_source_bytes = base64.b64decode(encoded)
                
                if img_data_source_bytes:
                    pil_image = Image.open(io.BytesIO(img_data_source_bytes))
                    if pil_image.mode != 'RGBA':
                         pil_image = pil_image.convert('RGBA')
                    img_width, img_height = pil_image.size
                    img_data_formatted = pil_image.tobytes("raw", "RGBA", 0, -1)
                    
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data_formatted)
                    glGenerateMipmap(GL_TEXTURE_2D)
                    logger.info(f"Texture loaded successfully from embedded GLB data (Image {image_index}).")
                else:
                    logger.warning(f"Unsupported image data source for image {image_index}: URI {image.uri}, BufferView: {image.bufferView}")
                    glBindTexture(GL_TEXTURE_2D, 0) # Unbind if loading failed
                    texture_id = None # Mark as no texture
                    # Consider loading a default placeholder texture here

            except ImportError:
                logger.error("Pillow library not found (pip install Pillow). Cannot load embedded textures.")
                glBindTexture(GL_TEXTURE_2D, 0)
                texture_id = None
                return False # Critical for textures
            except Exception as e:
                logger.error(f"Error processing embedded image data with Pillow: {e}", exc_info=True)
                glBindTexture(GL_TEXTURE_2D, 0)
                texture_id = None
                return False # Critical for textures
        else:
            logger.warning("Material has no baseColorTexture. Model will be untextured.")
    else:
        logger.warning("Primitive has no material assigned. Model will be untextured.")

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    if tex_coords is not None: # Should always exist now, even if default
        vbo_texcoords = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
        glBufferData(GL_ARRAY_BUFFER, tex_coords.nbytes, tex_coords, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

    if normals is not None: # Should always exist now, even if default
        vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    logger.info("Model VBOs and VAO created successfully.")
    return True


def draw_scene(pitch, roll, yaw):
    global vao, shader_program, model_matrix_location, view_matrix_location, projection_matrix_location, texture_id, vertex_count_for_drawing

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(shader_program)

    # --- Projection Matrix (Using GLU temporarily - recommend PyGLM) ---
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, (SCREEN_WIDTH / SCREEN_HEIGHT), NEAR_CLIP, FAR_CLIP)
    projection_matrix_gl = glGetFloatv(GL_PROJECTION_MATRIX)
    glUniformMatrix4fv(projection_matrix_location, 1, GL_FALSE, projection_matrix_gl)

    # --- View Matrix (Camera - Using GLU temporarily) ---
    glMatrixMode(GL_MODELVIEW) # Switches current matrix to ModelView
    glLoadIdentity()
    # Eye position (0,1,5) - slightly above and back, looking at origin (0,0,0), Y is up. Adjust Z for model size.
    gluLookAt(0, 1, 5,  # Eye X, Y, Z
              0, 0, 0,  # Center X, Y, Z (looking at origin)
              0, 1, 0)  # Up X, Y, Z
    view_matrix_gl = glGetFloatv(GL_MODELVIEW_MATRIX) # This is now the view matrix
    glUniformMatrix4fv(view_matrix_location, 1, GL_FALSE, view_matrix_gl)
    
    # --- Model Matrix (Object Transformation - Using glRotatef temporarily) ---
    # Create model matrix separately then apply to current ModelView stack
    # This is where the fixed-function style gets confusing with shaders.
    # Ideally, we'd build model_matrix with PyGLM and send it.
    # For now, we apply rotations to the *current* MODELVIEW matrix which starts as identity
    # after gluLookAt effectively sets it and we retrieve it.
    # We need to reset GL_MODELVIEW for *just the model's* transformation.
    glLoadIdentity() # Reset current MODELVIEW matrix to identity FOR THE MODEL
    
    # Apply Sense HAT rotations:
    # Order: Yaw (around Y), Pitch (around X), Roll (around Z) is a common convention.
    # Test and adjust signs and axes based on Sense HAT and model orientation.
    glRotatef(yaw, 0, 1, 0)     # Yaw around Y axis
    glRotatef(pitch, 1, 0, 0)   # Pitch around X axis
    glRotatef(roll, 0, 0, 1)    # Roll around Z axis
    
    # Potentially scale the model if it's too big/small
    # glScalef(0.5, 0.5, 0.5) # Example: make it half size

    model_matrix_gl = glGetFloatv(GL_MODELVIEW_MATRIX) # This is now the model's matrix
    glUniformMatrix4fv(model_matrix_location, 1, GL_FALSE, model_matrix_gl)

    if texture_id:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        texture_sampler_loc = glGetUniformLocation(shader_program, "textureSampler")
        if texture_sampler_loc != -1: # Check if uniform exists
             glUniform1i(texture_sampler_loc, 0)
    else:
        # Optionally bind a default texture or ensure shader handles no texture
        glBindTexture(GL_TEXTURE_2D, 0)


    if vao and vertex_count_for_drawing > 0:
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, vertex_count_for_drawing)
        glBindVertexArray(0)
    else:
        if not vao: logger.warning("Drawing skipped: VAO not loaded.")
        if vertex_count_for_drawing <= 0: logger.warning("Drawing skipped: Vertex count is zero or negative.")


    pygame.display.flip()

def run_schematics_viewer(screen):
    logger.info("Starting Schematics Viewer mode.")
    
    if not init_gl():
        logger.error("OpenGL initialization failed. Exiting schematics viewer.")
        return
        
    if not load_model_glb(MODEL_PATH):
        logger.error(f"Failed to load model: {MODEL_PATH}. Exiting schematics viewer.")
        # Consider showing an error on the Pygame screen if possible
        return

    running = True
    clock = pygame.time.Clock()
    current_pitch, current_roll, current_yaw = 0.0, 0.0, 0.0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            # TODO: Add joystick event handling for exiting (e.g., back button)

        orientation = get_orientation()
        if orientation:
            # Mapping: Adjust based on physical setup and visual feedback
            # Common Sense HAT to OpenGL mapping (may need negation or axis swaps):
            # Pitch: rotation around X-axis
            # Roll: rotation around Z-axis
            # Yaw: rotation around Y-axis
            current_pitch = orientation['pitch']
            current_roll =  orientation['roll'] # Sense HAT roll often maps to Z
            current_yaw = orientation['yaw']
            # logger.debug(f"Raw Orientation - P: {current_pitch:.1f}, R: {current_roll:.1f}, Y: {current_yaw:.1f}")
        else:
            logger.warning("No orientation data received from sensors.")


        draw_scene(current_pitch, current_roll, current_yaw)
        clock.tick(30) 

    logger.info("Exiting Schematics Viewer mode.")
    cleanup_gl()


def cleanup_gl():
    """Cleanup OpenGL resources."""
    global vao, vbo_vertices, vbo_texcoords, vbo_normals, texture_id, shader_program
    logger.info("Cleaning up OpenGL resources.")
    if vbo_vertices: glDeleteBuffers(1, [vbo_vertices])
    if vbo_texcoords: glDeleteBuffers(1, [vbo_texcoords])
    if vbo_normals: glDeleteBuffers(1, [vbo_normals])
    if texture_id: glDeleteTextures(1, [texture_id])
    if vao: glDeleteVertexArrays(1, [vao])
    if shader_program: glDeleteProgram(shader_program)
    # Reset globals
    vao = vbo_vertices = vbo_texcoords = vbo_normals = texture_id = shader_program = None
    vertex_count_for_drawing = 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    pygame.init()
    
    # Attempt to initialize Sense HAT sensors directly for standalone testing
    # This requires data.sensors.init_sensors() to be callable and work.
    # If your project structure prevents direct import like this for standalone,
    # you might need to adjust imports or mock sensor data.
    try:
        from data.sensors import init_sensors
        if not init_sensors(): # Initialize sensors from the main data module
            logger.warning("Sense HAT could not be initialized via data.sensors.init_sensors(). Orientation will be static (0,0,0).")
    except ImportError:
        logger.warning("Could not import init_sensors from data.sensors. Ensure PYTHONPATH is correct or run from project root.")
        logger.warning("Orientation will be static (0,0,0).")


    display_flags = DOUBLEBUF | OPENGL
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags, 16) # Try 16-bit depth
    except pygame.error as e_16:
        logger.warning(f"Failed to set_mode with 16-bit depth ({SCREEN_WIDTH}x{SCREEN_HEIGHT}): {e_16}. Trying 24-bit.")
        try:
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags, 24) # Try 24-bit depth
        except pygame.error as e_24:
            logger.warning(f"Failed to set_mode with 24-bit depth: {e_24}. Trying default depth.")
            try:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags) # Try default depth
            except pygame.error as e_def:
                logger.error(f"Failed to set Pygame display mode with OpenGL: {e_def}", exc_info=True)
                pygame.quit()
                exit()
                
    pygame.display.set_caption("Tricorder Schematics")
    
    run_schematics_viewer(screen)
    
    pygame.quit() 