#!/usr/bin/env python3
"""
Quick test of enhanced geometric feasibility checks.
Runs a small optimization to verify no degenerate solutions.
"""
import sys
sys.path.insert(0, '.')

from src.optimization.crankshaft_opt import run_optimization, create_geometry_from_vector

if __name__ == '__main__':
    print("Testing enhanced geometric checks with small optimization...")
    best, log = run_optimization(pop_size=10, generations=5, cxpb=0.7, mutpb=0.3)
    
    print(f"\nBest individual: {best}")
    print(f"Fitness: {best.fitness.values}")
    
    # Evaluate geometry
    from src.engine.crankshaft import CrankshaftAnalyzer
    geo = create_geometry_from_vector(best)
    analyzer = CrankshaftAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(2800.0, 180000.0, 8500.0)
    
    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    print("Constraints satisfied:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    
    # Geometric checks
    from src.optimization.crankshaft_opt import geometric_feasibility
    geom_viol = geometric_feasibility(geo)
    print(f"Geometric violations: {geom_viol}")
    
    if geom_viol == 0 and all(cons.values()):
        print("\n✅ Enhanced checks passed – design is feasible and non‑degenerate.")
    else:
        print("\n❌ Design fails checks.")