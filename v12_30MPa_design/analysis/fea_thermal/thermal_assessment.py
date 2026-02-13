#!/usr/bin/env python3
"""
Analytical thermal stress assessment for piston crown.
Assumes 1D steady‑state heat transfer with convection.
"""
import numpy as np

# Geometry
bore_radius = 94.5 / 2          # mm
crown_thickness = 12.294        # mm

# Material (forged steel)
young = 210000.0                # MPa
poisson = 0.29
alpha = 1.2e-5                  # 1/K
conductivity = 0.05             # W/(mm·K)
convection_coeff = 0.005        # W/(mm²·K)

# Loads
pressure = 30.0                 # MPa
coolant_temp = 90.0             # °C

# Heat flux range (W/mm²)
heat_fluxes = np.array([0.1, 0.2, 0.3, 0.5, 1.0])  # 0.1 → 100 kW/m²

print("Piston crown thermal stress assessment at 30 MPa pressure")
print("=========================================================")
print(f"Crown thickness: {crown_thickness:.2f} mm")
print(f"Conductivity: {conductivity} W/(mm·K) (={conductivity*1000} W/(m·K))")
print(f"Convection h: {convection_coeff} W/(mm²·K) (={convection_coeff*1e6} W/(m²·K))")
print(f"Pressure stress (FEA): {pressure} MPa → ~300 MPa von Mises")
print()

# Thermal resistances
R_cond = crown_thickness / conductivity          # K/(W/mm²)
R_conv = 1.0 / convection_coeff                 # K/(W/mm²)
R_total = R_cond + R_conv
print(f"Thermal resistances:")
print(f"  Conduction R_cond = {R_cond:.1f} K/(W/mm²)")
print(f"  Convection R_conv = {R_conv:.1f} K/(W/mm²)")
print(f"  Total R_total = {R_total:.1f} K/(W/mm²)")
print()

print("Heat flux & temperature rise:")
print(" q (W/mm²) | q (MW/m²) | ΔT_total (K) | ΔT_crown (K) | σ_th (MPa) | σ_total (MPa) | SF (0.9×yield)")
print("-----------|------------|--------------|--------------|------------|---------------|---------------")
yield_strength = 429.0  # MPa
relaxed_yield = 0.9 * yield_strength  # 386.1 MPa
for q in heat_fluxes:
    q_mw = q * 1e6 / 1e6  # same numeric
    dT_total = q * R_total
    dT_crown = q * R_cond
    # Thermal stress (linear gradient, fully constrained)
    sigma_th = alpha * young * dT_crown / (2 * (1 - poisson))
    sigma_pressure = 300.0  # from FEA
    sigma_total = sigma_pressure + sigma_th
    sf = relaxed_yield / sigma_total
    print(f" {q:7.2f}   | {q_mw:8.2f}    | {dT_total:7.0f}      | {dT_crown:7.0f}      | {sigma_th:7.0f}    | {sigma_total:7.0f}      | {sf:.2f}")

print()
print("Critical heat flux for σ_total = relaxed yield (386 MPa):")
# Solve sigma_total = sigma_pressure + sigma_th = relaxed_yield
# sigma_th = alpha*young*(q*R_cond)/(2*(1-poisson))
# q_crit = (relaxed_yield - sigma_pressure) * 2*(1-poisson) / (alpha*young*R_cond)
q_crit = (relaxed_yield - sigma_pressure) * 2 * (1 - poisson) / (alpha * young * R_cond)
print(f" q_crit = {q_crit:.3f} W/mm² = {q_crit*1e6:.0f} kW/m²")
print(f" Corresponding ΔT_crown = {q_crit * R_cond:.0f} K")
print(f" Corresponding ΔT_total = {q_crit * R_total:.0f} K")
print()
print("Recommendations:")
print("  • Increase crown thickness (raises R_cond but also reduces pressure stress).")
print("  • Improve convection cooling (lower R_conv).")
print("  • Use higher‑conductivity material (copper alloy, but strength trade‑off).")
print("  • Active cooling (oil jet impingement).")
print("  • Limit continuous power to keep heat flux below critical.")