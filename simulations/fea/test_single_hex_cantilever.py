#!/usr/bin/env python3
"""
Single hex element cantilever.
"""
import subprocess
import os
import tempfile
import numpy as np

def create_inp():
    width = 70.0
    height = 30.0
    length = 47.5
    force = 180000.0
    
    inp = []
    inp.append("*HEADING")
    inp.append("Single hex cantilever")
    inp.append("*NODE")
    # Bottom face (z=0)
    inp.append("1,0,0,0")
    inp.append(f"2,{length},0,0")
    inp.append(f"3,{length},{width},0")
    inp.append(f"4,0,{width},0")
    # Top face (z=height)
    inp.append(f"5,0,0,{height}")
    inp.append(f"6,{length},0,{height}")
    inp.append(f"7,{length},{width},{height}")
    inp.append(f"8,0,{width},{height}")
    
    inp.append("*ELEMENT,TYPE=C3D8,ELSET=BEAM")
    inp.append("1,1,2,3,4,5,6,7,8")
    inp.append("*SOLID SECTION,ELSET=BEAM,MATERIAL=STEEL")
    inp.append("*MATERIAL,NAME=STEEL")
    inp.append("*ELASTIC")
    inp.append("210000,0.3")
    inp.append("*NSET,NSET=FIXED")
    inp.append("1,4,5,8")  # nodes at x=0 (fixed end)
    inp.append("*BOUNDARY")
    inp.append("FIXED,1,3")
    inp.append("*STEP")
    inp.append("*STATIC")
    # Apply force on nodes at x=length (2,3,6,7) in -z direction
    force_per_node = force / 4
    inp.append(f"2,3,{-force_per_node}")
    inp.append(f"3,3,{-force_per_node}")
    inp.append(f"6,3,{-force_per_node}")
    inp.append(f"7,3,{-force_per_node}")
    inp.append("*EL PRINT,ELSET=BEAM")
    inp.append("S")
    inp.append("*END STEP")
    return "\n".join(inp)

def analytical_stress(width, height, length, force):
    moment = force * length
    c = height / 2
    I = width * height**3 / 12
    return moment * c / I

inp = create_inp()
print("Generated inp")
print("First few lines:")
for i, line in enumerate(inp.splitlines()[:20]):
    print(f"{i+1:3}: {line}")

with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "single.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    
    result = subprocess.run(["ccx", "-i", "single"], cwd=tmpdir,
                          capture_output=True, text=True)
    print(f"\nReturn code: {result.returncode}")
    if result.returncode != 0:
        print("stderr:", result.stderr[:300])
    
    dat_path = os.path.join(tmpdir, "single.dat")
    if os.path.exists(dat_path) and os.path.getsize(dat_path) > 0:
        with open(dat_path, 'r') as f:
            lines = f.readlines()
        sxx = []
        for line in lines:
            if line.strip() and not line.startswith(" ") and not line.startswith("stresses"):
                parts = line.split()
                if len(parts) >= 8:
                    try:
                        sxx.append(float(parts[2]))
                    except:
                        pass
        if sxx:
            max_sxx = max(sxx, key=abs)
            avg_sxx = np.mean(sxx)
            print(f"FEA max Sxx: {max_sxx:.2f} MPa")
            sigma_anal = analytical_stress(width=70, height=30, length=47.5, force=180000)
            print(f"Analytical bending stress: {sigma_anal:.2f} MPa")
            diff = abs(max_sxx - sigma_anal) / sigma_anal * 100
            print(f"Difference: {diff:.1f}%")
        else:
            print("Could not parse stress")
            print("Sample .dat lines:")
            for line in lines[:10]:
                print(line.rstrip())
    else:
        print(".dat missing or empty")
        for f in os.listdir(tmpdir):
            if f.startswith("single."):
                print(f"  {f}")