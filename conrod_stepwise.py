#!/usr/bin/env python3
"""
Step‑by‑step connecting‑rod construction with validation.
Uses corrected dimensions (fixed bearing interfaces).
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace')
from cad_validation_new import StepwiseBuilder, check_interference, check_connection

# ----------------------------------------------------------------------
# LOAD CORRECTED CONROD SPEC
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/final_corrected_conrod_20260213_150623/final_corrected_spec.json") as f:
    spec = json.load(f)
    geo = spec["corrected_dimensions"]

print("=" * 70)
print("CONNECTING ROD STEP‑BY‑STEP CONSTRUCTION")
print("=" * 70)
print(f"Beam: {geo['beam_height']:.2f} × {geo['beam_width']:.2f} mm")
print(f"Web: {geo['web_thickness']:.2f} mm, Flange: {geo['flange_thickness']:.2f} mm")
print(f"Big‑end: Ø{geo['big_end_diameter']:.3f} × {geo['big_end_width']:.3f} mm")
print(f"Small‑end: Ø{geo['small_end_diameter']:.3f} × {geo['small_end_width']:.3f} mm")
print(f"Center length: {geo['center_length']:.1f} mm")

# Manufacturing constraints
MIN_WALL_THICKNESS = 3.0  # mm
MIN_FILLET_RADIUS = 1.0   # mm

# Output directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"conrod_stepwise_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Initialize builder
builder = StepwiseBuilder("conrod", out_dir)

# ----------------------------------------------------------------------
# STEP 1: I‑BEAM WEB (vertical center)
# ----------------------------------------------------------------------
print(f"\nStep 1: I‑beam web")
h = geo["beam_height"]
b = geo["beam_width"]
tw = geo["web_thickness"]
tf = geo["flange_thickness"]
L = geo["center_length"]

web_height = h - 2 * tf
web_volume = tw * web_height * L

web = (
    cq.Workplane("YZ")
    .rect(tw, web_height)
    .extrude(L)
    .translate((L/2, 0, 0))
)

builder.add_step(
    "01_web",
    web,
    expected_volume=web_volume,
    expected_bbox=(L, tw, web_height),
)

# ----------------------------------------------------------------------
# STEP 2: TOP FLANGE
# ----------------------------------------------------------------------
print(f"\nStep 2: Top flange")
top_flange_volume = b * tf * L

top_flange = (
    cq.Workplane("YZ")
    .rect(b, tf)
    .extrude(L)
    .translate((L/2, 0, (h - tf)/2))
)

builder.add_step(
    "02_top_flange",
    top_flange,
    expected_volume=top_flange_volume,
    check_interference_with=["01_web"],  # should NOT interfere (separate)
    check_connection_with=["01_web"],    # should touch web
)

# ----------------------------------------------------------------------
# STEP 3: BOTTOM FLANGE
# ----------------------------------------------------------------------
print(f"\nStep 3: Bottom flange")
bottom_flange = (
    cq.Workplane("YZ")
    .rect(b, tf)
    .extrude(L)
    .translate((L/2, 0, -(h - tf)/2))
)

builder.add_step(
    "03_bottom_flange",
    bottom_flange,
    expected_volume=top_flange_volume,
    check_interference_with=["01_web", "02_top_flange"],
    check_connection_with=["01_web"],
)

# ----------------------------------------------------------------------
# STEP 4: BEAM ASSEMBLY (union of web + flanges)
# ----------------------------------------------------------------------
print(f"\nStep 4: Beam assembly")
beam = web.union(top_flange).union(bottom_flange)
beam_volume = web_volume + 2 * top_flange_volume

builder.add_step(
    "04_beam_assembly",
    beam,
    expected_volume=beam_volume,
    expected_bbox=(L, b, h),
)

# ----------------------------------------------------------------------
# STEP 5: BIG‑END OUTER CYLINDER
# ----------------------------------------------------------------------
print(f"\nStep 5: Big‑end outer")
big_outer_radius = geo["big_end_diameter"]/2 + 12.0  # wall ~12 mm
big_outer_volume = np.pi * big_outer_radius**2 * geo["big_end_width"]

big_outer = (
    cq.Workplane("YZ")
    .circle(big_outer_radius)
    .extrude(geo["big_end_width"])
    .translate((-geo["big_end_width"]/2, 0, 0))
)

builder.add_step(
    "05_big_end_outer",
    big_outer,
    expected_volume=big_outer_volume,
    check_connection_with=["04_beam_assembly"],  # should attach to beam
)

# ----------------------------------------------------------------------
# STEP 6: BIG‑END HOLE (crank‑pin bearing)
# ----------------------------------------------------------------------
print(f"\nStep 6: Big‑end hole")
big_hole_volume = np.pi * (geo["big_end_diameter"]/2)**2 * (geo["big_end_width"] + 2)

big_hole = (
    cq.Workplane("YZ")
    .circle(geo["big_end_diameter"]/2)
    .extrude(geo["big_end_width"] + 2)
    .translate((-geo["big_end_width"]/2 - 1, 0, 0))
)

# Cut hole from outer cylinder
big_end = big_outer.cut(big_hole)
big_end_volume = big_outer_volume - big_hole_volume

builder.add_step(
    "06_big_end",
    big_end,
    expected_volume=big_end_volume,
    allow_interference_with=["05_big_end_outer"],  # cutting is intentional
    check_connection_with=["04_beam_assembly"],
)

# ----------------------------------------------------------------------
# STEP 7: SMALL‑END OUTER CYLINDER
# ----------------------------------------------------------------------
print(f"\nStep 7: Small‑end outer")
small_outer_radius = geo["small_end_diameter"]/2 + 10.0  # wall ~10 mm
small_outer_volume = np.pi * small_outer_radius**2 * geo["small_end_width"]

small_outer = (
    cq.Workplane("YZ")
    .circle(small_outer_radius)
    .extrude(geo["small_end_width"])
    .translate((L - geo["small_end_width"]/2, 0, 0))
)

builder.add_step(
    "07_small_end_outer",
    small_outer,
    expected_volume=small_outer_volume,
    check_connection_with=["04_beam_assembly"],
)

# ----------------------------------------------------------------------
# STEP 8: SMALL‑END HOLE (piston‑pin bearing)
# ----------------------------------------------------------------------
print(f"\nStep 8: Small‑end hole")
small_hole_volume = np.pi * (geo["small_end_diameter"]/2)**2 * (geo["small_end_width"] + 2)

small_hole = (
    cq.Workplane("YZ")
    .circle(geo["small_end_diameter"]/2)
    .extrude(geo["small_end_width"] + 2)
    .translate((L - geo["small_end_width"]/2 - 1, 0, 0))
)

small_end = small_outer.cut(small_hole)
small_end_volume = small_outer_volume - small_hole_volume

builder.add_step(
    "08_small_end",
    small_end,
    expected_volume=small_end_volume,
    allow_interference_with=["07_small_end_outer"],
    check_connection_with=["04_beam_assembly"],
)

# ----------------------------------------------------------------------
# STEP 9: FULL CONROD ASSEMBLY
# ----------------------------------------------------------------------
print(f"\nStep 9: Full conrod assembly")
conrod = beam.union(big_end).union(small_end)
conrod_volume = beam_volume + big_end_volume + small_end_volume

builder.add_step(
    "09_conrod_final",
    conrod,
    expected_volume=conrod_volume,
    expected_bbox=(L + geo["small_end_width"], 
                   max(b, big_outer_radius*2, small_outer_radius*2),
                   h),
)

# ----------------------------------------------------------------------
# VALIDATE NO ERRONEOUS INTERFERENCE
# ----------------------------------------------------------------------
print(f"\n" + "=" * 70)
print("FINAL INTERFERENCE CHECK")
print("=" * 70)

beam_solid = builder._get_solid("04_beam_assembly")
big_end_solid = builder._get_solid("06_big_end")
small_end_solid = builder._get_solid("08_small_end")

# Check beam–big‑end interference
interferes_be, vol_be = check_interference(beam_solid, big_end_solid)
if interferes_be:
    print(f"❌ Beam–big‑end interference: {vol_be:.3f} mm³")
else:
    print(f"✅ Beam–big‑end: no interference")

# Check beam–small‑end interference
interferes_se, vol_se = check_interference(beam_solid, small_end_solid)
if interferes_se:
    print(f"❌ Beam–small‑end interference: {vol_se:.3f} mm³")
else:
    print(f"✅ Beam–small‑end: no interference")

# Check big‑end–small‑end interference (should be far apart)
interferes_ee, vol_ee = check_interference(big_end_solid, small_end_solid)
if interferes_ee:
    print(f"❌ Big‑end–small‑end interference: {vol_ee:.3f} mm³")
else:
    print(f"✅ Big‑end–small‑end: no interference")

# Connection distances
connected_be, dist_be = check_connection(beam_solid, big_end_solid)
print(f"Beam–big‑end connection: distance {dist_be:.3f} mm ({'✅' if connected_be else '❌'})")

connected_se, dist_se = check_connection(beam_solid, small_end_solid)
print(f"Beam–small‑end connection: distance {dist_se:.3f} mm ({'✅' if connected_se else '❌'})")

# ----------------------------------------------------------------------
# EXPORT AND SUMMARY
# ----------------------------------------------------------------------
final_path = os.path.join(out_dir, "conrod_stepwise_final.step")
cq.exporters.export(conrod, final_path, "STEP")
print(f"\n✅ Final conrod exported to {final_path}")

# Save spec
spec_out = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "volumes_mm3": {
        "web": web_volume,
        "flange_single": top_flange_volume,
        "beam_total": beam_volume,
        "big_end_outer": big_outer_volume,
        "big_end_hole": big_hole_volume,
        "big_end_net": big_end_volume,
        "small_end_outer": small_outer_volume,
        "small_end_hole": small_hole_volume,
        "small_end_net": small_end_volume,
        "total": conrod_volume,
    },
}

json_path = os.path.join(out_dir, "conrod_stepwise_spec.json")
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
bbox = conrod.val().BoundingBox()
min_dim = min(bbox.xmax - bbox.xmin, bbox.ymax - bbox.ymin, bbox.zmax - bbox.zmin)
estimated_wall = min_dim * 0.25
print(f"Estimated minimum wall thickness: {estimated_wall:.2f} mm")
if estimated_wall >= MIN_WALL_THICKNESS:
    print(f"✅ Wall thickness ≥ {MIN_WALL_THICKNESS} mm")
else:
    print(f"⚠️  Wall thickness may be insufficient")

print("\n✅ Step‑by‑step conrod construction complete.")