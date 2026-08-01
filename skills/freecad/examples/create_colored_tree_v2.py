import trimesh
import numpy as np
import os

def create_simple_colored_tree():
    print("Creating colorful tree mesh using Trimesh...")
    
    # 1. Create Trunk (Brown)
    trunk = trimesh.creation.cylinder(radius=8, height=60, sections=16)
    trunk.apply_translation([0, 0, 30])
    trunk.visual.face_colors = [139, 69, 19, 255]
    trunk.metadata['name'] = 'Trunk'
    
    # 2. Create Foliage Clusters (Green)
    f1 = trimesh.creation.uv_sphere(radius=30, count=[32, 32])
    f1.apply_translation([0, 0, 60])
    f1.visual.face_colors = [34, 139, 34, 255]
    f1.metadata['name'] = 'Foliage'
    
    clusters_data = [
        (20, 0, 45, 18),
        (-20, 0, 45, 18),
        (0, 20, 45, 18),
        (0, -20, 45, 18)
    ]
    
    foliage_group = [f1]
    for i, (x, y, z, r) in enumerate(clusters_data):
        c = trimesh.creation.uv_sphere(radius=r, count=[16, 16])
        c.apply_translation([x, y, z])
        c.visual.face_colors = [34, 139, 34, 255]
        c.metadata['name'] = f'Foliage_{i}'
        foliage_group.append(c)
        
    # Rotate Z-up to Y-up
    rotation = trimesh.transformations.rotation_matrix(np.radians(-90), [1, 0, 0])
    trunk.apply_transform(rotation)
    for f in foliage_group:
        f.apply_transform(rotation)
    
    # Create Scene instead of concatenated mesh
    scene = trimesh.Scene()
    scene.add_geometry(trunk, node_name='Trunk')
    for i, f in enumerate(foliage_group):
        scene.add_geometry(f, node_name=f'Foliage_{i}')
    
    # Export to GLB
    output_path = "/home/kaiser/gemini_project2/tree_model_colored.glb"
    scene.export(output_path)
    print(f"Colorful tree successfully exported to {output_path}")

if __name__ == "__main__":
    create_simple_colored_tree()
