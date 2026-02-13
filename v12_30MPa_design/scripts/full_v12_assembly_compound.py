#!/usr/bin/env python3
"""
Full V12 assembly using Compound (multiple solids without union).
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import json
import cadquery as cq
from cadquery import Compound

print("Loading geometry data...")
with open('full_assembly_data.json', 'r') as f:
    data = json.load(f)

cyl_positions = data['cylinder_positions']
crank_center_z = -data['deck_thickness'] - data['crank_radius']

# Load component shapes
print("Loading components...")
block_shape = cq.importers.importStep('cylinder_block_deck_12mm.step').val()
crank_shape = cq.importers.importStep('crankshaft_30MPa_unified.step').val()
piston_shape = cq.importers.importStep('piston_crown_15mm_full.step').val()
rod_shape = cq.importers.importStep('conrod_opt_relaxed2_30MPa_results_20260213_010504.step').val()
head_shape = cq.importers.importStep('cylinder_head_simplified.step').val()

# Position crankshaft
crank_shape = crank_shape.translate(cq.Vector(0, 0, crank_center_z))

# Collect all shapes
all_shapes = [block_shape, crank_shape]

# Add pistons and rods
for cyl in cyl_positions:
    x, y = cyl['x'], cyl['y']
    # Piston
    piston = piston_shape.translate(cq.Vector(x, y, 0))
    all_shapes.append(piston)
    # Rod
    rod = rod_shape.translate(cq.Vector(x, y, -38.0))  # compression height
    all_shapes.append(rod)
    # Head
    head = head_shape.translate(cq.Vector(x, y, 0))
    all_shapes.append(head)

print(f"Total shapes: {len(all_shapes)}")

# Create compound
print("Creating compound...")
compound = Compound.makeCompound(all_shapes)

# Export
output_step = "v12_full_assembly_compound.step"
cq.exporters.export(compound, output_step, "STEP")
print(f"✅ Assembly exported to {output_step}")

# Also export STL
output_stl = "v12_full_assembly_compound.stl"
cq.exporters.export(compound, output_stl, "STL")
print(f"✅ STL exported to {output_stl}")

print("\nNote: Assembly contains separate solids (no boolean union).")
print("  - Pistons at TDC.")
print("  - Rods placed vertically.")
print("  - Heads duplicated per cylinder.")