---
name: freecad
description: Procedural 3D modeling, CAD automation, and engineering analysis using FreeCAD. Use for creating CAD parts, exporting STEP/STL/GLB files, Boolean CSG operations, parametric part design, and performing geometric computations.
version: 1.0.0
---

# FreeCAD Automation Skill

Use this skill to generate 3D geometry and perform engineering workflows using the FreeCAD Python API.

## Core Workflow

1. **Write a Python Script**: Use the `Part`, `Mesh`, `Draft`, and `importOBJ` modules.
2. **Ensure Path Compatibility**: Always add `/usr/lib/freecad/lib` and `/usr/share/freecad/Mod` to `sys.path`.
3. **Headless Execution**:
   - Use `freecadcmd -c script.py` for purely geometric tasks.
   - Use `xvfb-run -a freecad script.py` if GUI modules or offscreen rendering are required.
4. **Export & Convert**:
   - **STEP**: `Part.export([objs], "file.step")`
   - **STL**: `Mesh.export([objs], "file.stl")` or `shape.exportStl(path)`
   - **GLB**: Export to OBJ via `Mesh.export`, then convert using `obj2gltf -i file.obj -o file.glb --binary`.

## Python API Patterns

### Document Setup
```python
import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("PartName")
```

### Creating Primitives
```python
box = doc.addObject("Part::Box", "MyBox")
box.Length, box.Width, box.Height = 10, 10, 10
doc.recompute()
```

### Direct Shape API (simpler, for pure geometry)
```python
trunk = Part.makeCylinder(5, 50)
trunk.Placement.Base = FreeCAD.Vector(0, 0, 30)
shape = Part.makeCompound([trunk, foliage])
shape.exportStl(output_path)
```

### Boolean CSG Operations

```python
# Fuse (union)
fused = doc.addObject("Part::MultiFuse", "Fused")
fused.Shapes = [shape1, shape2, shape3]
doc.recompute()

# Cut (subtract)
cut = doc.addObject("Part::Cut", "CutBody")
cut.Base = base_shape
cut.Tool = tool_to_remove
doc.recompute()

# Common (intersection)
intersection = base.common(tool)
```

### Transformations
```python
# Translation
shape.Placement.Base = FreeCAD.Vector(x, y, z)
# or for direct shapes:
shape.translate(FreeCAD.Vector(dx, dy, dz))

# Rotation
shape.Placement.Rotation = FreeCAD.Rotation(axis_vector, angle_degrees)
# or for direct shapes:
shape.rotate(FreeCAD.Vector(cx, cy, cz), FreeCAD.Vector(ax, ay, az), angle_degrees)
```

### Patterned Features (Hole Arrays)
```python
holes = []
for i, x in enumerate(range(min_x, max_x, spacing)):
    offset = (spacing / 2.0) if (i % 2 == 1) else 0.0
    for y in range(min_y, max_y, spacing):
        if x**2 + (y + offset)**2 < (radius - margin)**2:
            h = Part.makeCylinder(hole_r, thickness + 2.0)
            h.translate(FreeCAD.Vector(x, y + offset, -1.0))
            holes.append(h)

all_holes = Part.makeCompound(holes)
result = base.cut(all_holes)
```

## Export Workflows

| Format | Method | Use Case |
|--------|--------|----------|
| STEP | `Part.export([obj], "file.step")` | CAD interchange |
| STL | `Mesh.export([obj], "file.stl")` or `shape.exportStl(path)` | 3D printing |
| OBJ | `Mesh.export([obj], "file.obj")` | Intermediate for GLB |
| GLB | `obj2gltf -i file.obj -o file.glb --binary` | Web/AR viewers |

### GLB with Vertex Colors (Trimesh)
```python
import trimesh
mesh = trimesh.load("model.stl")
mesh.visual.face_colors = [R, G, B, 255]
mesh.export("model.glb")
```

## Critical Constraints

- **Absolute Paths**: Always use `os.path.abspath()` for export to avoid directory confusion in `freecadcmd`.
- **Recompute**: Always call `doc.recompute()` after modifying properties and before export.
- **Unit System**: Default is mm.
- **Orientation**: FreeCAD is **Z-up**. For web/GLB viewers, apply a -90 deg X-axis rotation to convert to **Y-up**.

## Dependencies

| Package | Install | Purpose |
|---------|---------|---------|
| freecad | `sudo apt install freecad` | CAD engine + Python API |
| xvfb | `sudo apt install xvfb` | Headless GUI |
| obj2gltf | `npm install -g obj2gltf` | GLB export |
| trimesh | `pip install trimesh` | Mesh manipulation, vertex colors |
| jax/jax-fem | `pip install jax jax-fem` | Differentiable optimization (optional) |

## LLM-Driven CAD (Ollama Pattern)

For agentic LLM-to-CAD workflows:

1. Send FreeCAD API cheat sheet + user instruction to Ollama
2. Extract Python code from LLM response
3. Prepend `sys.path` setup for FreeCAD libraries
4. Execute via `freecadcmd -c generated_script.py`
5. Check if output file was created
6. On failure: feed error back to LLM for self-correction (max 3 retries)

Constrain the LLM to only use documented functions:
```python
prompt = f"""
You are a FreeCAD Python expert. Write a script for: {instruction}

ONLY use these APIs:
- Part.makeCylinder(radius, height)
- Part.makeSphere(radius)
- shape.Placement.Base = FreeCAD.Vector(x, y, z)
- Mesh.export([shapes], output_path)

CRITICAL RULES:
1. ONLY output Python code. No explanations.
2. NEVER invent functions.
"""
```

## Testing

```python
# Smoke test pattern
import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("TestDoc")
box = doc.addObject("Part::Box", "TestBox")
box.Length, box.Width, box.Height = 10.0, 10.0, 10.0
doc.recompute()

output_path = os.path.abspath("test_box.stl")
Mesh.export([box], output_path)
assert os.path.exists(output_path), f"Export failed: {output_path}"
```
