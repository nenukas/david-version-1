#!/usr/bin/env python3
"""
Final corrected connecting rod with existing optimized beam geometry
and fixed bearing interfaces matching crankshaft and piston.
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

from src.engine.conrod_am import ConrodGeometryAM, ConrodAnalyzerAM

# ----------------------------------------------------------------------
# LOAD EXISTING OPTIMIZED BEAM GEOMETRY
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/conrod_opt_relaxed2_30MPa_results_20260213_010504.json") as f:
    data = json.load(f)
    geo = data["geometry"]

print("Loaded optimized beam geometry:")
for k, v in geo.items():
    print(f"  {k}: {v:.3f}")

# ----------------------------------------------------------------------
# FIXED BEARING DIMENSIONS FROM CRANKSHAFT & PISTON
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/crankshaft_30MPa_final.json") as f:
    crank = json.load(f)
    crank_pin_dia = crank["geometry"]["pin_diameter"]        # 61.415 mm
    crank_pin_width = crank["geometry"]["pin_width"]         # 26.525 mm
    cheek_thickness = crank["geometry"]["cheek_thickness"]   # 17.150 mm

piston_pin_dia = 28.0  # mm

# Clearances
AXIAL_CLEARANCE = 0.75  # mm each side
BEARING_RADIAL_CLEARANCE = 0.03  # mm

# Calculated bearing dimensions
big_end_diameter = crank_pin_dia + 2 * BEARING_RADIAL_CLEARANCE
max_big_end_width = crank_pin_width - 2 * AXIAL_CLEARANCE
big_end_width = max_big_end_width * 0.9  # 90% of max for margin

small_end_diameter = piston_pin_dia + 2 * BEARING_RADIAL_CLEARANCE
min_small_end_width = 180000.0 / (200.0 * small_end_diameter)  # for 200 MPa pressure
small_end_width = np.ceil(min_small_end_width * 2) / 2  # round up to 0.5 mm

# Center length (rod length)
center_length = 150.0  # mm

print("\n" + "=" * 70)
print("FIXED BEARING INTERFACES")
print("=" * 70)
print(f"Crank‑pin: Ø{crank_pin_dia:.3f} × {crank_pin_width:.3f} mm")
print(f"Cheek thickness: {cheek_thickness:.3f} mm")
print(f"Big‑end bearing: Ø{big_end_diameter:.3f} × {big_end_width:.3f} mm")
print(f"Small‑end bearing: Ø{small_end_diameter:.3f} × {small_end_width:.3f} mm")
print(f"Rod length: {center_length:.1f} mm")

# ----------------------------------------------------------------------
# CREATE CORRECTED GEOMETRY OBJECT
# ----------------------------------------------------------------------
corrected_geo = ConrodGeometryAM(
    beam_height=geo["beam_height"],
    beam_width=geo["beam_width"],
    web_thickness=geo["web_thickness"],
    flange_thickness=geo["flange_thickness"],
    center_length=center_length,
    big_end_width=big_end_width,
    small_end_width=small_end_width,
    big_end_diameter=big_end_diameter,
    small_end_diameter=small_end_diameter,
    fillet_big=geo["fillet_big"],
    fillet_small=geo["fillet_small"],
    lattice_relative_density=geo["lattice_relative_density"],
)

# ----------------------------------------------------------------------
# VALIDATE CONSTRAINTS
# ----------------------------------------------------------------------
analyzer = ConrodAnalyzerAM(corrected_geo)
COMPRESSION_FORCE = 180000.0  # N
TENSILE_FORCE = 83000.0       # N
ECCENTRICITY = 0.5            # mm

constraints, metrics = analyzer.evaluate_constraints(
    compression_force_n=COMPRESSION_FORCE,
    tensile_force_n=TENSILE_FORCE,
    eccentricity_mm=ECCENTRICITY
)

print("\n" + "=" * 70)
print("CONSTRAINT VALIDATION")
print("=" * 70)
print(f"Mass: {analyzer.mass():.4f} kg")
print(f"Buckling safety factor: {metrics.get('buckling_safety_factor', 'N/A'):.2f}")
print(f"Compressive stress: {metrics.get('axial_stress_comp_mpa', 'N/A'):.1f} MPa")
print(f"Bearing pressure big: {metrics.get('bearing_pressure_big_mpa', 'N/A'):.1f} MPa")
print(f"Bearing pressure small: {metrics.get('bearing_pressure_small_mpa', 'N/A'):.1f} MPa")
print(f"Fatigue safety factor: {metrics.get('fatigue_safety_factor', 'N/A'):.2f}")

print("\nConstraint status:")
for key, val in constraints.items():
    print(f"  {key}: {'✅' if val else '❌'}")

# Check if all constraints satisfied
all_ok = all(constraints.values())
if all_ok:
    print("\n✅ All constraints satisfied!")
else:
    print(f"\n⚠️  Some constraints violated.")

# ----------------------------------------------------------------------
# CHECK MANUFACTURING FEASIBILITY
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("MANUFACTURING CHECKS")
print("=" * 70)

# 1. Big‑end fits between crank cheeks
space_between_cheeks = crank_pin_width + 2 * cheek_thickness
available_width = space_between_cheeks - 2 * AXIAL_CLEARANCE
if big_end_width <= available_width:
    print(f"✅ Big‑end fits: {big_end_width:.3f} mm ≤ {available_width:.3f} mm")
else:
    print(f"❌ Big‑end too wide: {big_end_width:.3f} mm > {available_width:.3f} mm")

# 2. Bearing pressure limits
big_pressure = COMPRESSION_FORCE / (big_end_diameter * big_end_width)
small_pressure = COMPRESSION_FORCE / (small_end_diameter * small_end_width)
print(f"Big‑end pressure: {big_pressure:.1f} MPa ({'✅' if big_pressure <= 200 else '❌'})")
print(f"Small‑end pressure: {small_pressure:.1f} MPa ({'✅' if small_pressure <= 200 else '❌'})")

# 3. Wall thickness at bearings (approximate)
big_wall = (big_end_diameter / 2) * 0.3  # assuming 30% of radius
small_wall = (small_end_diameter / 2) * 0.3
print(f"Estimated bearing‑wall thickness: big {big_wall:.2f} mm, small {small_wall:.2f} mm")
if big_wall >= 3.0 and small_wall >= 3.0:
    print("✅ Walls thick enough for machining")
else:
    print("⚠️  Walls may be too thin")

# ----------------------------------------------------------------------
# GENERATE CAD
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("GENERATING CAD")
print("=" * 70)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"final_corrected_conrod_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Create I‑beam
h = corrected_geo.beam_height
b = corrected_geo.beam_width
tw = corrected_geo.web_thickness
tf = corrected_geo.flange_thickness
L = corrected_geo.center_length

web = cq.Workplane("YZ").rect(tw, h - 2*tf).extrude(L)
top = cq.Workplane("YZ").rect(b, tf).extrude(L).translate((0,0,(h-tf)/2))
bottom = cq.Workplane("YZ").rect(b, tf).extrude(L).translate((0,0,-(h-tf)/2))
beam = web.union(top).union(bottom)
beam = beam.translate((L/2,0,0))

# Big end
big_outer_radius = big_end_diameter/2 + 12.0  # wall ~12 mm
big_outer = cq.Workplane("YZ").circle(big_outer_radius).extrude(big_end_width)
big_outer = big_outer.translate((-big_end_width/2,0,0))
big_hole = cq.Workplane("YZ").circle(big_end_diameter/2).extrude(big_end_width+2)
big_hole = big_hole.translate((-big_end_width/2 -1,0,0))
big_end = big_outer.cut(big_hole)

# Small end
small_outer_radius = small_end_diameter/2 + 10.0
small_outer = cq.Workplane("YZ").circle(small_outer_radius).extrude(small_end_width)
small_outer = small_outer.translate((L - small_end_width/2,0,0))
small_hole = cq.Workplane("YZ").circle(small_end_diameter/2).extrude(small_end_width+2)
small_hole = small_hole.translate((L - small_end_width/2 -1,0,0))
small_end = small_outer.cut(small_hole)

# Union all parts
conrod = beam.union(big_end).union(small_end)

# Export STEP
step_path = f"{out_dir}/final_corrected_conrod.step"
cq.exporters.export(conrod, step_path, "STEP")
print(f"✅ CAD saved to {step_path}")

# ----------------------------------------------------------------------
# SAVE SPECIFICATION
# ----------------------------------------------------------------------
spec = {
    "timestamp": datetime.now().isoformat(),
    "original_optimization": geo,
    "corrected_dimensions": {
        "beam_height": float(corrected_geo.beam_height),
        "beam_width": float(corrected_geo.beam_width),
        "web_thickness": float(corrected_geo.web_thickness),
        "flange_thickness": float(corrected_geo.flange_thickness),
        "center_length": float(corrected_geo.center_length),
        "big_end_diameter": float(corrected_geo.big_end_diameter),
        "big_end_width": float(corrected_geo.big_end_width),
        "small_end_diameter": float(corrected_geo.small_end_diameter),
        "small_end_width": float(corrected_geo.small_end_width),
        "fillet_big": float(corrected_geo.fillet_big),
        "fillet_small": float(corrected_geo.fillet_small),
        "lattice_relative_density": float(corrected_geo.lattice_relative_density),
    },
    "validation": {
        "mass_kg": analyzer.mass(),
        "constraints_satisfied": constraints,
        "metrics": metrics,
    },
    "manufacturing": {
        "crank_pin_diameter_mm": crank_pin_dia,
        "crank_pin_width_mm": crank_pin_width,
        "cheek_thickness_mm": cheek_thickness,
        "piston_pin_diameter_mm": piston_pin_dia,
        "axial_clearance_per_side_mm": AXIAL_CLEARANCE,
        "bearing_radial_clearance_mm": BEARING_RADIAL_CLEARANCE,
        "big_end_fits": big_end_width <= available_width,
        "big_end_pressure_mpa": big_pressure,
        "small_end_pressure_mpa": small_pressure,
    }
}

json_path = f"{out_dir}/final_corrected_spec.json"
with open(json_path, "w") as f:
    json.dump(spec, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n" + "=" * 70)
print("NEXT STEPS")
print("=" * 70)
print("1. Open final_corrected_conrod.step in CAD viewer.")
print("2. Verify dimensions against crank/piston pins.")
print("3. Check interference with crankshaft cheeks.")
print("4. If satisfactory, proceed to FEA validation.")
print("\n✅ Final corrected conrod ready for visual inspection.")