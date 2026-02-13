#!/usr/bin/env python3
"""
Single hex element test.
"""
import subprocess
import os
import tempfile

inp = """*HEADING
Single hex element test
*NODE
1,0,0,0
2,10,0,0
3,10,10,0
4,0,10,0
5,0,0,10
6,10,0,10
7,10,10,10
8,0,10,10
*ELEMENT,TYPE=C3D8,ELSET=CUBE
1,1,2,3,4,5,6,7,8
*SOLID SECTION,ELSET=CUBE,MATERIAL=STEEL
*MATERIAL,NAME=STEEL
*ELASTIC
210000,0.3
*NSET,NSET=FIXED
1,2,3,4
*BOUNDARY
FIXED,1,3
*STEP
*STATIC
*CLOAD
5,3,-1000
6,3,-1000
7,3,-1000
8,3,-1000
*EL PRINT,ELSET=CUBE
S
*END STEP
"""

with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "hex.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    print("Running ccx...")
    result = subprocess.run(["ccx", "-i", "hex"], cwd=tmpdir,
                          capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    if result.returncode != 0:
        print("stderr:", result.stderr[:300])
        print("stdout:", result.stdout[:500])
    else:
        print("Success!")
    
    dat_path = os.path.join(tmpdir, "hex.dat")
    if os.path.exists(dat_path):
        size = os.path.getsize(dat_path)
        print(f".dat size: {size}")
        if size > 0:
            with open(dat_path, 'r') as f:
                content = f.read()
            print("=== .dat content ===")
            print(content)
    else:
        print("No .dat")
    
    for f in os.listdir(tmpdir):
        if f.startswith("hex."):
            print(f"  {f}")