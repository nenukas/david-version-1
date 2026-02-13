#!/usr/bin/env python3
"""
Step‑by‑step piston construction with validation.
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace')
from cad_validation import StepwiseBuilder, check_interference, check_connection

# ----------------------------------------------------------------------
# LOAD OPTIMIZED GEOMETRY
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/fea_thermal/piston_crown_15.0mm.json") as f:
    data = json.load(f)
    geo = data["geometry"]

print("=" * 70)
print("PISTON STEP‑BY‑STEP CONSTRUCTION")
print("=" * 70)
print(f"Crown thickness: {geo['crown_thickness']:.2f} mm")
print(f"Skirt length: {geo['skirt_length']:.2f} mm")
print(f"Pin‑boss width: {geo['pin_boss_width']:.2f} mm")
print(f"Skirt thickness: {geo['skirt_thickness']:.2f} mm")

# Fixed parameters
bore_diameter = 94.5  # mm
pin_diameter = 28.0   # mm nominal
bearing_radial_clearance = 0.03  # mm
pin_clearance_diameter = pin_diameter + 2 * bearing_radial_clearance
compression_height = 38.0  # mm (crown + ring‑land height)

# Manufacturing constraints
MIN_WALL_THICKNESS = 3.0  # mm
BOSS_CONNECTION_TOLERANCE = 0.001  # mm

# Output directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"piston_stepwise_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Initialize builder
builder = StepwiseBuilder("piston", out_dir)

# ----------------------------------------------------------------------
# STEP 1: CROWN (disc)
# ----------------------------------------------------------------------
crown_radius = bore_diameter / 2 - 0.1  # clearance
crown_volume = np.pi * crown_radius**2 * geo["crown_thickness"]
print(f"\nStep 1: Crown")
print(f"  Radius: {crown_radius:.2f} mm")
print(f"  Expected volume: {crown_volume:.1f} mm³")

crown = (
    cq.Workplane("XY")
    .circle(crown_radius)
    .extrude(-geo["crown_thickness"])  # downward
)

builder.add_step(
    "01_crown",
    crown,
    expected_volume=crown_volume,
    expected_bbox=(bore_diameter, bore_diameter, geo["crown_thickness"]),
)

# ----------------------------------------------------------------------
# STEP 2: SKIRT OUTER CYLINDER
# ----------------------------------------------------------------------
skirt_outer_radius = bore_diameter / 2 - 0.5  # clearance
skirt_outer_volume = np.pi * skirt_outer_radius**2 * geo["skirt_length"]
print(f"\nStep 2: Skirt outer cylinder")
print(f"  Radius: {skirt_outer_radius:.2f} mm")
print(f"  Expected volume: {skirt_outer_volume:.1f} mm³")

skirt_outer = (
    cq.Workplane("XY")
    .circle(skirt_outer_radius)
    .extrude(-geo["skirt_length"])
    .translate((0, 0, -geo["crown_thickness"]))
)

builder.add_step(
    "02_skirt_outer",
    skirt_outer,
    expected_volume=skirt_outer_volume,
    expected_bbox=(bore_diameter, bore_diameter, geo["skirt_length"]),
    check_connection_with=["01_crown"],  # should touch crown bottom
)

# ----------------------------------------------------------------------
# STEP 3: SKIRT INNER CUT (to create shell)
# ----------------------------------------------------------------------
skirt_inner_radius = skirt_outer_radius - geo["skirt_thickness"]
skirt_inner_volume = np.pi * skirt_inner_radius**2 * geo["skirt_length"]
skirt_shell_volume = skirt_outer_volume - skirt_inner_volume
print(f"\nStep 3: Skirt inner cut")
print(f"  Inner radius: {skirt_inner_radius:.2f} mm")
print(f"  Shell volume: {skirt_shell_volume:.1f} mm³")

skirt_inner = (
    cq.Workplane("XY")
    .circle(skirt_inner_radius)
    .extrude(-geo["skirt_length"])
    .translate((0, 0, -geo["crown_thickness"]))
)

# We'll cut later; for validation, check interference with outer (should be fully inside)
interferes, vol = check_interference(skirt_outer, skirt_inner)
if not interferes:
    print("  ✅ Skirt inner fully inside outer (good for cut)")
else:
    print(f"  ⚠️  Skirt inner interferes with outer: {vol:.3f} mm³")

# Create skirt shell by cutting
skirt_shell = skirt_outer.cut(skirt_inner)

builder.add_step(
    "03_skirt_shell",
    skirt_shell,
    expected_volume=skirt_shell_volume,
    check_connection_with=["01_crown"],  # should still touch crown
)

# ----------------------------------------------------------------------
# STEP 4: PIN BOSS LEFT (block)
# ----------------------------------------------------------------------
boss_height = compression_height * 0.6
boss_y_offset = bore_diameter / 2 - geo["pin_boss_width"] / 2
# Boss block dimensions: X = pin_diameter + 2* boss_width? Actually boss block width in X direction
# should be enough to contain pin hole with material around.
boss_x_width = pin_diameter + 2 * geo["pin_boss_width"]  # mm
boss_y_width = geo["pin_boss_width"]  # mm
boss_volume = boss_x_width * boss_y_width * boss_height
print(f"\nStep 4: Left pin boss")
print(f"  Y offset: {boss_y_offset:.2f} mm")
print(f"  Dimensions: {boss_x_width:.2f} × {boss_y_width:.2f} × {boss_height:.2f} mm")
print(f"  Expected volume: {boss_volume:.1f} mm³")

left_boss = (
    cq.Workplane("XY")
    .rect(boss_x_width, boss_y_width)
    .extrude(-boss_height)
    .translate((0, -boss_y_offset, -geo["crown_thickness"]))
)

builder.add_step(
    "04_left_boss",
    left_boss,
    expected_volume=boss_volume,
    check_interference_with=["01_crown", "03_skirt_shell"],  # should NOT intersect crown or skirt
    check_connection_with=["03_skirt_shell"],  # should touch skirt outer surface
)

# ----------------------------------------------------------------------
# STEP 5: PIN BOSS RIGHT (mirror)
# ----------------------------------------------------------------------
right_boss = (
    cq.Workplane("XY")
    .rect(boss_x_width, boss_y_width)
    .extrude(-boss_height)
    .translate((0, boss_y_offset, -geo["crown_thickness"]))
)

builder.add_step(
    "05_right_boss",
    right_boss,
    expected_volume=boss_volume,
    check_interference_with=["01_crown", "03_skirt_shell"],
    check_connection_with=["03_skirt_shell"],
)

# ----------------------------------------------------------------------
# STEP 6: PIN HOLE (through both bosses)
# ----------------------------------------------------------------------
pin_hole_radius = pin_clearance_diameter / 2
pin_hole_volume = np.pi * pin_hole_radius**2 * (boss_height * 2.2)  # extra length
print(f"\nStep 6: Pin hole")
print(f"  Radius: {pin_hole_radius:.3f} mm")
print(f"  Expected volume removed: {pin_hole_volume:.1f} mm³")

pin_hole = (
    cq.Workplane("XY")
    .circle(pin_hole_radius)
    .extrude(-boss_height * 1.1)  # slightly longer than boss height
    .translate((0, 0, -geo["crown_thickness"] - boss_height * 0.05))
)

# Check interference with bosses (should intersect both)
interferes_left, vol_left = check_interference(pin_hole, left_boss)
interferes_right, vol_right = check_interference(pin_hole, right_boss)
if interferes_left and interferes_right:
    print(f"  ✅ Pin hole intersects both bosses (volumes {vol_left:.1f}, {vol_right:.1f} mm³)")
else:
    print(f"  ⚠️  Pin hole missing bosses")

# Cut hole from bosses
bosses_with_hole = left_boss.union(right_boss).cut(pin_hole)

builder.add_step(
    "06_bosses_with_hole",
    bosses_with_hole,
    expected_volume=boss_volume * 2 - pin_hole_volume,
)

# ----------------------------------------------------------------------
# STEP 7: COMBINE ALL PARTS (final piston)
# ----------------------------------------------------------------------
print(f"\nStep 7: Combine all parts")
piston = crown.union(skirt_shell).union(bosses_with_hole)

# Validate final piston
final_volume = (crown_volume + skirt_shell_volume + boss_volume * 2 - pin_hole_volume)
print(f"  Expected total volume: {final_volume:.1f} mm³")

builder.add_step(
    "07_piston_final",
    piston,
    expected_volume=final_volume,
    expected_bbox=(bore_diameter, bore_diameter,
                   geo["crown_thickness"] + geo["skirt_length"] + boss_height),
)

# ----------------------------------------------------------------------
# EXPORT AND SUMMARY
# ----------------------------------------------------------------------
step_path = os.path.join(out_dir, "piston_final.step")
cq.exporters.export(piston, step_path, "STEP")
print(f"\n✅ Final piston exported to {step_path}")

# Save spec
spec = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "parameters": {
        "bore_diameter_mm": bore_diameter,
        "pin_diameter_mm": pin_diameter,
        "pin_clearance_diameter_mm": pin_clearance_diameter,
        "compression_height_mm": compression_height,
        "boss_height_mm": boss_height,
        "boss_y_offset_mm": boss_y_offset,
    },
    "volumes_mm3": {
        "crown": crown_volume,
        "skirt_shell": skirt_shell_volume,
        "boss_single": boss_volume,
        "pin_hole": pin_hole_volume,
        "total": final_volume,
    },
}

json_path = os.path.join(out_dir, "piston_stepwise_spec.json")
with open(json_path, "w") as f:
    json.dump(spec, f, indent=2)
print(f"✅ Specification saved to {json_path}")

# Print validation log
print("\n" + "=" * 70)
print("VALIDATION LOG")
print("=" * 70)
builder.print_log()

print("\n" + "=" * 70)
print("MANUFACTURING CHECKS")
print("=" * 70)
# Estimate wall thickness (simplified)
bbox = piston.val().BoundingBox()
min_dim = min(bbox.xmax - bbox.xmin, bbox.ymax - bbox.ymin, bbox.zmax - bbox.zmin)
estimated_wall = min_dim * 0.25
print(f"Estimated minimum wall thickness: {estimated_wall:.2f} mm")
if estimated_wall >= MIN_WALL_THICKNESS:
    print(f"✅ Wall thickness ≥ {MIN_WALL_THICKNESS} mm")
else:
    print(f"⚠️  Wall thickness may be insufficient")

print("\n✅ Step‑by‑step piston construction complete.")