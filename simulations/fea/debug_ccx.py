#!/usr/bin/env python3
"""
Debug Calculix run.
"""
import subprocess
import os
import tempfile
import sys

def test_ccx():
    """Run a minimal Calculix input and capture all output."""
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
*STEP
*STATIC
*END STEP
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        inp_path = os.path.join(tmpdir, "test.inp")
        with open(inp_path, 'w') as f:
            f.write(inp)
        
        print(f"Working dir: {tmpdir}")
        print("Files before ccx:", os.listdir(tmpdir))
        
        # Run ccx
        cmd = ["ccx", "-i", "test"]
        result = subprocess.run(
            cmd,
            cwd=tmpdir,
            capture_output=True,
            text=True
        )
        
        print("ccx stdout:", result.stdout[:500] if result.stdout else "(empty)")
        print("ccx stderr:", result.stderr[:500] if result.stderr else "(empty)")
        print("Return code:", result.returncode)
        
        print("\nFiles after ccx:")
        for f in os.listdir(tmpdir):
            print(f"  {f}")
            if f.endswith('.dat'):
                with open(os.path.join(tmpdir, f), 'r') as fp:
                    content = fp.read()
                    print(f"  First 500 chars:\n{content[:500]}")
            elif f.endswith('.sta'):
                with open(os.path.join(tmpdir, f), 'r') as fp:
                    print(f"  .sta content:\n{fp.read()}")

if __name__ == '__main__':
    test_ccx()