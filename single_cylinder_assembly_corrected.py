#!/usr/bin/env python3
"""
Single‑cylinder assembly with corrected components:
- Piston (crown thickness 15 mm)
- Connecting rod (fixed bearing interfaces)
- Crankshaft throw (optimized)
- Cylinder block (simplified representation)
"""
import json
import cadquery as cq
import numpy as np
from datetime import datetime

# ----------------------------------------------------------------------
# LOAD SPECIFICATIONS
# ----------------------------------------------------------------------
print("=" * 70)
print("SINGLE‑CYLINDER ASSEMBLY WITH CORRECTED COMPONENTS")
print("=" * 70)

# Load conrod spec
with open("/home/nenuka/.openclaw/workspace/final_corrected_conrod_20260213_150623/final_corrected_spec.json") as f:
    conrod_spec = json.load(f)
conrod_geo = conrod_spec["corrected_dimensions"]

# Load piston spec
with open("/home/nenuka/.openclaw/workspace/final_piston_20260213_150906/final_piston_spec.json") as f:
    piston_spec = json.load(f)
piston_geo = piston_spec["geometry"]

# Load crankshaft spec
with open("/home/nenuka/.openclaw/workspace/final_crankshaft_throw_20260213_150959/final_crankshaft_throw_spec.json") as f:
    crank_spec = json.load(f)
crank_geo = crank_spec["geometry"]

print("\nComponent summary:")
print(f"Piston: crown {piston_geo['crown_thickness']:.2f} mm, skirt {piston_geo['skirt_length']:.2f} mm")
print(f"Conrod: beam {conrod_geo['beam_height']:.2f} × {conrod_geo['beam_width']:.2f} mm")
print(f"Crank: pin Ø{crank_geo['pin_diameter']:.2f} × {crank_geo['pin_width']:.2f} mm")

# ----------------------------------------------------------------------
# ASSEMBLY POSITIONS
# ----------------------------------------------------------------------
# Coordinate system: Z up, X along crankshaft axis, Y across engine
# TDC: piston crown at Z = deck_clearance
deck_clearance = 0.8  # mm
bore_diameter = 94.5  # mm
stroke = crank_geo["stroke"]  # 47.5 mm
crank_radius = stroke / 2  # 23.75 mm

# Piston at TDC (crown top at Z = deck_clearance)
piston_z_tdc = deck_clearance

# Conrod: small‑end at piston pin, big‑end at crank pin
# Conrod length = center_length = 150 mm
conrod_length = conrod_geo["center_length"]

# Crank pin at angle 0° (TDC) – pin center at (crank_radius, 0, -crank_radius)
# Actually, for Z‑up: crank center at (0,0,0), pin at (crank_radius, 0, 0)
# But we want pin at TDC: pin at (crank_radius, 0, 0) relative to crank center

print("\nAssembly positions:")
print(f"Deck clearance: {deck_clearance} mm")
print(f"Stroke: {stroke} mm, radius {crank_radius} mm")
print(f"Conrod length: {conrod_length} mm")

# ----------------------------------------------------------------------
# LOAD CAD FILES (or create simplified geometry)
# ----------------------------------------------------------------------
# Since we have STEP files, we could import them, but CadQuery import is tricky.
# Instead, create simplified geometry for assembly visualization.

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"single_cylinder_assembly_corrected_{timestamp}"
import os
os.makedirs(out_dir, exist_ok=True)

# Create simplified representations
print("\nCreating simplified assembly geometry...")

# 1. Piston (simplified cylinder)
piston = (
    cq.Workplane("XY")
    .circle(bore_diameter / 2 - 0.1)  # clearance
    .extrude(-(piston_geo["crown_thickness"] + piston_geo["skirt_length"]))
    .translate((0, 0, piston_z_tdc + piston_geo["crown_thickness"]/2))
)
# Add pin bosses (blocks)
boss_y = bore_diameter/2 - piston_geo["pin_boss_width"]/2
boss = (
    cq.Workplane("XY")
    .rect(piston_geo["pin_boss_width"]*2, piston_geo["pin_boss_width"])
    .extrude(-piston_geo["crown_thickness"]*0.6)
    .translate((0, -boss_y, piston_z_tdc - piston_geo["crown_thickness"]*0.3))
)
piston = piston.union(boss)

# 2. Connecting rod (simplified I‑beam)
h = conrod_geo["beam_height"]
b = conrod_geo["beam_width"]
tw = conrod_geo["web_thickness"]
tf = conrod_geo["flange_thickness"]
L = conrod_length

web = cq.Workplane("YZ").rect(tw, h - 2*tf).extrude(L)
top = cq.Workplane("YZ").rect(b, tf).extrude(L).translate((0,0,(h-tf)/2))
bottom = cq.Workplane("YZ").rect(b, tf).extrude(L).translate((0,0,-(h-tf)/2))
beam = web.union(top).union(bottom)
beam = beam.translate((L/2,0,0))

# Add bearing ends (cylinders)
big_end = (
    cq.Workplane("YZ")
    .circle(conrod_geo["big_end_diameter"]/2 + 5)
    .extrude(conrod_geo["big_end_width"])
    .translate((-conrod_geo["big_end_width"]/2,0,0))
)
small_end = (
    cq.Workplane("YZ")
    .circle(conrod_geo["small_end_diameter"]/2 + 5)
    .extrude(conrod_geo["small_end_width"])
    .translate((L - conrod_geo["small_end_width"]/2,0,0))
)

