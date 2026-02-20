#!/usr/bin/env python3
"""Load an OBJ and print its bounding box and the scale factor the app would use.
Run from project root: python scripts/check_obj_bounds.py "assets/ship/NCC Enterprise/NCC-1701.obj"
"""
import sys
import os

# Run from project root so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components.rendering.obj_loader import OBJLoader

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_obj_bounds.py <path/to/model.obj>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
    print(f"Loading {path} ...")
    model = OBJLoader.load(path)
    if not model:
        print("Failed to load OBJ")
        sys.exit(1)
    if not model.bounds:
        model.calculate_bounds()
    min_x, min_y, min_z, max_x, max_y, max_z = model.bounds
    width = max_x - min_x
    height = max_y - min_y
    depth = max_z - min_z
    max_dim = max(width, height, depth)
    center = model.get_center()
    scale_5 = model.get_scale_factor(target_size=5.0)
    scale_35 = model.get_scale_factor(target_size=3.5)
    print()
    print("Bounds (min_x, min_y, min_z, max_x, max_y, max_z):")
    print(f"  {model.bounds}")
    print()
    print("Dimensions:")
    print(f"  width  (X): {width}")
    print(f"  height (Y): {height}")
    print(f"  depth  (Z): {depth}")
    print(f"  max dimension: {max_dim}")
    print()
    print("Center:", center)
    print()
    print("Scale factor (target_size=5.0):", scale_5)
    print("Scale factor (target_size=3.5):", scale_35)
    print()
    print("Vertices:", len(model.vertices))
    print("Faces:", len(model.faces))

if __name__ == "__main__":
    main()
