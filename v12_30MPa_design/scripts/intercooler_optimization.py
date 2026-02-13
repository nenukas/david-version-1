#!/usr/bin/env python3
"""
Optimize intercooler design with relaxed targets and higher performance cores.
"""
import math

# Heat loads
Q1_total = 133.2e3  # W
Q2_total = 59.9e3

# Target hot outlet temperatures (relaxed)
T_hot_out1 = 70.0  # °C (instead of 50)
T_hot_out2 = 60.0  # °C
T_ambient = 30.0
T_hot_in1 = 115.1
T_hot_in2 = 79.3

# Passive fraction (adjustable)
passive_fraction = 0.3  # 30% passive
Q1_passive = Q1_total * passive_fraction
Q2_passive = Q2_total * passive_fraction
print(f"Passive fraction: {passive_fraction*100:.0f}%")
print(f"Passive load stage 1: {Q1_passive/1000:.1f} kW")
print(f"Passive load stage 2: {Q2_passive/1000:.1f} kW")

# Sidepod airflow
sidepod_intake_area = 0.4  # m² per side (larger)
velocity = 27.8  # m/s (100 km/h)
air_density = 1.2
ram_flow = air_density * velocity * sidepod_intake_area
core_flow_factor = 0.7
air_flow_core = ram_flow * core_flow_factor
print(f"\nAir flow per side: {air_flow_core:.2f} kg/s")

# Cold air temperature rise
cp_air = 1005
deltaT_cold1 = Q1_passive / (air_flow_core * cp_air)
deltaT_cold2 = Q2_passive / (air_flow_core * cp_air)
print(f"Cold air ΔT stage 1: {deltaT_cold1:.1f} K")
print(f"Cold air ΔT stage 2: {deltaT_cold2:.1f} K")

# Effectiveness required
epsilon1 = (T_hot_in1 - T_hot_out1) / (T_hot_in1 - T_ambient)
epsilon2 = (T_hot_in2 - T_hot_out2) / (T_hot_in2 - T_ambient)
print(f"\nEffectiveness required:")
print(f"  Stage 1: {epsilon1:.3f}")
print(f"  Stage 2: {epsilon2:.3f}")

# NTU (crossflow unmixed)
NTU1 = -math.log(1 - epsilon1)
NTU2 = -math.log(1 - epsilon2)

# Higher U (improved fin design)
U = 300  # W/(m²·K)
C_min = air_flow_core * cp_air
A1 = NTU1 * C_min / U
A2 = NTU2 * C_min / U
print(f"\nHeat transfer area (U={U} W/m²·K):")
print(f"  Stage 1: {A1:.2f} m²")
print(f"  Stage 2: {A2:.2f} m²")
print(f"  Total: {A1+A2:.2f} m²")

# Core dimensions (frontal area = sidepod intake area)
frontal = sidepod_intake_area
depth1 = A1 / frontal / 2
depth2 = A2 / frontal / 2
print(f"\nWith frontal area {frontal*10000:.0f} cm²:")
print(f"  Stage 1 core depth ≈{depth1*1000:.0f} mm")
print(f"  Stage 2 core depth ≈{depth2*1000:.0f} mm")

# Check packaging
sidepod_length = 1200  # mm
if depth1*1000 <= sidepod_length and depth2*1000 <= sidepod_length:
    print("  ✅ Core depth fits within sidepod.")
else:
    print("  ⚠️  Core depth exceeds sidepod length; consider serpentine or stacked cores.")

# Active cooling load
active_fraction = 1 - passive_fraction
Q_active = (Q1_total + Q2_total) * active_fraction
print(f"\nActive cooling load ({active_fraction*100:.0f}%): {Q_active/1000:.1f} kW")

print("\n--- Recommendations ---")
print("1. Use high‑performance plate‑fin cores (U≈300 W/m²·K).")
print("2. Target relaxed outlet temperatures: stage 1 → 70 °C, stage 2 → 60 °C.")
print("3. Active refrigeration brings final intake temperature to 50 °C.")
print("4. Consider water‑cooled intercoolers (coolant loop) for compactness.")
print("5. Add electric fans for low‑speed operation.")
print("6. CFD validation required.")