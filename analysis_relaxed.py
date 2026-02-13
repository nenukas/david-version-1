#!/usr/bin/env python3
"""
Compute minimum dimensions to satisfy relaxed constraints.
"""
import math

# Parameters
BORE_DIAMETER = 94.5          # mm
PIN_DIAMETER = 28.0           # mm
PEAK_PRESSURE_MPA = 25.0      # MPa
PEAK_FORCE_N = 180000.0       # N
TENSILE_FORCE_N = 83000.0     # N
YIELD_STRENGTH = 310.0        # MPa
CROWN_FACTOR = 0.8            # 0.8×yield
BEARING_LIMIT = 80.0          # MPa

# Crown bending stress formula: sigma = (3 * p * r^2) / (4 * t^2)
r = BORE_DIAMETER / 2
# Required crown thickness for sigma < YIELD*CROWN_FACTOR
required_crown_thickness = math.sqrt((3 * PEAK_PRESSURE_MPA * r**2) / (4 * YIELD_STRENGTH * CROWN_FACTOR))
print(f"Minimum crown thickness for sigma < {YIELD_STRENGTH*CROWN_FACTOR:.1f} MPa: {required_crown_thickness:.2f} mm")

# Pin bearing pressure: sigma = F / (2 * pin_diameter * pin_boss_width)
# Compression force is larger
required_pin_boss_width_comp = PEAK_FORCE_N / (2 * PIN_DIAMETER * BEARING_LIMIT)
required_pin_boss_width_tens = TENSILE_FORCE_N / (2 * PIN_DIAMETER * BEARING_LIMIT)
required_pin_boss_width = max(required_pin_boss_width_comp, required_pin_boss_width_tens)
print(f"Minimum pin boss width for bearing pressure < {BEARING_LIMIT} MPa:")
print(f"  Compression ({PEAK_FORCE_N/1000:.1f} kN): {required_pin_boss_width_comp:.2f} mm")
print(f"  Tension ({TENSILE_FORCE_N/1000:.1f} kN): {required_pin_boss_width_tens:.2f} mm")
print(f"  Overall minimum: {required_pin_boss_width:.2f} mm")

# Compare with bounds
bounds_crown = (8.0, 20.0)
bounds_pin = (10.0, 25.0)
print(f"\nBounds: crown thickness {bounds_crown}, pin boss width {bounds_pin}")
print(f"Crown thickness feasible? {required_crown_thickness <= bounds_crown[1]}")
print(f"Pin boss width feasible? {required_pin_boss_width <= bounds_pin[1]}")

# If both feasible, there is a feasible region.
if required_crown_thickness <= bounds_crown[1] and required_pin_boss_width <= bounds_pin[1]:
    print("Feasible region exists within bounds.")
else:
    print("Feasible region does NOT exist within bounds.")
    # Compute needed expansion
    if required_crown_thickness > bounds_crown[1]:
        print(f"Crown thickness upper bound must be at least {required_crown_thickness:.2f} mm (currently {bounds_crown[1]}).")
    if required_pin_boss_width > bounds_pin[1]:
        print(f"Pin boss width upper bound must be at least {required_pin_boss_width:.2f} mm (currently {bounds_pin[1]}).")

# Check mass constraint (500g) - not likely limiting
print("\nMass constraint <500 g likely satisfied.")