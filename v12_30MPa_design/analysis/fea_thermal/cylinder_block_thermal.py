#!/usr/bin/env python3
"""
Thermal stress assessment for cylinder block (7075‑T6) at 30 MPa peak pressure.
Geometry from optimized design.
Assumes radial heat transfer through cylinder wall with convection cooling.
"""
import numpy as np
import json

# ========== LOAD OPTIMIZED GEOMETRY ==========
results_path = "/home/nenuka/.openclaw/workspace/cylinder_block_30MPa_7075_T6_results_20260213_004412.json"
with open(results_path, 'r') as f:
    data = json.load(f)

geo = data['geometry']
metrics = data['metrics']

bore_diameter = 94.5  # mm (fixed)
inner_radius = bore_diameter / 2.0  # mm
wall_thickness = geo['cylinder_wall_thickness']  # mm
water_jacket_thickness = geo['water_jacket_thickness']  # mm (distance to coolant)

print("Cylinder block thermal analysis (7075‑T6)")
print("==========================================")
print(f"Bore diameter: {bore_diameter} mm")
print(f"Wall thickness: {wall_thickness:.3f} mm")
print(f"Water jacket thickness: {water_jacket_thickness:.3f} mm")
print(f"Hoop stress (pressure only): {metrics['hoop_stress_mpa']:.1f} MPa")
print(f"Deck stress (pressure only): {metrics['deck_stress_mpa']:.1f} MPa")
print(f"Bulkhead bending stress: {metrics['bulkhead_bending_stress_mpa']:.1f} MPa")

# ========== MATERIAL PROPERTIES (7075‑T6) ==========
E = 71.7e3  # MPa (71.7 GPa)
nu = 0.33
alpha = 23.0e-6  # 1/K (thermal expansion coefficient)
k = 0.15  # W/(mm·K) (150 W/(m·K))
yield_strength = 503.0  # MPa (0.2% offset)
relaxed_yield = 0.9 * yield_strength  # 452.7 MPa

# ========== COOLING ==========
h_water = 0.008  # W/(mm²·K) (8000 W/(m²·K))
coolant_temp = 90.0  # °C

# ========== HEAT FLUX RANGE ==========
# Typical peak combustion flux to cylinder wall is lower than piston crown.
# Values in W/mm² (1 W/mm² = 1 MW/m²)
heat_fluxes = np.array([0.001, 0.002, 0.003, 0.005, 0.01, 0.02])  # W/mm²

print(f"\nMaterial properties:")
print(f"  Young's modulus: {E/1000:.1f} GPa")
print(f"  Poisson's ratio: {nu}")
print(f"  Thermal expansion: {alpha*1e6:.1f} ppm/K")
print(f"  Thermal conductivity: {k*1000:.0f} W/(m·K)")
print(f"  Yield strength: {yield_strength} MPa")
print(f"  Relaxed yield (0.9×): {relaxed_yield:.1f} MPa")

# Thermal resistances (radial direction)
R_cond = wall_thickness / k  # K/(W/mm²)
R_conv = 1.0 / h_water       # K/(W/mm²)
R_total = R_cond + R_conv

print(f"\nThermal resistances:")
print(f"  Conduction R_cond = {R_cond:.1f} K/(W/mm²)")
print(f"  Convection R_conv = {R_conv:.1f} K/(W/mm²)")
print(f"  Total R_total = {R_total:.1f} K/(W/mm²)")

# Temperature drop across wall (ΔT_wall = q * R_cond)
# Thermal stress formula for flat plate (valid for wall thickness << radius)
# σ_th = α * E * ΔT_wall / (2 * (1 - ν))

print("\nHeat flux & thermal stress (inner surface):")
print(" q (W/mm²) | q (MW/m²) | ΔT_wall | σ_th (MPa) | σ_hoop+th | σ_total (von Mises) | SF")
print("-----------|------------|---------|------------|-----------|---------------------|------")

