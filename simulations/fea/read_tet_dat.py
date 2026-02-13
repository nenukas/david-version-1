#!/usr/bin/env python3
"""
Read tet.dat from previous run.
"""
import subprocess
import os
import tempfile

inp = """*HEADING
Simple tetrahedron test
*NODE
1,0,0,0
2,1,0,0
3,0,1,0
4,0,0,1
*ELEMENT,TYPE=C3D4,ELSET=TET
1,1,2,3,4
*SOLID SECTION,ELSET=TET,MATERIAL=STEEL
*MATERIAL,NAME=STEEL
*ELASTIC
210000,0.3
*NSET,NSET=FIXED
1,2,3
*BOUNDARY
FIXED,1,3
*STEP
*STATIC
*CLOAD
4,2,100
*EL PRINT,ELSET=TET
S
*END STEP
"""

with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "tet.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    subprocess.run(["ccx", "-i", "tet"], cwd=tmpdir, capture_output=True)
    dat_path = os.path.join(tmpdir, "tet.dat")
    if os.path.exists(dat_path):
        with open(dat_path, 'r') as f:
            content = f.read()
        print("=== .dat content ===")
        print(content)
        print("=== end ===")
        # Parse for stress
        lines = content.splitlines()
        in_stress = False
        for line in lines:
            if 'STRESS' in line:
                in_stress = True
                continue
            if in_stress and line.strip():
                print(f"Stress line: {line}")
                parts = line.split()
                print(f"Parts: {parts}")
                # Expect something like "1  1.234E+00  2.345E+00 ..."
                break