import random
import subprocess
import sys
import os
import json
import datetime

def run_optimization(seed):
    """Run piston_opt_am_v2 with a given random seed."""
    # Set environment variable for random seed
    env = os.environ.copy()
    env['PYTHONHASHSEED'] = str(seed)
    # Run the module with seed passed as argument? We'll need to modify the script.
    # Instead, let's import the module and call its functions directly.
    sys.path.insert(0, '.')
    from src.optimization.piston_opt_am_v2 import run_optimization, save_results, create_geometry_from_vector
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)
    print(f"\n--- Seed {seed} ---")
    best, log, feasible = run_optimization(pop_size=30, generations=20)
    return best, log, feasible

def main():
    seeds = [42, 123, 456, 789, 999]
    all_feasible = []
    best_feasible = None
    best_mass = float('inf')
    for seed in seeds:
        try:
            best, log, feasible = run_optimization(seed)
            # Evaluate feasibility
            if best.fitness.values[1] == 0:
                all_feasible.append((seed, best))
                if best.fitness.values[0] < best_mass:
                    best_mass = best.fitness.values[0]
                    best_feasible = (seed, best)
        except Exception as e:
            print(f"Error with seed {seed}: {e}")
            continue
    print(f"\nTotal feasible designs found: {len(all_feasible)}")
    if best_feasible:
        seed, best = best_feasible
        print(f"Best feasible design (seed {seed}): mass {best.fitness.values[0]:.2f} g")
        # Save results
        from src.optimization.piston_opt_am_v2 import save_results, create_geometry_from_vector
        results, filename = save_results(best, [], [best])  # empty log for simplicity
        print(f"Saved to {filename}")
    else:
        print("No feasible designs found across seeds.")
        # Save the best infeasible design from last seed? We'll just return None

if __name__ == "__main__":
    main()