#!/usr/bin/env python3
"""
Condenser radiator sizing for front‑mounted, micro‑channel.
"""
import math

Q_cond = 105.5e3  # W (from forced_induction_cooling_revised.py)
print(f"Heat rejection: {Q_cond/1000:.1f} kW")

# Improved micro‑channel radiator
U = 200  # W/(m²·K) (aggressive)
deltaT_air = 30  # K (air temp rise)
A = Q_cond / (U * deltaT_air)
print(f"\nRequired area (U={U} W/m²·K, ΔT={deltaT_air} K): {A:.2f} m²")

# Frontal area constraints (front of mid‑engine car)
frontal_width = 1.0  # m
frontal_height = 0.4  # m
frontal_area = frontal_width * frontal_height
print(f"Frontal area available: {frontal_area:.2f} m² ({frontal_width*1000:.0f} x {frontal_height*1000:.0f} mm)")

# Core depth
depth = A / frontal_area / 2  # assume both sides
print(f"Core depth (approx): {depth*1000:.0f} mm")

# Airflow through core (vehicle speed 100 km/h)
velocity = 27.8  # m/s
air_density = 1.2
air_flow = air_density * velocity * frontal_area
print(f"\nRam‑air flow: {air_flow:.2f} kg/s")

# Pressure drop estimate (micro‑channel, high fin density)
K = 150
delta_p = 0.5 * air_density * velocity**2 * K
print(f"Estimated pressure drop: {delta_p:.0f} Pa ({delta_p/1000:.2f} kPa)")
if delta_p > 1000:
    print("⚠️  High pressure drop – may need larger frontal area or lower fin density.")

# Packaging check
if depth <= 0.2:  # 200 mm depth reasonable?
    print("✅ Depth fits within front compartment.")
else:
    print("⚠️  Depth excessive; consider dual radiators or increased frontal area.")

# Recommendations
print("\n--- Recommendations ---")
print("1. Use micro‑channel aluminum radiator with U≈200 W/m²·K.")
print("2. Split into two cores (left/right) for packaging.")
print("3. Add electric fans for low‑speed cooling.")
print("4. CFD verification of airflow and pressure drop.")

print("\n✅ Condenser radiator sizing complete.")