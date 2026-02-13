#!/usr/bin/env python3
"""
Select reasonable spring stiffness with natural frequency >150 Hz.
"""
import math

redline_rpm = 12000
cam_freq = redline_rpm / 60 / 2
target_fn = 150.0  # Hz (1.5× cam frequency)
print(f"Cam frequency: {cam_freq:.1f} Hz")
print(f"Target natural frequency: {target_fn:.0f} Hz (1.5×)")

m_intake = 0.0375
m_exhaust = 0.0317
spring_mass = 0.1
m_eff_intake = m_intake + spring_mass
m_eff_exhaust = m_exhaust + spring_mass

k_intake = (2 * math.pi * target_fn)**2 * m_eff_intake
k_exhaust = (2 * math.pi * target_fn)**2 * m_eff_exhaust
print(f"\nSpring rate:")
print(f"  Intake: {k_intake/1000:.1f} N/mm")
print(f"  Exhaust: {k_exhaust/1000:.1f} N/mm")

lift_intake = 0.01106
lift_exhaust = 0.00934
max_force_intake = k_intake * lift_intake / 0.4
max_force_exhaust = k_exhaust * lift_exhaust / 0.4
print(f"\nMax spring force at max lift:")
print(f"  Intake: {max_force_intake:.1f} N")
print(f"  Exhaust: {max_force_exhaust:.1f} N")

required_intake = 495.1
required_exhaust = 353.6
if max_force_intake > required_intake and max_force_exhaust > required_exhaust:
    print("✅ Forces exceed required.")
else:
    print("⚠️  Forces insufficient.")

# Check actual natural frequency with these springs (including valve mass only)
fn_intake = (1/(2*math.pi)) * math.sqrt(k_intake / (m_intake + spring_mass))
fn_exhaust = (1/(2*math.pi)) * math.sqrt(k_exhaust / (m_exhaust + spring_mass))
print(f"\nActual natural frequency (valve+spring mass):")
print(f"  Intake: {fn_intake:.1f} Hz")
print(f"  Exhaust: {fn_exhaust:.1f} Hz")
print(f"  Ratio to cam frequency: {fn_intake/cam_freq:.2f}×, {fn_exhaust/cam_freq:.2f}×")

# Spring wire estimate
G = 79e9
D = 0.025
Na = 6
d_intake = (k_intake * 8 * D**3 * Na / G)**0.25
d_exhaust = (k_exhaust * 8 * D**3 * Na / G)**0.25
print(f"\nWire diameter (D={D*1000:.0f} mm, Na={Na}):")
print(f"  Intake: {d_intake*1000:.2f} mm")
print(f"  Exhaust: {d_exhaust*1000:.2f} mm")

print("\n✅ Reasonable spring selection.")