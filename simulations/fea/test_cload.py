#!/usr/bin/env python3
"""
Test Calculix with *CLOAD (point force).
"""
import subprocess
import os
import tempfile

inp = """*NODE
1,0,0,0
2,10,0,0
3,10,10,0
4,0,10,0
5,0,0,10
6,10,0,10
7,10,10,10
8,0,10,10
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
*STEP
*STATIC
*CLOAD
5,1,1000
6,1,1000
7,1,1000
8,1,1000
*EL PRINT,ELSET=E1
S
*END STEP
"""

with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "testcload.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    print("Input written")
    
    # Run ccx with both stdout and stderr
    result = subprocess.run(["ccx", "-i", "testcload"], cwd=tmpdir,
                          capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    print(f"stdout length: {len(result.stdout)}")
    print(f"stderr length: {len(result.stderr)}")
    if result.stdout:
        print("stdout first 500:", result.stdout[:500])
    if result.stderr:
        print("stderr:", result.stderr)
    
    # Check files
    for fname in os.listdir(tmpdir):
        if fname.startswith("testcload."):
            fpath = os.path.join(tmpdir, fname)
            size = os.path.getsize(fpath)
            print(f"  {fname}: {size} bytes")
            if size > 0 and size < 1000:
                with open(fpath, 'r') as f:
                    content = f.read()
                print(f"    First 300 chars: {content[:300]}")