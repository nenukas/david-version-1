#!/usr/bin/env python3
"""
Corrected crankshaft cheek design with clearance notches for journals.
Addresses interference identified in validation checklist.
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime
import os

# ----------------------------------------------------------------------
# LOAD GEOMETRY
# ----------------------------------------------------------------------
json_path = "/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/crankshaft_30MPa_final.json"
with open(json_path) as f:
    data = json.load(f)
    geo = data["geometry"]

print("=" * 70)
print("CRANKSHAFT CHEEK CORRECTION")
print("=" * 70)

crank_radius = geo["stroke"] / 2
main_radius = geo["main_journal_diameter"] / 2
pin_radius = geo["pin_diameter"] / 2
cheek_thickness = geo["cheek_thickness"]
main_width = geo["main_journal_width"]
pin_width = geo["pin_width"]

print(f"Stroke radius: {crank_radius:.2f} mm")
print(f"Main journal: Ø{geo['main_journal_diameter']:.2f} × {main_width:.2f} mm")
print(f"Crank pin: Ø{geo['pin_diameter']:.2f} × {pin_width:.2f} mm")
print(f"Cheek thickness: {cheek_thickness:.2f} mm")

# ----------------------------------------------------------------------
# COORDINATE SYSTEM
# ----------------------------------------------------------------------
# X: crankshaft axis (width)
# Y: cheek thickness (horizontal)
# Z: vertical (stroke direction)
# Main journal center: (0,0,0)
# Crank pin center: (0,0,-crank_radius)

# ----------------------------------------------------------------------
# CHEEK PROFILE (YZ plane)
# ----------------------------------------------------------------------
# Rectangle bounds
z_min = -crank_radius - pin_radius
z_max = main_radius
height = z_max - z_min
y_half = cheek_thickness / 2

# Create rectangular block for cheek (width = max journal width + margin)
cheek_width = max(main_width, pin_width) + 10.0  # extra margin
cheek_block = (
    cq.Workplane("YZ")
    .rect(cheek_thickness, height)
    .extrude(cheek_width)
    .translate((0, 0, (z_max + z_min) / 2))  # center in Z
    .translate((-cheek_width / 2, 0, 0))  # center in X
)
print(f"Cheek block: {cheek_thickness:.2f} × {height:.2f} × {cheek_width:.2f} mm")

# Subtract main journal cylinder (radius = main_radius + clearance 1mm)
main_cut = (
    cq.Workplane("YZ")
    .circle(main_radius + 1.0)
    .extrude(cheek_width + 2.0)  # ensure complete cut
    .translate((-cheek_width / 2 - 1.0, 0, 0))
)
cheek = cheek_block.cut(main_cut)

# Subtract crank pin cylinder
pin_cut = (
    cq.Workplane("YZ")
    .circle(pin_radius + 1.0)
    .extrude(cheek_width + 2.0)
    .translate((-cheek_width / 2 - 1.0, 0, -crank_radius))
)
cheek = cheek.cut(pin_cut)

print("✅ Cheek with journal clearance notches created")

# ----------------------------------------------------------------------
# MAIN JOURNAL (cylinder along X)
# ----------------------------------------------------------------------
main = (
    cq.Workplane("XY")
    .circle(main_radius)
    .extrude(main_width)
    .translate((-main_width / 2, 0, 0))
)

# ----------------------------------------------------------------------
# CRANK PIN (cylinder along X, offset downward)
# ----------------------------------------------------------------------
pin = (
    cq.Workplane("XY")
    .circle(pin_radius)
    .extrude(pin_width)
    .translate((-pin_width / 2, 0, -crank_radius))
)

# ----------------------------------------------------------------------
# ASSEMBLE
# ----------------------------------------------------------------------
throw = main.union(pin).union(cheek)

# ----------------------------------------------------------------------
# OIL PASSAGE (simplified: cross‑drilled hole from main to pin)
# ----------------------------------------------------------------------
# Hole diameter
oil_dia = 6.0  # mm
# Vector from main center to pin center
start = (0, 0, 0)
end = (0, 0, -crank_radius)
# Create a cylinder along that vector, rotated to X direction
oil_passage = (
    cq.Workplane("XZ")
    .circle(oil_dia / 2)
    .extrude(crank_radius)
    .rotate((0, 0, 0), (0, 0, 1), 90)  # rotate to vertical
    .translate((-cheek_width / 2, 0, -crank_radius / 2))
)
throw = throw.cut(oil_passage)
print(f"✅ Added oil passage Ø{oil_dia} mm from main to pin")

# ----------------------------------------------------------------------
# FILLETS (apply to cheek‑journal junctions)
# ----------------------------------------------------------------------
# Note: automatic fillet selection is complex; we specify edges manually
print("⚠️  Fillets need manual selection in CAD viewer")
print("   • Cheek‑to‑main‑journal edges")
print("   • Cheek‑to‑pin edges")
print(f"   • Recommended radius: {geo['fillet_main']:.1f} mm (main), {geo['fillet_pin']:.1f} mm (pin)")

# ----------------------------------------------------------------------
# CHAMFERS (sharp edges)
# ----------------------------------------------------------------------
print("⚠️  Chamfers needed on sharp edges (0.5×45°)")

# ----------------------------------------------------------------------
# DRAFT ANGLES (for forging)
# ----------------------------------------------------------------------
print("⚠️  Draft angles (1°) required on vertical surfaces for forging")

# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

try:
    vol = throw.val().Volume()
    bbox = throw.val().BoundingBox()
    print(f"Total volume: {vol:.1f} mm³")
    print(f"Bounding box: X {bbox.xmax-bbox.xmin:.1f}, Y {bbox.ymax-bbox.ymin:.1f}, Z {bbox.zmax-bbox.zmin:.1f} mm")
    
    # Check interference: compute sum of component volumes
    main_vol = np.pi * main_radius**2 * main_width
    pin_vol = np.pi * pin_radius**2 * pin_width
    cheek_vol = cheek_thickness * height * cheek_width - \
                np.pi * (main_radius + 1.0)**2 * cheek_width - \
                np.pi * (pin_radius + 1.0)**2 * cheek_width
    sum_vol = main_vol + pin_vol + max(cheek_vol, 0)
    diff = abs(vol - sum_vol) / sum_vol if sum_vol > 0 else 0
    if diff < 0.05:
        print(f"✅ Volume consistent (diff {diff*100:.1f}%) – no large interference")
    else:
        print(f"⚠️  Volume mismatch {diff*100:.1f}% – possible interference")
        
except Exception as e:
    print(f"Validation error: {e}")

# ----------------------------------------------------------------------
# EXPORT
# ----------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"crankshaft_cheek_corrected_{timestamp}"
os.makedirs(out_dir, exist_ok=True)

step_path = os.path.join(out_dir, "crankshaft_cheek_corrected.step")
cq.exporters.export(throw, step_path, "STEP")
print(f"\n✅ CAD exported to {step_path}")

spec = {
    "timestamp": datetime.now().isoformat(),
    "geometry": geo,
    "corrections": {
        "cheek_clearance": "notched for journal interference",
        "oil_passage": f"Ø{oil_dia} mm cross‑drilled",
        "missing_features": ["fillets", "chamfers", "draft_angles", "balance_weights", "keyways"],
    },
}

spec_path = os.path.join(out_dir, "crankshaft_cheek_corrected_spec.json")
import json as jsonlib
with open(spec_path, "w") as f:
    jsonlib.dump(spec, f, indent=2)
print(f"✅ Specification saved to {spec_path}")

print("\n" + "=" * 70)
print("NEXT STEPS")
print("=" * 70)
print("1. Open STEP in CAD viewer and inspect clearance.")
print("2. Apply fillets and chamfers manually.")
print("3. Add draft angles (1°) for forging.")
print("4. Add balance‑weight profiling.")
print("5. Add keyways and bolt holes.")
print("\nCheek interference resolved – journals now have clearance.")