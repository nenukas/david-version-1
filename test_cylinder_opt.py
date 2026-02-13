import sys
sys.path.insert(0, '.')

from src.optimization.cylinder_block_opt import run_optimization_for_material

try:
    best, log, feasible = run_optimization_for_material(
        material_key="CGI_450",
        pop_size=5,
        generations=1,
        seed=1
    )
    print("SUCCESS")
    print(f"best fitness: {best.fitness.values[0]}")
    print(f"feasible count: {len(feasible)}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()