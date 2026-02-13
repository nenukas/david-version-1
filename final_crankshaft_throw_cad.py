#!/usr/bin/env python3
"""
Generate crankshaft single‑throw CAD from optimized geometry.
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

print("Loaded optimized crankshaft geometry:")
for k, v in geo.items():
    print(f"  {k}: {v:.3f}")

stroke = geo["stroke"]  # 47.5 mm
crank_radius = stroke / 2

print("\n" + "=" * 70)
print("CRANKSHAFT THROW PARAMETERS")
print("=" * 70)
print(f"Stroke: {stroke:.2f} mm (radius {crank_radius:.2f} mm)")
print(f"Main journal: Ø{geo['main_journal_diameter']:.2f} × {geo['main_journal_width']:.2f} mm")
print(f"Crank pin: Ø{geo['pin_diameter']:.2f} × {geo['pin_width']:.2f} mm")
print(f"Cheek thickness: {geo['cheek_thickness']:.2f} mm")
print(f"Cheek radius: {geo['cheek_radius']:.2f} mm")
print(f"Cheek hole radius: {geo['cheek_hole_radius']:.2f} mm")

# ----------------------------------------------------------------------
# GENERATE CAD (single throw)
# ----------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"final_crankshaft_throw_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Main journal (cylinder at origin)
main = (
    cq.Workplane("XY")
    .circle(geo["main_journal_diameter"] / 2)
    .extrude(geo["main_journal_width"])
    .translate((-geo["main_journal_width"] / 2, 0, 0))
)
print("Main journal created")

# Crank pin (offset cylinder)
pin = (
    cq.Workplane("XY")
    .circle(geo["pin_diameter"] / 2)
    .extrude(geo["pin_width"])
    .translate((crank_radius, 0, 0))
    .translate((-geo["pin_width"] / 2, 0, 0))
)
print("Crank pin created")

# Cheek (disc with hole) – simplified as rectangular block for now
# Actually, create a cheek as a block connecting main journal to pin
cheek_length = crank_radius - geo["main_journal_diameter"]/2 - geo["pin_diameter"]/2
cheek_height = geo["cheek_thickness"]
cheek_width = max(geo["main_journal_width"], geo["pin_width"]) + 10.0

cheek = (
    cq.Workplane("XY")
    .rect(cheek_length, cheek_height)
    .extrude(cheek_width)
    .translate((crank_radius/2, 0, 0))
    .translate((-cheek_width/2, 0, 0))
)
print("Cheek created (simplified block)")

# Combine
throw = main.union(pin).union(cheek)
print("Throw assembled")

# Export STEP
step_path = f"{out_dir}/final_crankshaft_throw.step"
cq.exporters.export(throw, step_path, "STEP")
print(f"✅ CAD saved to {step_path}")

# ----------------------------------------------------------------------
# SAVE SPECIFICATION
# ----------------------------------------------------------------------
spec = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "derived": {
        "crank_radius_mm": crank_radius,
        "cheek_length_mm": cheek_length,
        "cheek_height_mm": cheek_height,
        "cheek_width_mm": cheek_width,
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

json_path = f"{out_dir}/final_crankshaft_throw_spec.json"
with open(json_path, "w") as f:
    json.dump(spec, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n" + "=" * 70)
print("CRANKSHAFT THROW CAD COMPLETE")
print("=" * 70)
print(f"Output directory: {out_dir}/")
print("\nInterface with conrod:")
print(f"  Crank‑pin width: {geo['pin_width']:.3f} mm")
print(f"  Conrod big‑end width: 22.522 mm")
print(f"  Axial clearance each side: {(geo['pin_width'] - 22.522)/2:.3f} mm")
print(f"  Radial clearance: {(61.475 - geo['pin_diameter'])/2:.3f} mm")
print("\nNext steps:")
print("1. Open final_crankshaft_throw.step in CAD viewer.")
print("2. Verify pin dimensions match conrod big‑end.")
print("3. Check cheek‑to‑conrod clearance (should be >0).")