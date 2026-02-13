#!/usr/bin/env python3
"""
Generate piston CAD from optimized geometry (crown thickness 15 mm).
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime

# ----------------------------------------------------------------------
# LOAD OPTIMIZED PISTON GEOMETRY
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/fea_thermal/piston_crown_15.0mm.json") as f:
    data = json.load(f)
    geo = data["geometry"]

print("Loaded optimized piston geometry:")
for k, v in geo.items():
    print(f"  {k}: {v:.3f}")

# Fixed parameters
bore_diameter = 94.5  # mm
pin_diameter = 28.0   # mm (nominal)
bearing_radial_clearance = 0.03  # mm
pin_clearance_diameter = pin_diameter + 2 * bearing_radial_clearance  # 28.06 mm

# Compression height (crown thickness + ring‑land height)
# Approximate: crown + 3 ring grooves + lands ≈ 38 mm total
compression_height = 38.0  # mm (from earlier spec)

print("\n" + "=" * 70)
print("PISTON PARAMETERS")
print("=" * 70)
print(f"Bore: Ø{bore_diameter:.2f} mm")
print(f"Pin nominal diameter: Ø{pin_diameter:.2f} mm")
print(f"Pin clearance diameter: Ø{pin_clearance_diameter:.2f} mm")
print(f"Crown thickness: {geo['crown_thickness']:.2f} mm")
print(f"Skirt length: {geo['skirt_length']:.2f} mm")
print(f"Pin‑boss width: {geo['pin_boss_width']:.2f} mm")
print(f"Skirt thickness: {geo['skirt_thickness']:.2f} mm")
print(f"Compression height: {compression_height:.2f} mm")

# ----------------------------------------------------------------------
# GENERATE CAD
# ----------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"final_piston_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# ---- 1. Crown (disc) ----
crown = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.1)  # clearance
    .extrude(-geo["crown_thickness"])  # downward
)
print("Crown created")

# ---- 2. Ring‑land region (simplified cylinder) ----
ring_land = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.2)
    .extrude(-compression_height)
    .translate((0, 0, -geo["crown_thickness"]))
)
print("Ring‑land region created")

# ---- 3. Skirt (cylindrical shell) ----
skirt_outer = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.5)  # clearance
    .extrude(-geo["skirt_length"])
    .translate((0, 0, -geo["crown_thickness"] - compression_height))
)
skirt_inner = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.5 - geo["skirt_thickness"])
    .extrude(-geo["skirt_length"])
    .translate((0, 0, -geo["crown_thickness"] - compression_height))
)
skirt = skirt_outer.cut(skirt_inner)
print("Skirt created")

# ---- 4. Pin bosses (two blocks with hole) ----
boss_height = compression_height * 0.6
boss_y_offset = bore_diameter / 2 - geo["pin_boss_width"] / 2
# Left boss
left_boss = (
    cq.Workplane("XY")
    .rect(pin_diameter + 2 * geo["pin_boss_width"], geo["pin_boss_width"])
    .extrude(-boss_height)
    .translate((0, -boss_y_offset, -geo["crown_thickness"]))
)
# Right boss
right_boss = (
    cq.Workplane("XY")
    .rect(pin_diameter + 2 * geo["pin_boss_width"], geo["pin_boss_width"])
    .extrude(-boss_height)
    .translate((0, boss_y_offset, -geo["crown_thickness"]))
)
# Pin hole through both bosses
pin_hole = (
    cq.Workplane("XY")
    .circle(pin_clearance_diameter / 2)
    .extrude(-boss_height * 1.1)  # slightly longer
    .translate((0, 0, -geo["crown_thickness"] - boss_height * 0.05))
)
bosses = left_boss.union(right_boss).cut(pin_hole)
print("Pin bosses created")

# ---- 5. Combine all parts ----
piston = crown.union(ring_land).union(skirt).union(bosses)
print("Parts combined")

# Export STEP
step_path = f"{out_dir}/final_piston.step"
cq.exporters.export(piston, step_path, "STEP")
print(f"✅ CAD saved to {step_path}")

# ----------------------------------------------------------------------
# SAVE SPECIFICATION
# ----------------------------------------------------------------------
spec = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "fixed_parameters": {
        "bore_diameter_mm": bore_diameter,
        "pin_nominal_diameter_mm": pin_diameter,
        "pin_clearance_diameter_mm": pin_clearance_diameter,
        "compression_height_mm": compression_height,
        "bearing_radial_clearance_mm": bearing_radial_clearance,
    },
    "validation_notes": {
        "crown_thickness_ok": geo["crown_thickness"] >= 15.0,
        "skirt_length_ok": geo["skirt_length"] > 30.0,
        "pin_boss_width_vs_conrod": f"Piston boss width {geo['pin_boss_width']:.2f} mm, conrod small‑end width 32.50 mm",
        "clearance_fit": f"Pin clearance {bearing_radial_clearance} mm radial",
    }
}

json_path = f"{out_dir}/final_piston_spec.json"
with open(json_path, "w") as f:
    json.dump(spec, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n" + "=" * 70)
print("PISTON CAD COMPLETE")
print("=" * 70)
print(f"Output directory: {out_dir}/")
print("\nNext steps:")
print("1. Open final_piston.step in CAD viewer.")
print("2. Verify pin‑boss alignment with conrod small‑end.")
print("3. Check skirt clearance in cylinder bore.")
print("4. Confirm crown thickness matches thermal analysis.")