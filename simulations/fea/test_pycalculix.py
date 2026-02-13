#!/usr/bin/env python3
"""
Test pycalculix geometry and export.
"""
import sys
sys.path.insert(0, '/home/nenuka/.local/lib/python3.12/site-packages')
from pycalculix import Project

proj = Project()
part = proj.part
# Create a simple rectangle
rect = part.goto(0, 0).rectangle(10, 100)
proj.set_units('mm')
proj.set_material('steel', 210000, 0.3)
# Mesh
proj.set_eshape('quad', 2)
proj.set_etype('plstress', part, 1)
proj.mesh(0.5, 'gmsh')
# Save .inp
proj.save_fea_model('test_pyc.inp')
print("Saved test_pyc.inp")
# Run ccx
proj.solve()
print("Solved")
# Get results
stress = proj.rfile.get_nmax('Sx')
print(f"Max Sx stress: {stress}")