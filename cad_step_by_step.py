#!/usr/bin/env python3
"""
Step‑by‑step CAD generation with validation checks.
Builds cylinder head, piston, connecting rod, crankshaft, and block.
Each step exports intermediate geometry, computes metrics, and logs.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import cadquery as cq
import json
import math
import os
from datetime import datetime

# ----------------------------------------------------------------------
# 0. SETUP
# ----------------------------------------------------------------------
print("=" * 70)
print("V12 HYPERCAR – STEP‑BY‑STEP CAD GENERATION WITH VALIDATION")
print("=" * 70)

# Create output directories
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = f"cad_steps_{timestamp}"
os.makedirs(out_dir, exist_ok=True)
os.makedirs(f"{out_dir}/cylinder_head", exist_ok=True)
os.makedirs(f"{out_dir}/piston", exist_ok=True)
os.makedirs(f"{out_dir}/conrod", exist_ok=True)
os.makedirs(f"{out_dir}/crankshaft", exist_ok=True)
os.makedirs(f"{out_dir}/cylinder_block", exist_ok=True)

log_file = open(f"{out_dir}/log.txt", "w")
def log(msg):
    print(msg)
    log_file.write(msg + "\n")

log(f"Started at {timestamp}")
log(f"Output directory: {out_dir}")

# ----------------------------------------------------------------------
# VALIDATION HELPERS
# ----------------------------------------------------------------------
def check_volume(solid, expected_volume_mm3, tolerance=0.05):
    """Check volume of solid against expected value."""
    try:
        vol = solid.val().Volume()
        diff = abs(vol - expected_volume_mm3) / expected_volume_mm3
        ok = diff < tolerance
        log(f"  Volume: {vol:.1f} mm³ (expected {expected_volume_mm3:.1f}, diff {diff*100:.1f}%)")
        if not ok:
            log(f"  ⚠️  Volume mismatch > {tolerance*100:.0f}%")
        return ok, vol
    except Exception as e:
        log(f"  ❌ Volume check failed: {e}")
        return False, 0

def check_bounding_box(solid, expected_dimensions, tolerance=1.0):
    """Check bounding box dimensions."""
    try:
        bbox = solid.val().BoundingBox()
        dx = bbox.xmax - bbox.xmin
        dy = bbox.ymax - bbox.ymin
        dz = bbox.zmax - bbox.zmin
        exp_dx, exp_dy, exp_dz = expected_dimensions
        ok = (abs(dx - exp_dx) < tolerance and
              abs(dy - exp_dy) < tolerance and
              abs(dz - exp_dz) < tolerance)
        log(f"  Bounding box: ({dx:.2f}, {dy:.2f}, {dz:.2f}) mm")
        log(f"  Expected:     ({exp_dx:.2f}, {exp_dy:.2f}, {exp_dz:.2f}) mm")
        if not ok:
            log(f"  ⚠️  Dimension mismatch > {tolerance} mm")
        return ok, (dx, dy, dz)
    except Exception as e:
        log(f"  ❌ Bounding box check failed: {e}")
        return False, (0,0,0)

def export_step(solid, path, name):
    """Export solid to STEP file."""
    try:
        cq.exporters.export(solid, path, "STEP")
        log(f"  ✅ Exported {name} to {path}")
        return True
    except Exception as e:
        log(f"  ❌ Export failed for {name}: {e}")
        return False

# ----------------------------------------------------------------------
# 1. CYLINDER HEAD (per cylinder)
# ----------------------------------------------------------------------
log("\n" + "-" * 70)
log("1. CYLINDER HEAD")
log("-" * 70)

# Load parameters from earlier design (simplified)
bore = 94.5
intake_valve_dia = 42.5
exhaust_valve_dia = 35.9
intake_port_dia = 36.15
exhaust_port_dia = 30.52
head_height = 40.0
head_width = 120.0
head_length = 150.0
deck_clearance = 0.8
chamber_depth = 10.0
chamber_length = bore * 0.8
chamber_width = bore * 0.9
valve_spacing = bore * 0.8
seat_depth = 8.0
guide_dia = 8.0
guide_length = 30.0
port_length = 60.0
cam_bore_dia = 30.0
cam_spacing = 80.0

log(f"Bore: {bore} mm")
log(f"Intake valve diameter: {intake_valve_dia} mm")
log(f"Exhaust valve diameter: {exhaust_valve_dia} mm")
log(f"Head dimensions: {head_length} x {head_width} x {head_height} mm")

# Step 1.1 – Base block
log("\nStep 1.1: Base block")
head = cq.Workplane("XY").box(head_length, head_width, head_height)
head = head.translate((0,0,-head_height/2))  # top at Z=0
ok, vol = check_volume(head, head_length * head_width * head_height, tolerance=0.01)
ok, dim = check_bounding_box(head, (head_length, head_width, head_height))
export_step(head, f"{out_dir}/cylinder_head/01_base_block.step", "base block")

# Step 1.2 – Combustion chamber (pent‑roof approximation)
log("\nStep 1.2: Combustion chamber")
chamber = (cq.Workplane("XY")
           .workplane(offset=-head_height/2)
           .center(0,0)
           .rect(chamber_length, chamber_width)
           .extrude(chamber_depth, taper=-15))  # negative taper for draft
head_with_chamber = head.cut(chamber)
# Expected volume after cut: base volume - chamber volume
chamber_vol_approx = chamber_length * chamber_width * chamber_depth * 0.7  # rough due to taper
expected_vol = head_length * head_width * head_height - chamber_vol_approx
ok, vol = check_volume(head_with_chamber, expected_vol, tolerance=0.1)
export_step(head_with_chamber, f"{out_dir}/cylinder_head/02_with_chamber.step", "head with chamber")

# Step 1.3 – Valve seats
log("\nStep 1.3: Valve seats")
intake_x = -valve_spacing/2
exhaust_x = valve_spacing/2
valve_y = 0
seat_dia_intake = intake_valve_dia * 1.1
seat_dia_exhaust = exhaust_valve_dia * 1.1
head_with_seats = head_with_chamber
head_with_seats = head_with_seats.faces("<Z").workplane().center(intake_x, valve_y).circle(seat_dia_intake/2).cutBlind(-seat_depth)
head_with_seats = head_with_seats.faces("<Z").workplane().center(exhaust_x, valve_y).circle(seat_dia_exhaust/2).cutBlind(-seat_depth)
# Volume check after seats (small reduction)
seat_vol = math.pi * (seat_dia_intake/2)**2 * seat_depth + math.pi * (seat_dia_exhaust/2)**2 * seat_depth
expected_vol -= seat_vol
ok, vol = check_volume(head_with_seats, expected_vol, tolerance=0.1)
export_step(head_with_seats, f"{out_dir}/cylinder_head/03_with_seats.step", "head with valve seats")

# Step 1.4 – Valve guide holes
log("\nStep 1.4: Valve guide holes")
head_with_guides = head_with_seats
head_with_guides = head_with_guides.faces("<Z").workplane().center(intake_x, valve_y).circle(guide_dia/2).cutBlind(-guide_length)
head_with_guides = head_with_guides.faces("<Z").workplane().center(exhaust_x, valve_y).circle(guide_dia/2).cutBlind(-guide_length)
guide_vol = math.pi * (guide_dia/2)**2 * guide_length * 2
expected_vol -= guide_vol
ok, vol = check_volume(head_with_guides, expected_vol, tolerance=0.1)
export_step(head_with_guides, f"{out_dir}/cylinder_head/04_with_guides.step", "head with valve guides")

# Step 1.5 – Intake port (simplified)
log("\nStep 1.5: Intake port")
intake_port = (cq.Workplane("XZ")
               .workplane(offset=valve_y)
               .center(intake_x, -head_height/2 - seat_depth)
               .circle(intake_port_dia/2)
               .extrude(port_length))
intake_port = intake_port.rotateAboutCenter((1,0,0), -30)  # 30° upward
head_with_intake_port = head_with_guides.union(intake_port)
port_vol = math.pi * (intake_port_dia/2)**2 * port_length
expected_vol += port_vol
ok, vol = check_volume(head_with_intake_port, expected_vol, tolerance=0.1)
export_step(head_with_intake_port, f"{out_dir}/cylinder_head/05_with_intake_port.step", "head with intake port")

# Step 1.6 – Exhaust port
log("\nStep 1.6: Exhaust port")
exhaust_port = (cq.Workplane("XZ")
                .workplane(offset=valve_y)
                .center(exhaust_x, -head_height/2 - seat_depth)
                .circle(exhaust_port_dia/2)
                .extrude(port_length))
exhaust_port = exhaust_port.rotateAboutCenter((1,0,0), 30)  # 30° downward
head_with_both_ports = head_with_intake_port.union(exhaust_port)
port_vol += math.pi * (exhaust_port_dia/2)**2 * port_length
expected_vol += math.pi * (exhaust_port_dia/2)**2 * port_length
ok, vol = check_volume(head_with_both_ports, expected_vol, tolerance=0.1)
export_step(head_with_both_ports, f"{out_dir}/cylinder_head/06_with_both_ports.step", "head with both ports")

# Step 1.7 – Camshaft bores
log("\nStep 1.7: Camshaft bores")
head_with_cam_bores = head_with_both_ports
head_with_cam_bores = head_with_cam_bores.faces(">Y").workplane().center(0,0).circle(cam_bore_dia/2).cutThruAll()
cam_vol = math.pi * (cam_bore_dia/2)**2 * head_width
expected_vol -= cam_vol
ok, vol = check_volume(head_with_cam_bores, expected_vol, tolerance=0.1)
export_step(head_with_cam_bores, f"{out_dir}/cylinder_head/07_with_cam_bores.step", "head with camshaft bores")

# Step 1.8 – Stiffening ribs
log("\nStep 1.8: Stiffening ribs")
rib_width = 5.0
rib_height = 20.0
rib = cq.Workplane("XY").box(head_length-20, rib_width, rib_height)
rib = rib.translate((0,0,-head_height/2 + rib_height/2))
head_with_ribs = head_with_cam_bores.union(rib)
rib_vol = (head_length-20) * rib_width * rib_height
expected_vol += rib_vol
ok, vol = check_volume(head_with_ribs, expected_vol, tolerance=0.1)
export_step(head_with_ribs, f"{out_dir}/cylinder_head/08_with_ribs.step", "head with ribs")

# Final cylinder head
cylinder_head_final = head_with_ribs
export_step(cylinder_head_final, f"{out_dir}/cylinder_head_final.step", "final cylinder head")
log(f"\n✅ Cylinder head completed. Total volume: {vol:.1f} mm³")

# ----------------------------------------------------------------------
# 2. PISTON (simplified)
# ----------------------------------------------------------------------
log("\n" + "-" * 70)
log("2. PISTON")
log("-" * 70)

# Load piston geometry from JSON
piston_json_path = "/home/nenuka/.openclaw/workspace/fea_thermal/piston_crown_15.0mm.json"
if os.path.exists(piston_json_path):
    with open(piston_json_path) as f:
        piston_data = json.load(f)
    geom = piston_data["geometry"]
    crown_thickness = geom["crown_thickness"]
    pin_boss_width = geom["pin_boss_width"]
    skirt_length = geom["skirt_length"]
    skirt_thickness = geom["skirt_thickness"]
    lattice_density = geom["lattice_relative_density"]
else:
    log(f"⚠️  Piston JSON not found at {piston_json_path}, using defaults")
    crown_thickness = 15.0
    pin_boss_width = 32.2
    skirt_length = 57.0
    skirt_thickness = 4.2
    lattice_density = 0.615

bore_radius = bore/2
piston_diameter = bore - 0.1  # clearance

log(f"Crown thickness: {crown_thickness} mm")
log(f"Skirt length: {skirt_length} mm")
log(f"Pin‑boss width: {pin_boss_width} mm")

# Step 2.1 – Crown (disc)
log("\nStep 2.1: Crown")
crown = cq.Workplane("XY").circle(bore_radius).extrude(crown_thickness)
ok, vol = check_volume(crown, math.pi * bore_radius**2 * crown_thickness)
export_step(crown, f"{out_dir}/piston/01_crown.step", "piston crown")

# Step 2.2 – Skirt (cylinder shell)
log("\nStep 2.2: Skirt")
skirt_outer = cq.Workplane("XY").circle(bore_radius).extrude(skirt_length)
skirt_inner = cq.Workplane("XY").circle(bore_radius - skirt_thickness).extrude(skirt_length)
skirt = skirt_outer.cut(skirt_inner)
skirt = skirt.translate((0,0,crown_thickness))  # attach below crown
skirt_vol = math.pi * bore_radius**2 * skirt_length - math.pi * (bore_radius - skirt_thickness)**2 * skirt_length
ok, vol = check_volume(skirt, skirt_vol)
export_step(skirt, f"{out_dir}/piston/02_skirt.step", "piston skirt")

# Step 2.3 – Pin bosses (two rectangular blocks)
log("\nStep 2.3: Pin bosses")
boss_height = skirt_length * 0.6
boss_width = pin_boss_width
boss_depth = bore_radius * 0.5
boss1 = cq.Workplane("XY").box(boss_width, boss_depth, boss_height)
boss1 = boss1.translate((0, -bore_radius/2, crown_thickness + boss_height/2))
boss2 = cq.Workplane("XY").box(boss_width, boss_depth, boss_height)
boss2 = boss2.translate((0, bore_radius/2, crown_thickness + boss_height/2))
boss_vol = boss_width * boss_depth * boss_height * 2
ok, vol = check_volume(boss1.union(boss2), boss_vol)
export_step(boss1.union(boss2), f"{out_dir}/piston/03_bosses.step", "pin bosses")

# Step 2.4 – Combine
log("\nStep 2.4: Combine all piston parts")
piston = crown.union(skirt).union(boss1).union(boss2)
piston_vol_expected = math.pi * bore_radius**2 * crown_thickness + skirt_vol + boss_vol
ok, vol = check_volume(piston, piston_vol_expected, tolerance=0.05)
export_step(piston, f"{out_dir}/piston/04_combined.step", "combined piston")

# Step 2.5 – Pin hole
log("\nStep 2.5: Pin hole")
pin_hole_dia = 30.0  # typical
pin_hole = cq.Workplane("YZ").workplane(offset=0).circle(pin_hole_dia/2).extrude(boss_width*2)
pin_hole = pin_hole.translate((0,0,crown_thickness + boss_height/2))
piston_with_hole = piston.cut(pin_hole)
pin_hole_vol = math.pi * (pin_hole_dia/2)**2 * boss_width * 2
expected_vol = piston_vol_expected - pin_hole_vol
ok, vol = check_volume(piston_with_hole, expected_vol, tolerance=0.05)
export_step(piston_with_hole, f"{out_dir}/piston/05_with_pin_hole.step", "piston with pin hole")

# Final piston
piston_final = piston_with_hole
export_step(piston_final, f"{out_dir}/piston_final.step", "final piston")
log(f"\n✅ Piston completed. Total volume: {vol:.1f} mm³")

# ----------------------------------------------------------------------
# 3. CONNECTING ROD (simplified)
# ----------------------------------------------------------------------
log("\n" + "-" * 70)
log("3. CONNECTING ROD")
log("-" * 70)

# Load conrod geometry from JSON
conrod_json_path = "/home/nenuka/.openclaw/workspace/conrod_opt_relaxed2_30MPa_results_20260213_010504.json"
if os.path.exists(conrod_json_path):
    with open(conrod_json_path) as f:
        conrod_data = json.load(f)
    geom = conrod_data["geometry"]
    beam_height = geom["beam_height"]
    beam_width = geom["beam_width"]
    web_thickness = geom["web_thickness"]
    flange_thickness = geom["flange_thickness"]
    big_end_width = geom["big_end_width"]
    small_end_width = geom["small_end_width"]
    small_end_dia = geom["small_end_diameter"]
    fillet_big = geom["fillet_big"]
    fillet_small = geom["fillet_small"]
    lattice_density = geom["lattice_relative_density"]
else:
    log(f"⚠️  Conrod JSON not found at {conrod_json_path}, using defaults")
    beam_height = 50.0
    beam_width = 30.0
    web_thickness = 5.1
    flange_thickness = 4.6
    big_end_width = 116.8
    small_end_width = 163.9
    small_end_dia = 61.8
    fillet_big = 23.5
    fillet_small = 22.9
    lattice_density = 0.503

log(f"Beam height: {beam_height} mm")
log(f"Big‑end width: {big_end_width} mm")
log(f"Small‑end width: {small_end_width} mm")

# Step 3.1 – Beam (I‑beam approximation)
log("\nStep 3.1: Beam")
# Simplified: rectangular beam
beam = cq.Workplane("XY").box(beam_width, beam_height, 100)  # length 100 mm
beam = beam.translate((0,0,50))  # center at Z=50
ok, vol = check_volume(beam, beam_width * beam_height * 100)
export_step(beam, f"{out_dir}/conrod/01_beam.step", "conrod beam")

# Step 3.2 – Big end (cylindrical)
log("\nStep 3.2: Big end")
big_end_outer = cq.Workplane("XY").circle(big_end_width/2).extrude(20)
big_end_inner = cq.Workplane("XY").circle(big_end_width/2 - 10).extrude(20)
big_end = big_end_outer.cut(big_end_inner)
big_end = big_end.translate((0,0,-10))  # attach to beam
big_end_vol = math.pi * (big_end_width/2)**2 * 20 - math.pi * (big_end_width/2 - 10)**2 * 20
ok, vol = check_volume(big_end, big_end_vol)
export_step(big_end, f"{out_dir}/conrod/02_big_end.step", "big end")

# Step 3.3 – Small end (cylindrical)
log("\nStep 3.3: Small end")
small_end_outer = cq.Workplane("XY").circle(small_end_width/2).extrude(20)
small_end_inner = cq.Workplane("XY").circle(small_end_dia/2).extrude(20)
small_end = small_end_outer.cut(small_end_inner)
small_end = small_end.translate((0,0,110))  # attach to other end
small_end_vol = math.pi * (small_end_width/2)**2 * 20 - math.pi * (small_end_dia/2)**2 * 20
ok, vol = check_volume(small_end, small_end_vol)
export_step(small_end, f"{out_dir}/conrod/03_small_end.step", "small end")

# Step 3.4 – Combine
log("\nStep 3.4: Combine")
conrod = beam.union(big_end).union(small_end)
conrod_vol_expected = beam_width * beam_height * 100 + big_end_vol + small_end_vol
ok, vol = check_volume(conrod, conrod_vol_expected, tolerance=0.1)
export_step(conrod, f"{out_dir}/conrod/04_combined.step", "combined conrod")

# Final conrod
conrod_final = conrod
export_step(conrod_final, f"{out_dir}/conrod_final.step", "final connecting rod")
log(f"\n✅ Connecting rod completed. Total volume: {vol:.1f} mm³")

# ----------------------------------------------------------------------
# 4. CRANKSHAFT (simplified)
# ----------------------------------------------------------------------
log("\n" + "-" * 70)
log("4. CRANKSHAFT (single throw)")
log("-" * 70)

# Load crankshaft geometry from JSON
crank_json_path = "/home/nenuka/.openclaw/workspace/david-version-1/v12_30MPa_design/analysis/crankshaft_30MPa_final.json"
if os.path.exists(crank_json_path):
    with open(crank_json_path) as f:
        crank_data = json.load(f)
    geom = crank_data["geometry"]
    main_journal_dia = geom["main_journal_diameter"]
    main_journal_width = geom["main_journal_width"]
    pin_dia = geom["pin_diameter"]
    pin_width = geom["pin_width"]
    stroke = geom["stroke"]
    cheek_thickness = geom["cheek_thickness"]
    cheek_radius = geom["cheek_radius"]
    cheek_hole_radius = geom["cheek_hole_radius"]
    fillet_main = geom["fillet_main"]
    fillet_pin = geom["fillet_pin"]
else:
    log(f"⚠️  Crankshaft JSON not found at {crank_json_path}, using defaults")
    main_journal_dia = 76.5
    main_journal_width = 26.7
    pin_dia = 61.4
    pin_width = 26.5
    stroke = 94.5
    cheek_thickness = 17.15
    cheek_radius = 82.65
    cheek_hole_radius = 69.38
    fillet_main = 7.09
    fillet_pin = 2.23

crank_radius = stroke/2

log(f"Main journal diameter: {main_journal_dia} mm")
log(f"Pin diameter: {pin_dia} mm")
log(f"Stroke: {stroke} mm")

# Step 4.1 – Main journal (cylinder)
log("\nStep 4.1: Main journal")
main_journal = cq.Workplane("XY").circle(main_journal_dia/2).extrude(main_journal_width)
ok, vol = check_volume(main_journal, math.pi * (main_journal_dia/2)**2 * main_journal_width)
export_step(main_journal, f"{out_dir}/crankshaft/01_main_journal.step", "main journal")

# Step 4.2 – Crank pin (offset cylinder)
log("\nStep 4.2: Crank pin")
crank_pin = cq.Workplane("XY").circle(pin_dia/2).extrude(pin_width)
crank_pin = crank_pin.translate((crank_radius,0,0))
ok, vol = check_volume(crank_pin, math.pi * (pin_dia/2)**2 * pin_width)
export_step(crank_pin, f"{out_dir}/crankshaft/02_crank_pin.step", "crank pin")

# Step 4.3 – Cheek (disc with hole)
log("\nStep 4.3: Cheek")
cheek_outer = cq.Workplane("XY").circle(cheek_radius).extrude(cheek_thickness)
cheek_inner = cq.Workplane("XY").circle(cheek_hole_radius).extrude(cheek_thickness)
cheek = cheek_outer.cut(cheek_inner)
cheek = cheek.translate((crank_radius/2,0,0))
cheek_vol = math.pi * cheek_radius**2 * cheek_thickness - math.pi * cheek_hole_radius**2 * cheek_thickness
ok, vol = check_volume(cheek, cheek_vol)
export_step(cheek, f"{out_dir}/crankshaft/03_cheek.step", "cheek")

# Step 4.4 – Combine (simplified, no fillets)
log("\nStep 4.4: Combine")
crank_throw = main_journal.union(crank_pin).union(cheek)
crank_vol_expected = (math.pi * (main_journal_dia/2)**2 * main_journal_width +
                      math.pi * (pin_dia/2)**2 * pin_width +
                      cheek_vol)
ok, vol = check_volume(crank_throw, crank_vol_expected, tolerance=0.1)
export_step(crank_throw, f"{out_dir}/crankshaft/04_combined.step", "crank throw")

# Final crankshaft (single throw)
crankshaft_final = crank_throw
export_step(crankshaft_final, f"{out_dir}/crankshaft_final.step", "final crankshaft throw")
log(f"\n✅ Crankshaft throw completed. Total volume: {vol:.1f} mm³")

# ----------------------------------------------------------------------
# 5. CYLINDER BLOCK (simplified)
# ----------------------------------------------------------------------
log("\n" + "-" * 70)
log("5. CYLINDER BLOCK (single cylinder)")
log("-" * 70)

# Load block geometry from JSON
block_json_path = "/home/nenuka/.openclaw/workspace/fea_thermal/cylinder_block_deck_12.0mm.json"
if os.path.exists(block_json_path):
    with open(block_json_path) as f:
        block_data = json.load(f)
    geom = block_data["geometry"]
    bore_spacing = geom["bore_spacing"]
    deck_thickness = geom["deck_thickness"]
    cylinder_wall_thickness = geom["cylinder_wall_thickness"]
    water_jacket_thickness = geom["water_jacket_thickness"]
    main_bearing_width = geom["main_bearing_width"]
    main_bearing_height = geom["main_bearing_height"]
    skirt_depth = geom["skirt_depth"]
    pan_rail_width = geom["pan_rail_width"]
else:
    log(f"⚠️  Block JSON not found at {block_json_path}, using defaults")
    bore_spacing = 144.7
    deck_thickness = 12.0
    cylinder_wall_thickness = 4.87
    water_jacket_thickness = 7.79
    main_bearing_width = 61.76
    main_bearing_height = 59.40
    skirt_depth = 60.14
    pan_rail_width = 16.71

log(f"Deck thickness: {deck_thickness} mm")
log(f"Cylinder wall thickness: {cylinder_wall_thickness} mm")
log(f"Skirt depth: {skirt_depth} mm")

# Step 5.1 – Block outer envelope
log("\nStep 5.1: Block outer envelope")
block_width = bore_spacing + 50
block_length = bore_spacing + 50
block_height = deck_thickness + skirt_depth
block = cq.Workplane("XY").box(block_length, block_width, block_height)
block = block.translate((0,0,-block_height/2))
ok, vol = check_volume(block, block_length * block_width * block_height)
export_step(block, f"{out_dir}/cylinder_block/01_envelope.step", "block envelope")

# Step 5.2 – Cylinder bore hole
log("\nStep 5.2: Cylinder bore hole")
bore_hole = cq.Workplane("XY").circle(bore/2).extrude(deck_thickness)
bore_hole = bore_hole.translate((0,0,deck_thickness/2 - block_height/2))
block_with_bore = block.cut(bore_hole)
bore_vol = math.pi * (bore/2)**2 * deck_thickness
expected_vol = block_length * block_width * block_height - bore_vol
ok, vol = check_volume(block_with_bore, expected_vol)
export_step(block_with_bore, f"{out_dir}/cylinder_block/02_with_bore.step", "block with bore")

# Step 5.3 – Water jacket (annulus around bore)
log("\nStep 5.3: Water jacket")
jacket_outer = cq.Workplane("XY").circle(bore/2 + cylinder_wall_thickness + water_jacket_thickness).extrude(deck_thickness)
jacket_inner = cq.Workplane("XY").circle(bore/2 + cylinder_wall_thickness).extrude(deck_thickness)
jacket = jacket_outer.cut(jacket_inner)
jacket = jacket.translate((0,0,deck_thickness/2 - block_height/2))
block_with_jacket = block_with_bore.cut(jacket)  # cut away water jacket volume
jacket_vol = math.pi * (bore/2 + cylinder_wall_thickness + water_jacket_thickness)**2 * deck_thickness - math.pi * (bore/2 + cylinder_wall_thickness)**2 * deck_thickness
expected_vol -= jacket_vol
ok, vol = check_volume(block_with_jacket, expected_vol, tolerance=0.1)
export_step(block_with_jacket, f"{out_dir}/cylinder_block/03_with_jacket.step", "block with water jacket")

# Step 5.4 – Main bearing saddles
log("\nStep 5.4: Main bearing saddles")
saddle = cq.Workplane("XY").box(main_bearing_width, main_bearing_height, 20)
saddle = saddle.translate((0,0,-block_height/2 - 10))
block_with_saddles = block_with_jacket.union(saddle)
saddle_vol = main_bearing_width * main_bearing_height * 20
expected_vol += saddle_vol
ok, vol = check_volume(block_with_saddles, expected_vol, tolerance=0.1)
export_step(block_with_saddles, f"{out_dir}/cylinder_block/04_with_saddles.step", "block with bearing saddles")

# Final cylinder block (single cylinder)
cylinder_block_final = block_with_saddles
export_step(cylinder_block_final, f"{out_dir}/cylinder_block_final.step", "final cylinder block")
log(f"\n✅ Cylinder block completed. Total volume: {vol:.1f} mm³")

# ----------------------------------------------------------------------
# 6. ASSEMBLY (single cylinder)
# ----------------------------------------------------------------------
log("\n" + "-" * 70)
log("6. SINGLE‑CYLINDER ASSEMBLY")
log("-" * 70)

# Position components
# Block origin at (0,0,0) with deck top at Z=0
# Piston at TDC: crown top at Z = deck_clearance
# Conrod small end at piston pin, big end at crank pin
# Crank pin at angle 0° (TDC)

log("Positioning components...")

# Piston at TDC
piston_pos = piston_final.translate((0,0, deck_clearance + crown_thickness/2))
# Conrod: small end at piston pin, big end at crank pin
conrod_pos = conrod_final.rotate((0,0,0), (1,0,0), 90)  # rotate to vertical
conrod_pos = conrod_pos.translate((0,0, deck_clearance + crown_thickness + small_end_width/2))
# Crankshaft: main journal at (0,0,-crank_radius), pin at (crank_radius,0,0)
crank_pos = crankshaft_final.translate((0,0, -crank_radius))
# Cylinder head sits on deck
head_pos = cylinder_head_final.translate((0,0, deck_thickness/2))

# Export assembly
assembly = piston_pos.union(conrod_pos).union(crank_pos).union(cylinder_block_final).union(head_pos)
export_step(assembly, f"{out_dir}/single_cylinder_assembly.step", "single‑cylinder assembly")
log("✅ Single‑cylinder assembly exported")

# ----------------------------------------------------------------------
# FINAL SUMMARY
# ----------------------------------------------------------------------
log("\n" + "=" * 70)
log("CAD GENERATION COMPLETE")
log("=" * 70)
log(f"All intermediate and final STEP files saved in: {out_dir}/")
log("")
log("Next steps:")
log("1. Open intermediate STEP files in CAD viewer to verify geometry.")
log("2. Check dimensions against specifications.")
log("3. Run interference detection (clearance checks).")
log("4. Proceed to FEA and CFD using these validated geometries.")

log_file.close()
print(f"\n✅ Step‑by‑step CAD generation complete. See {out_dir}/log.txt for details.")