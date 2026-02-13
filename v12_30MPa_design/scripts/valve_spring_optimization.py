#!/usr/bin/env python3
"""
Optimize valve spring stiffness to achieve natural frequency >200 Hz (2× cam frequency).
"""
import math

# Parameters
redline_rpm = 12000
cam_freq = redline_rpm / 60 / 2  # Hz
target_fn = 2.0 * cam_freq  # >200 Hz
print(f"Cam frequency: {cam_freq:.1f} Hz")
print(f"Target natural frequency: {target_fn:.0f} Hz")

# Titanium valve masses (kg)
m_intake = 0.0375
m_exhaust = 0.0317
spring_mass = 0.1  # kg (approx)
m_eff_intake = m_intake + spring_mass
m_eff_exhaust = m_exhaust + spring_mass

# Required spring rate k = (2π·fn)² * m_eff
k_intake = (2 * math.pi * target_fn)**2 * m_eff_intake
k_exhaust = (2 * math.pi * target_fn)**2 * m_eff_exhaust
print(f"\nRequired spring rate for fn={target_fn:.0f} Hz:")
print(f"  Intake: {k_intake/1000:.1f} N/mm")
print(f"  Exhaust: {k_exhaust/1000:.1f} N/mm")

# Check spring force at max lift (lift from earlier: 11.06 mm, 9.34 mm)
lift_intake = 0.01106  # m
lift_exhaust = 0.00934
# Preload at closed valve: assume preload = 0.6 * max force
# Max force = k * lift / 0.4 (since spring rate formula earlier used factor 0.4)
max_force_intake = k_intake * lift_intake / 0.4
max_force_exhaust = k_exhaust * lift_exhaust / 0.4
print(f"\nMax spring force at max lift:")
print(f"  Intake: {max_force_intake:.1f} N")
print(f"  Exhaust: {max_force_exhaust:.1f} N")

# Compare with required force (from titanium_valves.py)
required_intake = 495.1  # N
required_exhaust = 353.6  # N
print(f"Required force (from earlier): {required_intake:.1f} N intake, {required_exhaust:.1f} N exhaust")
if max_force_intake > required_intake and max_force_exhaust > required_exhaust:
    print("✅ Spring forces exceed required (safe).")
else:
    print("⚠️  Spring forces insufficient; need higher rate or lower target fn.")

# Spring wire diameter estimate (simplified)
# Use formula for helical compression spring: k = G * d^4 / (8 * D^3 * Na)
# G = 79 GPa (steel), assume mean coil diameter D = 0.025 m, active coils Na = 6
G = 79e9
D = 0.025
Na = 6
d_intake = (k_intake * 8 * D**3 * Na / G)**0.25
d_exhaust = (k_exhaust * 8 * D**3 * Na / G)**0.25
print(f"\nEstimated spring wire diameter (D={D*1000:.0f} mm, Na={Na}):")
print(f"  Intake: {d_intake*1000:.2f} mm")
print(f"  Exhaust: {d_exhaust*1000:.2f} mm")

# Spring solid length (approx)
solid_length_intake = Na * d_intake
solid_length_exhaust = Na * d_exhaust
print(f"  Solid length: {solid_length_intake*1000:.1f} mm intake, {solid_length_exhaust*1000:.1f} mm exhaust")

print("\n✅ Valve spring optimization complete.")