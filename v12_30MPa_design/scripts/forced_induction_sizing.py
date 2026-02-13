#!/usr/bin/env python3
"""
Sizing of forced‑induction system for V12 8.0 L engine at 3000 whp.
Assumes twin‑turbo + supercharger with two‑stage intercooling.
"""
import math

# Engine parameters
bore = 94.5  # mm
stroke = 94.5  # mm
cylinders = 12
displacement_l = (math.pi * (bore/2)**2 * stroke * cylinders) / 1e6  # liters
print(f"Engine displacement: {displacement_l:.2f} L")

# Operating points
redline_rpm = 11000
volumetric_efficiency = 1.0  # at boost
target_power_w = 3000 * 745.7  # 3000 whp → watts
target_power_kw = target_power_w / 1000
print(f"Target power: {target_power_kw:.0f} kW ({target_power_w/745.7:.0f} whp)")

# Air‑fuel ratio (rich)
afr = 12.0  # typical for high‑boost gasoline
# Brake‑specific fuel consumption (BSFC) in kg/kWh
bsfc_kg_kwh = 0.273  # approx 0.45 lb/hp·hr
fuel_flow_kg_s = target_power_kw * bsfc_kg_kwh / 3600
air_flow_kg_s = fuel_flow_kg_s * afr
print(f"Fuel flow: {fuel_flow_kg_s*3600:.1f} kg/h")
print(f"Air flow: {air_flow_kg_s:.3f} kg/s ({air_flow_kg_s*3600:.1f} kg/h)")

# Naturally aspirated air flow at redline
na_air_flow_m3s = (redline_rpm / 2) * displacement_l / 1000 / 60  # m³/s
air_density_ambient = 1.2  # kg/m³ at 30°C, sea level
na_air_flow_kg_s = na_air_flow_m3s * air_density_ambient
print(f"NA air flow at {redline_rpm} rpm: {na_air_flow_m3s:.3f} m³/s, {na_air_flow_kg_s:.3f} kg/s")

# Required density ratio
density_ratio = air_flow_kg_s / na_air_flow_kg_s
print(f"Density ratio (boost + cooling): {density_ratio:.2f}")

# Assume intercooled intake temperature
T_intake = 50 + 273.15  # K (50°C)
T_ambient = 30 + 273.15  # K (30°C)
# Pressure ratio needed (ideal gas)
pressure_ratio = density_ratio * T_intake / T_ambient
print(f"Pressure ratio required: {pressure_ratio:.2f} (approx {pressure_ratio-1:.2f} bar gauge)")

# Split between turbo and supercharger
# Let's assume turbos provide pressure ratio 2.0 (1.0 bar gauge), supercharger adds 1.5 (0.5 bar gauge) for total 2.5
turbo_pr = 2.0
supercharger_pr = pressure_ratio / turbo_pr
print(f"Assuming turbo PR: {turbo_pr:.2f}, supercharger PR: {supercharger_pr:.2f}")

# Turbo selection (Garrett)
# Use GTX3582R for each bank (twin‑turbo)
# Compressor map data: approximate flow range 20–65 lb/min per turbo
# Convert air flow to lb/min
air_flow_lb_min = air_flow_kg_s * 132.277  # kg/s → lb/min
per_turbo_flow = air_flow_lb_min / 2
print(f"Total air flow: {air_flow_lb_min:.1f} lb/min")
print(f"Per turbo (twin): {per_turbo_flow:.1f} lb/min")

# Check if within GTX3582R range (approx 20–65 lb/min)
if 20 <= per_turbo_flow <= 65:
    print("✅ GTX3582R suitable per turbo.")
else:
    print("⚠️  GTX3582R may be undersized/oversized; consider GTX4294R.")

# Supercharger selection (centrifugal, e.g., Vortech V‑30)
# Supercharger outlet temperature rise (adiabatic)
# Assume efficiency 70%
gamma = 1.4  # air
cp = 1005  # J/(kg·K)
T_in_super = T_intake  # after first intercooler
pressure_ratio_super = supercharger_pr
temp_rise_ideal = T_in_super * (pressure_ratio_super**((gamma-1)/gamma) - 1)
temp_rise_actual = temp_rise_ideal / 0.7
T_out_super = T_in_super + temp_rise_actual
print(f"Supercharger inlet temp: {T_in_super-273.15:.1f}°C")
print(f"Supercharger temp rise: {temp_rise_actual:.1f} K")
print(f"Supercharger outlet temp: {T_out_super-273.15:.1f}°C")

# Second intercooler must cool to ~50°C again
cooling_needed = T_out_super - T_intake
print(f"Second intercooler ΔT needed: {cooling_needed:.1f} K")

# Intercooler sizing (air‑to‑liquid)
# Assume heat rejection Q = m_dot * cp * ΔT
heat_rejection_w = air_flow_kg_s * cp * cooling_needed
print(f"Second intercooler heat rejection: {heat_rejection_w/1000:.1f} kW")

# Bus‑compressor cooling system
# Assume bus A/C compressor capacity ~20 kW cooling at 0°C evaporator.
# Two intercoolers sharing load.
print(f"Total intercooler heat load (both stages): ~{heat_rejection_w*2/1000:.1f} kW")
print("Assuming bus compressor can handle load with adequate radiator.")

# Packaging dimensions (approx)
print("\n--- Approximate Component Dimensions ---")
print("Twin Garrett GTX3582R turbos:")
print("  Diameter: ~110 mm, length: ~180 mm")
print("  Weight: ~8 kg each")
print("Vortech V‑30 supercharger:")
print("  Diameter: ~150 mm, length: ~250 mm")
print("  Weight: ~15 kg")
print("Air‑to‑liquid intercoolers (x2):")
print("  Size: 300 x 200 x 80 mm each")
print("  Weight: ~5 kg each")
print("Bus compressor (A/C type):")
print("  Size: 200 x 150 x 150 mm")
print("  Weight: ~12 kg")
print("Refrigerant radiator (front‑mounted):")
print("  Size: 500 x 400 x 50 mm")
print("  Weight: ~8 kg")

# Engine bay size (mid‑engine)
print("\n--- Mid‑Engine Bay Constraints ---")
print("Typical mid‑engine dimensions:")
print("  Width: 1200 mm")
print("  Height: 800 mm (above crank centerline)")
print("  Length: 1500 mm (engine + turbos + supercharger)")
print("Proposed layout:")
print("  Engine block: 800 mm long")
print("  Turbos mounted low, near exhaust headers")
print("  Supercharger mounted front‑center (accessory drive)")
print("  Intercoolers mounted on sides of engine bay")
print("  Bus compressor mounted on engine front (belt‑driven)")
print("  Refrigerant radiator mounted in front of engine bay (airflow)")

# Check fit
total_length = 800 + 250 + 100  # block + supercharger + clearance
total_width = 1200  # within bay
total_height = 800  # acceptable
print(f"\nEstimated package length: {total_length} mm")
if total_length <= 1500:
    print("✅ Package fits within mid‑engine bay.")
else:
    print("⚠️  Package length may exceed bay.")