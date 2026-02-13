#!/usr/bin/env python3
"""
Cantilever beam with *CLOAD (point forces).
"""
import subprocess
import os
import tempfile
import numpy as np

def create_cantilever_inp_cload(width=70.0, height=30.0, length=47.5, force_n=180000.0):
    """Generate cantilever .inp with nodal forces."""
    nx, ny, nz = 2, 2, 2
    dx = length / nx
    dy = width / ny
    dz = height / nz
    
    E = 210000.0
    nu = 0.3
    density = 7.85e-9
    
    inp = []
    inp.append("** Cantilever beam validation (CLOAD)")
    inp.append("*NODE")
    node_id = 1
    nodes = {}
    for ix in range(nx + 1):
        x = ix * dx
        for iy in range(ny + 1):
            y = iy * dy
            for iz in range(nz + 1):
                z = iz * dz
                inp.append(f"{node_id},{x:.6f},{y:.6f},{z:.6f}")
                nodes[(ix, iy, iz)] = node_id
                node_id += 1
    
    inp.append("*ELEMENT, TYPE=C3D8, ELSET=BEAM")
    elem_id = 1
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                n1 = nodes[(ix, iy, iz)]
                n2 = nodes[(ix+1, iy, iz)]
                n3 = nodes[(ix+1, iy+1, iz)]
                n4 = nodes[(ix, iy+1, iz)]
                n5 = nodes[(ix, iy, iz+1)]
                n6 = nodes[(ix+1, iy, iz+1)]
                n7 = nodes[(ix+1, iy+1, iz+1)]
                n8 = nodes[(ix, iy+1, iz+1)]
                inp.append(f"{elem_id},{n1},{n2},{n3},{n4},{n5},{n6},{n7},{n8}")
                elem_id += 1
    
    inp.append("*MATERIAL, NAME=STEEL")
    inp.append("*ELASTIC")
    inp.append(f"{E:.1f},{nu:.2f}")
    inp.append("*DENSITY")
    inp.append(f"{density:.6e}")
    inp.append("*SOLID SECTION, ELSET=BEAM, MATERIAL=STEEL")
    
    # Fixed end nodes (x=0)
    fixed_nodes = []
    for iy in range(ny + 1):
        for iz in range(nz + 1):
            fixed_nodes.append(nodes[(0, iy, iz)])
    inp.append("*NSET, NSET=FIXED")
    inp.append(",".join(str(n) for n in fixed_nodes))
    inp.append("*BOUNDARY")
    inp.append("FIXED,1,3")
    
    # Load nodes (x=length)
    load_nodes = []
    for iy in range(ny + 1):
        for iz in range(nz + 1):
            load_nodes.append(nodes[(nx, iy, iz)])
    # Distribute total force equally among load nodes
    n_load = len(load_nodes)
    force_per_node = force_n / n_load
    inp.append("*STEP")
    inp.append("*STATIC")
    for node in load_nodes:
        # Apply force in -z direction (F3)
        inp.append(f"{node},3,{-force_per_node:.6f}")
    inp.append("*EL PRINT, ELSET=BEAM")
    inp.append("S")
    inp.append("*END STEP")
    
    return "\n".join(inp)

def analytical_bending_stress(width, height, length, force):
    moment = force * length
    c = height / 2
    I = width * height**3 / 12
    return moment * c / I

def parse_dat(dat_path):
    with open(dat_path, 'r') as f:
        lines = f.readlines()
    sxx_values = []
    for line in lines:
        if line.strip() and not line.startswith(" ") and not line.startswith("stresses"):
            # Format: "         1   1  0.000000E+00  0.000000E+00 ..."
            parts = line.split()
            if len(parts) >= 8:
                try:
                    sxx = float(parts[2])  # third column
                    sxx_values.append(sxx)
                except ValueError:
                    pass
    return sxx_values

# Run
width = 70.0
height = 30.0
length = 47.5
force = 180000.0

inp = create_cantilever_inp_cload(width, height, length, force)
print("Generated inp")

with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "cload.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    
    result = subprocess.run(["ccx", "-i", "cload"], cwd=tmpdir,
                          capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    if result.returncode != 0:
        print("stderr:", result.stderr[:500])
    
    dat_path = os.path.join(tmpdir, "cload.dat")
    if os.path.exists(dat_path) and os.path.getsize(dat_path) > 0:
        sxx = parse_dat(dat_path)
        if sxx:
            max_sxx = max(sxx, key=abs)
            avg_sxx = np.mean(sxx)
            print(f"FEA max Sxx: {max_sxx:.2f} MPa")
            print(f"FEA avg Sxx: {avg_sxx:.2f} MPa")
            sigma_anal = analytical_bending_stress(width, height, length, force)
            print(f"Analytical bending stress: {sigma_anal:.2f} MPa")
            diff = abs(max_sxx - sigma_anal) / sigma_anal * 100
            print(f"Difference: {diff:.1f}%")
        else:
            print("No stress values parsed")
            # Print .dat content for debugging
            with open(dat_path, 'r') as f:
                print(f".dat content:\n{f.read()[:500]}")
    else:
        print(".dat missing or empty")
        # List files
        for f in os.listdir(tmpdir):
            if f.startswith("cload."):
                print(f"  {f}")