conrod = beam.union(big_end).union(small_end)
# Position conrod: small‑end at piston pin, big‑end at crank pin
# At TDC, small‑end Z = piston pin center ≈ piston_z_tdc - crown_thickness/2
piston_pin_z = piston_z_tdc - piston_geo["crown_thickness"]/2
conrod = conrod.translate((0,0,piston_pin_z))
# Rotate to vertical (original beam along X)
conrod = conrod.rotate((0,0,0), (1,0,0), 90)

# 3. Crankshaft throw (simplified)
main = (
    cq.Workplane("XY")
    .circle(crank_geo["main_journal_diameter"]/2)
    .extrude(crank_geo["main_journal_width"])
    .translate((-crank_geo["main_journal_width"]/2, 0, -crank_radius))
)
pin = (
    cq.Workplane("XY")
    .circle(crank_geo["pin_diameter"]/2)
    .extrude(crank_geo["pin_width"])
    .translate((crank_radius, 0, -crank_radius))
    .translate((-crank_geo["pin_width"]/2, 0, 0))
)
cheek = (
    cq.Workplane("XY")
    .rect(crank_radius*0.7, crank_geo["cheek_thickness"])
    .extrude(crank_geo["pin_width"]+10)
    .translate((crank_radius/2, 0, -crank_radius))
    .translate((-(crank_geo["pin_width"]+10)/2, 0, 0))
)
crank = main.union(pin).union(cheek)

# 4. Cylinder block (simplified box)
block_length = 200
block_width = 200
block_height = 100
block = (
    cq.Workplane("XY")
    .box(block_length, block_width, block_height)
    .translate((0,0,-block_height/2))
)
# Bore hole
bore = (
    cq.Workplane("XY")
    .circle(bore_diameter/2)
    .extrude(block_height)
    .translate((0,0,-block_height/2))
)
block = block.cut(bore)

# ----------------------------------------------------------------------
# COMBINE AND EXPORT
# ----------------------------------------------------------------------
assembly = piston.union(conrod).union(crank).union(block)

step_path = f"{out_dir}/single_cylinder_assembly_corrected.step"
cq.exporters.export(assembly, step_path, "STEP")
print(f"✅ Assembly CAD saved to {step_path}")

# ----------------------------------------------------------------------
# CLEARANCE CHECK
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("CLEARANCE CHECK (SIMPLIFIED)")
print("=" * 70)

# Piston‑to‑bore radial clearance
piston_clearance = 0.1  # mm
print(f"Piston‑bore radial clearance: {piston_clearance/2:.3f} mm")

# Conrod big‑end to crank‑pin clearance
axial_clearance = (crank_geo["pin_width"] - conrod_geo["big_end_width"]) / 2
radial_clearance = (conrod_geo["big_end_diameter"] - crank_geo["pin_diameter"]) / 2
print(f"Conrod‑crank axial clearance: {axial_clearance:.3f} mm each side")
print(f"Conrod‑crank radial clearance: {radial_clearance:.3f} mm")

# Conrod small‑end to piston‑pin clearance (diameters)
small_radial = (conrod_geo["small_end_diameter"] - 28.0) / 2  # vs nominal pin
print(f"Conrod‑piston radial clearance: {small_radial:.3f} mm")

# Piston‑to‑valve clearance (rough)
valve_clearance = deck_clearance + 5.0  # approx
print(f"Piston‑to‑valve clearance (approx): {valve_clearance:.2f} mm")

# ----------------------------------------------------------------------
# SAVE ASSEMBLY SPEC
# ----------------------------------------------------------------------
spec = {
    "timestamp": datetime.now().isoformat(),
    "components": {
        "piston": piston_spec["geometry"],
        "conrod": conrod_geo,
        "crankshaft": crank_geo,
    },
    "positions": {
        "deck_clearance_mm": deck_clearance,
        "piston_z_tdc_mm": piston_z_tdc,
        "crank_radius_mm": crank_radius,
        "conrod_length_mm": conrod_length,
    },
    "clearances": {
        "piston_bore_radial_mm": piston_clearance/2,
        "conrod_crank_axial_mm": axial_clearance,
        "conrod_crank_radial_mm": radial_clearance,
        "conrod_piston_radial_mm": small_radial,
        "piston_valve_approx_mm": valve_clearance,
    }
}

json_path = f"{out_dir}/single_cylinder_assembly_spec.json"
with open(json_path, "w") as f:
    json.dump(spec, f, indent=2)
print(f"✅ Assembly specification saved to {json_path}")

print("\n" + "=" * 70)
print("ASSEMBLY COMPLETE")
print("=" * 70)
print(f"Output directory: {out_dir}/")
print("\nNext steps:")
print("1. Open single_cylinder_assembly_corrected.step in CAD viewer.")
print("2. Verify component alignment and clearances.")
print("3. Check for interference (should be none).")
print("4. If satisfactory, proceed to detailed CAD with fillets, threads, etc.")
print("\n✅ Ready for visual feedback.")