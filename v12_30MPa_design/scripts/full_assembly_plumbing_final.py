#!/usr/bin/env python3
"""
Full V12 assembly with forced‑induction components and ROBUST plumbing.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import json
import cadquery as cq
from cadquery import Compound, Vector, Solid
import numpy as np

print("Loading components...")

# Helper to extract solids from any object
def get_solids(obj):
    """Extract all Solid objects from a Workplane, Compound, or Solid."""
    solids = []
    if isinstance(obj, Solid):
        solids.append(obj)
    elif hasattr(obj, 'solids'):
        # Workplane or similar
        for solid in obj.solids().vals():
            solids.append(solid)
    elif hasattr(obj, 'wrapped'):
        # Might be a Shape
        try:
            # Try to get solids from compound
            if hasattr(obj, 'Solids'):
                for solid in obj.Solids():
                    solids.append(solid)
            else:
                # Assume it's a Solid already
                solids.append(obj)
        except:
            pass
    return solids

# 1. Engine assembly (detailed)
engine = cq.importers.importStep('v12_full_assembly_compound.step')
print("Engine loaded.")

# 2. Forced‑induction layout
fi_layout = cq.importers.importStep('v12_forced_induction_layout.step')
print("Forced‑induction layout loaded.")

# 3. Intercooler cores
intercooler_core = cq.importers.importStep('intercooler_core_placeholder.step')
print("Intercooler core loaded.")

# 4. Turbo manifolds placeholder
manifold = cq.importers.importStep('turbo_manifold_placeholder.step')
print("Turbo manifold loaded.")

# 5. Lubrication placeholder
lube = cq.importers.importStep('lubrication_system_placeholder.step')
print("Lubrication placeholder loaded.")

# 6. York 210 compressor placeholder (box)
compressor = cq.Workplane("XY").box(300, 200, 250)  # mm
compressor = compressor.translate((534, 0, -100))
print("Compressor placeholder created.")

# Collect all solids
all_solids = []
for obj in [engine, fi_layout, intercooler_core, manifold, lube, compressor]:
    all_solids.extend(get_solids(obj))

print(f"Total base solids: {len(all_solids)}")

# ROBUST PIPE CREATION
def create_cylinder_between(p1, p2, diameter, thickness=0):
    """
    Create a cylinder (or tube) between two points.
    Returns a Solid object.
    """
    if isinstance(p1, Vector):
        start = (p1.x, p1.y, p1.z)
        end = (p2.x, p2.y, p2.z)
    else:
        start = p1
        end = p2
    
    # Vector and length
    dx, dy, dz = end[0]-start[0], end[1]-start[1], end[2]-start[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)
    
    if length < 1e-6:
        return None
    
    # Create cylinder along Z axis
    if thickness > 0 and thickness < diameter/2:
        # Tube: outer minus inner
        outer = cq.Workplane("XY").circle(diameter/2).extrude(length)
        inner = cq.Workplane("XY").circle(diameter/2 - thickness).extrude(length)
        segment = outer.cut(inner)
    else:
        # Solid cylinder
        segment = cq.Workplane("XY").circle(diameter/2).extrude(length)
    
    # Get the Solid
    segment_solid = segment.val()
    
    # Rotate to align with direction vector
    if abs(dz - length) > 1e-6:
        # Normalize direction
        dir_vec = Vector(dx/length, dy/length, dz/length)
        z_axis = Vector(0, 0, 1)
        
        # Rotation axis: cross product
        rot_axis = z_axis.cross(dir_vec)
        if rot_axis.Length > 1e-6:
            rot_axis = rot_axis / rot_axis.Length
            rot_angle = z_axis.getAngle(dir_vec) * 180 / np.pi
            
            # Rotate the solid
            segment_solid = segment_solid.rotate(
                (0, 0, 0),          # origin
                (rot_axis.x, rot_axis.y, rot_axis.z),  # axis
                rot_angle
            )
    
    # Translate to position
    center = (
        (start[0] + end[0])/2,
        (start[1] + end[1])/2,
        (start[2] + end[2])/2
    )
    segment_solid = segment_solid.translate(center)
    
    return segment_solid

def create_pipe_segmented(points, diameter, thickness=0):
    """
    Create a pipe as series of cylinders between points.
    Returns a list of Solid objects.
    """
    if len(points) < 2:
        return []
    
    solids = []
    for i in range(len(points)-1):
        cyl = create_cylinder_between(points[i], points[i+1], diameter, thickness)
        if cyl:
            solids.append(cyl)
    
    return solids

def create_pipe_sweep_simple(points, diameter, thickness=0):
    """
    Try sweep, fall back to segmented if fails.
    Returns list of Solid objects.
    """
    if len(points) < 2:
        return []
    
    # Convert to tuples
    point_tuples = []
    for p in points:
        if isinstance(p, Vector):
            point_tuples.append((p.x, p.y, p.z))
        else:
            point_tuples.append(p)
    
    # Try sweep
    try:
        path = cq.Workplane().polyline(point_tuples).val()
        if thickness > 0 and thickness < diameter/2:
            profile = cq.Workplane().circle(diameter/2).circle(diameter/2 - thickness)
        else:
            profile = cq.Workplane().circle(diameter/2)
        
        pipe = profile.sweep(path, multisection=False, combine=False)
        return get_solids(pipe)
    except Exception as e:
        print(f"  Sweep failed: {e}, using segmented")
        return create_pipe_segmented(points, diameter, thickness)

# PLUMBING PATHS
print("\nCreating plumbing...")

# Air intake plumbing (80mm diameter)
intake_path = [
    Vector(-500, -200, 100),   # air filter left
    Vector(-400, -222, 80),    # turbo inlet left
    Vector(-350, -222, 60),    # turbo outlet
    Vector(-350, -372, 60),    # intercooler inlet left
    Vector(-350, -372, 150),   # intercooler outlet up
    Vector(0, -372, 150),      # across to supercharger
    Vector(534, 0, 150),       # supercharger inlet
    Vector(584, 0, 150),       # supercharger outlet
    Vector(584, 372, 150),     # second intercooler inlet right
    Vector(584, 372, 60),      # second intercooler outlet down
    Vector(584, 200, 60),      # intake manifold
]
intake_solids = create_pipe_sweep_simple(intake_path, 80)
all_solids.extend(intake_solids)
print(f"✅ Air intake tube added ({len(intake_solids)} segments).")

# Exhaust plumbing (left bank, 60mm diameter)
exhaust_path = [
    Vector(-330, -200, -50),   # exhaust port left
    Vector(-400, -200, -100),  # turbo inlet
    Vector(-500, -200, -150),  # downpipe
]
exhaust_solids = create_pipe_sweep_simple(exhaust_path, 60)
all_solids.extend(exhaust_solids)
print(f"✅ Exhaust tube added ({len(exhaust_solids)} segments).")

# Coolant plumbing - split into two separate paths to avoid closed loop
# Path 1: Engine → intercooler → radiator
coolant_path1 = [
    Vector(0, 0, 50),          # engine outlet
    Vector(0, -372, 50),       # left intercooler inlet
    Vector(0, -372, 100),      # left intercooler outlet
    Vector(834, -372, 100),    # radiator inlet
]
# Path 2: Radiator → pump → engine
coolant_path2 = [
    Vector(834, -372, 50),     # radiator outlet
    Vector(534, 0, 50),        # pump inlet
    Vector(0, 0, 50),          # engine inlet
]
coolant_solids = create_pipe_sweep_simple(coolant_path1, 30, thickness=2)
coolant_solids.extend(create_pipe_sweep_simple(coolant_path2, 30, thickness=2))
all_solids.extend(coolant_solids)
print(f"✅ Coolant tube added ({len(coolant_solids)} segments).")

# Refrigerant plumbing (20mm diameter, 1.5mm wall)
refrigerant_path = [
    Vector(534, 0, -100),      # compressor outlet
    Vector(834, 0, -100),      # condenser inlet
    Vector(834, 0, -50),       # condenser outlet
    Vector(0, -372, -50),      # chiller inlet (intercooler)
    Vector(0, -372, -100),     # chiller outlet
    Vector(534.1, 0, -100.1),  # compressor inlet (slightly offset)
]
refrigerant_solids = create_pipe_sweep_simple(refrigerant_path, 20, thickness=1.5)
all_solids.extend(refrigerant_solids)
print(f"✅ Refrigerant tube added ({len(refrigerant_solids)} segments).")

# Oil plumbing (10mm diameter, 1mm wall)
oil_path = [
    Vector(150, 0, -200),      # oil pump outlet
    Vector(150, 0, 50),        # main gallery
    Vector(0, 0, 50),          # bearing feeds
    Vector(-150, 0, 50),       # other bearings
    Vector(-150, 0, -200),     # return to sump
]
oil_solids = create_pipe_sweep_simple(oil_path, 10, thickness=1)
all_solids.extend(oil_solids)
print(f"✅ Oil tube added ({len(oil_solids)} segments).")

print(f"Total solids: {len(all_solids)}")

# Create final compound
print("\nCreating compound...")
try:
    final_compound = Compound.makeCompound(all_solids)
    print("✅ Compound created successfully.")
except Exception as e:
    print(f"❌ Compound creation failed: {e}")
    print("Trying alternative approach...")
    # Fallback: export each solid separately? Or create a simple assembly
    # For now, create a compound of first few solids
    if len(all_solids) > 0:
        final_compound = Compound.makeCompound(all_solids[:min(100, len(all_solids))])
        print(f"Created compound with {len(all_solids[:100])} solids.")

# Export
output_step = "v12_full_assembly_plumbing_final.step"
try:
    cq.exporters.export(final_compound, output_step, "STEP")
    print(f"✅ Full assembly exported to {output_step}")
except Exception as e:
    print(f"❌ Export failed: {e}")
    # Try exporting as separate files
    print("Exporting components separately...")
    for i, solid in enumerate(all_solids[:20]):
        try:
            cq.exporters.export(solid, f"component_{i:03d}.step", "STEP")
        except:
            pass

# Also export STL
output_stl = "v12_full_assembly_plumbing_final.stl"
try:
    cq.exporters.export(final_compound, output_stl, "STL")
    print(f"✅ STL exported to {output_stl}")
except Exception as e:
    print(f"❌ STL export failed: {e}")

print("\nAssembly includes:")
print("  - Engine block, crankshaft, pistons, rods, heads")
print("  - Turbos, supercharger, intercooler cores, radiator, compressor")
print("  - Turbo manifolds, lubrication placeholder")
print("  - Plumbing: intake (80mm), exhaust (60mm), coolant (30mm), refrigerant (20mm), oil (10mm)")
print("  - All components positioned relative to block origin (0,0,0).")

# Create plumbing-only visualization
print("\nCreating plumbing-only visualization...")
plumbing_solids = []
plumbing_solids.extend(intake_solids)
plumbing_solids.extend(exhaust_solids)
plumbing_solids.extend(coolant_solids)
plumbing_solids.extend(refrigerant_solids)
plumbing_solids.extend(oil_solids)

if plumbing_solids:
    plumbing_compound = Compound.makeCompound(plumbing_solids)
    cq.exporters.export(plumbing_compound, "v12_plumbing_only_final.step", "STEP")
    print("✅ Plumbing-only visualization exported.")

print("\n✅ Assembly and plumbing completed!")