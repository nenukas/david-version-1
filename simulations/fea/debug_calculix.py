#!/usr/bin/env python3
"""
Debug Calculix input generation.
"""
import subprocess
import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(__file__))
from direct_calculix import create_cantilever_inp

# Generate inp
inp = create_cantilever_inp(width=70.0, height=30.0, length=47.5, force_n=180000.0)
lines = inp.splitlines()
print(f"Total lines: {len(lines)}")
print("First 30 lines:")
for i, line in enumerate(lines[:30]):
    print(f"{i+1:3}: {line}")
print("\nLast 30 lines:")
for i, line in enumerate(lines[-30:]):
    print(f"{len(lines)-30+i+1:3}: {line}")

# Check for long lines
print("\nLine lengths:")
for i, line in enumerate(lines):
    if len(line) > 80:
        print(f"Line {i+1}: length {len(line)}")
        print(f"  {line[:80]}...")

# Write and run
with tempfile.TemporaryDirectory() as tmpdir:
    inp_path = os.path.join(tmpdir, "debug.inp")
    with open(inp_path, 'w') as f:
        f.write(inp)
    print(f"\nWritten to {inp_path}")
    # Run ccx with verbose
    result = subprocess.run(["ccx", "-i", "debug"], cwd=tmpdir, 
                          capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    if result.returncode != 0:
        print("stderr:")
        print(result.stderr)
    else:
        print("ccx succeeded")
    
    # Check output files
    for fname in os.listdir(tmpdir):
        if fname.startswith("debug."):
            fpath = os.path.join(tmpdir, fname)
            size = os.path.getsize(fpath)
            print(f"  {fname}: {size} bytes")
            if size < 500 and size > 0:
                with open(fpath, 'r') as f:
                    print(f"    Content:\n{f.read()}")