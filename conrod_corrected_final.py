#!/usr/bin/env python3
"""
Corrected conrod with proper coordinate system.
Big‑end center at X=0, small‑end center at X=L, beam connecting them.
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime

# ----------------------------------------------------------------------
# LOAD CORRECTED CONROD SPEC
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/final_corrected_conrod_20260213_150623/final_corrected_spec.json") as f:
    spec = json.load(f)
    geo = spec["corrected_dimensions"]

print("=" * 70)
print("CORRECTED CONROD (Fixed Coordinates)")
print("=" * 70)

h = geo["beam_height"]
b = geo["beam_width"]
tw = geo["web_thickness"]
tf = geo["flange_thickness"]
L = geo["center_length"]

# ----------------------------------------------------------------------
# CREATE BEAM (I‑beam from X=0 to X=L)
# ----------------------------------------------------------------------
# Web: vertical center, thickness tw, height h-2tf
web = (
    cq.Workplane("YZ")
    .rect(tw, h - 2*tf)
    .extrude(L)  # from X=0 to X=L
)

# Top flange
top = (
    cq.Workplane("YZ")
    .rect(b, tf)
    .extrude(L)
    .translate((0, 0, (h - tf)/2))
)

# Bottom flange
bottom = (
    cq.Workplane("YZ")
    .rect(b, tf)
    .extrude(L)
    .translate((0, 0, -(h - tf)/2))
)

beam = web.union(top).union(bottom)
print(f"Beam created: length {L:.1f} mm")

# ----------------------------------------------------------------------
# BIG END (centered at X=0)
# ----------------------------------------------------------------------
big_outer_radius = geo["big_end_diameter"]/2 + 12.0
big_outer = (
    cq.Workplane("YZ")
    .circle(big_outer_radius)
    .extrude(geo["big_end_width"])
    .translate((-geo["big_end_width"]/2, 0, 0))  # center at X=0
)

big_hole = (
    cq.Workplane("YZ")
    .circle(geo["big_end_diameter"]/2)
    .extrude(geo["big_end_width"] + 2)
    .translate((-geo["big_end_width"]/2 - 1, 0, 0))
)

big_end = big_outer.cut(big_hole)
print(f"Big‑end: Ø{geo['big_end_diameter']:.3f} × {geo['big_end_width']:.3f} mm")

# ----------------------------------------------------------------------
# SMALL END (centered at X=L)
# ----------------------------------------------------------------------
small_outer_radius = geo["small_end_diameter"]/2 + 10.0
small_outer = (
    cq.Workplane("YZ")
    .circle(small_outer_radius)
    .extrude(geo["small_end_width"])
    .translate((L - geo["small_end_width"]/2, 0, 0))
)

small_hole = (
    cq.Workplane("YZ")
    .circle(geo["small_end_diameter"]/2)
    .extrude(geo["small_end_width"] + 2)
    .translate((L - geo["small_end_width"]/2 - 1, 0, 0))
)

small_end = small_outer.cut(small_hole)
print(f"Small‑end: Ø{geo['small_end_diameter']:.3f} × {geo['small_end_width']:.3f} mm")

# ----------------------------------------------------------------------
# ASSEMBLE
# ----------------------------------------------------------------------
conrod = beam.union(big_end).union(small_end)

# ----------------------------------------------------------------------
# VALIDATE
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

try:
    vol = conrod.val().Volume()
    bbox = conrod.val().BoundingBox()
    print(f"Volume: {vol:.1f} mm³")
    print(f"Bounding box: X {bbox.xmax-bbox.xmin:.1f}, Y {bbox.ymax-bbox.ymin:.1f}, Z {bbox.zmax-bbox.zmin:.1f} mm")
    
    # Check beam–big‑end connection (should be at X=0)
    if bbox.xmin <= 0.1 and bbox.xmin >= -0.1:
        print("✅ Big‑end at X≈0")
    else:
        print(f"⚠️  Big‑end X min: {bbox.xmin:.2f}")
    
    # Check beam–small‑end connection (should be at X≈L)
    if abs(bbox.xmax - L) <= 0.1:
        print(f"✅ Small‑end at X≈{L:.1f}")
    else:
        print(f"⚠️  Small‑end X max: {bbox.xmax:.2f} (expected {L})")
        
except Exception as e:
    print(f"Validation error: {e}")

# ----------------------------------------------------------------------
# EXPORT
# ----------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"conrod_corrected_final_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

step_path = os.path.join(out_dir, "conrod_corrected_final.step")
cq.exporters.export(conrod, step_path, "STEP")
print(f"\n✅ CAD exported to {step_path}")

# Save spec
spec_out = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "coordinates": {
        "big_end_center_x": 0,
        "small_end_center_x": L,
        "beam_x_range": [0, L],
    }
}

json_path = os.path.join(out_dir, "conrod_corrected_final_spec.json")
with open(json_path, "w") as f:
    json.dump(spec_out, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n✅ Corrected conrod ready.")