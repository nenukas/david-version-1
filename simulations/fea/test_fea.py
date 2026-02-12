"""
Simple FEA validation of analytical crankshaft stress using pycalculix.
Models a cylindrical journal under torsion, compares shear stress.
"""
import sys
import os
# Ensure gmsh is in PATH
os.environ['PATH'] = os.path.expanduser('~/.local/bin') + ':' + os.environ.get('PATH', '')

import pycalculix as pyc
import numpy as np

def test_journal_torsion():
    """Model a main journal as a cylinder under pure torsion."""
    # Geometry from optimized crankshaft
    radius = 35.0  # mm (70 mm diameter)
    length = 26.6  # mm (width)
    
    # Material: steel
    E = 210000.0  # MPa (Young's modulus)
    nu = 0.3      # Poisson's ratio
    
    # Create model
    model = pyc.FeaModel('journal_torsion')
    model.set_units('mm')  # millimeters
    
    # Draw cylinder cross‑section (axisymmetric model)
    # We'll model a 2D axisymmetric slice
    inner = model.set_rho(0.0)  # center
    outer = model.set_rho(radius)
    top = model.set_z(length)
    bottom = model.set_z(0.0)
    
    # Create points
    p1 = model.point(inner, bottom)
    p2 = model.point(outer, bottom)
    p3 = model.point(outer, top)
    p4 = model.point(inner, top)
    
    # Create lines
    model.line(p1, p2)  # bottom
    model.line(p2, p3)  # outer
    model.line(p3, p4)  # top
    model.line(p4, p1)  # inner
    
    # Set material
    mat = pyc.Material('steel')
    mat.set_mech_props(E, nu)
    model.set_mat(mat)
    
    # Apply boundary conditions
    # Fix bottom (z=0) in radial and axial directions
    model.constrain_line(0, 'z', 0)  # bottom line (axial fix)
    model.constrain_line(0, 'rho', 0)  # bottom line (radial fix)
    
    # Apply torque as a tangential displacement on outer surface
    # For axisymmetric torsion, we apply a circumferential displacement
    # Torque T = 2800 Nm / 7 mains = 400 Nm per main
    torque_per_main = 400.0  # N·m
    # Convert to shear strain: gamma = tau / G, tau = T * r / J
    G = E / (2 * (1 + nu))
    J = np.pi * radius**4 / 2  # polar moment (mm⁴)
    tau = torque_per_main * 1000 * radius / J  # MPa
    gamma = tau / G  # shear strain
    # Displacement at outer radius = gamma * radius
    disp = gamma * radius  # mm
    # Apply circumferential displacement on outer line (rho = radius)
    model.apply_line_disp(1, 'theta', disp)  # outer line
    
    # Mesh
    model.set_etype('axisym')
    model.set_elem_size(5.0)  # mm
    model.mesh()
    
    # Solve
    model.solve()
    
    # Get results
    results = model.get_results()
    # Extract shear stress (tau_rho_theta) at outer surface
    # We'll get average shear stress on outer line
    shear_stress_fea = results.get_avg_shear('rho', 'theta', line=1)
    
    # Analytical shear stress
    shear_stress_analytical = tau
    
    print(f"Journal radius: {radius} mm, length: {length} mm")
    print(f"Torque per main: {torque_per_main} N·m")
    print(f"Analytical shear stress: {shear_stress_analytical:.2f} MPa")
    print(f"FEA shear stress (avg): {shear_stress_fea:.2f} MPa")
    print(f"Difference: {abs(shear_stress_fea - shear_stress_analytical):.2f} MPa ({abs((shear_stress_fea - shear_stress_analytical)/shear_stress_analytical*100):.1f}%)")
    
    # Plot (optional)
    # model.plot('stress', 'rho', 'theta', filename='journal_shear.png')
    
    return shear_stress_analytical, shear_stress_fea

if __name__ == '__main__':
    print("Running FEA validation of crankshaft journal torsion...")
    try:
        anal, fea = test_journal_torsion()
        if abs(fea - anal) / anal < 0.1:
            print("✅ FEA matches analytical within 10% – validation passed.")
        else:
            print("⚠️  FEA differs significantly – check model.")
    except Exception as e:
        print(f"❌ FEA failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)