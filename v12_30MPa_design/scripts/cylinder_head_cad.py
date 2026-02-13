#!/usr/bin/env python3
"""
Generate a simplified cylinder head CAD for one cylinder.
Placeholder geometry with combustion chamber, valve seats, ports.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import cadquery as cq
import math

# Parameters from cylinder_head_design.py
bore = 94.5
intake_valve_dia = 42.52
exhaust_valve_dia = 35.91
intake_port_dia = 36.15
exhaust_port_dia = 30.52
head_chamber_volume = 72400  # mm³ (from earlier)
deck_clearance = 0.8
deck_thickness = 12.0  # block deck thickness

# Head overall dimensions
head_width = 120  # mm (per cylinder)
head_length = 150  # mm
head_height = 40   # mm (excluding combustion chamber)

print("Creating cylinder head...")
# Start with a block
head = cq.Workplane("XY").box(head_length, head_width, head_height)
# Move top to Z=0 (combustion side up)
head = head.translate((0,0,-head_height/2))

# Combustion chamber (pent‑roof shape approximated as a slanted box)
# Create a recess in the bottom face
chamber_depth = 10  # mm (depth of pent‑roof)
# Cut a rectangular recess with angled sides
# We'll do a simple extrusion cut with draft
chamber_length = bore * 0.8
chamber_width = bore * 0.9
chamber = cq.Workplane("XY").workplane(offset=-head_height/2).center(0,0)
chamber = chamber.rect(chamber_length, chamber_width).extrude(chamber_depth, taper=-15)  # negative taper for draft
head = head.cut(chamber)

# Valve seats (cylindrical holes)
# Valve positions: intake on one side, exhaust on other, spaced ~0.8*bore center‑to‑center
valve_spacing = bore * 0.8
intake_x = -valve_spacing/2
exhaust_x = valve_spacing/2
valve_y = 0  # centered in cylinder
# Valve seat depth ~8 mm
seat_depth = 8
seat_dia_intake = intake_valve_dia * 1.1
seat_dia_exhaust = exhaust_valve_dia * 1.1
head = head.faces("<Z").workplane().center(intake_x, valve_y).circle(seat_dia_intake/2).cutBlind(-seat_depth)
head = head.faces("<Z").workplane().center(exhaust_x, valve_y).circle(seat_dia_exhaust/2).cutBlind(-seat_depth)

# Valve guide holes (smaller holes through seat)
guide_dia = 8.0
guide_length = 30
head = head.faces("<Z").workplane().center(intake_x, valve_y).circle(guide_dia/2).cutBlind(-guide_length)
head = head.faces("<Z").workplane().center(exhaust_x, valve_y).circle(guide_dia/2).cutBlind(-guide_length)

# Ports (tubes from valve seats to side of head)
port_length = 60
# Intake port (curved outward) – simplified as straight tube
intake_port = cq.Workplane("XZ").workplane(offset=valve_y).center(intake_x, -head_height/2 - seat_depth)
intake_port = intake_port.circle(intake_port_dia/2).extrude(port_length)
# Rotate port upward
intake_port = intake_port.rotateAboutCenter((1,0,0), -30)  # 30° upward
head = head.union(intake_port)

# Exhaust port (curved downward)
exhaust_port = cq.Workplane("XZ").workplane(offset=valve_y).center(exhaust_x, -head_height/2 - seat_depth)
exhaust_port = exhaust_port.circle(exhaust_port_dia/2).extrude(port_length)
exhaust_port = exhaust_port.rotateAboutCenter((1,0,0), 30)  # 30° downward
head = head.union(exhaust_port)

# Camshaft bores (two camshafts per bank)
cam_bore_dia = 30
cam_spacing = 80
cam1_y = -cam_spacing/2
cam2_y = cam_spacing/2
head = head.faces(">Y").workplane().center(0,0).circle(cam_bore_dia/2).cutThruAll()

# Add some ribs for stiffness
rib_width = 5
rib_height = 20
rib = cq.Workplane("XY").box(head_length-20, rib_width, rib_height)
rib = rib.translate((0,0,-head_height/2 + rib_height/2))
head = head.union(rib)

# Export
output_step = "cylinder_head_simplified.step"
cq.exporters.export(head, output_step, "STEP")
print(f"✅ Cylinder head CAD exported to {output_step}")

# Also export STL
output_stl = "cylinder_head_simplified.stl"
cq.exporters.export(head, output_stl, "STL")
print(f"✅ STL exported to {output_stl}")

print("\nNote: This is a simplified placeholder geometry.")
print("  - Pent‑roof chamber approximated.")
print("  - Ports are straight tubes (not optimized for flow).")
print("  - No water jackets, bolt holes, or complex features.")
print("  - For detailed design, use CFD and FEA.")