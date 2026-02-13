#!/usr/bin/env python3
"""
Extract geometry data for full V12 assembly.
"""
import json
import math

# Load block geometry
with open('cylinder_block_30MPa_7075_T6_updated.json', 'r') as f:
    block_data = json.load(f)
block_geo = block_data['geometry']
bore_spacing = block_geo['bore_spacing']
deck_thickness = block_geo['deck_thickness']
stroke = 94.5  # mm (engine stroke)
crank_radius = stroke / 2.0  # 47.25 mm
bank_angle = 60.0  # degrees
bank_offset = bore_spacing * math.sin(math.radians(bank_angle / 2.0))

# Load piston geometry
with open('fea_thermal/piston_crown_15.0mm.json', 'r') as f:
    piston_data = json.load(f)
piston_geo = piston_data['geometry']
compression_height = 38.0  # mm (fixed)
crown_thickness = piston_geo['crown_thickness']

# Load conrod geometry
with open('conrod_opt_relaxed2_30MPa_results_20260213_010504.json', 'r') as f:
    conrod_data = json.load(f)
conrod_geo = conrod_data['geometry']
rod_length = 150.0  # mm (center_length)

# Load crankshaft geometry (from final JSON)
with open('crankshaft_30MPa_final.json', 'r') as f:
    crank_data = json.load(f)
crank_geo = crank_data['geometry']
main_journal_width = crank_geo['main_journal_width']
pin_width = crank_geo['pin_width']
throw_spacing = main_journal_width + pin_width + 10.0  # from CAD script

print("=== V12 Engine Geometry ===")
print(f"Bore spacing: {bore_spacing:.3f} mm")
print(f"Bank offset: {bank_offset:.3f} mm")
print(f"Deck thickness: {deck_thickness:.3f} mm")
print(f"Engine stroke: {stroke:.1f} mm (crank radius = {crank_radius:.2f} mm)")
print(f"Piston compression height: {compression_height:.1f} mm")
print(f"Connecting rod length: {rod_length:.1f} mm")
print(f"Crankshaft throw spacing: {throw_spacing:.2f} mm")
print(f"Number of cylinders: 12 (6 per bank)")
print(f"Bank angle: {bank_angle}°")

# Cylinder positions (center of bore)
# Index 0–5 left bank, 6–11 right bank
cyl_positions = []
for i in range(12):
    bank = 0 if i < 6 else 1
    bank_sign = -1 if bank == 0 else 1
    idx_in_bank = i % 6
    # X along engine length, centered around origin
    x = (idx_in_bank - 2.5) * bore_spacing
    y = bank_sign * bank_offset
    z = 0  # deck top
    cyl_positions.append({
        'index': i,
        'bank': 'left' if bank == 0 else 'right',
        'x': x,
        'y': y,
        'z': z,
    })

print("\nCylinder bore centers (mm):")
for cyl in cyl_positions:
    print(f"  Cyl {cyl['index']:2d} ({cyl['bank']}): X={cyl['x']:7.2f}, Y={cyl['y']:7.2f}")

# Crank pin positions (relative to crankshaft origin)
# Crankshaft origin at first main journal centerline.
# Assume crankshaft axis along X, at Y=0, Z = crank_center_z (below deck).
crank_center_z = -deck_thickness - crank_radius  # approximate
print(f"\nCrankshaft centerline Z: {crank_center_z:.2f} mm")

crank_pin_positions = []
for i in range(6):  # 6 throws
    x = i * throw_spacing
    # Pin offset in Y direction (stroke) relative to crankshaft axis
    y_offset = crank_radius  # at TDC, pin is at topmost in Y? Actually pin rotates in Y‑Z plane.
    # For simplicity, assume pin at Y = stroke, Z = 0 relative to crankshaft axis.
    y = crank_radius
    z = 0
    crank_pin_positions.append({
        'index': i,
        'x': x,
        'y': y,
        'z': z,
    })
    print(f"  Crank pin {i}: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")

print("\nNote: This is a simplified static representation. Kinematic positions require crank angle.")

# Save data to JSON
data = {
    'bore_spacing': bore_spacing,
    'bank_offset': bank_offset,
    'deck_thickness': deck_thickness,
    'stroke': stroke,
    'crank_radius': crank_radius,
    'compression_height': compression_height,
    'rod_length': rod_length,
    'throw_spacing': throw_spacing,
    'cylinder_positions': cyl_positions,
    'crank_pin_positions': crank_pin_positions,
}
with open('full_assembly_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("✅ Data saved to full_assembly_data.json")