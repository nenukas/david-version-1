"""
FEA validation of bending stress formula using pycalculix.
Cantilever beam representing crank pin under conrod force.
"""
import sys
import os
os.environ['PATH'] = os.path.expanduser('~/.local/bin') + ':' + os.environ.get('PATH', '')

import pycalculix as pyc
import numpy as np

def test_bending():
    """Cantilever beam bending stress comparison."""
    # Beam dimensions (pin cross‑section)
    width = 70.0   # mm (pin diameter)
    height = 30.0  # mm (pin width)
    length = 47.5  # mm (stroke)
    
    # Material: steel
    E = 210000.0  # MPa
    nu = 0.3
    
    # Load: conrod force (worst‑case)
    force = 180000.0  # N (overdrive)
    
    # Create model
    model = pyc.FeaModel('cantilever')
    model.set_units('mm')
    
    # Draw rectangle in XY plane (plane stress)
    # Points
    p1 = model.point(0, 0)
    p2 = model.point(width, 0)
    p3 = model.point(width, height)
    p4 = model.point(0, height)
    
    # Lines
    model.line(p1, p2)
    model.line(p2, p3)
    model.line(p3, p4)
    model.line(p4, p1)
    
    # Material
    mat = pyc.Material('steel')
    mat.set_mech_props(E, nu)
    model.set_mat(mat)
    
    # Boundary condition: fix left edge (x=0)
    left_line = model.get_line(p1, p4)
    model.constrain_line(left_line, 'x', 0)
    model.constrain_line(left_line, 'y', 0)
    
    # Apply force on right edge (x=width) as pressure
    # Force distributed over area = width * height
    pressure = force / (width * height)  # MPa
    right_line = model.get_line(p2, p3)
    model.apply_line_pressure(right_line, pressure, 'x')
    
    # Set plane stress
    model.set_etype('plstress')
    model.set_elem_size(5.0)
    model.mesh()
    
    # Solve
    model.solve()
    
    # Get bending stress at fixed end (max stress)
    results = model.get_results()
    # Get maximum principal stress at left edge
    stress_max = results.get_max_prin('left')
    
    # Analytical bending stress: sigma = M * c / I
    # M = force * length (N·mm)
    moment = force * length
    # c = height/2 (distance from neutral axis)
    c = height / 2
    # I = width * height**3 / 12 (area moment of inertia)
    I = width * height**3 / 12
    sigma_analytical = moment * c / I
    
    print(f"Beam: {width} mm × {height} mm, length {length} mm")
    print(f"Force: {force/1000:.1f} kN")
    print(f"Analytical bending stress: {sigma_analytical:.2f} MPa")
    print(f"FEA max principal stress: {stress_max:.2f} MPa")
    print(f"Difference: {abs(stress_max - sigma_analytical):.2f} MPa ({abs((stress_max - sigma_analytical)/sigma_analytical*100):.1f}%)")
    
    return sigma_analytical, stress_max

if __name__ == '__main__':
    print("Running bending stress FEA validation...")
    try:
        anal, fea = test_bending()
        if abs(fea - anal) / anal < 0.15:
            print("✅ FEA matches analytical within 15% – validation passed.")
        else:
            print("⚠️  FEA differs significantly – check model.")
    except Exception as e:
        print(f"❌ FEA failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)