#!/usr/bin/env python3
"""
Simple cantilever beam with single element.
"""
import subprocess
import os
import tempfile

def create_simple_inp():
    inp = []
    inp.append("** Simple cantilever beam (single element)")
    inp.append("*NODE")
    inp.append("1,0,0,0")
    inp.append("2,10,0,0")
    inp.append("3,10,10,0")
    inp.append("4,0,10,0")
    inp.append("5,0,0,10")
    inp.append("6,10,0,10")
    inp.append("7,10,10,10")
    inp.append("8,0,10,10")
    inp.append("*ELEMENT,TYPE=C3D8,ELSET=E1")
    inp.append("1,1,2,3,4,5,6,7,8")
    inp.append("*MATERIAL,NAME=STEEL")
    inp.append("*ELASTIC")
    inp.append("210000,0.3")
    inp.append("*SOLID SECTION,ELSET=E1,MATERIAL=STEEL")
    inp.append("*NSET,NSET=FIX")
    inp.append("1,2,3,4")
    inp.append("*BOUNDARY")
    inp.append("FIX,1,3")
    inp.append("*STEP")
    inp.append("*STATIC")
    inp.append("*CLOAD")
    inp.append("5,F1,1000")
    inp.append("6,F1,1000")
    inp.append("7,F1,1000")
    inp.append("8,F1,1000")
    inp.append("*EL PRINT,ELSET=E1")
    inp.append("S")
    inp.append("*END STEP")
    return "\n".join(inp)

with tempfile.TemporaryDirectory() as tmpdir:
    inp = create_simple_inp()
    with open(os.path.join(tmpdir, "simple.inp"), 'w') as f:
        f.write(inp)
    print("Running ccx...")
    result = subprocess.run(["ccx", "-i", "simple"], cwd=tmpdir, 
                          capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    if result.stderr:
        print("stderr:", result.stderr[:300])
    
    dat_path = os.path.join(tmpdir, "simple.dat")
    if os.path.exists(dat_path):
        size = os.path.getsize(dat_path)
        print(f".dat size: {size} bytes")
        if size > 0:
            with open(dat_path, 'r') as f:
                lines = f.readlines()
            print(f".dat lines: {len(lines)}")
            for i, line in enumerate(lines[:20]):
                if line.strip():
                    print(f"{i:3}: {line.rstrip()}")
    else:
        print("No .dat file")
    
    # List all files
    for f in os.listdir(tmpdir):
        if f.startswith("simple."):
            print(f"  {f}")