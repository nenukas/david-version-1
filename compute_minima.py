import math

# Parameters
bore = 94.5
pin_dia = 28.0
peak_pressure = 25.0
peak_force = 180000.0
tensile_force = 83000.0
yield_solid = 800.0

# Crown stress constraint: stress < 0.8 * yield_eff
# yield_eff = yield_solid * rho**1.5
# Stress = (3 * p * r^2) / (4 * t^2)
r = bore / 2
def crown_thickness_min(rho):
    stress_limit = 0.8 * yield_solid * rho**1.5
    t = math.sqrt((3 * peak_pressure * r**2) / (4 * stress_limit))
    return t

# Pin bearing pressure constraint: pressure < 100 MPa
# pressure = force / (2 * pin_dia * width)
def pin_boss_width_min(force):
    width = force / (2 * pin_dia * 100.0)
    return width

# Lattice density bounds
rho_min = 0.5
rho_max = 1.0

print("Minimum dimensions to satisfy constraints (single constraint):")
for rho in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    t = crown_thickness_min(rho)
    w_comp = pin_boss_width_min(peak_force)
    w_tens = pin_boss_width_min(tensile_force)
    print(f"rho={rho:.1f}: crown thickness >= {t:.2f} mm, pin boss width >= {max(w_comp, w_tens):.2f} mm (comp {w_comp:.2f}, tens {w_tens:.2f})")

# Combined constraints: need to satisfy both simultaneously.
print("\nChecking if bounds allow feasible designs:")
print(f"Crown thickness bounds: 8 - 25 mm")
print(f"Pin boss width bounds: 10 - 40 mm")
print(f"Skirt length bounds: 30 - 80 mm")
print(f"Skirt thickness bounds: 2 - 10 mm")
print(f"Lattice density bounds: 0.5 - 1.0")

# For rho = 0.5, required crown thickness:
t_needed = crown_thickness_min(0.5)
w_needed = pin_boss_width_min(peak_force)
print(f"\nFor rho=0.5: need crown thickness >= {t_needed:.2f} mm, pin boss width >= {w_needed:.2f} mm")
print(f"Within bounds? Crown: {t_needed <= 25} (max 25), Pin width: {w_needed <= 40} (max 40)")
if t_needed <= 25 and w_needed <= 40:
    print("Feasible region exists.")
else:
    print("Feasible region may be impossible.")
    # Check if we can increase rho to reduce t_needed (since stress limit increases with rho)
    for rho in [0.6, 0.7, 0.8, 0.9, 1.0]:
        t = crown_thickness_min(rho)
        if t <= 25:
            print(f"At rho={rho:.1f}, crown thickness needed {t:.2f} <= 25, feasible.")
            break
    # w_needed independent of rho
    if w_needed > 40:
        print(f"Pin boss width needed {w_needed:.2f} > 40, cannot satisfy.")