for q in heat_fluxes:
    dT_wall = q * R_cond
    sigma_th = alpha * E * dT_wall / (2.0 * (1.0 - nu))
    sigma_hoop = metrics['hoop_stress_mpa']
    # Approximate von Mises: sqrt(σ_hoop² + σ_th²) (assuming orthogonal principal stresses)
    sigma_total = np.sqrt(sigma_hoop**2 + sigma_th**2)
    sf = relaxed_yield / sigma_total if sigma_total > 0 else 999
    print(f" {q:7.4f}   | {q*1e3:8.2f}    | {dT_wall:6.1f} K | {sigma_th:7.1f}   | {sigma_hoop+sigma_th:7.1f} | {sigma_total:10.1f}      | {sf:.2f}")

# Critical heat flux for σ_total = relaxed yield
# Solve sqrt(σ_hoop² + σ_th²) = relaxed_yield
# σ_th = α*E*(q*R_cond)/(2*(1-ν))
# Let a = α*E*R_cond/(2*(1-ν))
a = alpha * E * R_cond / (2.0 * (1.0 - nu))
# σ_total² = σ_hoop² + (a*q)² = relaxed_yield²
q_crit = np.sqrt(relaxed_yield**2 - sigma_hoop**2) / a if relaxed_yield > sigma_hoop else 0.0

print(f"\nCritical heat flux for σ_total = relaxed yield ({relaxed_yield:.1f} MPa):")
if q_crit > 0:
    print(f"  q_crit = {q_crit:.5f} W/mm² = {q_crit*1e6:.0f} kW/m²")
    print(f"  ΔT_wall at q_crit = {q_crit * R_cond:.1f} K")
    print(f"  Total ΔT (wall+conv) = {q_crit * R_total:.1f} K")
else:
    print(f"  Hoop stress alone ({sigma_hoop:.1f} MPa) exceeds relaxed yield – need thicker wall.")

# Check if typical heat flux (0.003 W/mm²) is safe
q_typical = 0.003
dT_wall_typical = q_typical * R_cond
sigma_th_typical = alpha * E * dT_wall_typical / (2.0 * (1.0 - nu))
sigma_total_typical = np.sqrt(sigma_hoop**2 + sigma_th_typical**2)
sf_typical = relaxed_yield / sigma_total_typical

print(f"\nAt typical cylinder‑wall heat flux {q_typical*1e3:.1f} MW/m²:")
print(f"  ΔT_wall = {dT_wall_typical:.1f} K")
print(f"  Thermal stress = {sigma_th_typical:.1f} MPa")
print(f"  Combined von Mises stress = {sigma_total_typical:.1f} MPa")
print(f"  Safety factor = {sf_typical:.2f} ({'✅ safe' if sf_typical >= 1.0 else '❌ unsafe'})")

# Recommendations
print(f"\nRecommendations:")
if sf_typical >= 1.0:
    print("  ✅ Current wall thickness is sufficient for typical heat fluxes.")
else:
    print("  ❌ Wall thickness insufficient – increase wall thickness or improve cooling.")
    # Required wall thickness to achieve SF >= 1 at q_typical
    # Solve for t such that sqrt(σ_hoop(t)² + σ_th(t)²) = relaxed_yield
    # σ_hoop scales with 1/t (thin‑wall formula: σ = p*r/t)
    # σ_th scales with t (R_cond = t/k)
    # We'll iterate numerically.
    from scipy.optimize import fsolve
    # But we can approximate: increase wall thickness by factor.
    # Let's compute required R_cond to reduce σ_th.
    # For simplicity, suggest increase wall thickness by 20% and re‑evaluate.
    new_wall = wall_thickness * 1.2
    new_R_cond = new_wall / k
    new_sigma_hoop = sigma_hoop * wall_thickness / new_wall  # inverse proportionality
    new_sigma_th = alpha * E * (q_typical * new_R_cond) / (2.0 * (1.0 - nu))
    new_total = np.sqrt(new_sigma_hoop**2 + new_sigma_th**2)
    new_sf = relaxed_yield / new_total
    print(f"  Suggested: increase wall thickness to {new_wall:.2f} mm (SF ≈ {new_sf:.2f})")

print("\nNote: This analysis assumes radial heat transfer, flat‑plate thermal stress,")
print("and neglects axial/radial stress components. For accurate results, run")
print("coupled thermo‑mechanical FEA (Ansys).")