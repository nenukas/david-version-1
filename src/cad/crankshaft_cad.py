"""
Parametric CAD model of V12 crankshaft using CadQuery.
Generates geometry based on CrankshaftGeometry.
"""
import cadquery as cq
import numpy as np
from src.engine.crankshaft import CrankshaftGeometry

def create_throw(geo: CrankshaftGeometry, angle_deg: float = 0.0):
    """
    Create a single crank throw (main journal + pin + two cheeks).
    Returns a CadQuery Workplane centered on main journal axis.
    The throw is rotated about Z‑axis by angle_deg (for V12 phasing).
    """
    # Main journal (cylinder along X‑axis)
    main = (
        cq.Workplane("XZ")
        .circle(geo.main_journal_diameter / 2)
        .extrude(geo.main_journal_width)
    )
    
    # Crank pin (offset by stroke, also along X‑axis)
    pin = (
        cq.Workplane("XZ")
        .transformed(offset=(0, geo.stroke, 0))
        .circle(geo.pin_diameter / 2)
        .extrude(geo.pin_width)
    )
    
    # Cheeks (counterweight disks) – two per throw
    # Simplified as a rectangular block with a hole, oriented along X
    cheek_height = geo.cheek_radius * geo.cheek_sector_factor  # depth along X
    cheek = (
        cq.Workplane("XY")
        .rect(geo.cheek_thickness, geo.cheek_radius * 2)  # Y‑Z plane
        .circle(geo.cheek_hole_radius)
        .extrude(cheek_height)
        .rotateAboutCenter((0,1,0), 90)  # orient along X
    )
    # Position cheeks on each side of pin
    cheek1 = cheek.translate((0, geo.stroke, -geo.cheek_radius))
    cheek2 = cheek.translate((0, geo.stroke, geo.cheek_radius))
    
    # Combine components of this throw
    throw = main.union(pin).union(cheek1).union(cheek2)
    
    # Apply rotation for V12 phasing (60° between throws)
    if angle_deg != 0.0:
        throw = throw.rotateAboutCenter((0,0,1), angle_deg)
    
    return throw

def create_crankshaft(geo: CrankshaftGeometry):
    """
    Assemble full V12 crankshaft with 7 mains and 6 throws.
    Returns CadQuery assembly.
    """
    # Start with first main journal at origin
    # V12 firing order spacing: 60° between throws, 180° between banks
    # Simplified: we'll create 6 throws, each rotated by 60°
    throws = []
    for i in range(6):
        angle = i * 60.0
        throw = create_throw(geo, angle_deg=angle)
        # Offset along X‑axis (distance between throws = main_journal_width + pin_width + gap)
        x_offset = i * (geo.main_journal_width + geo.pin_width + 10.0)  # 10 mm gap
        throw = throw.translate((x_offset, 0, 0))
        throws.append(throw)
    
    # Union all throws
    crankshaft = throws[0]
    for t in throws[1:]:
        crankshaft = crankshaft.union(t)
    
    # Add extra main journal at the end
    last_main = (
        cq.Workplane("XZ")
        .circle(geo.main_journal_diameter / 2)
        .extrude(geo.main_journal_width)
        .translate((6 * (geo.main_journal_width + geo.pin_width + 10.0), 0, 0))
    )
    crankshaft = crankshaft.union(last_main)
    
    return crankshaft

def export_step(assembly, filename: str):
    """Export assembly to STEP file."""
    cq.exporters.export(assembly, filename, "STEP")

if __name__ == "__main__":
    # Test with baseline geometry
    from src.engine.crankshaft import baseline
    print("Generating crankshaft CAD...")
    crankshaft = create_crankshaft(baseline)
    print("Exporting to STEP...")
    export_step(crankshaft, "crankshaft_baseline.step")
    print("Done. Saved as 'crankshaft_baseline.step'")
    
    # Also export to STL for quick viewing
    cq.exporters.export(crankshaft, "crankshaft_baseline.stl", "STL")
    print("STL exported as well.")