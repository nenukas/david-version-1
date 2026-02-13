#!/usr/bin/env python3
"""
Version 2: adjust small‑end width to meet bearing‑pressure limit.
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime

# Load previous corrected spec
with open("/home/nenuka/.openclaw/workspace/corrected_conrod_20260213_145815/corrected_spec.json") as f:
    spec = json.load(f)

corrected = spec["corrected_dimensions"]

# ----------------------------------------------------------------------
# ADJUST SMALL‑END WIDTH FOR BEARING PRESSURE
# ----------------------------------------------------------------------
force = 180000.0  # N
target_pressure = 200.0  # MPa
required_area = force / target_pressure  # mm²
required_width = required_area / corrected["small_end_diameter"]
# Round up to nearest 0.5 mm
new_small_width = np.ceil(required_width * 2) / 2
print(f"Required small‑end area: {required_area:.1f} mm²")
print(f"Required width: {required_width:.2f} mm → rounded to {new_small_width:.2f} mm")

corrected["small_end_width"] = float(new_small_width)

# Recalculate pressure
small_area = corrected["small_end_diameter"] * corrected["small_end_width"]
small_pressure = force / small_area
print(f"New small‑end pressure: {small_pressure:.1f} MPa")
if small_pressure <= target_pressure:
    print("✅ Pressure within limit")
else:
    print("❌ Still too high – increase diameter or width further")

# ----------------------------------------------------------------------
# GENERATE CAD
# ----------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"corrected_conrod_v2_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Simplified I‑beam
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

# Big end
big_outer_radius = corrected["big_end_diameter"]/2 + 12.0
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

conrod = beam.union(big_end).union(small_end)

step_path = f"{out_dir}/corrected_conrod_v2.step"
cq.exporters.export(conrod, step_path, "STEP")
print(f"✅ CAD saved to {step_path}")

# ----------------------------------------------------------------------
# SAVE UPDATED SPEC
# ----------------------------------------------------------------------
spec_v2 = {
    "timestamp": datetime.now().isoformat(),
    "previous_correction": spec["corrected_dimensions"],
    "corrected_dimensions": corrected,
    "validation": {
        "big_end_pressure_mpa": force / (corrected["big_end_diameter"] * corrected["big_end_width"]),
        "small_end_pressure_mpa": small_pressure,
        "small_end_width_adjusted_to": new_small_width,
        "pressure_target_mpa": target_pressure,
    }
}

json_path = f"{out_dir}/corrected_spec_v2.json"
with open(json_path, "w") as f:
    json.dump(spec_v2, f, indent=2)
print(f"✅ Specification saved to {json_path}")

print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)
print(f"Big‑end: {corrected['big_end_width']:.2f} × {corrected['big_end_diameter']:.2f} mm")
print(f"Small‑end: {corrected['small_end_width']:.2f} × {corrected['small_end_diameter']:.2f} mm")
print(f"Pressures: big {spec_v2['validation']['big_end_pressure_mpa']:.1f} MPa, small {small_pressure:.1f} MPa")
print("\n✅ Ready for interference check with crankshaft & piston.")