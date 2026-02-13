#!/usr/bin/env python3
"""
Cylinder head valve spring sizing for 12 k RPM (safety margin).
"""
import math

bore = 94.5  # mm
redline_rpm = 12000  # rpm with margin
print(f"Redline: {redline_rpm} rpm")

# Valve diameters (same as before)
intake_valve_dia = bore * 0.45
exhaust_valve_dia = bore * 0.38
print(f"Intake valve: {intake_valve_dia:.2f} mm")
print(f"Exhaust valve: {exhaust_valve_dia:.2f} mm")

# Valve lift (same ratio)
lift_intake = intake_valve_dia * 0.26
lift_exhaust = exhaust_valve_dia * 0.26
print(f"Valve lift:")
print(f"  Intake: {lift_intake:.2f} mm")
print(f"  Exhaust: {lift_exhaust:.2f} mm")

# Valve mass estimates (maybe slightly heavier for durability)
valve_mass_intake = 0.065  # kg (65 g)
valve_mass_exhaust = 0.055  # kg (55 g)

# Maximum valve acceleration (harmonic cam)
cam_accel_factor = (math.pi**2) / 2.0  # approx 4.93
max_valve_accel_intake = cam_accel_factor * (lift_intake/1000) * (redline_rpm/30)**2
max_valve_accel_exhaust = cam_accel_factor * (lift_exhaust/1000) * (redline_rpm/30)**2
print(f"\nValve acceleration at {redline_rpm} rpm:")
print(f"  Intake: {max_valve_accel_intake:.0f} m/s²")
print(f"  Exhaust: {max_valve_accel_exhaust:.0f} m/s²")

# Inertia force
force_intake = valve_mass_intake * max_valve_accel_intake
force_exhaust = valve_mass_exhaust * max_valve_accel_exhaust
print(f"  Inertia force:")
print(f"    Intake: {force_intake:.1f} N")
print(f"    Exhaust: {force_exhaust:.1f} N")

# Gas force (pressure differential across valve)
# Assume 0.6 bar (60 kPa) for safety
pressure_diff = 0.6e5  # Pa
gas_force_intake = pressure_diff * (math.pi * (intake_valve_dia/1000/2)**2)
gas_force_exhaust = pressure_diff * (math.pi * (exhaust_valve_dia/1000/2)**2)
print(f"  Gas force (0.6 bar diff):")
print(f"    Intake: {gas_force_intake:.1f} N")
print(f"    Exhaust: {gas_force_exhaust:.1f} N")

# Total required spring force at max lift (add 20% margin for safety)
margin = 1.20
total_force_intake = (force_intake + gas_force_intake) * margin
total_force_exhaust = (force_exhaust + gas_force_exhaust) * margin
print(f"\nRequired spring force at max lift (incl. {margin*100-100:.0f}% margin):")
print(f"  Intake: {total_force_intake:.1f} N")
print(f"  Exhaust: {total_force_exhaust:.1f} N")

# Spring rate (assuming spring preload at closed valve ~60% of max force)
spring_rate_intake = total_force_intake / (lift_intake/1000) * 0.4  # N/m
spring_rate_exhaust = total_force_exhaust / (lift_exhaust/1000) * 0.4
print(f"  Spring rate (approx):")
print(f"    Intake: {spring_rate_intake/1000:.1f} N/mm")
print(f"    Exhaust: {spring_rate_exhaust/1000:.1f} N/mm")

# Natural frequency of valve‑spring system
# Spring mass + valve mass; approximate natural frequency should be > 2× cam frequency
# Cam frequency = redline_rpm / 60 / 2 (since cam runs at half crank speed)
cam_freq = redline_rpm / 60 / 2  # Hz
print(f"\nCamshaft frequency at {redline_rpm} rpm: {cam_freq:.1f} Hz")
# Spring natural frequency fn = (1/(2π)) * sqrt(k/m)
# Assume spring mass ≈ 0.1 kg
spring_mass = 0.1  # kg
fn_intake = (1/(2*math.pi)) * math.sqrt(spring_rate_intake / (valve_mass_intake + spring_mass))
fn_exhaust = (1/(2*math.pi)) * math.sqrt(spring_rate_exhaust / (valve_mass_exhaust + spring_mass))
print(f"  Valve‑spring natural frequency:")
print(f"    Intake: {fn_intake:.1f} Hz")
print(f"    Exhaust: {fn_exhaust:.1f} Hz")
if fn_intake > 2 * cam_freq and fn_exhaust > 2 * cam_freq:
    print("  ✅ Natural frequency > 2× cam frequency (safe from resonance).")
else:
    print("  ⚠️  Natural frequency may be too low; consider stiffer springs.")

# Valve timing (optional: need more duration at 12 k RPM?)
print(f"\nValve timing suggestions:")
print(f"  Intake duration: 280–300° crank")
print(f"  Exhaust duration: 280–300° crank")
print(f"  Overlap: 50–70°")

print("\n✅ Valve spring sizing for 12 k RPM completed.")