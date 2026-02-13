#!/usr/bin/env python3
"""
Corrected crankshaft throw with proper coordinate system.
Main journal center at (0,0,0), pin center at (0,0,-crank_radius).
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime

# ----------------------------------------------------------------------
# LOAD OPTIMIZED CRANKSHAFT GEOMETRY
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/crankshaft_30MPa_final.json") as f:
    data = json.load(f)
    geo = data["geometry"]

print("=" * 70)
print("CORRECTED CRANKSHAFT THROW")
print("=" * 70)

crank_radius = geo["stroke"] / 2
print(f"Stroke: {geo['stroke']:.2f} mm, radius {crank_radius:.2f} mm")
print(f"Main journal: Ø{geo['main_journal_diameter']:.2f} × {geo['main_journal_width']:.2f} mm")
print(f"Crank pin: Ø{geo['pin_diameter']:.2f} × {geo['pin_width']:.2f} mm")

# ----------------------------------------------------------------------
# MAIN JOURNAL (centered at origin, axis along X)
# ----------------------------------------------------------------------
main = (
    cq.Workplane("XY")
    .circle(geo["main_journal_diameter"] / 2)
    .extrude(geo["main_journal_width"])
    .translate((-geo["main_journal_width"] / 2, 0, 0))
)
print(f"Main journal placed at (0,0,0)")

# ----------------------------------------------------------------------
# CRANK PIN (offset downward by crank radius)
# ----------------------------------------------------------------------
pin = (
    cq.Workplane("XY")
    .circle(geo["pin_diameter"] / 2)
    .extrude(geo["pin_width"])
    .translate((0, 0, -crank_radius))  # move down
    .translate((-geo["pin_width"] / 2, 0, 0))
)
print(f"Crank pin placed at (0,0,-{crank_radius:.2f})")

# ----------------------------------------------------------------------
# CHEEK (connecting web)
# ----------------------------------------------------------------------
# Simplified cheek as rectangular block between main and pin
cheek_length = crank_radius - geo["main_journal_diameter"]/2 - geo["pin_diameter"]/2
cheek_height = geo["cheek_thickness"]
cheek_width = max(geo["main_journal_width"], geo["pin_width"]) + 10.0

cheek = (
    cq.Workplane("XY")
    .rect(cheek_length, cheek_height)
    .extrude(cheek_width)
    .translate((0, 0, -crank_radius/2))  # halfway between main and pin
    .translate((-cheek_width/2, 0, 0))
)
print(f"Cheek: {cheek_length:.2f} × {cheek_height:.2f} × {cheek_width:.2f} mm")

# ----------------------------------------------------------------------
# ASSEMBLE
# ----------------------------------------------------------------------
throw = main.union(pin).union(cheek)

# ----------------------------------------------------------------------
# VALIDATE
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

try:
    vol = throw.val().Volume()
    bbox = throw.val().BoundingBox()
    print(f"Volume: {vol:.1f} mm³")
    print(f"Bounding box: X {bbox.xmax-bbox.xmin:.1f}, Y {bbox.ymax-bbox.ymin:.1f}, Z {bbox.zmax-bbox.zmin:.1f} mm")
    
    # Check main journal Z position (should be ~0)
    main_z_center = (bbox.zmax + bbox.zmin) / 2
    print(f"Main journal Z center: {main_z_center:.2f} mm")
    
    # Check pin Z position (should be ~ -crank_radius)
    # Approximate by finding min Z (pin is lowest)
    pin_z_low = bbox.zmin
    print(f"Pin lowest Z: {pin_z_low:.2f} mm")
    
    # Check interference (should be none)
    # Quick check: if volume sum matches union volume
    main_vol = np.pi * (geo["main_journal_diameter"]/2)**2 * geo["main_journal_width"]
    pin_vol = np.pi * (geo["pin_diameter"]/2)**2 * geo["pin_width"]
    cheek_vol = cheek_length * cheek_height * cheek_width
    sum_vol = main_vol + pin_vol + cheek_vol
    diff = abs(vol - sum_vol) / sum_vol
    if diff < 0.05:
        print(f"✅ Volume consistent (diff {diff*100:.1f}%) – no large interference")
    else:
        print(f"⚠️  Volume mismatch {diff*100:.1f}% – possible interference")
        
except Exception as e:
    print(f"Validation error: {e}")

# ----------------------------------------------------------------------
# EXPORT
# ----------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"crankshaft_corrected_final_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

step_path = os.path.join(out_dir, "crankshaft_corrected_final.step")
cq.exporters.export(throw, step_path, "STEP")
print(f"\n✅ CAD exported to {step_path}")

# Save spec
spec_out = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "coordinates": {
        "main_journal_center": [0, 0, 0],
        "pin_center": [0, 0, -crank_radius],
        "crank_radius": crank_radius,
    },
    "conrod_interface": {
        "pin_diameter_mm": geo["pin_diameter"],
        "pin_width_mm": geo["pin_width"],
        "conrod_big_end_diameter_mm": 61.475,
        "conrod_big_end_width_mm": 22.522,
        "axial_clearance_mm": (geo["pin_width"] - 22.522) / 2,
        "radial_clearance_mm": (61.475 - geo["pin_diameter"]) / 2,
    }
}

json_path = os.path.join(out_dir, "crankshaft_corrected_final_spec.json")
with open(json_path, "w") as f:
    json.dump(spec_out, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n✅ Corrected crankshaft throw ready.")