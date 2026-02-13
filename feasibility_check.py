import math

# Constants
p = 25.0  # MPa
r = 94.5 / 2  # mm
pin_diameter = 28.0  # mm
peak_force = 180000.0  # N
yield_solid = 800.0  # MPa

# Lattice density effects
for rho in [0.5, 1.0]:
    yield_eff = yield_solid * rho**1.5
    crown_stress_limit = 0.8 * yield_eff
    t_min = math.sqrt((3 * p * r**2) / (4 * crown_stress_limit))
    print(f"Lattice density {rho:.1f}: effective yield = {yield_eff:.1f} MPa, crown stress limit = {crown_stress_limit:.1f} MPa")
    print(f"  Minimum crown thickness: {t_min:.1f} mm")
    # pin boss width
    bearing_limit = 100.0  # MPa
    w_min = peak_force / (2 * pin_diameter * bearing_limit)
    print(f"  Minimum pin boss width: {w_min:.1f} mm")
    # mass estimate (rough)
    # ignore for now
    print()

# Check if bounds allow these minima
print("Bounds: crown thickness 8-35 mm, pin boss width 10-60 mm")
print("Thus feasible region exists if crown thickness >=13.6 mm (rho=0.5) or >=8.1 mm (rho=1.0) and pin boss width >=32.1 mm.")
print("The optimization may not have explored this region due to mass minimization pressure.")