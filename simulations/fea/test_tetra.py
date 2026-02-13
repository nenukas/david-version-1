#!/usr/bin/env python3
"""
Test Calculix with a single tetrahedron element.
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
    print("Input written")
    
    result = subprocess.run(["ccx", "-i", "tet"], cwd=tmpdir,
                          capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    print("="*60)
    print("STDOUT:")
    print(result.stdout)
    print("="*60)
    print("STDERR:")
    print(result.stderr)
    print("="*60)
    
    for fname in os.listdir(tmpdir):
        if fname.startswith("tet."):
            fpath = os.path.join(tmpdir, fname)
            size = os.path.getsize(fpath)
            print(f"  {fname}: {size} bytes")