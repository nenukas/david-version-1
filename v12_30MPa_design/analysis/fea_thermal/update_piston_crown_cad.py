#!/usr/bin/env python3
"""
Update piston crown thickness to 15 mm and generate new CAD (STEP) for Ansys.
"""
import json
import sys
from pathlib import Path
import cadquery as cq

sys.path.insert(0, str(Path('/home/nenuka/.openclaw/workspace/david-version-1')))

from src.engine.piston_am import PistonGeometryAM
from src.engine.piston import PistonGeometry
from src.cad.piston_cad import create_piston, export_step

def load_results(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def create_geometry_from_results(data, new_crown_thickness=None):
    """Create PistonGeometry from saved results, optionally override crown thickness."""
    geo_am = PistonGeometryAM(
        bore_diameter=94.5,
        compression_height=38.0,
        pin_diameter=28.0,
        pin_boss_width=data['geometry']['pin_boss_width'],
        crown_thickness=new_crown_thickness if new_crown_thickness is not None else data['geometry']['crown_thickness'],
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
    # Find latest relaxed piston results
    results_dir = Path('/home/nenuka/.openclaw/workspace')
    json_files = list(results_dir.glob('piston_opt_relaxed_30MPa_results_*.json'))
    if not json_files:
        print("No relaxed piston results JSON found.")
        sys.exit(1)
    latest = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading base geometry from {latest.name}")
    data = load_results(latest)
    
    # Original crown thickness
    orig = data['geometry']['crown_thickness']
    print(f"Original crown thickness: {orig:.3f} mm")
    
    # New crown thickness (15 mm)
    new_thickness = 15.0
    print(f"New crown thickness: {new_thickness} mm")
    
    # Create geometry with updated thickness
    geo = create_geometry_from_results(data, new_crown_thickness=new_thickness)
    print("Updated geometry:")
    for key, val in geo.__dict__.items():
        if not key.startswith('_'):
            print(f"  {key}: {val:.3f}")
    
    # Generate CAD
    print("Generating CAD model...")
    piston = create_piston(geo)
    
    # Export STEP with descriptive name
    step_name = f"piston_crown_{new_thickness}mm.step"
    export_step(piston, step_name)
    print(f"Exported STEP to {step_name}")
    
    # Export STL
    stl_name = f"piston_crown_{new_thickness}mm.stl"
    cq.exporters.export(piston, stl_name, 'STL')
    print(f"Exported STL to {stl_name}")
    
    # Also save updated JSON for reference
    data['geometry']['crown_thickness'] = new_thickness
    updated_json = f"piston_crown_{new_thickness}mm.json"
    with open(updated_json, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved updated geometry to {updated_json}")
    
    print("\n✅ CAD updated with improved crown thickness.")
    print("   Use the STEP file for Ansys thermal‑stress simulation.")

if __name__ == '__main__':
    main()