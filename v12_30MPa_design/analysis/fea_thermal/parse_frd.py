#!/usr/bin/env python3
"""
Parse CalculiX .frd file to extract max von Mises stress.
"""
import sys
import numpy as np

frd_file = "piston_crown_axisymmetric.frd"
with open(frd_file, 'r') as f:
    lines = f.readlines()

# Find stress block
stress_start = None
for i, line in enumerate(lines):
    if '-4  STRESS' in line:
        stress_start = i
        break

if stress_start is None:
    print("No stress block found")
    sys.exit(1)

# Parse stress values
# Format: after -4 STRESS line, there is a line with "  1P" maybe.
# Then each element stress: line with element id, then 6 stress components?
# Actually for axisymmetric CAX4: 4 stress components? Let's assume 6.
stresses = []
i = stress_start + 1
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('-1') or line.startswith('-2') or line.startswith('-3'):
        # Start of new dataset, stop
        break
    # Stress data lines: element id, then values
    parts = line.split()
    if len(parts) >= 7:
        try:
            elem_id = int(parts[0])
            # Components: S11, S22, S33, S12, S13, S23? For axisymmetric order?
            # Assume S11=radial, S22=axial, S33=hoop, S12=shear
            s11 = float(parts[1])
            s22 = float(parts[2])
            s33 = float(parts[3])
            s12 = float(parts[4])
            # von Mises for plane strain axisymmetric
            vm = np.sqrt(0.5 * ((s11 - s22)**2 + (s22 - s33)**2 + (s33 - s11)**2 + 6 * s12**2))
            stresses.append((elem_id, vm, s11, s22, s33, s12))
        except ValueError:
            pass
    i += 1

if stresses:
    stresses.sort(key=lambda x: x[1], reverse=True)
    print(f"Found {len(stresses)} element stress records")
    print("Top 5 highest von Mises stresses (MPa):")
    for elem_id, vm, s11, s22, s33, s12 in stresses[:5]:
        print(f"  Element {elem_id}: {vm:.1f} MPa (radial {s11:.1f}, axial {s22:.1f}, hoop {s33:.1f}, shear {s12:.1f})")
    avg_vm = np.mean([v[1] for v in stresses])
    max_vm = stresses[0][1]
    print(f"\nMax von Mises stress: {max_vm:.1f} MPa")
    print(f"Average von Mises stress: {avg_vm:.1f} MPa")
else:
    print("No stress data parsed. Check .frd format.")
    # Debug: print lines around stress block
    for j in range(stress_start, min(stress_start+20, len(lines))):
        print(lines[j].rstrip())