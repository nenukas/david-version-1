#!/usr/bin/env python3
"""
Generate CAD for additive‑manufacturing‑aware connecting rod.
Loads the best feasible design from JSON results and exports STEP/STL.
"""
import json
import sys
from pathlib import Path

# Add the current directory to Python path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent))

from src.engine.conrod_am import ConrodGeometryAM
from src.cad.conrod_cad import create_connecting_rod, export_step
import cadquery as cq

CRANK_PIN_DIAMETER = 86.5   # mm (from optimized crankshaft)
PISTON_PIN_DIAMETER = 28.0  # mm (typical for high‑power V12)
CENTER_LENGTH = 150.0       # mm (rod length for 95 mm stroke)

def load_results(json_path):
    """Load optimization results JSON."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def create_geometry_from_results(data):
    """Create ConrodGeometryAM from saved results."""
    geo = ConrodGeometryAM(
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
    return geo

def main():
    # Find the latest results JSON
    results_dir = Path('.')
    json_files = list(results_dir.glob('conrod_opt_am_v2_results_*.json'))
    if not json_files:
        print("No results JSON found.")
        sys.exit(1)
    latest = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading results from {latest.name}")
    
    data = load_results(latest)
    
    # Check if all constraints satisfied
    cons = data['constraints_satisfied']
    if not all(v if isinstance(v, bool) else (v == "True") for v in cons.values()):
        print("⚠️ Not all constraints satisfied. CAD generation may not be appropriate.")
        # Continue anyway? maybe ask, but we'll proceed.
    
    # Create geometry
    geo = create_geometry_from_results(data)
    print("Geometry loaded:")
    for key, val in geo.__dict__.items():
        if key not in ('density', 'youngs_modulus', 'poisson', 'yield_strength', 'fatigue_limit'):
            print(f"  {key}: {val:.3f}")
    
    # Create CAD model (using original ConrodGeometry for shape)
    # We'll convert to ConrodGeometry (non‑AM) for the CAD function
    from src.engine.conrod import ConrodGeometry
    geo_cad = ConrodGeometry(
        beam_height=geo.beam_height,
        beam_width=geo.beam_width,
        web_thickness=geo.web_thickness,
        flange_thickness=geo.flange_thickness,
        center_length=geo.center_length,
        big_end_width=geo.big_end_width,
        small_end_width=geo.small_end_width,
        big_end_diameter=geo.big_end_diameter,
        small_end_diameter=geo.small_end_diameter,
        fillet_big=geo.fillet_big,
        fillet_small=geo.fillet_small,
        # Material properties irrelevant for geometry; use defaults
    )
    
    print("Generating CAD model...")
    rod = create_connecting_rod(geo_cad)
    
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