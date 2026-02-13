#!/usr/bin/env python3
"""
Run piston_opt_am_v2 multiple times with different random seeds.
Collect feasible designs, output best feasible.
"""
import random
import sys
import os
import json
import datetime

# Add current directory to sys.path to import modules
sys.path.insert(0, '.')

from src.optimization.piston_opt_am_v2 import (
    run_optimization,
    save_results,
    create_geometry_from_vector,
    PEAK_PRESSURE_MPA,
    PEAK_FORCE_N,
    TENSILE_FORCE_N,
    BOUNDS,
)

def run_one(seed, pop_size=30, generations=20):
    """Run a single optimization with given seed."""
    random.seed(seed)
    import numpy as np
    np.random.seed(seed)
    print(f"\n--- Seed {seed} ---")
    best, log, feasible = run_optimization(pop_size=pop_size, generations=generations)
    return best, log, feasible

def main():
    seeds = list(range(1, 11))  # seeds 1 to 10
    all_feasible = []
    best_infeasible = None
    best_infeasible_violations = float('inf')
    
    for seed in seeds:
        try:
            best, log, feasible = run_one(seed)
            violations = best.fitness.values[1]
            if violations == 0:
                all_feasible.append((seed, best, log, feasible))
                print(f"Seed {seed}: found feasible design with mass {best.fitness.values[0]:.2f} g")
            else:
                print(f"Seed {seed}: infeasible, violations {violations}, mass {best.fitness.values[0]:.2f} g")
                if violations < best_infeasible_violations:
                    best_infeasible_violations = violations
                    best_infeasible = (seed, best, log, feasible)
        except Exception as e:
            print(f"Seed {seed}: error {e}")
            continue
    
    print(f"\nTotal runs: {len(seeds)}")
    print(f"Feasible designs found: {len(all_feasible)}")
    
    if all_feasible:
        # Pick the one with lowest mass
        best_seed, best_ind, best_log, best_feas = min(all_feasible, key=lambda x: x[1].fitness.values[0])
        print(f"\nBest feasible design (seed {best_seed}):")
        print(f"  Mass: {best_ind.fitness.values[0]:.2f} g")
        print(f"  Vector: {best_ind}")
        # Save results
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"piston_opt_am_v2_feasible_{timestamp}.json"
        geo = create_geometry_from_vector(best_ind)
        from src.engine.piston_am import PistonAnalyzerAM
        analyzer = PistonAnalyzerAM(geo)
        cons, metrics = analyzer.evaluate_constraints(PEAK_PRESSURE_MPA, PEAK_FORCE_N, TENSILE_FORCE_N)
        results = {
            "best_individual": best_ind,
            "fitness_mass": best_ind.fitness.values[0],
            "fitness_violations": best_ind.fitness.values[1],
            "geometry": {
                "crown_thickness": geo.crown_thickness,
                "pin_boss_width": geo.pin_boss_width,
                "skirt_length": geo.skirt_length,
                "skirt_thickness": geo.skirt_thickness,
                "lattice_relative_density": geo.lattice_relative_density,
            },
            "metrics": metrics,
            "constraints_satisfied": cons,
            "feasible_count": len(best_feas),
            "bounds": BOUNDS,
            "loads": {
                "peak_pressure_mpa": PEAK_PRESSURE_MPA,
                "peak_force_n": PEAK_FORCE_N,
                "tensile_force_n": TENSILE_FORCE_N
            },
            "seed": best_seed,
        }
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {filename}")
        
        # Generate CAD if all constraints satisfied
        if all(cons.values()):
            print("\nAll constraints satisfied. Generating CAD...")
            # TODO: call CAD generation function
            # For now, placeholder
            print("CAD generation placeholder.")
        else:
            print("\nUnexpected: some constraints not satisfied.")
        return results, filename
    else:
        print("\nNo feasible designs found across all seeds.")
        if best_infeasible:
            seed, best, log, feasible = best_infeasible
            print(f"Best infeasible design (seed {seed}): violations {best.fitness.values[1]}, mass {best.fitness.values[0]:.2f} g")
            # Save infeasible results for reference
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"piston_opt_am_v2_infeasible_{timestamp}.json"
            geo = create_geometry_from_vector(best)
            from src.engine.piston_am import PistonAnalyzerAM
            analyzer = PistonAnalyzerAM(geo)
            cons, metrics = analyzer.evaluate_constraints(PEAK_PRESSURE_MPA, PEAK_FORCE_N, TENSILE_FORCE_N)
            results = {
                "best_individual": best,
                "fitness_mass": best.fitness.values[0],
                "fitness_violations": best.fitness.values[1],
                "geometry": {
                    "crown_thickness": geo.crown_thickness,
                    "pin_boss_width": geo.pin_boss_width,
                    "skirt_length": geo.skirt_length,
                    "skirt_thickness": geo.skirt_thickness,
                    "lattice_relative_density": geo.lattice_relative_density,
                },
                "metrics": metrics,
                "constraints_satisfied": cons,
                "feasible_count": len(feasible),
                "bounds": BOUNDS,
                "loads": {
                    "peak_pressure_mpa": PEAK_PRESSURE_MPA,
                    "peak_force_n": PEAK_FORCE_N,
                    "tensile_force_n": TENSILE_FORCE_N
                },
                "seed": seed,
            }
            with open(filename, "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Infeasible results saved to {filename}")
        return None, None

if __name__ == "__main__":
    main()