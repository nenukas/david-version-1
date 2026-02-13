#!/usr/bin/env python3
"""
Analyze the piston CAD error: interference between cylinder (crown) and cuboid (boss).
"""
import json
import cadquery as cq
import numpy as np
from cad_validation import check_interference, check_connection

print("=" * 70)
print("PISTON ERROR ANALYSIS")
print("=" * 70)

# Load geometry
with open("/home/nenuka/.openclaw/workspace/fea_thermal/piston_crown_15.0mm.json") as f:
    data = json.load(f)
    geo = data["geometry"]

bore_diameter = 94.5
pin_diameter = 28.0
bearing_radial_clearance = 0.03
pin_clearance_diameter = pin_diameter + 2 * bearing_radial_clearance
compression_height = 38.0

# Recreate the erroneous piston (based on final_piston_cad.py)
crown = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.1)
    .extrude(-geo["crown_thickness"])
)

ring_land = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.2)
    .extrude(-compression_height)
    .translate((0, 0, -geo["crown_thickness"]))
)

skirt_outer = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.5)
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

boss_height = compression_height * 0.6
boss_y_offset = bore_diameter / 2 - geo["pin_boss_width"] / 2
# Left boss (as in original script)
left_boss = (
    cq.Workplane("XY")
    .rect(pin_diameter + 2 * geo["pin_boss_width"], geo["pin_boss_width"])
    .extrude(-boss_height)
    .translate((0, -boss_y_offset, -geo["crown_thickness"]))
)
right_boss = (
    cq.Workplane("XY")
    .rect(pin_diameter + 2 * geo["pin_boss_width"], geo["pin_boss_width"])
    .extrude(-boss_height)
    .translate((0, boss_y_offset, -geo["crown_thickness"]))
)
pin_hole = (
    cq.Workplane("XY")
    .circle(pin_clearance_diameter / 2)
    .extrude(-boss_height * 1.1)
    .translate((0, 0, -geo["crown_thickness"] - boss_height * 0.05))
)
bosses = left_boss.union(right_boss).cut(pin_hole)

# Combine
piston = crown.union(ring_land).union(skirt).union(bosses)

# Check interference between crown and left_boss (original, before hole)
interferes_crown_left, vol_cl = check_interference(crown, left_boss)
interferes_crown_right, vol_cr = check_interference(crown, right_boss)
print(f"Crown–boss interference: left {vol_cl:.3f} mm³, right {vol_cr:.3f} mm³")
if vol_cl > 0.001 or vol_cr > 0.001:
    print("❌ Crown and boss intersect – this is the error.")
else:
    print("✅ Crown and boss do not intersect.")

# Check interference between ring_land and boss
interferes_ring_left, vol_rl = check_interference(ring_land, left_boss)
interferes_ring_right, vol_rr = check_interference(ring_land, right_boss)
print(f"Ring‑land–boss interference: left {vol_rl:.3f} mm³, right {vol_rr:.3f} mm³")

# Check interference between skirt and boss
skirt_solid = skirt_outer.cut(skirt_inner)
interferes_skirt_left, vol_sl = check_interference(skirt_solid, left_boss)
interferes_skirt_right, vol_sr = check_interference(skirt_solid, right_boss)
print(f"Skirt–boss interference: left {vol_sl:.3f} mm³, right {vol_sr:.3f} mm³")

# Check connection distances
connected_cl, dist_cl = check_connection(crown, left_boss)
connected_cr, dist_cr = check_connection(crown, right_boss)
print(f"Crown–boss connection: left {dist_cl:.3f} mm, right {dist_cr:.3f} mm")

# Visualize positions
print("\n" + "=" * 70)
print("GEOMETRY DETAILS")
print("=" * 70)
print(f"Crown: Z = 0 to {-geo['crown_thickness']:.2f} mm")
print(f"Boss top Z = {-geo['crown_thickness']:.2f} mm")
print(f"Boss height = {boss_height:.2f} mm")
print(f"Boss Y center = ±{boss_y_offset:.2f} mm")
print(f"Boss Y width = {geo['pin_boss_width']:.2f} mm")
print(f"Boss X width = {pin_diameter + 2*geo['pin_boss_width']:.2f} mm")
print(f"Skirt outer radius = {bore_diameter/2 - 0.5:.2f} mm")
print(f"Boss outer Y edge = {boss_y_offset + geo['pin_boss_width']/2:.2f} mm")

# Determine if boss is inside skirt
skirt_outer_radius = bore_diameter/2 - 0.5
boss_outer_y = boss_y_offset + geo["pin_boss_width"]/2
boss_inner_y = boss_y_offset - geo["pin_boss_width"]/2
print(f"\nSkirt outer radius: {skirt_outer_radius:.2f} mm")
print(f"Boss Y range: [{boss_inner_y:.2f}, {boss_outer_y:.2f}] mm")
if boss_outer_y > skirt_outer_radius:
    print("Boss extends beyond skirt outer surface (maybe okay).")
else:
    print("Boss inside skirt outer surface.")

# Export problematic solids for visual inspection
import os
os.makedirs("error_analysis", exist_ok=True)
cq.exporters.export(crown, "error_analysis/crown.step", "STEP")
cq.exporters.export(left_boss, "error_analysis/left_boss.step", "STEP")
cq.exporters.export(skirt_solid, "error_analysis/skirt.step", "STEP")
print("\n✅ Exported crown, boss, skirt to error_analysis/")

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
if vol_cl > 0:
    print("1. Adjust boss Z position to avoid crown intersection.")
if vol_sl > 0:
    print("2. Boss intersects skirt – ensure they merge smoothly.")
print("3. Re‑design boss dimensions: X width likely too large.")
print("4. Use step‑wise construction with interference checks.")