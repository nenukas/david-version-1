#!/usr/bin/env python3
"""
Thermal stress assessment for cylinder block DECK (7075‑T6) at 30 MPa peak pressure.
Deck is the top surface that seals against cylinder head.
"""
import numpy as np
import json

# ========== LOAD OPTIMIZED GEOMETRY ==========
results_path = "/home/nenuka/.openclaw/workspace/cylinder_block_30MPa_7075_T6_results_20260213_004412.json"
with open(results_path, 'r') as f:
    data = json.load(f)

geo = data['geometry']
metrics = data['metrics']

deck_thickness = geo['deck_thickness']  # mm
print("Cylinder block DECK thermal analysis (7075‑T6)")
print("==============================================")
print(f"Deck thickness: {deck_thickness:.3f} mm")
print(f"Deck stress (pressure only): {metrics['deck_stress_mpa']:.1f} MPa")

# ========== MATERIAL PROPERTIES (7075‑T6) ==========
E = 71.7e3  # MPa
nu = 0.33
alpha = 23.0e-6  # 1/K
k = 0.15  # W/(mm·K) (150 W/(m·K))
yield_strength = 503.0  # MPa
relaxed_yield = 0.9 * yield_strength  # 452.7 MPa

# ========== COOLING ==========
h_water = 0.008  # W/(mm²·K) (8000 W/(m²·K))
coolant_temp = 90.0  # °C

# ========== HEAT FLUX RANGE ==========
# Deck sees combustion heat flux similar to piston crown but somewhat lower
# due to head gasket and cooling passages. Use same range.
heat_fluxes = np.array([0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1])  # W/mm²

print(f"\nMaterial properties:")
print(f"  Young's modulus: {E/1000:.1f} GPa")
print(f"  Poisson's ratio: {nu}")
print(f"  Thermal expansion: {alpha*1e6:.1f} ppm/K")
print(f"  Thermal conductivity: {k*1000:.0f} W/(m·K)")
print(f"  Yield strength: {yield_strength} MPa")
print(f"  Relaxed yield (0.9×): {relaxed_yield:.1f} MPa")

# Thermal resistances (1D through deck)
R_cond = deck_thickness / k  # K/(W/mm²)
R_conv = 1.0 / h_water       # K/(W/mm²)
R_total = R_cond + R_conv

print(f"\nThermal resistances:")
print(f"  Conduction R_cond = {R_cond:.1f} K/(W/mm²)")
print(f"  Convection R_conv = {R_conv:.1f} K/(W/mm²)")
print(f"  Total R_total = {R_total:.1f} K/(W/mm²)")

# Temperature drop across deck (ΔT_deck = q * R_cond)
# Thermal stress formula for constrained plate (fully restrained)
# σ_th = α * E * ΔT_deck / (2 * (1 - ν))

print("\nHeat flux & thermal stress (deck top surface):")
print(" q (W/mm²) | q (MW/m²) | ΔT_deck | σ_th (MPa) | σ_deck+th | σ_total (MPa) | SF")
print("-----------|------------|---------|------------|-----------|---------------|------")

for q in heat_fluxes:
    dT_deck = q * R_cond
    sigma_th = alpha * E * dT_deck / (2.0 * (1.0 - nu))
    sigma_deck = metrics['deck_stress_mpa']
    # Conservative: add directly (worst‑case same direction)
    sigma_total = sigma_deck + sigma_th
    sf = relaxed_yield / sigma_total if sigma_total > 0 else 999
    print(f" {q:7.4f}   | {q*1e3:8.2f}    | {dT_deck:6.1f} K | {sigma_th:7.1f}   | {sigma_total:7.1f} | {sigma_total:7.1f}      | {sf:.2f}")

# Critical heat flux for σ_total = relaxed yield
# sigma_total = sigma_deck + a*q = relaxed_yield, where a = α*E*R_cond/(2*(1-ν))
a = alpha * E * R_cond / (2.0 * (1.0 - nu))
q_crit = (relaxed_yield - sigma_deck) / a if relaxed_yield > sigma_deck else 0.0

print(f"\nCritical heat flux for σ_total = relaxed yield ({relaxed_yield:.1f} MPa):")
if q_crit > 0:
    print(f"  q_crit = {q_crit:.5f} W/mm² = {q_crit*1e6:.0f} kW/m²")
    print(f"  ΔT_deck at q_crit = {q_crit * R_cond:.1f} K")
    print(f"  Total ΔT (deck+conv) = {q_crit * R_total:.1f} K")
else:
    print(f"  Deck stress alone ({sigma_deck:.1f} MPa) exceeds relaxed yield – need thicker deck.")

# Typical heat flux (3 MW/m² = 0.003 W/mm²)
q_typical = 0.003
dT_deck_typical = q_typical * R_cond
sigma_th_typical = alpha * E * dT_deck_typical / (2.0 * (1.0 - nu))
sigma_total_typical = sigma_deck + sigma_th_typical
sf_typical = relaxed_yield / sigma_total_typical

print(f"\nAt typical deck heat flux {q_typical*1e3:.1f} MW/m²:")
print(f"  ΔT_deck = {dT_deck_typical:.1f} K")
print(f"  Thermal stress = {sigma_th_typical:.1f} MPa")
print(f"  Combined stress (pressure+thermal) = {sigma_total_typical:.1f} MPa")
print(f"  Safety factor = {sf_typical:.2f} ({'✅ safe' if sf_typical >= 1.0 else '❌ unsafe'})")

# Recommendations
print(f"\nRecommendations:")
if sf_typical >= 1.0:
    print("  ✅ Current deck thickness is sufficient for typical heat fluxes.")
else:
    print("  ❌ Deck thickness insufficient – increase deck thickness or improve cooling.")
    # Required deck thickness to achieve SF >= 1 at q_typical
    # Solve sigma_deck(t) + sigma_th(t) = relaxed_yield
    # sigma_deck scales with 1/t² (bending), sigma_th scales with t (R_cond)
    # We'll iterate simple increase.
    new_deck = deck_thickness * 1.2
    new_R_cond = new_deck / k
    # Approximate deck stress scaling: σ ∝ 1/t² (bending of clamped circular plate)
    new_sigma_deck = sigma_deck * (deck_thickness / new_deck)**2
    new_sigma_th = alpha * E * (q_typical * new_R_cond) / (2.0 * (1.0 - nu))
    new_total = new_sigma_deck + new_sigma_th
    new_sf = relaxed_yield / new_total
    print(f"  Suggested: increase deck thickness to {new_deck:.2f} mm (SF ≈ {new_sf:.2f})")

print("\nNote: This analysis assumes 1D heat transfer through deck, fully restrained")
print("thermal expansion, and linear addition of pressure and thermal stresses.")
print("For accurate results, run coupled thermo‑mechanical FEA (Ansys).")