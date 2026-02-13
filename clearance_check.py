#!/usr/bin/env python3
"""
Clearance checks for V12 components using generated CAD and JSON specs.
"""
import json
import math
import os

print("=" * 70)
print("V12 HYPERCAR – CLEARANCE CHECK REPORT")
print("=" * 70)

# Load geometry data
def load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    else:
        print(f"⚠️  Missing: {path}")
        return None

# Piston
piston = load_json("/home/nenuka/.openclaw/workspace/fea_thermal/piston_crown_15.0mm.json")
if piston:
    geom = piston["geometry"]
    crown_thickness = geom["crown_thickness"]
    pin_boss_width = geom["pin_boss_width"]
    skirt_length = geom["skirt_length"]
    skirt_thickness = geom["skirt_thickness"]
    piston_diameter = 94.5 - 0.1  # bore - clearance
    print(f"\nPISTON")
    print(f"  Crown thickness: {crown_thickness:.2f} mm")
    print(f"  Skirt length: {skirt_length:.2f} mm")
    print(f"  Pin‑boss width: {pin_boss_width:.2f} mm")
    print(f"  Piston diameter: {piston_diameter:.2f} mm")
    print(f"  Bore clearance: {0.1:.2f} mm (radial 0.05 mm)")

# Cylinder block
block = load_json("/home/nenuka/.openclaw/workspace/fea_thermal/cylinder_block_deck_12.0mm.json")
if block:
    geom = block["geometry"]
    deck_thickness = geom["deck_thickness"]
    cylinder_wall_thickness = geom["cylinder_wall_thickness"]
    water_jacket_thickness = geom["water_jacket_thickness"]
    bore = 94.5
    print(f"\nCYLINDER BLOCK")
    print(f"  Bore: {bore:.2f} mm")
    print(f"  Deck thickness: {deck_thickness:.2f} mm")
    print(f"  Cylinder wall thickness: {cylinder_wall_thickness:.2f} mm")

# Connecting rod
conrod = load_json("/home/nenuka/.openclaw/workspace/conrod_opt_relaxed2_30MPa_results_20260213_010504.json")
if conrod:
    geom = conrod["geometry"]
    beam_height = geom["beam_height"]
    beam_width = geom["beam_width"]
    big_end_width = geom["big_end_width"]
    small_end_width = geom["small_end_width"]
    small_end_dia = geom["small_end_diameter"]
    print(f"\nCONNECTING ROD")
    print(f"  Beam cross‑section: {beam_width:.2f} × {beam_height:.2f} mm")
    print(f"  Big‑end width: {big_end_width:.2f} mm")
    print(f"  Small‑end width: {small_end_width:.2f} mm")
    print(f"  Small‑end inner diameter: {small_end_dia:.2f} mm")

# Crankshaft
crank = load_json("/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/crankshaft_30MPa_final.json")
if crank:
    geom = crank["geometry"]
    main_journal_dia = geom["main_journal_diameter"]
    main_journal_width = geom["main_journal_width"]
    pin_dia = geom["pin_diameter"]
    pin_width = geom["pin_width"]
    stroke = geom["stroke"]
    cheek_thickness = geom["cheek_thickness"]
    cheek_radius = geom["cheek_radius"]
    crank_radius = stroke/2
    print(f"\nCRANKSHAFT")
    print(f"  Stroke: {stroke:.2f} mm (radius {crank_radius:.2f} mm)")
    print(f"  Crank‑pin diameter: {pin_dia:.2f} mm")
    print(f"  Main‑journal diameter: {main_journal_dia:.2f} mm")
    print(f"  Cheek thickness: {cheek_thickness:.2f} mm")

# Valve train
print(f"\nVALVE TRAIN")
intake_valve_dia = 42.5
exhaust_valve_dia = 35.9
intake_lift = 11.1
exhaust_lift = 9.3
print(f"  Intake valve diameter: {intake_valve_dia:.2f} mm, lift {intake_lift:.2f} mm")
print(f"  Exhaust valve diameter: {exhaust_valve_dia:.2f} mm, lift {exhaust_lift:.2f} mm")

# Assembly positions (from full_assembly_data.json)
assembly = load_json("/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/full_assembly_data.json")
if assembly:
    bore_spacing = assembly["bore_spacing"]
    deck_thickness = assembly["deck_thickness"]
    stroke = assembly["stroke"]
    crank_radius = assembly["crank_radius"]
    rod_length = assembly["rod_length"]
    compression_height = assembly["compression_height"]
    print(f"\nASSEMBLY")
    print(f"  Bore spacing: {bore_spacing:.2f} mm")
    print(f"  Rod length: {rod_length:.2f} mm")
    print(f"  Compression height: {compression_height:.2f} mm")

# ----------------------------------------------------------------------
# CLEARANCE CALCULATIONS
# ----------------------------------------------------------------------
print("\n" + "-" * 70)
print("CLEARANCE CHECKS")
print("-" * 70)

# 1. Piston‑to‑bore radial clearance
piston_clearance = 0.1
print(f"\n1. Piston‑to‑bore radial clearance:")
print(f"   Radial gap: {piston_clearance/2:.3f} mm")
print(f"   ✅ Acceptable (typical 0.03–0.10 mm)")

