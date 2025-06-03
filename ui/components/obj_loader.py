# --- ui/components/obj_loader.py ---
# Wavefront OBJ file loader for 3D models

import logging
import os
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class OBJModel:
    """Represents a loaded OBJ model with vertices, faces, and materials."""
    
    def __init__(self):
        self.vertices = []  # List of (x, y, z) tuples
        self.normals = []   # List of (nx, ny, nz) tuples
        self.tex_coords = [] # List of (u, v) tuples
        self.faces = []     # List of face data
        self.materials = {} # Material definitions
        self.groups = {}    # Object groups and their faces
        self.bounds = None  # Bounding box (min_x, min_y, min_z, max_x, max_y, max_z)
        
    def calculate_bounds(self):
        """Calculate the bounding box of the model."""
        if not self.vertices:
            self.bounds = (0, 0, 0, 0, 0, 0)
            return
            
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        
        self.bounds = (
            min(xs), min(ys), min(zs),  # min_x, min_y, min_z
            max(xs), max(ys), max(zs)   # max_x, max_y, max_z
        )
        
        logger.info(f"Model bounds: {self.bounds}")
        
    def get_center(self) -> Tuple[float, float, float]:
        """Get the center point of the model."""
        if not self.bounds:
            self.calculate_bounds()
        
        min_x, min_y, min_z, max_x, max_y, max_z = self.bounds
        return (
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        )
        
    def get_scale_factor(self, target_size: float = 2.0) -> float:
        """Get scale factor to fit model in target size."""
        if not self.bounds:
            self.calculate_bounds()
            
        min_x, min_y, min_z, max_x, max_y, max_z = self.bounds
        
        # Find the largest dimension
        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z
        max_dimension = max(width, height, depth)
        
        if max_dimension == 0:
            return 1.0
            
        return target_size / max_dimension

class OBJLoader:
    """Loads Wavefront OBJ files."""
    
    @staticmethod
    def load(file_path: str) -> Optional[OBJModel]:
        """
        Load an OBJ file and return an OBJModel.
        
        Args:
            file_path (str): Path to the OBJ file
            
        Returns:
            OBJModel or None if loading failed
        """
        if not os.path.exists(file_path):
            logger.error(f"OBJ file not found: {file_path}")
            return None
            
        model = OBJModel()
        current_material = None
        current_group = "default"
        
        try:
            with open(file_path, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                        
                    parts = line.split()
                    if not parts:
                        continue
                        
                    command = parts[0]
                    
                    try:
                        if command == 'v':  # Vertex
                            if len(parts) >= 4:
                                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                                model.vertices.append((x, y, z))
                                
                        elif command == 'vn':  # Vertex normal
                            if len(parts) >= 4:
                                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                                model.normals.append((nx, ny, nz))
                                
                        elif command == 'vt':  # Texture coordinate
                            if len(parts) >= 3:
                                u, v = float(parts[1]), float(parts[2])
                                model.tex_coords.append((u, v))
                                
                        elif command == 'f':  # Face
                            if len(parts) >= 4:
                                face_vertices = []
                                for vertex_data in parts[1:]:
                                    # Parse vertex/texture/normal indices (e.g., "1/1/1" or "1//1" or "1")
                                    indices = vertex_data.split('/')
                                    
                                    v_idx = int(indices[0]) - 1  # OBJ uses 1-based indexing
                                    t_idx = None
                                    n_idx = None
                                    
                                    if len(indices) > 1 and indices[1]:
                                        t_idx = int(indices[1]) - 1
                                    if len(indices) > 2 and indices[2]:
                                        n_idx = int(indices[2]) - 1
                                        
                                    face_vertices.append((v_idx, t_idx, n_idx))
                                
                                # Store face data with material and group info
                                face_data = {
                                    'vertices': face_vertices,
                                    'material': current_material,
                                    'group': current_group
                                }
                                model.faces.append(face_data)
                                
                                # Add to group
                                if current_group not in model.groups:
                                    model.groups[current_group] = []
                                model.groups[current_group].append(len(model.faces) - 1)
                                
                        elif command == 'usemtl':  # Use material
                            if len(parts) >= 2:
                                current_material = parts[1]
                                
                        elif command == 'o' or command == 'g':  # Object or group
                            if len(parts) >= 2:
                                current_group = parts[1]
                                
                        elif command == 'mtllib':  # Material library
                            if len(parts) >= 2:
                                mtl_file = parts[1]
                                mtl_path = os.path.join(os.path.dirname(file_path), mtl_file)
                                materials = OBJLoader._load_materials(mtl_path)
                                model.materials.update(materials)
                                
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing line {line_num} in {file_path}: {line} - {e}")
                        continue
                        
            # Calculate model bounds
            model.calculate_bounds()
            
            logger.info(f"OBJ loaded successfully: {file_path}")
            logger.info(f"  Vertices: {len(model.vertices)}")
            logger.info(f"  Normals: {len(model.normals)}")
            logger.info(f"  Texture coords: {len(model.tex_coords)}")
            logger.info(f"  Faces: {len(model.faces)}")
            logger.info(f"  Materials: {len(model.materials)}")
            logger.info(f"  Groups: {list(model.groups.keys())}")
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to load OBJ file {file_path}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _load_materials(mtl_path: str) -> Dict[str, Dict]:
        """Load material definitions from MTL file."""
        materials = {}
        
        if not os.path.exists(mtl_path):
            logger.warning(f"MTL file not found: {mtl_path}")
            return materials
            
        current_material = None
        
        try:
            with open(mtl_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    parts = line.split()
                    if not parts:
                        continue
                        
                    command = parts[0]
                    
                    if command == 'newmtl':  # New material
                        if len(parts) >= 2:
                            current_material = parts[1]
                            materials[current_material] = {}
                            
                    elif current_material and len(parts) >= 2:
                        if command == 'Kd':  # Diffuse color
                            if len(parts) >= 4:
                                r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                                materials[current_material]['diffuse'] = (r, g, b)
                        elif command == 'Ka':  # Ambient color
                            if len(parts) >= 4:
                                r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                                materials[current_material]['ambient'] = (r, g, b)
                        elif command == 'Ks':  # Specular color
                            if len(parts) >= 4:
                                r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                                materials[current_material]['specular'] = (r, g, b)
                        elif command == 'Ns':  # Specular exponent
                            materials[current_material]['shininess'] = float(parts[1])
                        elif command == 'd' or command == 'Tr':  # Transparency
                            materials[current_material]['transparency'] = float(parts[1])
                            
            logger.info(f"Materials loaded from {mtl_path}: {list(materials.keys())}")
            
        except Exception as e:
            logger.warning(f"Error loading materials from {mtl_path}: {e}")
            
        return materials 