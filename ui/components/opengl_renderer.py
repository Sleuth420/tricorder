# --- ui/components/opengl_renderer.py ---
# Handles OpenGL rendering for 3D models

import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import numpy as np
import logging

logger = logging.getLogger(__name__)

class OpenGLRenderer:
    def __init__(self, screen_width, screen_height, config_module):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config_module
        self.resources = self._init_resources()
        
    def _init_resources(self):
        """Initialize OpenGL resources and return a resource object."""
        resources = type('SchematicViewResources', (), {})()
        resources.vao = None
        resources.vbo_vertices = None
        resources.shader_program = None
        resources.model_matrix_location = None
        resources.view_matrix_location = None
        resources.projection_matrix_location = None
        resources.is_initialized = False
        
        if not self._init_gl(resources):
            return None
            
        return resources
        
    def _init_gl(self, resources):
        """Initialize OpenGL context and shaders."""
        try:
            # Set up OpenGL state
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Create and compile shaders
            vertex_shader = self._compile_shader(VERTEX_SHADER_CODE, GL_VERTEX_SHADER)
            fragment_shader = self._compile_shader(FRAGMENT_SHADER_CODE, GL_FRAGMENT_SHADER)
            
            if not vertex_shader or not fragment_shader:
                return False
                
            # Create and link shader program
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
            
            # Get uniform locations
            resources.model_matrix_location = glGetUniformLocation(resources.shader_program, "model")
            resources.view_matrix_location = glGetUniformLocation(resources.shader_program, "view")
            resources.projection_matrix_location = glGetUniformLocation(resources.shader_program, "projection")
            
            # Create VAO and VBO for cube
            resources.vao = glGenVertexArrays(1)
            glBindVertexArray(resources.vao)
            
            # Cube vertices (position only)
            vertices = np.array([
                # Front face
                -0.5, -0.5,  0.5,
                 0.5, -0.5,  0.5,
                 0.5,  0.5,  0.5,
                -0.5,  0.5,  0.5,
                # Back face
                -0.5, -0.5, -0.5,
                 0.5, -0.5, -0.5,
                 0.5,  0.5, -0.5,
                -0.5,  0.5, -0.5,
            ], dtype=np.float32)
            
            # Create and bind VBO
            resources.vbo_vertices = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, resources.vbo_vertices)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            
            # Set vertex attributes
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(0)
            
            # Unbind
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)
            
            resources.is_initialized = True
            logger.info("OpenGL initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing OpenGL: {e}", exc_info=True)
            return False
            
    def _compile_shader(self, source, shader_type):
        """Compile a shader from source."""
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            info_log = glGetShaderInfoLog(shader)
            logger.error(f"Shader compilation failed ({shader_type}): {info_log.decode() if isinstance(info_log, bytes) else info_log}")
            return None
        return shader
        
    def render(self, pitch, roll, yaw):
        """Render the cube with the given rotation."""
        if not self.resources or not self.resources.is_initialized:
            logger.error("OpenGL not initialized")
            return
            
        # Clear screen
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Use shader program
        glUseProgram(self.resources.shader_program)
        
        # Set up projection matrix
        aspect_ratio = self.screen_width / self.screen_height if self.screen_height > 0 else 1.0
        proj_matrix = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)
        glUniformMatrix4fv(self.resources.projection_matrix_location, 1, GL_FALSE, glm.value_ptr(proj_matrix))
        
        # Set up view matrix
        view_matrix = glm.lookAt(
            glm.vec3(0, 0, 3.0),  # Camera position
            glm.vec3(0, 0, 0),    # Look at center
            glm.vec3(0, 1, 0)     # Up vector
        )
        glUniformMatrix4fv(self.resources.view_matrix_location, 1, GL_FALSE, glm.value_ptr(view_matrix))
        
        # Set up model matrix with rotation
        model_matrix = glm.mat4(1.0)
        model_matrix = glm.rotate(model_matrix, glm.radians(yaw), glm.vec3(0, 1, 0))
        model_matrix = glm.rotate(model_matrix, glm.radians(pitch), glm.vec3(1, 0, 0))
        model_matrix = glm.rotate(model_matrix, glm.radians(roll), glm.vec3(0, 0, 1))
        glUniformMatrix4fv(self.resources.model_matrix_location, 1, GL_FALSE, glm.value_ptr(model_matrix))
        
        # Draw cube
        glBindVertexArray(self.resources.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)  # Front face
        glDrawArrays(GL_TRIANGLE_FAN, 4, 4)  # Back face
        glBindVertexArray(0)
        
    def cleanup(self):
        """Clean up OpenGL resources."""
        if self.resources:
            if self.resources.vbo_vertices:
                glDeleteBuffers(1, [self.resources.vbo_vertices])
            if self.resources.vao:
                glDeleteVertexArrays(1, [self.resources.vao])
            if self.resources.shader_program:
                glDeleteProgram(self.resources.shader_program)
            self.resources.is_initialized = False

# Shader code
VERTEX_SHADER_CODE = """
#version 300 es
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER_CODE = """
#version 300 es
precision mediump float;
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.0, 1.0, 0.0, 1.0);  // Green color
}
"""