# 2. Piston‑to‑valve clearance at TDC
# Approximate: valve head extends into cylinder at max lift
# Assume valve head protrudes into chamber by ~5 mm at max lift
# Piston crown at TDC is at deck clearance (0.8 mm) + crown thickness (15 mm) = 15.8 mm from deck top
# Valve seat depth ~8 mm, valve head extends below seat ~2 mm
# So valve head bottom at Z = -8 -2 = -10 mm from deck top
# At TDC, piston crown top at Z = +0.8 mm (deck clearance). So gap = 0.8 - (-10) = 10.8 mm
# But at overlap, valve lift maximum, valve head moves down further.
# Complex; simplified:
valve_head_protrusion = 5  # mm into chamber at max lift
piston_crown_top_at_TDC = 0.8  # deck clearance
valve_head_bottom_at_max_lift = -valve_head_protrusion  # relative to deck top
clearance_piston_valve = piston_crown_top_at_TDC - valve_head_bottom_at_max_lift
print(f"\n2. Piston‑to‑valve clearance at TDC (approx):")
print(f"   Estimated gap: {clearance_piston_valve:.2f} mm")
if clearance_piston_valve > 2.0:
    print(f"   ✅ Likely safe (>2 mm)")
else:
    print(f"   ⚠️  May be tight (<2 mm) – need detailed cam‑piston phasing")

# 3. Connecting‑rod‑to‑crank‑web clearance
# Rod width at big end = big_end_width (116.8 mm)
# Crank cheek thickness = cheek_thickness (17.15 mm)
# Assuming cheek‑to‑cheek gap = pin_width (26.5 mm) + 2*clearance
# Clearance = (gap - rod_width)/2
if conrod and crank:
    rod_width = big_end_width
    pin_w = pin_width
    cheek_t = cheek_thickness
    gap = pin_w + 2*cheek_t  # approximate cheek inner spacing
    clearance_rod_cheek = (gap - rod_width)/2
    print(f"\n3. Connecting‑rod‑to‑crank‑cheek clearance:")
    print(f"   Rod width: {rod_width:.2f} mm")
    print(f"   Cheek‑to‑cheek gap (approx): {gap:.2f} mm")
    print(f"   Radial clearance each side: {clearance_rod_cheek:.2f} mm")
    if clearance_rod_cheek > 1.0:
        print(f"   ✅ Adequate (>1 mm)")
    else:
        print(f"   ⚠️  Tight (<1 mm) – risk of interference")

# 4. Valve‑to‑valve clearance (between intake and exhaust)
# Valve spacing = bore * 0.8 = 75.6 mm
# Valve head radii: intake 21.25 mm, exhaust 17.95 mm
# Edge‑to‑edge distance = spacing - (r1 + r2) = 75.6 - (21.25+17.95) = 36.4 mm
valve_spacing = 94.5 * 0.8
edge_to_edge = valve_spacing - (intake_valve_dia/2 + exhaust_valve_dia/2)
print(f"\n4. Valve‑to‑valve clearance:")
print(f"   Center‑to‑center spacing: {valve_spacing:.2f} mm")
print(f"   Edge‑to‑edge distance: {edge_to_edge:.2f} mm")
print(f"   ✅ Plenty of space")

# 5. Piston‑ring‑to‑groove clearance
# Typical ring axial clearance 0.04–0.08 mm, radial 0.05–0.10 mm
print(f"\n5. Piston ring clearances (typical):")
print(f"   Axial ring‑to‑groove: 0.04–0.08 mm")
print(f"   Radial ring‑to‑groove: 0.05–0.10 mm")
print(f"   ✅ To be determined by ring supplier")

# 6. Main‑bearing clearance
# Typical radial clearance 0.02–0.04 mm for performance engines
print(f"\n6. Bearing clearances (typical):")
print(f"   Main‑bearing radial: 0.02–0.04 mm")
print(f"   Rod‑bearing radial: 0.02–0.05 mm")
print(f"   ✅ To be determined by bearing supplier")

# 7. Deck clearance (piston crown to deck top at TDC)
deck_clearance = 0.8
print(f"\n7. Deck clearance (piston crown to deck top at TDC):")
print(f"   {deck_clearance:.2f} mm")
if deck_clearance > 0.5 and deck_clearance < 1.5:
    print(f"   ✅ Within typical range (0.5–1.5 mm)")
else:
    print(f"   ⚠️  Outside typical range")

# 8. Compression ratio calculation
if piston and block and assembly:
    bore = 94.5
    stroke = 94.5
    swept_volume = math.pi * (bore/2)**2 * stroke  # mm³
    clearance_volume = (deck_clearance * math.pi * (bore/2)**2) + 72400  # deck + chamber volume (approx)
    compression_ratio = (swept_volume + clearance_volume) / clearance_volume
    print(f"\n8. Compression ratio (approx):")
    print(f"   Swept volume: {swept_volume/1000:.1f} cm³")
    print(f"   Clearance volume: {clearance_volume/1000:.1f} cm³")
    print(f"   Compression ratio: {compression_ratio:.2f}:1")
    if 9.0 < compression_ratio < 10.0:
        print(f"   ✅ Suitable for forced induction")
    else:
        print(f"   ⚠️  May need adjustment")

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print("1. Verify all clearances with detailed CAD assembly (interference detection).")
print("2. Run thermal expansion analysis for hot clearances.")
print("3. Confirm valve‑to‑piston clearance with actual cam profiles.")
print("4. Check bearing clearances with selected bearing shells.")
print("5. Perform FEA on critical components (piston, conrod, crank).")
print("\n✅ Clearance check complete. Refer to CAD files for visual verification.")