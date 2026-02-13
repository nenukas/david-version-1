#!/usr/bin/env python3
"""
Cylinder head design for V12 8.0 L engine (bore 94.5 mm, stroke 94.5 mm).
DOCH 4‑valve per cylinder, pent‑roof combustion chamber.
"""
import math

bore = 94.5  # mm
stroke = 94.5
redline_rpm = 11000

print("=== CYLINDER HEAD DESIGN PARAMETERS ===")
print(f"Bore: {bore} mm")
print(f"Stroke: {stroke} mm")
print(f"Redline: {redline_rpm} rpm")

# Valve sizing (typical high‑performance 4‑valve)
intake_valve_dia = bore * 0.45
exhaust_valve_dia = bore * 0.38
print(f"\nValve diameters:")
print(f"  Intake: {intake_valve_dia:.2f} mm")
print(f"  Exhaust: {exhaust_valve_dia:.2f} mm")

# Valve area per cylinder (two intakes, two exhausts)
area_intake = 2 * math.pi * (intake_valve_dia/2)**2
area_exhaust = 2 * math.pi * (exhaust_valve_dia/2)**2
area_total = area_intake + area_exhaust
area_bore = math.pi * (bore/2)**2
area_ratio = area_total / area_bore * 100
print(f"  Total valve area: {area_total:.1f} mm²")
print(f"  Bore area: {area_bore:.1f} mm²")
print(f"  Valve/bore area ratio: {area_ratio:.1f} %")

# Valve lift (typical lift = 0.25–0.28 of valve diameter)
lift_intake = intake_valve_dia * 0.26
lift_exhaust = exhaust_valve_dia * 0.26
print(f"\nValve lift:")
print(f"  Intake: {lift_intake:.2f} mm")
print(f"  Exhaust: {lift_exhaust:.2f} mm")

# Valve timing (estimated)
# For 11 k RPM, duration needed ~280–300° crank
intake_open = 30  # °BTDC
intake_close = 70  # °ABDC
exhaust_open = 70  # °BBDC
exhaust_close = 30  # °ATDC
overlap = intake_open + exhaust_close
print(f"\nValve timing (crank degrees):")
print(f"  IVO: {intake_open} °BTDC, IVC: {intake_close} °ABDC")
print(f"  EVO: {exhaust_open} °BBDC, EVC: {exhaust_close} °ATDC")
print(f"  Overlap: {overlap} °")

# Camshaft parameters
cam_lift_intake = lift_intake  # direct acting? assume 1:1 rocker ratio
cam_lift_exhaust = lift_exhaust
print(f"\nCamshaft lift (1:1 rocker):")
print(f"  Intake cam lift: {cam_lift_intake:.2f} mm")
print(f"  Exhaust cam lift: {cam_lift_exhaust:.2f} mm")

# Valve spring forces
# Required spring force at max lift to avoid float at 11 k RPM
# Valve mass estimate (intake: ~60 g, exhaust: ~50 g)
valve_mass_intake = 0.060  # kg
valve_mass_exhaust = 0.050  # kg
# Maximum valve acceleration from cam profile (simplified)
# For harmonic cam, max acceleration ~ (π²/2) * (lift/2) * (rpm/30)²
cam_accel_factor = (math.pi**2) / 2.0  # approx 4.93
max_valve_accel_intake = cam_accel_factor * (lift_intake/1000) * (redline_rpm/30)**2
max_valve_accel_exhaust = cam_accel_factor * (lift_exhaust/1000) * (redline_rpm/30)**2
print(f"\nValve dynamics at {redline_rpm} rpm:")
print(f"  Max valve acceleration (approx):")
print(f"    Intake: {max_valve_accel_intake:.0f} m/s²")
print(f"    Exhaust: {max_valve_accel_exhaust:.0f} m/s²")
# Force needed to overcome acceleration
force_intake = valve_mass_intake * max_valve_accel_intake
force_exhaust = valve_mass_exhaust * max_valve_accel_exhaust
print(f"  Inertia force at max acceleration:")
print(f"    Intake: {force_intake:.1f} N")
print(f"    Exhaust: {force_exhaust:.1f} N")
# Spring force at max lift must exceed inertia force + gas force
# Gas force (pressure differential) ~0.5 bar across valve area ≈ 0.5e5 Pa
pressure_diff = 0.5e5  # Pa
gas_force_intake = pressure_diff * (math.pi * (intake_valve_dia/1000/2)**2)
gas_force_exhaust = pressure_diff * (math.pi * (exhaust_valve_dia/1000/2)**2)
print(f"  Gas force (0.5 bar diff):")
print(f"    Intake: {gas_force_intake:.1f} N")
print(f"    Exhaust: {gas_force_exhaust:.1f} N")
total_force_intake = force_intake + gas_force_intake
total_force_exhaust = force_exhaust + gas_force_exhaust
print(f"  Total required spring force at max lift:")
print(f"    Intake: {total_force_intake:.1f} N")
print(f"    Exhaust: {total_force_exhaust:.1f} N")
# Spring rate (assuming spring preload at closed valve ~60% of max force)
spring_rate_intake = total_force_intake / (lift_intake/1000) * 0.4  # N/m
spring_rate_exhaust = total_force_exhaust / (lift_exhaust/1000) * 0.4
print(f"  Spring rate (approx):")
print(f"    Intake: {spring_rate_intake/1000:.1f} N/mm")
print(f"    Exhaust: {spring_rate_exhaust/1000:.1f} N/mm")

# Combustion chamber design (pent‑roof)
# Chamber volume to achieve compression ratio ~9.5:1 (with forced induction)
swept_volume = math.pi * (bore/2)**2 * stroke  # mm³
compression_ratio = 9.5
clearance_volume = swept_volume / (compression_ratio - 1)
print(f"\nCombustion chamber:")
print(f"  Swept volume: {swept_volume/1000:.1f} cm³")
print(f"  Clearance volume (CR={compression_ratio}): {clearance_volume/1000:.1f} cm³")
# Chamber volume includes piston dish, head chamber, deck clearance, gasket.
# Assume piston dish volume = 0, deck clearance height = 0.8 mm
deck_clearance = 0.8  # mm
deck_volume = math.pi * (bore/2)**2 * deck_clearance
head_chamber_volume = clearance_volume - deck_volume
print(f"  Deck clearance volume: {deck_volume/1000:.1f} cm³")
print(f"  Head chamber volume: {head_chamber_volume/1000:.1f} cm³")

# Port dimensions
# Intake port diameter ~0.85 * intake valve diameter
intake_port_dia = intake_valve_dia * 0.85
exhaust_port_dia = exhaust_valve_dia * 0.85
print(f"\nPort diameters:")
print(f"  Intake port: {intake_port_dia:.2f} mm")
print(f"  Exhaust port: {exhaust_port_dia:.2f} mm")

# Material: aluminum A356‑T6
print(f"\nMaterial: A356‑T6 aluminum (sand cast + T6 heat treat)")
print(f"  Ultimate tensile strength: ~310 MPa")
print(f"  Yield strength: ~250 MPa")

print("\n✅ Cylinder head parameters defined.")

# Next step: generate CAD geometry (optional)
print("\nTo generate CAD geometry, run a separate script.")