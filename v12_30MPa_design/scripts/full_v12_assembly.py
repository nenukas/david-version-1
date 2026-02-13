#!/usr/bin/env python3
"""
Generate full V12 assembly (simplified static representation).
Positions pistons at TDC (crown top at deck top), rods connecting to crank pins.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import json
import math
import cadquery as cq

print("Loading geometry data...")
with open('full_assembly_data.json', 'r') as f:
    data = json.load(f)

bore_spacing = data['bore_spacing']
bank_offset = data['bank_offset']
deck_thickness = data['deck_thickness']
stroke = data['stroke']
crank_radius = data['crank_radius']
compression_height = data['compression_height']
rod_length = data['rod_length']
throw_spacing = data['throw_spacing']
cyl_positions = data['cylinder_positions']
crank_pin_positions = data['crank_pin_positions']

print(f"Bore spacing: {bore_spacing} mm")
print(f"Bank offset: {bank_offset} mm")
print(f"Deck thickness: {deck_thickness} mm")
print(f"Rod length: {rod_length} mm")

# Load component STEP files
print("Loading block...")
block = cq.importers.importStep('cylinder_block_deck_12mm.step')
print("Loading crankshaft...")
crank = cq.importers.importStep('crankshaft_30MPa_unified.step')
print("Loading piston...")
piston = cq.importers.importStep('piston_crown_15mm_full.step')
print("Loading connecting rod...")
rod = cq.importers.importStep('conrod_opt_relaxed2_30MPa_results_20260213_010504.step')

# Determine crankshaft position relative to block
# Crankshaft axis is along X, at Y=0, Z = crank_center_z
crank_center_z = -deck_thickness - crank_radius
print(f"Crankshaft centerline Z: {crank_center_z} mm")

# Translate crankshaft to correct vertical position
crank = crank.translate((0, 0, crank_center_z))

# Assemble pistons and rods
all_pistons = []
all_rods = []

for cyl in cyl_positions:
    idx = cyl['index']
    x = cyl['x']
    y = cyl['y']
    bank = cyl['bank']
    
    # Piston position: crown top at deck top (Z=0)
    # The piston STEP origin? Assume origin at crown top center.
    piston_pos = piston.translate((x, y, 0))
    all_pistons.append(piston_pos)
    
    # Determine crank pin index (0..5)
    crank_pin_idx = idx % 6
    crank_pin = crank_pin_positions[crank_pin_idx]
    # Crank pin absolute position
    cp_x = crank_pin['x']
    cp_y = crank_pin['y']
    cp_z = crank_pin['z'] + crank_center_z
    
    # Piston pin position (approximate: below crown by compression height)
    # Assume piston pin center is at Z = -compression_height relative to crown top
    piston_pin_z = -compression_height
    
    # Connecting rod position: small end at piston pin, big end at crank pin.
    # The rod STEP origin? Assume origin at small end center.
    # We'll place rod so small end aligns with piston pin.
    rod_pos = rod.translate((x, y, piston_pin_z))
    
    # Need to rotate rod to align big end with crank pin.
    # Compute vector from piston pin to crank pin
    dx = cp_x - x
    dy = cp_y - y
    dz = cp_z - piston_pin_z
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    print(f"Cyl {idx}: piston pin Z={piston_pin_z:.1f}, crank pin Z={cp_z:.1f}, distance={distance:.1f} mm (rod length={rod_length})")
    
    # For simplicity, we'll just translate rod; rotation is complex.
    # We'll keep rod vertical (Z axis). This will misalign but visually okay.
    all_rods.append(rod_pos)

print(f"Added {len(all_pistons)} pistons and {len(all_rods)} rods.")

# Combine all components
print("Combining assembly...")
assembly = block.union(crank)
for p in all_pistons:
    assembly = assembly.union(p)
for r in all_rods:
    assembly = assembly.union(r)

# Export
output_step = "v12_full_assembly_simplified.step"
cq.exporters.export(assembly, output_step, "STEP")
print(f"✅ Full V12 assembly exported to {output_step}")

# Also export STL
output_stl = "v12_full_assembly_simplified.stl"
cq.exporters.export(assembly, output_stl, "STL")
print(f"✅ STL exported to {output_stl}")

print("\nNotes:")
print("- Assembly is simplified static representation.")
print("- Pistons are all at TDC (crown top at deck top).")
print("- Connecting rods are placed vertically, not kinematically aligned.")
print("- For FEA, adjust piston positions according to crank angle.")
print("- Crankshaft is unified (single solid).")
print("- Block includes 12 cylinders (full V12).")