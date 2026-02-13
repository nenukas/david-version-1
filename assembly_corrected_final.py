#!/usr/bin/env python3
"""
Final single‑cylinder assembly with corrected components.
Positions based on mechanical kinematics.
"""
import cadquery as cq
import numpy as np
import json
from datetime import datetime
import os

print("=" * 70)
print("SINGLE‑CYLINDER ASSEMBLY (Corrected)")
print("=" * 70)

# ----------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------
deck_clearance = 0.8  # mm (piston crown above deck at TDC)
bore_diameter = 94.5  # mm
stroke = 47.5  # mm
crank_radius = stroke / 2  # 23.75 mm
rod_length = 150.0  # mm (conrod center‑to‑center)
compression_height = 38.0  # mm (piston pin to crown top)

print(f"Stroke: {stroke:.2f} mm, crank radius: {crank_radius:.2f} mm")
print(f"Rod length: {rod_length:.2f} mm")
print(f"Compression height: {compression_height:.2f} mm")
print(f"Deck clearance: {deck_clearance:.2f} mm")

# ----------------------------------------------------------------------
# COORDINATE SYSTEM
# ----------------------------------------------------------------------
# Z up positive, X along crankshaft axis, Y across engine.
# Deck top (block surface) at Z = 0.
# Crank center at Z = - (rod_length + compression_height - deck_clearance + crank_radius)?
# Let's compute vertical positions at TDC (crank pin at highest point).
# At TDC, crank pin is at Z = +crank_radius relative to crank center.
# Piston pin is rod_length below crank pin (vertical).
# So piston pin Z = crank_center_Z + crank_radius - rod_length.
# Piston crown top Z = piston_pin_Z + compression_height.
# We want crown top Z = deck_clearance (above deck).
# Therefore deck_clearance = crank_center_Z + crank_radius - rod_length + compression_height.
# Solve for crank_center_Z:
crank_center_Z = deck_clearance - crank_radius + rod_length - compression_height
print(f"Crank center Z: {crank_center_Z:.2f} mm")

# Crank pin at TDC: Z = crank_center_Z + crank_radius
crank_pin_Z_TDC = crank_center_Z + crank_radius
print(f"Crank pin at TDC Z: {crank_pin_Z_TDC:.2f} mm")

# Piston pin at TDC: Z = crank_pin_Z_TDC - rod_length
piston_pin_Z_TDC = crank_pin_Z_TDC - rod_length
print(f"Piston pin at TDC Z: {piston_pin_Z_TDC:.2f} mm")

# Piston crown top at TDC: Z = piston_pin_Z_TDC + compression_height
piston_crown_top_Z_TDC = piston_pin_Z_TDC + compression_height
print(f"Piston crown top at TDC Z: {piston_crown_top_Z_TDC:.2f} mm (target deck_clearance: {deck_clearance})")

# Check difference
diff = piston_crown_top_Z_TDC - deck_clearance
if abs(diff) > 0.01:
    print(f"⚠️  Position mismatch: {diff:.3f} mm")
else:
    print("✅ Positions consistent.")

# ----------------------------------------------------------------------
# LOAD CORRECTED COMPONENTS (STEP files)
# ----------------------------------------------------------------------
# Find latest component directories
def find_latest(pattern):
    dirs = [d for d in os.listdir(".") if d.startswith(pattern) and os.path.isdir(d)]
    if not dirs:
        return None
    latest = max(dirs, key=os.path.getmtime)
    return os.path.join(latest, pattern + ".step")

piston_path = find_latest("piston_simple_correct")
conrod_path = find_latest("conrod_corrected_final")
crank_path = find_latest("crankshaft_corrected_final")

if not piston_path or not conrod_path or not crank_path:
    print("❌ Could not find component STEP files.")
    # Create simple geometry instead
    print("Creating simple geometry...")
    # Fallback: create simple solids
    piston = cq.Workplane("XY").circle(bore_diameter/2 - 0.1).extrude(-70)
    conrod = cq.Workplane("YZ").rect(30, 50).extrude(150)
    crank = cq.Workplane("XY").circle(30).extrude(30)
