#!/usr/bin/env python3
"""
Intercooler design for sidepod placement.
Assume two intercoolers (stage1 post‑turbo, stage2 post‑supercharger) mounted in sidepods.
"""
import math

# Heat loads (from forced_induction_cooling_revised.py)
Q1_total = 133.2e3  # W (post‑turbo)
Q2_total = 59.9e3   # W (post‑supercharger)
print(f"Heat loads:")
print(f"  Stage 1 (post‑turbo): {Q1_total/1000:.1f} kW")
print(f"  Stage 2 (post‑supercharger): {Q2_total/1000:.1f} kW")

# Passive fraction (60%)
passive_fraction = 0.6
Q1_passive = Q1_total * passive_fraction
Q2_passive = Q2_total * passive_fraction
print(f"\nPassive cooling load ({passive_fraction*100:.0f}%):")
print(f"  Stage 1 passive: {Q1_passive/1000:.1f} kW")
print(f"  Stage 2 passive: {Q2_passive/1000:.1f} kW")
print(f"  Total passive: {(Q1_passive+Q2_passive)/1000:.1f} kW")

# Sidepod airflow assumptions
vehicle_speed = 100  # km/h
velocity = vehicle_speed * 1000 / 3600  # m/s
print(f"\nVehicle speed: {vehicle_speed} km/h ({velocity:.1f} m/s)")
sidepod_intake_area = 0.25  # m² per side (estimate)
air_density = 1.2  # kg/m³
ram_air_flow_per_side = air_density * velocity * sidepod_intake_area  # kg/s
print(f"Ram‑air flow per side (intake {sidepod_intake_area} m²): {ram_air_flow_per_side:.2f} kg/s")
# Assume duct losses, flow distribution: effective flow through intercooler core ~70%
core_flow_factor = 0.7
air_flow_core = ram_air_flow_per_side * core_flow_factor
print(f"Effective air flow through core: {air_flow_core:.2f} kg/s per side")

# Temperature data
T_ambient = 30.0  # °C
# Hot side temperatures
T_hot_in1 = 115.1  # °C (post‑turbo)
T_hot_out1 = 50.0  # target
T_hot_in2 = 79.3   # °C (post‑supercharger)
T_hot_out2 = 50.0  # target

# Cold side (ambient air) temperature rise
# Assume both intercoolers in series in same sidepod? Let's assume separate sides.
# We'll allocate stage 1 to left sidepod, stage 2 to right sidepod for simplicity.
# Compute required cold air temperature rise.
cp_air = 1005  # J/(kg·K)
# For stage 1 left side:
deltaT_cold1 = Q1_passive / (air_flow_core * cp_air)
T_cold_out1 = T_ambient + deltaT_cold1
print(f"\nStage 1 (left sidepod):")
print(f"  Cold air ΔT: {deltaT_cold1:.1f} K")
print(f"  Cold air outlet: {T_cold_out1:.1f} °C")
# For stage 2 right side:
deltaT_cold2 = Q2_passive / (air_flow_core * cp_air)
T_cold_out2 = T_ambient + deltaT_cold2
print(f"Stage 2 (right sidepod):")
print(f"  Cold air ΔT: {deltaT_cold2:.1f} K")
print(f"  Cold air outlet: {T_cold_out2:.1f} °C")

# Effectiveness required
epsilon1 = (T_hot_in1 - T_hot_out1) / (T_hot_in1 - T_ambient)
epsilon2 = (T_hot_in2 - T_hot_out2) / (T_hot_in2 - T_ambient)
print(f"\nRequired effectiveness:")
print(f"  Stage 1: {epsilon1:.3f}")
print(f"  Stage 2: {epsilon2:.3f}")

# NTU method (crossflow, both fluids unmixed)
# NTU = -ln(1 - epsilon) for simple crossflow? Approximate.
NTU1 = -math.log(1 - epsilon1)
NTU2 = -math.log(1 - epsilon2)
print(f"  NTU stage 1: {NTU1:.2f}")
print(f"  NTU stage 2: {NTU2:.2f}")

# Overall heat transfer coefficient U (air‑to‑air, plate‑fin)
U = 150  # W/(m²·K) (improved fin design)
C_min1 = air_flow_core * cp_air  # cold side capacity rate
C_min2 = air_flow_core * cp_air
A1 = NTU1 * C_min1 / U
A2 = NTU2 * C_min2 / U
print(f"\nHeat transfer area required (U={U} W/m²·K):")
print(f"  Stage 1 area: {A1:.2f} m²")
print(f"  Stage 2 area: {A2:.2f} m²")
print(f"  Total passive area: {A1+A2:.2f} m²")

# Core dimensions
# Assume frontal area per core = sidepod intake area (0.25 m²)
frontal = sidepod_intake_area
depth1 = A1 / frontal / 2  # divide by 2 for both sides of plate? approximate
depth2 = A2 / frontal / 2
print(f"\nAssuming frontal area {frontal*10000:.0f} cm² per core:")
print(f"  Stage 1 core depth ≈{depth1*1000:.0f} mm")
print(f"  Stage 2 core depth ≈{depth2*1000:.0f} mm")

# Pressure drop estimation (simplified)
# Air velocity through core frontal area
vel_core = air_flow_core / (air_density * frontal)
print(f"\nAir velocity through core: {vel_core:.1f} m/s")
# Pressure drop Δp ≈ 0.5 * ρ * v² * K (K ~ 100 for dense fin pack)
K = 100
delta_p = 0.5 * air_density * vel_core**2 * K
print(f"Estimated pressure drop: {delta_p:.0f} Pa ({delta_p/1000:.2f} kPa)")
if delta_p > 500:
    print("  ⚠️  High pressure drop – may need larger frontal area or lower fin density.")

# Sidepod packaging
print(f"\nSidepod packaging constraints:")
sidepod_length = 1200  # mm
sidepod_width = 300    # mm
sidepod_height = 400   # mm
print(f"  Typical sidepod dimensions: {sidepod_length} x {sidepod_width} x {sidepod_height} mm")
if depth1*1000 <= sidepod_length and depth2*1000 <= sidepod_length:
    print("  ✅ Core depth fits within sidepod length.")
else:
    print("  ⚠️  Core depth exceeds sidepod length; consider serpentine or stacked cores.")

# Recommendations
print(f"\nRecommendations:")
print(f"  1. Use high‑performance plate‑fin cores (U≈150–200 W/m²·K).")
print(f"  2. Add electric fans for low‑speed cooling (e.g., 2 kW each side).")
print(f"  3. Design ducting to ensure even airflow across core.")
print(f"  4. Consider water‑cooled intercooler (coolant loop) if packaging too tight.")
print(f"  5. Test with CFD to verify airflow and heat transfer.")

print("\n✅ Intercooler sidepod design complete.")