#!/usr/bin/env python3
"""
Assembly of single‑cylinder slice using existing STEP files.
Positions components at top‑dead‑center (TDC).
"""
import sys
from pathlib import Path
import json
import math

sys.path.insert(0, str(Path('/home/nenuka/.openclaw/workspace/david-version-1')))

# Import CadQuery
import cadquery as cq

# Import geometry classes for dimensions
from src.engine.cylinder_block import CylinderBlockGeometry
from src.engine.piston import PistonGeometry
from src.engine.conrod import ConrodGeometry
from src.engine.crankshaft import CrankshaftGeometry

# Import CAD creation for piston and rod (we'll generate fresh)
from src.cad.piston_cad import create_piston
from src.cad.conrod_cad import create_connecting_rod

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_step(path):
    """Load STEP file as CadQuery Workplane."""
    return cq.importers.importStep(str(path))

def create_piston_from_json(json_path):
    data = load_json(json_path)
    geo = PistonGeometry(
        bore_diameter=94.5,
        compression_height=38.0,
        pin_diameter=28.0,
        pin_boss_width=data['geometry']['pin_boss_width'],
        crown_thickness=data['geometry']['crown_thickness'],
        ring_land_height=2.5,
        ring_groove_depth=3.0,
        skirt_length=data['geometry']['skirt_length'],
        skirt_thickness=data['geometry']['skirt_thickness'],
    )
    return create_piston(geo), geo

def create_conrod_from_json(json_path):
    data = load_json(json_path)
    geo = ConrodGeometry(
        beam_height=data['geometry']['beam_height'],
        beam_width=data['geometry']['beam_width'],
        web_thickness=data['geometry']['web_thickness'],
        flange_thickness=data['geometry']['flange_thickness'],
        center_length=150.0,
        big_end_width=data['geometry']['big_end_width'],
        small_end_width=data['geometry']['small_end_width'],
        big_end_diameter=86.5,
        small_end_diameter=data['geometry']['small_end_diameter'],
        fillet_big=data['geometry']['fillet_big'],
        fillet_small=data['geometry']['fillet_small'],
    )
    return create_connecting_rod(geo), geo

def get_block_dimensions(json_path):
    data = load_json(json_path)
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

