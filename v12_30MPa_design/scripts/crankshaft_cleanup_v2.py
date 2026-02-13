#!/usr/bin/env python3
"""
Clean up crankshaft CAD: union separate solids, export as single solid.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import cadquery as cq

input_step = "crankshaft_30MPa_final.step"
print(f"Loading {input_step}...")
crank = cq.importers.importStep(input_step)

solids = crank.solids()
print(f"Number of solids: {solids.size()}")

if solids.size() > 1:
    print("Unioning solids via workplane...")
    # Start with first solid
    wp = cq.Workplane().add(solids.vals()[0])
    # Union each subsequent solid
    for solid in solids.vals()[1:]:
        wp = wp.union(cq.Workplane().add(solid))
    crank_union = wp
else:
    crank_union = crank

# Export
output_step = "crankshaft_30MPa_unified.step"
cq.exporters.export(crank_union, output_step, "STEP")
print(f"Exported unified crankshaft to {output_step}")

# Also export STL
output_stl = "crankshaft_30MPa_unified.stl"
cq.exporters.export(crank_union, output_stl, "STL")
print(f"Exported STL to {output_stl}")

print("✅ Crankshaft cleanup completed.")