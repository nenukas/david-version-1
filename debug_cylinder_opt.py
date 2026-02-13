import sys
sys.path.insert(0, '.')

from src.optimization.cylinder_block_opt import (
    run_optimization_for_material,
    count_violations,
    create_geometry_from_vector,
    CylinderBlockAnalyzer,
    MATERIALS,
    PEAK_PRESSURE_MPA
)

best, log, feasible = run_optimization_for_material(
    material_key="CGI_450",
    pop_size=5,
    generations=1,
    seed=1
)

print(f"Best fitness: {best.fitness.values[0]}")
print(f"Feasible count: {len(feasible)}")

violations, feasible_flag = count_violations(best, "CGI_450")
print(f"Violations: {violations}, feasible_flag: {feasible_flag}")

geo = create_geometry_from_vector(best)
analyzer = CylinderBlockAnalyzer(geo, "CGI_450")
cons, metrics = analyzer.evaluate_constraints(PEAK_PRESSURE_MPA)

print("\nGeometry:")
for attr, val in geo.__dict__.items():
    if not attr.startswith('_'):
        print(f"  {attr}: {val}")

print("\nMetrics:")
for k, v in metrics.items():
    print(f"  {k}: {v}")

print("\nConstraints:")
for k, v in cons.items():
    print(f"  {k}: {v}")

# Also compute mass manually
mass_g = metrics['mass_g']
print(f"\nMass: {mass_g/1000:.2f} kg")

# Check if all constraints satisfied
if all(cons.values()):
    print("✅ All constraints satisfied")
else:
    print("❌ Some constraints violated")