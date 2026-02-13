#!/usr/bin/env python3
"""
Generate CAD for relaxed‑constraint connecting rod (30 MPa).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('/home/nenuka/.openclaw/workspace/david-version-1')))

from src.engine.conrod_am import ConrodGeometryAM
from src.engine.conrod import ConrodGeometry
from src.cad.conrod_cad import create_connecting_rod, export_step
import cadquery as cq

CRANK_PIN_DIAMETER = 86.5   # mm (from optimized crankshaft)
PISTON_PIN_DIAMETER = 28.0  # mm (typical for high‑power V12)
CENTER_LENGTH = 150.0       # mm (rod length for 95 mm stroke)

def load_results(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def create_geometry_from_results(data):
    """Create ConrodGeometry (non‑AM) from saved results."""
    geo_am = ConrodGeometryAM(
        beam_height=data['geometry']['beam_height'],
        beam_width=data['geometry']['beam_width'],
        web_thickness=data['geometry']['web_thickness'],
        flange_thickness=data['geometry']['flange_thickness'],
        center_length=CENTER_LENGTH,
        big_end_width=data['geometry']['big_end_width'],
        small_end_width=data['geometry']['small_end_width'],
        big_end_diameter=CRANK_PIN_DIAMETER,
        small_end_diameter=data['geometry']['small_end_diameter'],
        fillet_big=data['geometry']['fillet_big'],
        fillet_small=data['geometry']['fillet_small'],
        lattice_relative_density=data['geometry']['lattice_relative_density'],
    )
    # Convert to ConrodGeometry for CAD (material irrelevant)
    geo = ConrodGeometry(
        beam_height=geo_am.beam_height,
        beam_width=geo_am.beam_width,
        web_thickness=geo_am.web_thickness,
        flange_thickness=geo_am.flange_thickness,
        center_length=geo_am.center_length,
        big_end_width=geo_am.big_end_width,
        small_end_width=geo_am.small_end_width,
        big_end_diameter=geo_am.big_end_diameter,
        small_end_diameter=geo_am.small_end_diameter,
        fillet_big=geo_am.fillet_big,
        fillet_small=geo_am.fillet_small,
    )
    return geo

def main():
    # Find latest relaxed conrod results
    results_dir = Path('/home/nenuka/.openclaw/workspace')
    json_files = list(results_dir.glob('conrod_opt_relaxed2_30MPa_results_*.json'))
    if not json_files:
        print("No relaxed conrod results JSON found.")
        sys.exit(1)
    latest = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading results from {latest.name}")
    
    data = load_results(latest)
    
    # Check constraints
    cons = data['constraints_satisfied']
    if not all(cons.values()):
        print("⚠️ Not all constraints satisfied. CAD generation may not be appropriate.")
    
    # Create geometry
    geo = create_geometry_from_results(data)
    print("Geometry loaded:")
    for key, val in geo.__dict__.items():
        if not key.startswith('_'):
            print(f"  {key}: {val:.3f}")
    
    print("Generating CAD model...")
    rod = create_connecting_rod(geo)
    
    # Export STEP
    step_name = latest.stem + '.step'
    export_step(rod, step_name)
    print(f"Exported STEP to {step_name}")
    
    # Export STL
    stl_name = latest.stem + '.stl'
    cq.exporters.export(rod, stl_name, 'STL')
    print(f"Exported STL to {stl_name}")

if __name__ == '__main__':
    main()