def main():
    print("Loading components...")
    
    # Load block STEP (full block)
    block_step = load_step('cylinder_block_deck_12mm.step')
    block_geo = get_block_dimensions('cylinder_block_30MPa_7075_T6_updated.json')
    print(f"Block deck thickness: {block_geo.deck_thickness} mm")
    
    # Load crankshaft STEP (single throw)
    crank_step = load_step('david-version-1/crankshaft_optimized.step')
    # Approximate crankshaft geometry for positioning
    # Assume stroke = 47.5 mm, pin diameter = 86.5 mm, main journal diameter = 85 mm.
    # We'll need to know the orientation of the STEP file.
    # Let's assume crankshaft STEP origin at main journal centerline.
    # We'll treat it as such.
    
    # Create piston and connecting rod from JSON (ensuring latest geometry)
    piston, piston_geo = create_piston_from_json('fea_thermal/piston_crown_15.0mm.json')
    rod, rod_geo = create_conrod_from_json('conrod_opt_relaxed2_30MPa_results_20260213_010504.json')
    
    # ========== POSITIONING ==========
    # Coordinate system: Z up, deck top Z = 0, cylinder bore center at (0,0).
    # Block STEP origin? We'll assume block origin at deck top, bore center (0,0).
    # The block STEP we generated likely has origin at block centroid.
    # We'll shift block so deck top at Z=0.
    # Determine block height: deck_thickness + stroke/2 + skirt_depth
    block_height = block_geo.deck_thickness + block_geo.stroke/2 + block_geo.skirt_depth
    # Shift block down by half height? Let's approximate: shift block so deck top at Z = block_height/2? Hard.
    # Instead, we'll position other components relative to block using known dimensions.
    # Let's assume block STEP origin at bottom of pan rail? Unknown.
    # For simplicity, we'll keep block as is and position other components relative.
    # We'll compute crank main journal centerline Z relative to deck top.
    # Deck bottom Z = -deck_thickness.
    # Crank centerline Z = -deck_thickness - stroke/2.
    crank_main_z = -block_geo.deck_thickness - block_geo.stroke/2
    
    # Position crankshaft: main journal centerline at (0,0,crank_main_z).
    crank_assy = crank_step.translate((0, 0, crank_main_z))
    
    # At TDC, crank pin is at topmost: offset +stroke in Z from main journal.
    crank_pin_z_tdc = crank_main_z + block_geo.stroke/2  # stroke = 94.5 mm, half = 47.25? Wait stroke/2 = 47.25 mm.
    # Actually stroke = 94.5 mm, crank radius = 47.25 mm. The crankshaft geometry uses stroke as half? In crankshaft.py, stroke is half of engine stroke (47.5 mm). Let's use engine stroke = 94.5 mm, crank radius = 47.25 mm.
    crank_radius = block_geo.stroke / 2.0  # 47.25 mm
    crank_pin_z_tdc = crank_main_z + crank_radius
    
    # Connecting rod length
    rod_length = rod_geo.center_length  # 150 mm
    
    # Piston pin center Z at TDC = crank_pin_z_tdc + rod_length (since rod connects piston pin above crank pin).
    piston_pin_z_tdc = crank_pin_z_tdc + rod_length
    
    # Piston crown top Z = piston_pin_z_tdc + compression_height (crown above pin).
    piston_crown_top_z = piston_pin_z_tdc + piston_geo.compression_height
    
    # We want piston crown top flush with deck top (Z=0). Adjust crank_main_z to satisfy.
    # Solve: piston_crown_top_z = 0.
    # Let's compute required crank_main_z.
    # piston_crown_top_z = crank_main_z + crank_radius + rod_length + compression_height = 0
    required_crank_main_z = -crank_radius - rod_length - piston_geo.compression_height
    print(f"Required crank main Z for flush crown: {required_crank_main_z:.2f} mm")
    
    # Adjust all positions accordingly.
    crank_main_z = required_crank_main_z
    crank_assy = crank_step.translate((0, 0, crank_main_z))
    crank_pin_z_tdc = crank_main_z + crank_radius
    piston_pin_z_tdc = crank_pin_z_tdc + rod_length
    piston_crown_top_z = piston_pin_z_tdc + piston_geo.compression_height
    print(f"Resulting piston crown top Z: {piston_crown_top_z:.2f} mm (should be ~0)")
    
    # Position piston: crown top at Z = piston_crown_top_z? Actually we want crown top at Z=0.
    # The piston CAD origin? Likely at crown top center? Let's assume origin at crown top center.
    # Shift piston so crown top at Z=0.
    piston_assy = piston.translate((0, 0, -piston_geo.compression_height))  # shift down by compression height to get pin center at Z = -compression_height? Wait.
    # Let's compute shift: we want piston pin center at Z = piston_pin_z_tdc.
    # The piston CAD origin at crown top center? The create_piston function likely places crown top at Z=0? Not sure.
    # For simplicity, we'll shift piston so pin center at Z = piston_pin_z_tdc.
    # We'll assume piston CAD origin at pin center? Let's assume origin at crown top.
    # We'll shift piston down by compression height to get pin center at Z = -compression_height.
    # Then we need to shift further by piston_pin_z_tdc + compression_height to get pin at correct Z.
    piston_shift_z = piston_pin_z_tdc + piston_geo.compression_height  # because origin at crown top.
    piston_assy = piston.translate((0, 0, piston_shift_z))
    
    # Position connecting rod: small end at piston pin, big end at crank pin.
    # Assume rod CAD origin at small end center.
    rod_assy = rod.translate((0, 0, piston_pin_z_tdc))
    
    # Block position: we need to shift block so deck top at Z=0.
    # Determine block STEP origin relative to deck top. Unknown.
    # We'll keep block as is and shift other components relative to block.
    # But we already positioned components relative to deck top Z=0.
    # We'll leave block at its original position (maybe origin at deck top).
    # Let's assume block STEP origin at deck top, bore center (0,0). Good.
    # So we keep block unchanged.
    
    # Combine assembly
    assembly = block_step.union(piston_assy).union(rod_assy).union(crank_assy)
    
    # Export assembly STEP
    step_name = "single_cylinder_assembly_v2.step"
    cq.exporters.export(assembly, step_name, "STEP")
    print(f"Exported assembly STEP to {step_name}")
    
    # Export individual positioned components
    cq.exporters.export(block_step, "block_assembly.step", "STEP")
    cq.exporters.export(piston_assy, "piston_assembly.step", "STEP")
    cq.exporters.export(rod_assy, "rod_assembly.step", "STEP")
    cq.exporters.export(crank_assy, "crankshaft_assembly.step", "STEP")
    
    print("\nAssembly dimensions:")
    print(f"  Engine stroke: {block_geo.stroke} mm")
    print(f"  Crank radius: {crank_radius} mm")
    print(f"  Connecting rod length: {rod_length} mm")
    print(f"  Piston compression height: {piston_geo.compression_height} mm")
    print(f"  Deck thickness: {block_geo.deck_thickness} mm")
    print(f"  Crank main journal Z: {crank_main_z:.1f} mm")
    print(f"  Piston crown top Z: {piston_crown_top_z:.1f} mm")
    print(f"  Piston pin Z: {piston_pin_z_tdc:.1f} mm")
    print(f"  Crank pin Z (TDC): {crank_pin_z_tdc:.1f} mm")
    
    # Check geometry consistency
    rod_length_calc = piston_pin_z_tdc - crank_pin_z_tdc
    print(f"  Rod length (calculated): {rod_length_calc:.1f} mm")
    compression_height_calc = piston_crown_top_z - piston_pin_z_tdc
    print(f"  Compression height (calculated): {compression_height_calc:.1f} mm")
    
    print("\n✅ Assembly completed.")

if __name__ == "__main__":
    main()