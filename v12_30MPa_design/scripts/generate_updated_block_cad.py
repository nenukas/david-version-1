#!/usr/bin/env python3
"""
Generate CAD for updated cylinder block (deck thickness increased to 12 mm).
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path('/home/nenuka/.openclaw/workspace/david-version-1')))

from src.engine.cylinder_block import CylinderBlockGeometry
import cadquery as cq

def load_results(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def create_geometry_from_results(data):
    """Create CylinderBlockGeometry from saved results."""
    geo = CylinderBlockGeometry(
        bore_diameter=94.5,
        stroke=94.5,
        bank_angle=60.0,
        bore_spacing=data['geometry']['bore_spacing'],
        deck_thickness=data['geometry']['deck_thickness'],
        cylinder_wall_thickness=data['geometry']['cylinder_wall_thickness'],
        water_jacket_thickness=data['geometry']['water_jacket_thickness'],
        main_bearing_width=data['geometry']['main_bearing_width'],
        main_bearing_height=data['geometry']['main_bearing_height'],
        skirt_depth=data['geometry']['skirt_depth'],
        pan_rail_width=data['geometry']['pan_rail_width'],
    )
    return geo

def create_block(geo):
    """
    Create simplified V12 block CAD.
    Returns CadQuery assembly.
    """
    # Overall block dimensions
    # Length: bore_spacing * 6 (6 cylinders per bank)
    length = geo.bore_spacing * 6
    # Width: bank_offset * 2 + some margin
    bank_offset = geo.bank_offset
    width = bank_offset * 2 + geo.bore_diameter * 0.5
    # Height: deck_thickness + stroke/2 + skirt_depth
    height = geo.deck_thickness + geo.stroke/2 + geo.skirt_depth
    
    # Create base block
    block = cq.Workplane("XY").box(length, width, height)
    
    # Cylinder holes
    bore_radius = geo.bore_diameter / 2
    # Left bank (offset -bank_offset)
    for i in range(6):
        x = (i - 2.5) * geo.bore_spacing  # center around origin
        y = -bank_offset
        block = block.faces(">Z").workplane().center(x, y).circle(bore_radius).cutThruAll()
    # Right bank (offset +bank_offset)
    for i in range(6):
        x = (i - 2.5) * geo.bore_spacing
        y = bank_offset
        block = block.faces(">Z").workplane().center(x, y).circle(bore_radius).cutThruAll()
    
    # Main bearing saddles (simplified as rectangular cutouts)
    saddle_width = geo.main_bearing_width
    saddle_height = geo.main_bearing_height
    saddle_y = 0  # centerline
    for i in range(7):
        x = (i - 3) * geo.bore_spacing
        # Cut rectangular slot
        block = block.faces("<Z").workplane().center(x, saddle_y).rect(saddle_width, saddle_height).cutBlind(-geo.skirt_depth * 0.5)
    
    # Pan rail (simplified as extrusion at bottom)
    pan_rail = cq.Workplane("XY").box(length - 20, width - 20, geo.pan_rail_width).translate((0,0, -height/2 + geo.pan_rail_width/2))
    block = block.union(pan_rail)
    
    return block

def main():
    json_path = "cylinder_block_30MPa_7075_T6_updated.json"
    print(f"Loading updated design from {json_path}")
    data = load_results(json_path)
    
    # Create geometry
    geo = create_geometry_from_results(data)
    print("Updated geometry:")
    for key, val in geo.__dict__.items():
        if not key.startswith('_'):
            print(f"  {key}: {val:.3f}")
    
    print("Generating CAD model...")
    block = create_block(geo)
    
    # Export STEP
    step_name = "cylinder_block_deck_12mm.step"
    cq.exporters.export(block, step_name, "STEP")
    print(f"Exported STEP to {step_name}")
    
    # Export STL
    stl_name = "cylinder_block_deck_12mm.stl"
    cq.exporters.export(block, stl_name, "STL")
    print(f"Exported STL to {stl_name}")
    
    print("\n✅ Updated cylinder block CAD generated.")

if __name__ == '__main__':
    main()