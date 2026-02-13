#!/usr/bin/env python3
"""
Compressor selection for active refrigeration loop.
"""
print("=== ENGINE‑DRIVEN COMPRESSOR SELECTION ===")
print("Refrigeration load: 77.3 kW active cooling")
print("Required compressor power: ≈28 kW (COP ≈2.73)")

print("\nCandidate: York 210 (piston compressor)")
print("  Displacement: 210 cc/rev")
print("  Max speed: 3000 rpm")
print("  Max power: 30 kW")
print("  Dimensions: ≈300 x 200 x 250 mm")
print("  Weight: ≈20 kg")
print("  Drive: V‑belt, pulley ratio required (engine 12 k rpm → compressor ≤3000 rpm)")
print("  Cooling: oil‑cooled, integrated oil separator")

print("\nAlternative: Sanden 7H15 (rotary vane)")
print("  Displacement: 150 cc/rev")
print("  Max speed: 8000 rpm")
print("  Max power: 25 kW")
print("  Dimensions: smaller, lighter")
print("  May need two units in parallel.")

print("\nMounting:")
print("  - Engine front accessory drive")
print("  - Belt tensioner")
print("  - Dedicated pulley ratio ~1:4 (compressor slower)")
print("  - Vibration isolation mounts")

print("\nRefrigerant: R134a (standard)")
print("  Charge: ≈3 kg")
print("  Evaporator temperature: 0 °C")
print("  Condenser temperature: 60 °C")

print("\n✅ York 210 recommended for single‑unit solution.")