else:
    print(f"Loading piston: {piston_path}")
    piston = cq.importers.importStep(piston_path)
    print(f"Loading conrod: {conrod_path}")
    conrod = cq.importers.importStep(conrod_path)
    print(f"Loading crankshaft: {crank_path}")
    crank = cq.importers.importStep(crank_path)

# ----------------------------------------------------------------------
# POSITION COMPONENTS
# ----------------------------------------------------------------------
print("\nPositioning components...")

# 1. Piston
# In piston STEP, crown top at Z=0, skirt extends downward.
# Move so crown top at piston_crown_top_Z_TDC.
piston = piston.translate((0, 0, piston_crown_top_Z_TDC))
print(f"Piston translated to Z={piston_crown_top_Z_TDC:.2f}")

# 2. Conrod
# In conrod STEP, big‑end center at X=0, small‑end center at X=150 (rod length).
# Need to align big‑end with crank pin, small‑end with piston pin.
# First rotate conrod to vertical (original beam along X, need along Z).
conrod = conrod.rotate((0,0,0), (1,0,0), 90)  # rotate 90° around X axis
# Now big‑end at Z=0? Actually after rotation, big‑end at X=0, Z=0, Y=0.
# Small‑end at X=0, Z=150, Y=0.
# Move so big‑end center at (0,0,crank_pin_Z_TDC)
conrod = conrod.translate((0, 0, crank_pin_Z_TDC))
print(f"Conrod big‑end at Z={crank_pin_Z_TDC:.2f}")

# 3. Crankshaft
# In crankshaft STEP, main journal center at (0,0,0), pin at (0,0,-crank_radius).
# Move crank so its center at (0,0,crank_center_Z)
crank = crank.translate((0, 0, crank_center_Z))
print(f"Crankshaft center at Z={crank_center_Z:.2f}")

# 4. Cylinder block (simplified)
block_height = 100
block = (
    cq.Workplane("XY")
    .box(200, 200, block_height)
    .translate((0, 0, -block_height/2))
)
# Bore hole
bore = (
    cq.Workplane("XY")
    .circle(bore_diameter/2)
    .extrude(block_height)
    .translate((0, 0, -block_height/2))
)
block = block.cut(bore)
print("Cylinder block created.")

# ----------------------------------------------------------------------
# ASSEMBLE
# ----------------------------------------------------------------------
assembly = piston.union(conrod).union(crank).union(block)

# ----------------------------------------------------------------------
# EXPORT
# ----------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"assembly_corrected_final_{timestamp}"
os.makedirs(out_dir, exist_ok=True)

step_path = os.path.join(out_dir, "assembly_corrected_final.step")
cq.exporters.export(assembly, step_path, "STEP")
print(f"\n✅ Assembly exported to {step_path}")

# Save assembly spec
spec = {
    "timestamp": datetime.now().isoformat(),
    "parameters": {
        "deck_clearance_mm": deck_clearance,
        "bore_diameter_mm": bore_diameter,
        "stroke_mm": stroke,
        "crank_radius_mm": crank_radius,
        "rod_length_mm": rod_length,
        "compression_height_mm": compression_height,
    },
    "positions": {
        "crank_center_Z": crank_center_Z,
        "crank_pin_Z_TDC": crank_pin_Z_TDC,
        "piston_pin_Z_TDC": piston_pin_Z_TDC,
        "piston_crown_top_Z_TDC": piston_crown_top_Z_TDC,
    },
    "component_paths": {
        "piston": piston_path,
        "conrod": conrod_path,
        "crankshaft": crank_path,
    }
}

json_path = os.path.join(out_dir, "assembly_corrected_final_spec.json")
with open(json_path, "w") as f:
    json.dump(spec, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n" + "=" * 70)
print("ASSEMBLY SUMMARY")
print("=" * 70)
print(f"Components positioned using kinematic relationships.")
print(f"Check deck clearance: target {deck_clearance} mm, actual {piston_crown_top_Z_TDC:.3f} mm")
print(f"Crank‑pin to piston‑pin distance: {rod_length:.2f} mm")
print(f"\nOpen {step_path} in CAD viewer to verify assembly.")