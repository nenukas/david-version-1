#!/usr/bin/env python3
"""
Test parsing of Calculix .dat output.
"""
import subprocess
import os
import tempfile

inp = """*NODE
1,0,0,0
2,1,0,0
3,1,1,0
4,0,1,0
5,0,0,1
6,1,0,1
7,1,1,1
8,0,1,1
*ELEMENT, TYPE=C3D8, ELSET=E1
1,1,2,3,4,5,6,7,8
*MATERIAL, NAME=STEEL
*ELASTIC
210000,0.3
*SOLID SECTION, ELSET=E1, MATERIAL=STEEL
*NSET, NSET=FIXED
1,2,3,4
*BOUNDARY
FIXED,1,3
*EL PRINT, ELSET=E1
S
*STEP
*STATIC
*END STEP
"""

with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "test.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    
    # Run ccx
    subprocess.run(["ccx", "-i", "test"], cwd=tmpdir, capture_output=True)
    
    dat_path = os.path.join(tmpdir, "test.dat")
    if os.path.exists(dat_path):
        with open(dat_path, 'r') as f:
            lines = f.readlines()
        print("Total lines:", len(lines))
        for i, line in enumerate(lines):
            if 'STRESS' in line or 'S' in line or any(c.isdigit() for c in line):
                print(f"{i:4}: {line.rstrip()}")
    else:
        print("No .dat file")
    
    # List all files
    print("\nFiles in tempdir:")
    for f in os.listdir(tmpdir):
        print(f"  {f}")