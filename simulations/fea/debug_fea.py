#!/usr/bin/env python3
"""
Debug Calculix output.
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
*ELEMENT,TYPE=C3D8
1,1,2,3,4,5,6,7,8
*MATERIAL,NAME=STEEL
*ELASTIC
210000,0.3
*SOLID SECTION,ELSET=E1,MATERIAL=STEEL
*NSET,NSET=FIX
1,2,3,4
*BOUNDARY
FIX,1,3
*EL PRINT,ELSET=E1
S
*STEP
*STATIC
*END STEP
"""

with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "test.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    
    print("Running ccx...")
    result = subprocess.run(["ccx", "-i", "test"], cwd=tmpdir, capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    if result.stderr:
        print("stderr:", result.stderr[:500])
    
    print("\nFiles generated:")
    for fname in os.listdir(tmpdir):
        if fname.startswith("test."):
            fpath = os.path.join(tmpdir, fname)
            size = os.path.getsize(fpath)
            print(f"  {fname} ({size} bytes)")
            if size < 10000:
                with open(fpath, 'r') as f:
                    content = f.read()
                print(f"    First 500 chars:\n{content[:500]}")
                print()
            else:
                print(f"    (large file)")
    
    # Specifically check .dat
    dat_path = os.path.join(tmpdir, "test.dat")
    if os.path.exists(dat_path):
        with open(dat_path, 'r') as f:
            lines = f.readlines()
        print(f".dat lines: {len(lines)}")
        for i, line in enumerate(lines):
            if line.strip():
                print(f"{i:3}: {line.rstrip()}")
                if i > 20:
                    break