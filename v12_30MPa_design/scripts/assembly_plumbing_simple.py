#!/usr/bin/env python3
"""
Create V12 assembly with simple plumbing (solid cylinders for visualization).
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import cadquery as cq
from cadquery import Vector, Compound, Solid
import numpy as np
import time

print("=== V12 Assembly with Plumbing ===")
start_time = time.time()

# ------------------------------------------------------------
# 1. Load existing assemblies
# ------------------------------------------------------------
print("\n1. Loading existing assemblies...")
load_start = time.time()

# Engine assembly (already includes block, crank, pistons, rods, heads)
try:
    engine = cq.importers.importStep('v12_full_assembly_compound.step')
    engine_solids = engine.solids().vals()
    print(f"  Engine: {len(engine_solids)} solids")
except Exception as e:
    print(f"  ❌ Failed to load engine: {e}")
    engine_solids = []

# Forced‑induction layout (turbos, supercharger, intercoolers, radiator, compressor placeholder)
try:
    fi_layout = cq.importers.importStep('v12_forced_induction_layout.step')
    fi_solids = fi_layout.solids().vals()
    print(f"  Forced‑induction layout: {len(fi_solids)} solids")
except Exception as e:
    print(f"  ❌ Failed to load forced‑induction layout: {e}")
    fi_solids = []

# Additional components
additional_solids = []
for name, path in [
    ("Intercooler core", "intercooler_core_placeholder.step"),
    ("Turbo manifold", "turbo_manifold_placeholder.step"),
    ("Lubrication", "lubrication_system_placeholder.step"),
]:
    try:
        obj = cq.importers.importStep(path)
        additional_solids.extend(obj.solids().vals())
        print(f"  {name}: loaded")
    except Exception as e:
        print(f"  ❌ Failed to load {name}: {e}")

# Compressor placeholder (create simple box)
compressor = cq.Workplane("XY").box(300, 200, 250).translate((534, 0, -100))
compressor_solid = compressor.val()
additional_solids.append(compressor_solid)
print(f"  Compressor placeholder: created")

print(f"  Loading time: {time.time() - load_start:.1f}s")

# ------------------------------------------------------------
# 2. Create plumbing (solid cylinders for visualization)
# ------------------------------------------------------------
print("\n2. Creating plumbing (solid cylinders)...")
plumbing_start = time.time()

def create_cylinder_between(p1, p2, diameter):
    """Create a solid cylinder between two points. Returns Solid."""
    if isinstance(p1, Vector):
        start = (p1.x, p1.y, p1.z)
        end = (p2.x, p2.y, p2.z)
    else:
        start = p1
        end = p2
    
    dx, dy, dz = end[0]-start[0], end[1]-start[1], end[2]-start[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)
    
    if length < 1e-6:
        return None
    
    # Create cylinder along Z axis
    cyl_wp = cq.Workplane("XY").circle(diameter/2).extrude(length)
    cyl = cyl_wp.val()  # Get Solid
    
    # Rotate if not aligned with Z
    if abs(dz - length) > 1e-6:
        dir_vec = Vector(dx/length, dy/length, dz/length)
        z_axis = Vector(0, 0, 1)
        rot_axis = z_axis.cross(dir_vec)
        if rot_axis.Length > 1e-6:
            rot_axis = rot_axis / rot_axis.Length
            rot_angle = z_axis.getAngle(dir_vec) * 180 / np.pi
            cyl = cyl.rotate((0,0,0), (rot_axis.x, rot_axis.y, rot_axis.z), rot_angle)
    
    # Translate to position
    center = (
        (start[0] + end[0])/2,
        (start[1] + end[1])/2,
        (start[2] + end[2])/2
    )
    cyl = cyl.translate(center)
    return cyl

plumbing_solids = []

# Air intake (80mm)
intake_path = [
    Vector(-500, -200, 100),
    Vector(-400, -222, 80),
    Vector(-350, -222, 60),
    Vector(-350, -372, 60),
    Vector(-350, -372, 150),
    Vector(0, -372, 150),
    Vector(534, 0, 150),
    Vector(584, 0, 150),
    Vector(584, 372, 150),
    Vector(584, 372, 60),
    Vector(584, 200, 60),
]
for i in range(len(intake_path)-1):
    cyl = create_cylinder_between(intake_path[i], intake_path[i+1], 80)
    if cyl:
        plumbing_solids.append(cyl)
print(f"  Intake: {len(intake_path)-1} segments")

# Exhaust (left bank, 60mm)
exhaust_path = [
    Vector(-330, -200, -50),
    Vector(-400, -200, -100),
    Vector(-500, -200, -150),
]
for i in range(len(exhaust_path)-1):
    cyl = create_cylinder_between(exhaust_path[i], exhaust_path[i+1], 60)
    if cyl:
        plumbing_solids.append(cyl)
print(f"  Exhaust: {len(exhaust_path)-1} segments")

# Coolant (30mm) - split to avoid closed loop
coolant_paths = [
    [Vector(0, 0, 50), Vector(0, -372, 50), Vector(0, -372, 100), Vector(834, -372, 100)],
    [Vector(834, -372, 50), Vector(534, 0, 50), Vector(0, 0, 50)],
]
for path in coolant_paths:
    for i in range(len(path)-1):
        cyl = create_cylinder_between(path[i], path[i+1], 30)
        if cyl:
            plumbing_solids.append(cyl)
print(f"  Coolant: {sum(len(p)-1 for p in coolant_paths)} segments")

# Refrigerant (20mm)
refrigerant_path = [
    Vector(534, 0, -100),
    Vector(834, 0, -100),
    Vector(834, 0, -50),
    Vector(0, -372, -50),
    Vector(0, -372, -100),
    Vector(534.1, 0, -100.1),  # slightly offset
]
for i in range(len(refrigerant_path)-1):
    cyl = create_cylinder_between(refrigerant_path[i], refrigerant_path[i+1], 20)
    if cyl:
        plumbing_solids.append(cyl)
print(f"  Refrigerant: {len(refrigerant_path)-1} segments")

# Oil (10mm)
oil_path = [
    Vector(150, 0, -200),
    Vector(150, 0, 50),
    Vector(0, 0, 50),
    Vector(-150, 0, 50),
    Vector(-150, 0, -200),
]
for i in range(len(oil_path)-1):
    cyl = create_cylinder_between(oil_path[i], oil_path[i+1], 10)
    if cyl:
        plumbing_solids.append(cyl)
print(f"  Oil: {len(oil_path)-1} segments")

print(f"  Total plumbing segments: {len(plumbing_solids)}")
print(f"  Plumbing creation time: {time.time() - plumbing_start:.1f}s")

# ------------------------------------------------------------
# 3. Combine all solids
# ------------------------------------------------------------
print("\n3. Combining all solids...")
combine_start = time.time()

all_solids = []
all_solids.extend(engine_solids)
all_solids.extend(fi_solids)
all_solids.extend(additional_solids)
all_solids.extend(plumbing_solids)

print(f"  Total solids: {len(all_solids)}")

# Create compound
try:
    final_compound = Compound.makeCompound(all_solids)
    print(f"  Compound created successfully")
except Exception as e:
    print(f"  ❌ Compound creation failed: {e}")
    # Try creating compound in batches
    print("  Trying batch creation...")
    batch_size = 50
    compounds = []
    for i in range(0, len(all_solids), batch_size):
        batch = all_solids[i:i+batch_size]
        try:
            comp = Compound.makeCompound(batch)
            compounds.append(comp)
        except:
            pass
    if compounds:
        # Combine compounds
        final_compound = Compound.makeCompound(compounds)
        print(f"  Created compound from {len(compounds)} batches")
    else:
        print("  ❌ Could not create any compound")
        sys.exit(1)

print(f"  Combine time: {time.time() - combine_start:.1f}s")

# ------------------------------------------------------------
# 4. Export
# ------------------------------------------------------------
print("\n4. Exporting...")
export_start = time.time()

# Main assembly
output_step = "v12_assembly_with_plumbing_simple.step"
try:
    cq.exporters.export(final_compound, output_step, "STEP")
    print(f"  ✅ Main assembly exported to {output_step}")
except Exception as e:
    print(f"  ❌ Export failed: {e}")

# Plumbing-only assembly
if plumbing_solids:
    try:
        plumbing_compound = Compound.makeCompound(plumbing_solids)
        cq.exporters.export(plumbing_compound, "v12_plumbing_simple.step", "STEP")
        print(f"  ✅ Plumbing-only exported to v12_plumbing_simple.step")
    except Exception as e:
        print(f"  ❌ Plumbing export failed: {e}")

# STL version
try:
    cq.exporters.export(final_compound, "v12_assembly_with_plumbing_simple.stl", "STL")
    print(f"  ✅ STL exported to v12_assembly_with_plumbing_simple.stl")
except Exception as e:
    print(f"  ❌ STL export failed: {e}")

print(f"  Export time: {time.time() - export_start:.1f}s")

# ------------------------------------------------------------
# 5. Summary
# ------------------------------------------------------------
total_time = time.time() - start_time
print(f"\n=== Summary ===")
print(f"Total time: {total_time:.1f}s")
print(f"Total components: {len(all_solids)} solids")
print(f"Plumbing segments: {len(plumbing_solids)}")
print(f"\nFiles created:")
print(f"  - v12_assembly_with_plumbing_simple.step (full assembly)")
print(f"  - v12_plumbing_simple.step (plumbing only)")
print(f"  - v12_assembly_with_plumbing_simple.stl (3D print)")
print(f"\nPlumbing diameters:")
print(f"  - Intake: 80mm")
print(f"  - Exhaust: 60mm")
print(f"  - Coolant: 30mm")
print(f"  - Refrigerant: 20mm")
print(f"  - Oil: 10mm")
print(f"\n✅ Assembly with plumbing completed!")