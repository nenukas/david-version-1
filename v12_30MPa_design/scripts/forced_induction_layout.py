#!/usr/bin/env python3
"""
Generate simplified forced‑induction layout for V12 mid‑engine packaging.
Uses placeholder geometries for turbos, supercharger, intercoolers, bus compressor.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import cadquery as cq
import math

# Load engine block (simplified placeholder)
# We'll create a simple block because the actual STEP may be heavy.
print("Creating placeholder engine block...")
# Dimensions from earlier: bore spacing 144.7 mm, deck thickness 12 mm, stroke 94.5 mm, skirt depth 60 mm
bore_spacing = 144.707
deck_thickness = 12.0
stroke = 94.5
skirt_depth = 60.137
block_length = bore_spacing * 6  # 6 cylinders per bank
bank_offset = bore_spacing * math.sin(math.radians(30))  # 60° bank angle
block_width = bank_offset * 2 + 100  # approx
block_height = deck_thickness + stroke/2 + skirt_depth

block = cq.Workplane("XY").box(block_length, block_width, block_height)
# Add cylinder holes (simplified)
bore_radius = 94.5 / 2
for i in range(6):
    x = (i - 2.5) * bore_spacing
    y = -bank_offset
    block = block.faces(">Z").workplane().center(x, y).circle(bore_radius).cutThruAll()
    y = bank_offset
    block = block.faces(">Z").workplane().center(x, y).circle(bore_radius).cutThruAll()

print(f"Block dimensions: {block_length:.0f} x {block_width:.0f} x {block_height:.0f} mm")

# Turbo placeholder (cylinder + cone)
def make_turbo():
    base = cq.Workplane("YZ").circle(55).extrude(90)  # compressor housing
    turbine = cq.Workplane("YZ").circle(65).extrude(-70)  # turbine side
    center = cq.Workplane("YZ").circle(40).extrude(10)
    turbo = base.union(turbine).union(center)
    # Rotate so axis along X (engine length)
    turbo = turbo.rotateAboutCenter((0,1,0), 90)
    return turbo

print("Adding turbos...")
turbo_left = make_turbo().translate((-block_length/2 + 100, -bank_offset - 150, -block_height/2 + 80))
turbo_right = make_turbo().translate((-block_length/2 + 100, bank_offset + 150, -block_height/2 + 80))

# Supercharger placeholder (cylindrical)
supercharger = cq.Workplane("XZ").circle(75).extrude(250)
supercharger = supercharger.rotateAboutCenter((0,0,1), 90).rotateAboutCenter((0,1,0), 90)
supercharger = supercharger.translate((block_length/2 + 150, 0, 50))

# Intercooler placeholder (rectangular)
def make_intercooler():
    return cq.Workplane("XY").box(300, 200, 80)

intercooler1 = make_intercooler().translate((-block_length/2 - 200, -bank_offset - 300, 100))
intercooler2 = make_intercooler().translate((-block_length/2 - 200, bank_offset + 300, 100))

# Bus compressor placeholder (box)
compressor = cq.Workplane("XY").box(200, 150, 150).translate((block_length/2 + 100, 0, -block_height/2 - 100))

# Radiator placeholder (flat)
radiator = cq.Workplane("XY").box(500, 400, 50).translate((block_length/2 + 400, 0, 0))

# Combine all
assembly = block.union(turbo_left).union(turbo_right).union(supercharger)
assembly = assembly.union(intercooler1).union(intercooler2).union(compressor).union(radiator)

# Add simple exhaust headers (pipes)
def pipe(radius, length):
    return cq.Workplane("YZ").circle(radius).extrude(length)

header_left = pipe(30, 300).translate((-block_length/2 + 50, -bank_offset - 120, -block_height/2 + 120))
header_right = pipe(30, 300).translate((-block_length/2 + 50, bank_offset + 120, -block_height/2 + 120))
assembly = assembly.union(header_left).union(header_right)

# Add intake piping (simplified)
intake_pipe = pipe(40, 400).rotateAboutCenter((0,1,0), 90).translate((block_length/2 + 300, 0, 100))
assembly = assembly.union(intake_pipe)

# Export
output_step = "v12_forced_induction_layout.step"
cq.exporters.export(assembly, output_step, "STEP")
print(f"✅ Layout exported to {output_step}")

# Also export STL for viewing
output_stl = "v12_forced_induction_layout.stl"
cq.exporters.export(assembly, output_stl, "STL")
print(f"✅ STL exported to {output_stl}")

print("\nComponent positions (approx):")
print(f"  Block: center (0,0,0)")
print(f"  Turbos: left side Y≈{-bank_offset - 150:.0f} mm, right side Y≈{bank_offset + 150:.0f} mm")
print(f"  Supercharger: front X≈{block_length/2 + 150:.0f} mm")
print(f"  Intercoolers: side Y≈±{bank_offset + 300:.0f} mm")
print(f"  Bus compressor: front‑low X≈{block_length/2 + 100:.0f} mm")
print(f"  Radiator: front X≈{block_length/2 + 400:.0f} mm")
print(f"  Total length: ~{block_length + 800:.0f} mm")
print(f"  Total width: ~{block_width + 600:.0f} mm")
print(f"  Total height: ~{block_height + 300:.0f} mm")
print("\nNote: This is a simplified placeholder layout for packaging study.")