#!/usr/bin/env python3
"""
Generate CAD for updated piston (crown thickness 15 mm) using JSON.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('/home/nenuka/.openclaw/workspace/david-version-1')))

from src.engine.piston_am import PistonGeometryAM
from src.engine.piston import PistonGeometry
from src.cad.piston_cad import create_piston, export_step
import cadquery as cq

def load_results(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def create_geometry_from_results(data):
    """Create PistonGeometry (non‑AM) from saved results."""
    geo_am = PistonGeometryAM(
        bore_diameter=94.5,
        compression_height=38.0,
        pin_diameter=28.0,
        pin_boss_width=data['geometry']['pin_boss_width'],
        crown_thickness=data['geometry']['crown_thickness'],
        ring_land_height=2.5,
        ring_groove_depth=3.0,
        skirt_length=data['geometry']['skirt_length'],
        skirt_thickness=data['geometry']['skirt_thickness'],
        lattice_relative_density=data['geometry']['lattice_relative_density'],
    )
    # Convert to PistonGeometry for CAD
    geo = PistonGeometry(
        bore_diameter=geo_am.bore_diameter,
        compression_height=geo_am.compression_height,
        pin_diameter=geo_am.pin_diameter,
        pin_boss_width=geo_am.pin_boss_width,
        crown_thickness=geo_am.crown_thickness,
        ring_land_height=geo_am.ring_land_height,
        ring_groove_depth=geo_am.ring_groove_depth,
        skirt_length=geo_am.skirt_length,
        skirt_thickness=geo_am.skirt_thickness,
    )
    return geo

def main():
    json_path = "/home/nenuka/.openclaw/workspace/fea_thermal/piston_crown_15.0mm.json"
    print(f"Loading updated piston geometry from {json_path}")
    data = load_results(json_path)
    
    # Check constraints (if present)
    if 'constraints_satisfied' in data:
        cons = data['constraints_satisfied']
        if not all(cons.values()):
            print("⚠️ Not all constraints satisfied.")
    
    # Create geometry
    geo = create_geometry_from_results(data)
    print("Updated piston geometry:")
    for key, val in geo.__dict__.items():
        if not key.startswith('_'):
            print(f"  {key}: {val:.3f}")
    
    print("Generating CAD model...")
    piston = create_piston(geo)
    
    # Export STEP
    step_name = "piston_crown_15mm_full.step"
    export_step(piston, step_name)
    print(f"Exported STEP to {step_name}")
    
    # Export STL
    stl_name = "piston_crown_15mm_full.stl"
    cq.exporters.export(piston, stl_name, 'STL')
    print(f"Exported STL to {stl_name}")
    
    print("\n✅ Updated piston CAD generated.")

if __name__ == '__main__':
    main()