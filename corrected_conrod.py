#!/usr/bin/env python3
"""
Generate corrected connecting‑rod CAD with manufacturing‑compatible dimensions.
Fixes:
- big_end_diameter = actual crank‑pin diameter (61.415 mm)
- big_end_width ≤ crank‑pin axial length (26.5 mm) minus clearance
- small_end_diameter = piston‑pin diameter (28.0 mm)
- small_end_width reasonable (≈30 mm)
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime

# ----------------------------------------------------------------------
# 1. LOAD EXISTING OPTIMIZED GEOMETRY (for beam dimensions)
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/conrod_opt_relaxed2_30MPa_results_20260213_010504.json") as f:
    data = json.load(f)

geo = data["geometry"]
print("Loaded optimized geometry:")
for k, v in geo.items():
    print(f"  {k}: {v:.3f}")

# ----------------------------------------------------------------------
# 2. CORRECTED DIMENSIONS FROM CRANKSHAFT & PISTON
# ----------------------------------------------------------------------
# Crankshaft pin dimensions (from crankshaft_30MPa_final.json)
with open("/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/crankshaft_30MPa_final.json") as f:
    crank = json.load(f)
    crank_pin_dia = crank["geometry"]["pin_diameter"]
    crank_pin_width = crank["geometry"]["pin_width"]
    cheek_thickness = crank["geometry"]["cheek_thickness"]

print(f"\nCrank‑pin diameter: {crank_pin_dia:.3f} mm")
print(f"Crank‑pin axial width: {crank_pin_width:.3f} mm")
print(f"Cheek thickness: {cheek_thickness:.3f} mm")

# Piston‑pin diameter (fixed from earlier spec)
piston_pin_dia = 28.0  # mm

# ----------------------------------------------------------------------
# 3. MANUFACTURING CLEARANCES
# ----------------------------------------------------------------------
# Axial clearance between conrod big‑end and crank cheeks
axial_clearance = 0.75  # mm each side (typical for performance engines)
# Radial clearance (bearing clearance) – already accounted in bearing design
bearing_radial_clearance = 0.03  # mm (typical for plain bearings)

# ----------------------------------------------------------------------
# 4. CORRECTED CONROD DIMENSIONS
# ----------------------------------------------------------------------
corrected = {
    # Beam dimensions (keep from optimization)
    "beam_height": geo["beam_height"],
    "beam_width": geo["beam_width"],
    "web_thickness": geo["web_thickness"],
    "flange_thickness": geo["flange_thickness"],
    "center_length": 150.0,  # fixed rod length
    # Big end
    "big_end_diameter": crank_pin_dia + 2 * bearing_radial_clearance,  # bearing ID
    "big_end_width": crank_pin_width - 2 * axial_clearance,  # axial length
    # Small end
    "small_end_diameter": piston_pin_dia + 2 * bearing_radial_clearance,
    "small_end_width": 30.0,  # reasonable (can be optimized later)
    # Fillet radii (keep)
    "fillet_big": geo["fillet_big"],
    "fillet_small": geo["fillet_small"],
    # Lattice density (keep)
    "lattice_relative_density": geo["lattice_relative_density"],
}

print("\nCorrected conrod dimensions:")
for k, v in corrected.items():
    print(f"  {k}: {v:.3f}")

# ----------------------------------------------------------------------
# 5. VALIDATE AGAINST MANUFACTURING CONSTRAINTS
# ----------------------------------------------------------------------
print("\n" + "=" * 60)
print("MANUFACTURING VALIDATION")
print("=" * 60)

# 5.1. Big‑end fits between crank cheeks
space_between_cheeks = crank_pin_width + 2 * cheek_thickness
available_width = space_between_cheeks - 2 * axial_clearance
if corrected["big_end_width"] > available_width:
    print(f"❌ Big‑end width {corrected['big_end_width']:.3f} mm > available {available_width:.3f} mm")
else:
    print(f"✅ Big‑end fits: {corrected['big_end_width']:.3f} mm ≤ {available_width:.3f} mm")

# 5.2. Bearing pressure (approximate peak force 180 kN)
force = 180000.0  # N
big_end_area = corrected["big_end_diameter"] * corrected["big_end_width"]
big_end_pressure = force / big_end_area
print(f"Big‑end bearing pressure: {big_end_pressure:.1f} MPa")
if big_end_pressure < 200:
    print(f"✅ Acceptable (<200 MPa)")
else:
    print(f"❌ Too high")

small_end_area = corrected["small_end_diameter"] * corrected["small_end_width"]
small_end_pressure = force / small_end_area
print(f"Small‑end bearing pressure: {small_end_pressure:.1f} MPa")
if small_end_pressure < 200:
    print(f"✅ Acceptable (<200 MPa)")
else:
    print(f"❌ Too high")

# 5.3. Wall thickness at bearings
big_end_wall = (corrected["big_end_diameter"] / 2) * 0.3  # rough estimate
small_end_wall = (corrected["small_end_diameter"] / 2) * 0.3
print(f"Estimated bearing‑wall thickness: big {big_end_wall:.2f} mm, small {small_end_wall:.2f} mm")
if big_end_wall > 3.0 and small_end_wall > 3.0:
    print("✅ Walls thick enough for machining")
else:
    print("⚠️  Walls may be too thin")

# ----------------------------------------------------------------------
# 6. GENERATE CAD (simplified – just outer envelope for visualization)
# ----------------------------------------------------------------------
print("\n" + "=" * 60)
print("GENERATING CAD")
print("=" * 60)

# Create output directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"corrected_conrod_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Simplified I‑beam (as before)
h = corrected["beam_height"]
b = corrected["beam_width"]
tw = corrected["web_thickness"]
tf = corrected["flange_thickness"]
L = corrected["center_length"]

web = cq.Workplane("YZ").rect(tw, h - 2*tf).extrude(L)
top = cq.Workplane("YZ").rect(b, tf).extrude(L).translate((0,0,(h-tf)/2))
bottom = cq.Workplane("YZ").rect(b, tf).extrude(L).translate((0,0,-(h-tf)/2))
beam = web.union(top).union(bottom)
beam = beam.translate((L/2,0,0))

# Big end (cylinder with hole)
big_outer_radius = corrected["big_end_diameter"]/2 + 12.0  # wall ~12 mm
big_outer = cq.Workplane("YZ").circle(big_outer_radius).extrude(corrected["big_end_width"])
big_outer = big_outer.translate((-corrected["big_end_width"]/2,0,0))
big_hole = cq.Workplane("YZ").circle(corrected["big_end_diameter"]/2).extrude(corrected["big_end_width"]+2)
big_hole = big_hole.translate((-corrected["big_end_width"]/2 -1,0,0))
big_end = big_outer.cut(big_hole)

# Small end
small_outer_radius = corrected["small_end_diameter"]/2 + 10.0
small_outer = cq.Workplane("YZ").circle(small_outer_radius).extrude(corrected["small_end_width"])
small_outer = small_outer.translate((L - corrected["small_end_width"]/2,0,0))
small_hole = cq.Workplane("YZ").circle(corrected["small_end_diameter"]/2).extrude(corrected["small_end_width"]+2)
small_hole = small_hole.translate((L - corrected["small_end_width"]/2 -1,0,0))
small_end = small_outer.cut(small_hole)

# Union all parts
conrod = beam.union(big_end).union(small_end)

# Export
step_path = f"{out_dir}/corrected_conrod.step"
cq.exporters.export(conrod, step_path, "STEP")
print(f"✅ CAD saved to {step_path}")

# ----------------------------------------------------------------------
# 7. SAVE CORRECTED SPECIFICATION
# ----------------------------------------------------------------------
spec = {
    "timestamp": datetime.now().isoformat(),
    "original_optimization": data["geometry"],
    "corrected_dimensions": corrected,
    "validation": {
        "big_end_fits": corrected["big_end_width"] <= available_width,
        "big_end_pressure_mpa": big_end_pressure,
        "small_end_pressure_mpa": small_end_pressure,
        "wall_thickness_big_mm": big_end_wall,
        "wall_thickness_small_mm": small_end_wall,
    },
    "manufacturing_notes": {
        "crank_pin_diameter_mm": crank_pin_dia,
        "crank_pin_width_mm": crank_pin_width,
        "piston_pin_diameter_mm": piston_pin_dia,
        "axial_clearance_per_side_mm": axial_clearance,
        "bearing_radial_clearance_mm": bearing_radial_clearance,
    }
}

json_path = f"{out_dir}/corrected_spec.json"
with open(json_path, "w") as f:
    json.dump(spec, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n" + "=" * 60)
print("NEXT STEPS")
print("=" * 60)
print("1. Open corrected_conrod.step in CAD viewer.")
print("2. Verify dimensions against crank/piston pins.")
print("3. Run interference detection with crankshaft.")
print("4. Re‑run optimization with fixed diameters and width constraints.")
print("\n✅ Correction complete.")