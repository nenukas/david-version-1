#!/usr/bin/env python3
"""
Coupled thermo‑mechanical FEA of piston crown (axisymmetric).
Step 1: steady‑state heat transfer (combustion heat flux + coolant convection).
Step 2: static stress with pressure + thermal load.
"""
import numpy as np
import subprocess
import os
import sys

# ========== DIMENSIONS (mm) ==========
bore_radius = 94.5 / 2          # mm
crown_thickness = 12.294        # mm

# ========== MATERIAL (forged steel) ==========
young_modulus = 210000.0        # MPa
poisson = 0.29
density = 7.85e-9               # tonne/mm³
conductivity = 0.05             # W/(mm·K)  (50 W/(m·K))
specific_heat = 500.0e6         # J/(tonne·K) = 500 J/(kg·K) × 1e6
expansion_coeff = 1.2e-5        # 1/K (thermal expansion)

# ========== LOADS ==========
pressure = 30.0                 # MPa (300 bar)
heat_flux = 10.0                # W/mm² (10 MW/m²)
convection_coeff = 0.005        # W/(mm²·K) (5000 W/(m²·K))
coolant_temp = 90.0             # °C
initial_temp = 90.0             # °C

# ========== MESH ==========
nr = 20          # elements radial
nz = 10          # elements thickness

print("Generating axisymmetric thermo‑mechanical mesh...")
print(f"Radius: 0–{bore_radius} mm, thickness: {crown_thickness} mm")
print(f"Pressure: {pressure} MPa, Heat flux: {heat_flux} W/mm²")
print(f"Convection: h={convection_coeff} W/(mm²·K), T_cool={coolant_temp}°C")

# Node generation
nodes = []
for iz in range(nz + 1):
    z = iz * crown_thickness / nz
    for ir in range(nr + 1):
        r = ir * bore_radius / nr
        nodes.append((r, z))

# Element connectivity (CAX4)
elements = []
for iz in range(nz):
    for ir in range(nr):
        n1 = iz * (nr + 1) + ir
        n2 = iz * (nr + 1) + ir + 1
        n3 = (iz + 1) * (nr + 1) + ir + 1
        n4 = (iz + 1) * (nr + 1) + ir
        elements.append((n1 + 1, n2 + 1, n3 + 1, n4 + 1))

nnodes = len(nodes)
nelements = len(elements)
print(f"Mesh: {nnodes} nodes, {nelements} elements")

# ========== WRITE CALCULIX INPUT ==========
inp_filename = "piston_crown_thermomech.inp"
with open(inp_filename, "w") as f:
    # Header
    f.write("*HEADING\n")
    f.write("Coupled thermo‑mechanical analysis of piston crown (30 MPa + 10 MW/m²)\n")
    f.write("** Slothworks V12 at 3000 whp\n")
    # Nodes
    f.write("*NODE\n")
    for i, (r, z) in enumerate(nodes):
        f.write(f"{i+1}, {r:.6f}, {z:.6f}, 0.0\n")
    # Elements
    f.write("*ELEMENT, TYPE=CAX4, ELSET=CROWN\n")
    for i, (n1, n2, n3, n4) in enumerate(elements):
        f.write(f"{i+1}, {n1}, {n2}, {n3}, {n4}\n")
    # Material – mechanical
    f.write("*MATERIAL, NAME=STEEL\n")
    f.write("*ELASTIC\n")
    f.write(f"{young_modulus}, {poisson}\n")
    # Material – thermal
    f.write("*CONDUCTIVITY\n")
    f.write(f"{conductivity}\n")
    f.write("*DENSITY\n")
    f.write(f"{density}\n")
    f.write("*SPECIFIC HEAT\n")
    f.write(f"{specific_heat}\n")
    f.write("*EXPANSION\n")
    f.write(f"{expansion_coeff}\n")
    # Section
    f.write("*SOLID SECTION, ELSET=CROWN, MATERIAL=STEEL\n")
    f.write("1.0,\n")
    # Boundary conditions – mechanical
    # Fix bottom edge (z=0) in Z direction
    f.write("*NSET, NSET=FIXED_Z\n")
    for iz in [0]:
        for ir in range(nr + 1):
            node_id = iz * (nr + 1) + ir + 1
            f.write(f"{node_id},\n")
    # Symmetry on axis (r=0) in radial direction
    f.write("*NSET, NSET=SYMMETRY_R\n")
    for iz in range(nz + 1):
        for ir in [0]:
            node_id = iz * (nr + 1) + ir + 1
            f.write(f"{node_id},\n")
    # Thermal boundary conditions
    # Top surface (crown) receives heat flux
    f.write("*SURFACE, NAME=TOP, TYPE=ELEMENT\n")
    for iz in [nz - 1]:
        for ir in range(nr):
            elem_id = iz * nr + ir + 1
            f.write(f"{elem_id}, S3\n")
    # Bottom surface (coolant side) convection
    f.write("*SURFACE, NAME=BOTTOM, TYPE=ELEMENT\n")
    for iz in [0]:
        for ir in range(nr):
            elem_id = iz * nr + ir + 1
            f.write(f"{elem_id}, S1\n")
    # Initial conditions
    f.write("*INITIAL CONDITIONS, TYPE=TEMPERATURE\n")
    f.write(f"NALL, {initial_temp}\n")
    # ========== STEP 1: STEADY‑STATE HEAT TRANSFER ==========
    f.write("*STEP\n")
    f.write("*HEAT TRANSFER, STEADY STATE\n")
    # Boundary conditions – temperature on axis? No, just convection.
    # Convection on bottom surface
    f.write("*FILM\n")
    f.write(f"BOTTOM, {coolant_temp}, {convection_coeff}\n")
    # Heat flux on top surface
    f.write("*DFLUX\n")
    f.write(f"TOP, {heat_flux}\n")
    # Output
    f.write("*NODE FILE\n")
    f.write("NT\n")
    f.write("*EL FILE\n")
    f.write("HFL\n")
    f.write("*END STEP\n")
    # ========== STEP 2: STATIC STRESS WITH TEMPERATURE ==========
    f.write("*STEP\n")
    f.write("*STATIC\n")
    # Apply temperature from previous step
    f.write("*TEMPERATURE, FILE=piston_crown_thermomech, BSTEP=1\n")
    # Mechanical boundary conditions
    f.write("*BOUNDARY\n")
    f.write("FIXED_Z, 2, 2\n")
    f.write("SYMMETRY_R, 1, 1\n")
    # Pressure load
    f.write("*DLOAD\n")
    f.write(f"TOP, P, {pressure}\n")
    # Output
    f.write("*NODE FILE\n")
    f.write("U\n")
    f.write("*EL FILE\n")
    f.write("S, E\n")
    f.write("*END STEP\n")

print(f"Written {inp_filename}")

# ========== RUN CALCULIX ==========
print("Running CalculiX ccx...")
try:
    result = subprocess.run(
        ["ccx", "-i", inp_filename.rstrip('.inp')],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    if result.returncode == 0:
        print("✅ CalculiX completed successfully.")
        # Check output files
        for ext in ['.dat', '.frd', '.sta']:
            out = inp_filename.rstrip('.inp') + ext
            if os.path.exists(out):
                print(f"   Output: {out}")
    else:
        print("❌ CalculiX failed:")
        print(result.stderr[:500])
except FileNotFoundError:
    print("❌ CalculiX (ccx) not found in PATH.")
    sys.exit(1)

print("\n🎯 Next: parse temperature and combined stress.")