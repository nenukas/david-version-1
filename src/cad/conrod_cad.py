"""
Parametric CAD model of V12 connecting rod using CadQuery.
Generates geometry based on ConrodGeometry.
"""
import cadquery as cq
import numpy as np
from src.engine.conrod import ConrodGeometry

def create_connecting_rod(geo: ConrodGeometry):
    """
    Create a connecting rod assembly.
    Big end centered at origin, small end offset along X‑axis by center_length.
    Beam is I‑beam cross‑section extruded along X.
    """
    # ---- 1. Create I‑beam as three rectangular prisms (web + two flanges) ----
    h = geo.beam_height          # total height (Z direction)
    b = geo.beam_width           # total width (Y direction)
    tw = geo.web_thickness       # web thickness (vertical)
    tf = geo.flange_thickness    # flange thickness (horizontal)
    
    # Web: centered at Y=0, Z=0
    web = (
        cq.Workplane("YZ")
        .rect(tw, h - 2*tf)
        .extrude(geo.center_length)
    )
    # Top flange: centered at Y=0, Z = (h - tf)/2
    top_flange = (
        cq.Workplane("YZ")
        .rect(b, tf)
        .extrude(geo.center_length)
        .translate((0, 0, (h - tf)/2))
    )
    # Bottom flange: centered at Y=0, Z = -(h - tf)/2
    bottom_flange = (
        cq.Workplane("YZ")
        .rect(b, tf)
        .extrude(geo.center_length)
        .translate((0, 0, -(h - tf)/2))
    )
    # Union the three parts
    beam = web.union(top_flange).union(bottom_flange)
    # Center beam between ends
    beam = beam.translate((geo.center_length / 2, 0, 0))
    
    # ---- 3. Create big end (crank pin bearing) ----
    # Outer cylinder (axis along X)
    big_end_outer_radius = geo.big_end_diameter / 2 + 12.0  # wall thickness ~12mm
    big_end_outer = (
        cq.Workplane("YZ")
        .circle(big_end_outer_radius)
        .extrude(geo.big_end_width)  # extrude along X
        .translate((-geo.big_end_width / 2, 0, 0))  # center at X=0
    )
    # Hole for crank pin
    big_end_hole = (
        cq.Workplane("YZ")
        .circle(geo.big_end_diameter / 2)
        .extrude(geo.big_end_width + 2)  # slightly longer to ensure clean cut
        .translate((-geo.big_end_width / 2 - 1, 0, 0))
    )
    big_end = big_end_outer.cut(big_end_hole)
    
    # ---- 4. Create small end (piston pin bearing) ----
    small_end_outer_radius = geo.small_end_diameter / 2 + 10.0  # wall thickness ~10mm
    small_end_outer = (
        cq.Workplane("YZ")
        .circle(small_end_outer_radius)
        .extrude(geo.small_end_width)
        .translate((geo.center_length - geo.small_end_width / 2, 0, 0))
    )
    small_end_hole = (
        cq.Workplane("YZ")
        .circle(geo.small_end_diameter / 2)
        .extrude(geo.small_end_width + 2)
        .translate((geo.center_length - geo.small_end_width / 2 - 1, 0, 0))
    )
    small_end = small_end_outer.cut(small_end_hole)
    
    # ---- 5. Union all parts ----
    rod = beam.union(big_end).union(small_end)
    
    # ---- 6. Add fillets (simplified: chamfer edges) ----
    # We'll skip for now; complex edge selection
    
    return rod

def export_step(assembly, filename: str):
    """Export assembly to STEP file."""
    cq.exporters.export(assembly, filename, "STEP")

if __name__ == "__main__":
    # Create a test geometry using parameters from optimization
    test_geo = ConrodGeometry(
        beam_height=44.308,
        beam_width=20.237,
        web_thickness=5.993,
        flange_thickness=5.922,
        center_length=150.0,
        big_end_width=33.116,
        small_end_width=25.026,
        big_end_diameter=86.5,      # from crankshaft
        small_end_diameter=30.899,
        fillet_big=3.847,
        fillet_small=3.952,
    )
    
    print("Generating connecting rod CAD...")
    rod = create_connecting_rod(test_geo)
    print("Exporting to STEP...")
    export_step(rod, "conrod_test.step")
    print("Done. Saved as 'conrod_test.step'")
    
    # Also export STL
    cq.exporters.export(rod, "conrod_test.stl", "STL")
    print("Exported STL.")