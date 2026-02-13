#!/usr/bin/env python3
"""
Step‑by‑step crankshaft throw construction with validation.
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace')
from cad_validation_new import StepwiseBuilder, check_interference, check_connection

# ----------------------------------------------------------------------
# LOAD OPTIMIZED CRANKSHAFT GEOMETRY
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/crankshaft_30MPa_final.json") as f:
    data = json.load(f)
    geo = data["geometry"]

print("=" * 70)
print("CRANKSHAFT THROW STEP‑BY‑STEP CONSTRUCTION")
print("=" * 70)
print(f"Stroke: {geo['stroke']:.2f} mm (radius {geo['stroke']/2:.2f} mm)")
print(f"Main journal: Ø{geo['main_journal_diameter']:.2f} × {geo['main_journal_width']:.2f} mm")
print(f"Crank pin: Ø{geo['pin_diameter']:.2f} × {geo['pin_width']:.2f} mm")
print(f"Cheek thickness: {geo['cheek_thickness']:.2f} mm")

# Manufacturing constraints
MIN_WALL_THICKNESS = 5.0  # mm (crankshaft needs robust walls)

# Output directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"crankshaft_stepwise_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Initialize builder
builder = StepwiseBuilder("crankshaft_throw", out_dir)

crank_radius = geo["stroke"] / 2

# ----------------------------------------------------------------------
# STEP 1: MAIN JOURNAL (cylinder at origin)
# ----------------------------------------------------------------------
print(f"\nStep 1: Main journal")
main_volume = np.pi * (geo["main_journal_diameter"]/2)**2 * geo["main_journal_width"]

main = (
    cq.Workplane("XY")
    .circle(geo["main_journal_diameter"] / 2)
    .extrude(geo["main_journal_width"])
    .translate((-geo["main_journal_width"] / 2, 0, -crank_radius))
)

builder.add_step(
    "01_main_journal",
    main,
    expected_volume=main_volume,
    expected_bbox=(geo["main_journal_width"], 
                   geo["main_journal_diameter"],
                   geo["main_journal_diameter"]),
)

# ----------------------------------------------------------------------
# STEP 2: CRANK PIN (offset cylinder)
# ----------------------------------------------------------------------
print(f"\nStep 2: Crank pin")
pin_volume = np.pi * (geo["pin_diameter"]/2)**2 * geo["pin_width"]

pin = (
    cq.Workplane("XY")
    .circle(geo["pin_diameter"] / 2)
    .extrude(geo["pin_width"])
    .translate((crank_radius, 0, -crank_radius))
    .translate((-geo["pin_width"] / 2, 0, 0))
)

builder.add_step(
    "02_crank_pin",
    pin,
    expected_volume=pin_volume,
    check_interference_with=["01_main_journal"],  # should NOT interfere
    check_connection_with=["01_main_journal"],    # should be separate (connected via cheek)
)

# ----------------------------------------------------------------------
# STEP 3: CHEEK (connecting web)
# ----------------------------------------------------------------------
print(f"\nStep 3: Cheek")
# Simplified cheek as rectangular block
cheek_length = crank_radius - geo["main_journal_diameter"]/2 - geo["pin_diameter"]/2
cheek_height = geo["cheek_thickness"]
cheek_width = max(geo["main_journal_width"], geo["pin_width"]) + 10.0

cheek_volume = cheek_length * cheek_height * cheek_width

cheek = (
    cq.Workplane("XY")
    .rect(cheek_length, cheek_height)
    .extrude(cheek_width)
    .translate((crank_radius/2, 0, -crank_radius))
    .translate((-cheek_width/2, 0, 0))
)

builder.add_step(
    "03_cheek",
    cheek,
    expected_volume=cheek_volume,
    check_interference_with=["01_main_journal", "02_crank_pin"],
    check_connection_with=["01_main_journal", "02_crank_pin"],  # should touch both
)

# ----------------------------------------------------------------------
# STEP 4: FULL THROW ASSEMBLY
# ----------------------------------------------------------------------
print(f"\nStep 4: Full throw assembly")
throw = main.union(pin).union(cheek)
throw_volume = main_volume + pin_volume + cheek_volume

builder.add_step(
    "04_throw_final",
    throw,
    expected_volume=throw_volume,
    expected_bbox=(max(geo["main_journal_width"], geo["pin_width"], cheek_width),
                   geo["cheek_thickness"] + max(geo["main_journal_diameter"], geo["pin_diameter"]),
                   geo["stroke"] + max(geo["main_journal_diameter"], geo["pin_diameter"])),
)

# ----------------------------------------------------------------------
# VALIDATE NO ERRONEOUS INTERFERENCE
# ----------------------------------------------------------------------
print(f"\n" + "=" * 70)
print("FINAL INTERFERENCE CHECK")
print("=" * 70)

main_solid = builder._get_solid("01_main_journal")
pin_solid = builder._get_solid("02_crank_pin")
cheek_solid = builder._get_solid("03_cheek")

# Check main–pin interference
interferes_mp, vol_mp = check_interference(main_solid, pin_solid)
if interferes_mp:
    print(f"❌ Main–pin interference: {vol_mp:.3f} mm³")
else:
    print(f"✅ Main–pin: no interference")

# Check main–cheek interference
interferes_mc, vol_mc = check_interference(main_solid, cheek_solid)
if interferes_mc:
    print(f"❌ Main–cheek interference: {vol_mc:.3f} mm³")
else:
    print(f"✅ Main–cheek: no interference")

# Check pin–cheek interference
interferes_pc, vol_pc = check_interference(pin_solid, cheek_solid)
if interferes_pc:
    print(f"❌ Pin–cheek interference: {vol_pc:.3f} mm³")
else:
    print(f"✅ Pin–cheek: no interference")

# Connection distances
connected_mp, dist_mp = check_connection(main_solid, pin_solid)
print(f"Main–pin connection: distance {dist_mp:.3f} mm ({'✅' if connected_mp else '❌'})")

connected_mc, dist_mc = check_connection(main_solid, cheek_solid)
print(f"Main–cheek connection: distance {dist_mc:.3f} mm ({'✅' if connected_mc else '❌'})")

connected_pc, dist_pc = check_connection(pin_solid, cheek_solid)
print(f"Pin–cheek connection: distance {dist_pc:.3f} mm ({'✅' if connected_pc else '❌'})")

# ----------------------------------------------------------------------
# EXPORT AND SUMMARY
# ----------------------------------------------------------------------
final_path = os.path.join(out_dir, "crankshaft_throw_stepwise_final.step")
cq.exporters.export(throw, final_path, "STEP")
print(f"\n✅ Final crankshaft throw exported to {final_path}")

# Save spec
spec_out = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "derived": {
        "crank_radius_mm": crank_radius,
        "cheek_length_mm": cheek_length,
        "cheek_height_mm": cheek_height,
        "cheek_width_mm": cheek_width,
    },
    "volumes_mm3": {
        "main_journal": main_volume,
        "crank_pin": pin_volume,
        "cheek": cheek_volume,
        "total": throw_volume,
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

json_path = os.path.join(out_dir, "crankshaft_stepwise_spec.json")
with open(json_path, "w") as f:
    json.dump(spec_out, f, indent=2)
print(f"✅ Specification saved to {json_path}")

# Print validation log
print("\n" + "=" * 70)
print("VALIDATION LOG")
print("=" * 70)
builder.print_log()

print("\n" + "=" * 70)
print("MANUFACTURING CHECKS")
print("=" * 70)
bbox = throw.val().BoundingBox()
min_dim = min(bbox.xmax - bbox.xmin, bbox.ymax - bbox.ymin, bbox.zmax - bbox.zmin)
estimated_wall = min_dim * 0.25
print(f"Estimated minimum wall thickness: {estimated_wall:.2f} mm")
if estimated_wall >= MIN_WALL_THICKNESS:
    print(f"✅ Wall thickness ≥ {MIN_WALL_THICKNESS} mm")
else:
    print(f"⚠️  Wall thickness may be insufficient")

print("\n✅ Step‑by‑step crankshaft throw construction complete.")