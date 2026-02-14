#!/usr/bin/env python3
import numpy as np
import math

# Parameters
r = 23.75  # crank radius mm
L = 150.0  # conrod length mm
compression_height = 38.0  # pin center to crown
top_ring_below_crown = 5.0  # mm
bottom_ring_below_crown = 20.0  # mm
deck_clearance = 0.8  # mm
crankcase_bottom_z = -50.9  # mm (from simulation)

# Piston pin Z relative to crank center
def piston_pin_z(theta):
    """Theta in radians, 0 = TDC? Actually at theta=0 crank pin is at top? Assume crank pin vertical offset."""
    # Crank pin position relative to crank center: (0, -r) at theta=0? Let's use standard formula:
    # x = r*cos(theta), y = r*sin(theta) if crank pin rotates around center.
    # Vertical component (Z) = r*cos(theta) if Z is vertical axis.
    # Then piston pin Z = Z_crank + sqrt(L^2 - (r*sin(theta))**2)
    # We'll use same as kinematic simulation.
    crank_z = r * np.cos(theta)
    conrod_horizontal = r * np.sin(theta)
    conrod_vertical = np.sqrt(L**2 - conrod_horizontal**2)
    return crank_z + conrod_vertical

# Sample over full cycle
angles = np.linspace(0, 2*np.pi, 361)
pin_z = piston_pin_z(angles)

# Crown Z (top of piston)
crown_z = pin_z + compression_height

# Ring positions
top_ring_z = crown_z - top_ring_below_crown
bottom_ring_z = crown_z - bottom_ring_below_crown

# Extremes
pin_min, pin_max = np.min(pin_z), np.max(pin_z)
crown_min, crown_max = np.min(crown_z), np.max(crown_z)
top_ring_min, top_ring_max = np.min(top_ring_z), np.max(top_ring_z)
bottom_ring_min, bottom_ring_max = np.min(bottom_ring_z), np.max(bottom_ring_z)

print("=== Piston Kinematic Extremes ===")
print(f"Piston pin Z range: {pin_min:.2f} to {pin_max:.2f} mm (Δ {pin_max-pin_min:.2f} mm)")
print(f"Crown Z range: {crown_min:.2f} to {crown_max:.2f} mm")
print(f"Top ring Z range: {top_ring_min:.2f} to {top_ring_max:.2f} mm")
print(f"Bottom ring Z range: {bottom_ring_min:.2f} to {bottom_ring_max:.2f} mm")

# Deck surface (block top) = crown at TDC + deck clearance
# Find TDC angle (theta where crown is max)
tdc_idx = np.argmax(crown_z)
deck_surface_z = crown_z[tdc_idx] + deck_clearance
print(f"\nDeck surface Z (block top): {deck_surface_z:.2f} mm")

# Cylinder liner must contain ring travel plus margins
top_margin = 5.0  # mm above top ring at TDC
bottom_margin = 10.0  # mm below bottom ring at BDC
liner_top = top_ring_max + top_margin
liner_bottom = bottom_ring_min - bottom_margin
liner_length = liner_top - liner_bottom

print(f"\n=== Cylinder Liner Dimensions ===")
print(f"Liner top Z: {liner_top:.2f} mm (above crank center)")
print(f"Liner bottom Z: {liner_bottom:.2f} mm")
print(f"Liner length: {liner_length:.2f} mm")
print(f"Liner top relative to deck: {deck_surface_z - liner_top:.2f} mm (should be positive)")

# Check if liner fits within block
block_height = deck_surface_z - crankcase_bottom_z
print(f"\nBlock height (deck to crankcase bottom): {block_height:.2f} mm")
if liner_bottom > crankcase_bottom_z:
    print(f"✅ Liner bottom above crankcase bottom (clearance {liner_bottom - crankcase_bottom_z:.2f} mm)")
else:
    print(f"❌ Liner bottom below crankcase bottom – interference!")

# Ring belt travel within liner
ring_travel_top = top_ring_max - liner_top
ring_travel_bottom = liner_bottom - bottom_ring_min
print(f"\nRing travel margins:")
print(f"  Top ring to liner top: {ring_travel_top:.2f} mm (should be >= 0)")
print(f"  Bottom ring to liner bottom: {ring_travel_bottom:.2f} mm (should be >= 0)")

# Save results
import json, os
results = {
    "liner_top_z": float(liner_top),
    "liner_bottom_z": float(liner_bottom),
    "liner_length": float(liner_length),
    "deck_surface_z": float(deck_surface_z),
    "ring_travel_margins": {
        "top": float(ring_travel_top),
        "bottom": float(ring_travel_bottom)
    }
}
os.makedirs("liner_design", exist_ok=True)
with open("liner_design/liner_dimensions.json", "w") as f:
    json.dump(results, f, indent=2)
print("\n✅ Results saved to liner_design/liner_dimensions.json")