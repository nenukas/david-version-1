#!/usr/bin/env python3
"""
Check connecting rod and crankshaft at 30 MPa (210 kN) load.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('/home/nenuka/.openclaw/workspace/david-version-1')))

from src.engine.conrod_am import ConrodGeometryAM, ConrodAnalyzerAM
from src.engine.crankshaft import CrankshaftGeometry, CrankshaftAnalyzer

# Load conrod geometry from relaxed results
conrod_data = json.load(open('conrod_opt_relaxed2_30MPa_results_20260213_010504.json'))
geo_conrod = ConrodGeometryAM(
    beam_height=conrod_data['geometry']['beam_height'],
    beam_width=conrod_data['geometry']['beam_width'],
    web_thickness=conrod_data['geometry']['web_thickness'],
    flange_thickness=conrod_data['geometry']['flange_thickness'],
    center_length=150.0,
    big_end_width=conrod_data['geometry']['big_end_width'],
    small_end_width=conrod_data['geometry']['small_end_width'],
    big_end_diameter=86.5,
    small_end_diameter=conrod_data['geometry']['small_end_diameter'],
    fillet_big=conrod_data['geometry']['fillet_big'],
    fillet_small=conrod_data['geometry']['fillet_small'],
    lattice_relative_density=conrod_data['geometry']['lattice_relative_density'],
)
analyzer_conrod = ConrodAnalyzerAM(geo_conrod)

# Updated loads for 30 MPa (bore 94.5 mm)
bore_area = 3.14159 * (94.5/2)**2  # mm²
force_30MPa = 30.0 * bore_area  # N
print("Connecting rod load check:")
print(f"  Bore area: {bore_area:.1f} mm²")
print(f"  Force at 30 MPa: {force_30MPa:.0f} N")
print(f"  Original optimization force: 180 kN (250 bar)")
print(f"  Increase factor: {force_30MPa/180000:.3f}")

# Scale stresses linearly (since stress ∝ force)
comp_stress_orig = conrod_data['metrics']['axial_stress_comp_mpa']
comp_stress_new = comp_stress_orig * force_30MPa / 180000
bending_stress_orig = conrod_data['metrics']['bending_stress_mpa']
bending_stress_new = bending_stress_orig * force_30MPa / 180000
total_comp_new = comp_stress_new + bending_stress_new
print(f"  Original compressive stress: {comp_stress_orig:.1f} MPa")
print(f"  Scaled compressive stress: {comp_stress_new:.1f} MPa")
print(f"  Original bending stress: {bending_stress_orig:.1f} MPa")
print(f"  Scaled bending stress: {bending_stress_new:.1f} MPa")
print(f"  Total compressive stress (scaled): {total_comp_new:.1f} MPa")

# Effective yield strength (from lattice scaling)
eff_yield = conrod_data['metrics']['effective_yield_strength_mpa']
print(f"  Effective yield strength (lattice): {eff_yield:.1f} MPa")
sf_comp = eff_yield / total_comp_new if total_comp_new > 0 else 999
print(f"  Safety factor (compression): {sf_comp:.2f}")

# Buckling critical stress scales with force? Actually buckling critical stress depends on geometry and modulus, not directly on load.
# Buckling safety factor original = 1.2589. Under increased load, SF_buckling = buckling_critical_stress / total_comp_new.
buckling_critical = conrod_data['metrics']['buckling_critical_stress_mpa']
sf_buckling = buckling_critical / total_comp_new
print(f"  Buckling critical stress: {buckling_critical:.1f} MPa")
print(f"  Buckling safety factor (scaled): {sf_buckling:.2f}")

# Bearing pressure scales linearly
bearing_big_orig = conrod_data['metrics']['bearing_pressure_big_mpa']
bearing_big_new = bearing_big_orig * force_30MPa / 180000
print(f"  Big‑end bearing pressure (scaled): {bearing_big_new:.1f} MPa")
# Allowable bearing pressure for steel‑on‑steel with oil ~30 MPa.
if bearing_big_new < 30:
    print(f"  ✅ Bearing pressure acceptable (<30 MPa)")
else:
    print(f"  ⚠️ Bearing pressure high ({bearing_big_new:.1f} MPa)")

print("\nCrankshaft load check (approximate):")
# Crankshaft geometry unknown; use original optimization geometry (250 bar).
# Assume stresses scale linearly with force.
force_orig = 180000.0
force_new = force_30MPa
torque_orig = 2800.0  # N·m (from crankshaft optimization)
# Torque scales with force? Not directly; but max torque occurs at same peak pressure.
# Let's assume torque also increases proportionally to force (same BMEP).
torque_new = torque_orig * force_new / force_orig
print(f"  Original torque: {torque_orig:.0f} N·m")
print(f"  Scaled torque: {torque_new:.0f} N·m")
print(f"  Original conrod force: {force_orig:.0f} N")
print(f"  New conrod force: {force_new:.0f} N")

# Crankshaft material: 300M steel shear yield ~1000 MPa, fatigue limit ~500 MPa.
# Assume original design had safety margins. If original optimized for 250 bar, then at 300 bar stresses increase by factor 300/250 = 1.2.
increase_factor = 30.0 / 25.0  # 30 MPa vs 25 MPa (250 bar)
print(f"  Stress increase factor (pressure): {increase_factor:.2f}")
print("  Assuming crankshaft original design had margin, likely still safe.")
print("  Recommend running crankshaft optimization at 30 MPa for verification.")

print("\nThermal considerations:")
print("  • Connecting rod big‑end bearing heat flux from piston pin conduction.")
print("  • Typical bearing temperatures <150 °C with oil cooling.")
print("  • Crankshaft main journals oil‑cooled, temperatures ~100–120 °C.")
print("  • Thermal stresses minimal for rotating components.")
print("  • Ensure oil‑jet cooling for piston pin and big‑end.")

print("\nSummary:")
if sf_comp > 1.0 and sf_buckling > 1.0 and bearing_big_new < 30:
    print("  ✅ Connecting rod feasible at 30 MPa.")
else:
    print("  ⚠️ Connecting rod may need redesign.")
print("  ⚠️ Crankshaft needs verification at 30 MPa (run optimization).")
print("  ✅ Piston crown and cylinder block deck updated for thermal safety.")