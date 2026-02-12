"""
Parametric CAD model of V12 piston using CadQuery.
Generates geometry based on PistonGeometry.
"""
import cadquery as cq
import numpy as np
from src.engine.piston import PistonGeometry

def create_piston(geo: PistonGeometry):
    """
    Create a piston assembly.
    Crown top at Z=0, piston extends downward (negative Z).
    Pin bore along Y‑axis.
    """
    # ---- 1. Crown (disc) ----
    crown = (
        cq.Workplane("XY")
        .circle(geo.bore_diameter / 2)
        .extrude(-geo.crown_thickness)  # downward
    )
    
    # ---- 2. Ring lands (simplified as grooves) ----
    # We'll create a cylinder representing the ring‑land region
    ring_land_outer = (
        cq.Workplane("XY")
        .circle(geo.bore_diameter / 2 - 0.2)  # slight clearance
        .extrude(-geo.compression_height)
        .translate((0, 0, -geo.crown_thickness))
    )
    # Subtract ring grooves (simplified as rectangular cut)
    # For now, skip detailed grooves
    
    # ---- 3. Skirt (cylindrical shell) ----
    skirt_outer = (
        cq.Workplane("XY")
        .circle(geo.bore_diameter / 2 - 0.5)  # clearance
        .extrude(-geo.skirt_length)
        .translate((0, 0, -geo.crown_thickness - geo.compression_height))
    )
    skirt_inner = (
        cq.Workplane("XY")
        .circle(geo.bore_diameter / 2 - 0.5 - geo.skirt_thickness)
        .extrude(-geo.skirt_length)
        .translate((0, 0, -geo.crown_thickness - geo.compression_height))
    )
    skirt = skirt_outer.cut(skirt_inner)
    
    # ---- 4. Pin bosses (two blocks with hole) ----
    boss_height = geo.compression_height * 0.6
    boss_y_offset = geo.bore_diameter / 2 - geo.pin_boss_width / 2
    # Left boss
    left_boss = (
        cq.Workplane("XY")
        .rect(geo.pin_diameter + 2 * geo.pin_boss_width, geo.pin_boss_width)
        .extrude(-boss_height)
        .translate((0, -boss_y_offset, -geo.crown_thickness))
    )
    # Right boss (mirror)
    right_boss = (
        cq.Workplane("XY")
        .rect(geo.pin_diameter + 2 * geo.pin_boss_width, geo.pin_boss_width)
        .extrude(-boss_height)
        .translate((0, boss_y_offset, -geo.crown_thickness))
    )
    # Pin hole through both bosses
    pin_hole = (
        cq.Workplane("XY")
        .circle(geo.pin_diameter / 2)
        .extrude(-boss_height * 1.1)  # slightly longer
        .translate((0, 0, -geo.crown_thickness - boss_height * 0.05))
    )
    bosses = left_boss.union(right_boss).cut(pin_hole)
    
    # ---- 5. Combine all parts ----
    piston = crown.union(ring_land_outer).union(skirt).union(bosses)
    
    return piston

def export_step(assembly, filename: str):
    """Export assembly to STEP file."""
    cq.exporters.export(assembly, filename, "STEP")

if __name__ == "__main__":
    from src.engine.piston import baseline
    print("Generating piston CAD...")
    piston = create_piston(baseline)
    print("Exporting to STEP...")
    export_step(piston, "piston_baseline.step")
    print("Done. Saved as 'piston_baseline.step'")
    
    # Also export STL
    cq.exporters.export(piston, "piston_baseline.stl", "STL")
    print("Exported STL.")