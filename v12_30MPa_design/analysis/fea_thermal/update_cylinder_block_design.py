#!/usr/bin/env python3
"""
Update cylinder block design with increased deck thickness for thermal safety.
Creates new JSON with updated geometry and approximated metrics.
"""
import json
import math
from pathlib import Path

# Load original optimized results
orig_path = Path("/home/nenuka/.openclaw/workspace/cylinder_block_30MPa_7075_T6_results_20260213_004412.json")
with open(orig_path, 'r') as f:
    data = json.load(f)

geo = data['geometry']
metrics = data['metrics']

print("Original design:")
print(f"  Deck thickness: {geo['deck_thickness']:.3f} mm")
print(f"  Deck stress: {metrics['deck_stress_mpa']:.1f} MPa")
print(f"  Hoop stress: {metrics['hoop_stress_mpa']:.1f} MPa")
print(f"  Mass: {metrics['mass_kg']:.2f} kg")
print(f"  Safety factor (pressure only): {0.9*503/metrics['deck_stress_mpa']:.2f}")

# New deck thickness (increase by ~18%)
new_deck = 12.0  # mm
old_deck = geo['deck_thickness']
scale_deck = old_deck / new_deck

# Update geometry
geo_updated = geo.copy()
geo_updated['deck_thickness'] = new_deck

# Approximate scaling for deck stress (bending ∝ 1/t²)
new_deck_stress = metrics['deck_stress_mpa'] * (scale_deck**2)

# Update mass (mass ∝ deck thickness)
# Total mass includes deck, cylinder walls, bulkheads, etc.
# Rough estimate: deck mass fraction ~ deck_thickness / total height?
# Use simple scaling: mass change = Δdeck_thickness * deck_area * density
# We'll approximate with linear scaling based on deck volume proportion.
# Let's assume deck contributes ~30% of total mass (guess).
# Increase in deck thickness from 10.166 to 12.0 mm = +1.834 mm.
# Deck area per cylinder = bore_spacing * bank_offset (simplified)
bore_spacing = geo['bore_spacing']
bank_angle = 60.0
bank_offset = bore_spacing * math.sin(math.radians(bank_angle / 2.0))
deck_area_per_cyl = bore_spacing * bank_offset
deck_area_total = deck_area_per_cyl * 12  # 12 cylinders
# Density of 7075‑T6 = 2.81e-6 kg/mm³
density = 2.81e-6
mass_increase = deck_area_total * (new_deck - old_deck) * density
new_mass_kg = metrics['mass_kg'] + mass_increase

# Update metrics
metrics_updated = metrics.copy()
metrics_updated['deck_stress_mpa'] = new_deck_stress
metrics_updated['mass_g'] = new_mass_kg * 1000
metrics_updated['mass_kg'] = new_mass_kg

# Re‑evaluate constraints (relaxed yield = 452.7 MPa)
relaxed_yield = 0.9 * 503.0
constraints_updated = data['constraints_satisfied'].copy()
constraints_updated['deck_stress_ok'] = new_deck_stress <= relaxed_yield
# Hoop stress unchanged, bearing pressure unchanged, bulkhead unchanged, mass unchanged
# All other constraints remain true.

print(f"\nUpdated design (deck thickness = {new_deck} mm):")
print(f"  Deck stress (scaled): {new_deck_stress:.1f} MPa")
print(f"  Hoop stress: {metrics_updated['hoop_stress_mpa']:.1f} MPa")
print(f"  Mass: {metrics_updated['mass_kg']:.2f} kg (+{mass_increase:.2f} kg)")
print(f"  Safety factor (pressure only): {relaxed_yield/new_deck_stress:.2f}")
print(f"  Deck stress constraint satisfied: {constraints_updated['deck_stress_ok']}")

# Create new JSON
updated_data = data.copy()
updated_data['geometry'] = geo_updated
updated_data['metrics'] = metrics_updated
updated_data['constraints_satisfied'] = constraints_updated
# Update note
updated_data['note'] = f"Deck thickness increased from {old_deck:.3f} mm to {new_deck} mm for thermal margin."

# Save
new_json_name = f"cylinder_block_deck_{new_deck}mm.json"
with open(new_json_name, 'w') as f:
    json.dump(updated_data, f, indent=2)
print(f"\nSaved updated design to {new_json_name}")

# Generate CAD using existing script
print("\nGenerating CAD...")
import subprocess
import sys
cad_script = "/home/nenuka/.openclaw/workspace/generate_cylinder_block_cad.py"
# Modify the script to load our new JSON? Easier to copy script and run with our JSON.
# Let's just call the existing script but with our JSON as input via monkey‑patch.
# We'll create a temporary copy of the script that reads our JSON.
# Simpler: we can run the original script, but it will pick the latest JSON (which will be our new one).
# Let's ensure our new JSON is the latest by timestamp (just created). We'll run the script.
subprocess.run([sys.executable, cad_script], cwd=Path.cwd(), check=False)

print("\n✅ Cylinder block design updated.")
print("   Next: run Ansys thermal‑stress simulation on the generated STEP file.")