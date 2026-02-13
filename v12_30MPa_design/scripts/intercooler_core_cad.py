#!/usr/bin/env python3
"""
Generate simplified water‑cooled intercooler core (plate‑fin) placeholder.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import cadquery as cq

# Core dimensions (approx)
width = 400  # mm
height = 400
depth = 100
fin_thickness = 0.2  # mm
fin_spacing = 2.0    # mm
tube_thickness = 1.5
tube_width = 20
tube_height = 15

print("Creating intercooler core placeholder...")
# Base block
core = cq.Workplane("XY").box(width, depth, height)

# Add coolant tubes (simplified as rectangular ducts)
tube = cq.Workplane("YZ").box(tube_width, tube_height, height)
tubes = []
for i in range(int(width / (tube_width + 10))):
    x = -width/2 + 10 + i * (tube_width + 10)
    tubes.append(tube.translate((x, 0, 0)))
# Union all tubes
tubes_union = tubes[0]
for t in tubes[1:]:
    tubes_union = tubes_union.union(t)
# Subtract from core to create passages
core = core.cut(tubes_union)

# Add fins (simplified as thin plates)
fin = cq.Workplane("XZ").box(width, fin_thickness, height)
fins = []
for j in range(int(depth / fin_spacing)):
    y = -depth/2 + fin_spacing/2 + j * fin_spacing
    fins.append(fin.translate((0, y, 0)))
# Union fins
fins_union = fins[0]
for f in fins[1:]:
    fins_union = fins_union.union(f)
core = core.union(fins_union)

# Add inlet/outlet manifolds
manifold = cq.Workplane("XY").cylinder(50, 30)
inlet = manifold.translate((-width/2 - 30, 0, height/2 - 50))
outlet = manifold.translate((width/2 + 30, 0, height/2 - 50))
core = core.union(inlet).union(outlet)

# Export
output_step = "intercooler_core_placeholder.step"
cq.exporters.export(core, output_step, "STEP")
print(f"✅ Intercooler core placeholder exported to {output_step}")

# Also STL
output_stl = "intercooler_core_placeholder.stl"
cq.exporters.export(core, output_stl, "STL")
print(f"✅ STL exported to {output_stl}")

print("\nNote: This is a simplified geometry for visualization.")
print("  - Fins are solid plates (no detailed fin geometry).")
print("  - Coolant tubes are rectangular ducts.")
print("  - Actual design requires CFD for fin spacing, tube layout.")