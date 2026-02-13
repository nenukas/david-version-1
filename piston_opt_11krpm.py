"""
Generative design optimization for V12 piston using DEAP.
Forged aluminum 2618‑T6, minimize mass while satisfying stress and bearing pressure.
Updated 11k RPM loads (peak pressure 25 MPa, compression 180 kN, tensile inertia 83 kN).
Population 20, generations 15.
Output best feasible design metrics and generate CAD if constraints satisfied.
Save results to file.
"""
import numpy as np
import random
import json
import datetime
from deap import base, creator, tools, algorithms
from src.engine.piston import PistonGeometry, PistonAnalyzer

# Fixed parameters (from engine specification)
BORE_DIAMETER = 94.5          # mm (cylinder bore)
COMPRESSION_HEIGHT = 38.0     # mm (pin center to crown)
PIN_DIAMETER = 28.0           # mm (piston pin)
RING_LAND_HEIGHT = 2.5        # mm (each ring land)
RING_GROOVE_DEPTH = 3.0       # mm

# Load cases (11k RPM worst‑case)
PEAK_PRESSURE_MPA = 25.0      # MPa (250 bar peak cylinder pressure)
PEAK_FORCE_N = 180000.0       # N (compression)
TENSILE_FORCE_N = 83000.0     # N (inertia at 11 kRPM)

# Design variable bounds (mm) – expanded from original
BOUNDS = {
    "crown_thickness": (6.0, 15.0),
    "pin_boss_width": (8.0, 20.0),
    "skirt_length": (30.0, 60.0),
    "skirt_thickness": (2.0, 6.0),
}

LOWS = [b[0] for b in BOUNDS.values()]
HIGHS = [b[1] for b in BOUNDS.values()]

def create_geometry_from_vector(vec):
    """Convert DEAP individual vector to PistonGeometry."""
    return PistonGeometry(
        bore_diameter=BORE_DIAMETER,
        compression_height=COMPRESSION_HEIGHT,
        pin_diameter=PIN_DIAMETER,
        pin_boss_width=vec[1],
        crown_thickness=vec[0],
        ring_land_height=RING_LAND_HEIGHT,
        ring_groove_depth=RING_GROOVE_DEPTH,
        skirt_length=vec[2],
        skirt_thickness=vec[3],
    )

def geometric_feasibility(geo):
    """Check geometry for manufacturability, return violation count."""
    violations = 0
    # Crown thickness reasonable
    if geo.crown_thickness < 5.0:
        violations += 10
    # Pin boss width reasonable relative to pin diameter
    if geo.pin_boss_width < geo.pin_diameter * 0.3:
        violations += 5
    # Skirt thickness not too thin
    if geo.skirt_thickness < 2.0:
        violations += 5
    # Skirt length not excessive relative to bore
    if geo.skirt_length > geo.bore_diameter * 0.8:
        violations += 3
    return violations

def evaluate_individual(vec):
    """Evaluate one design candidate. Returns (mass, constraint_violations)."""
    # Bounds checking
    violations = 0
    for i, (low, high) in enumerate(zip(LOWS, HIGHS)):
        if vec[i] < low or vec[i] > high:
            violations += 5
    
    if violations > 0:
        return 1e6, violations
    
    # Create geometry and geometric feasibility
    geo = create_geometry_from_vector(vec)
    geom_violations = geometric_feasibility(geo)
    if geom_violations > 0:
        return 1e6, geom_violations
    
    # Engineering analysis
    analyzer = PistonAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(
        peak_pressure_mpa=PEAK_PRESSURE_MPA,
        peak_force_n=PEAK_FORCE_N,
        tensile_force_n=TENSILE_FORCE_N
    )
    # Mass is primary objective (minimize)
    mass = metrics["mass_g"]
    # Engineering constraint violations count
    violations += sum(1 for v in cons.values() if not v)
    return mass, violations

def setup_deap():
    """Configure DEAP toolbox."""
    creator.create("Fitness", base.Fitness, weights=(-1.0, -100.0))
    creator.create("Individual", list, fitness=creator.Fitness)
    
    toolbox = base.Toolbox()
    
    # Attribute generator
    for i, (key, (low, high)) in enumerate(BOUNDS.items()):
        toolbox.register(f"attr_{i}", random.uniform, low, high)
    
    # Structure initializers
    toolbox.register(
        "individual",
        tools.initCycle,
        creator.Individual,
        (toolbox.attr_0, toolbox.attr_1, toolbox.attr_2, toolbox.attr_3),
        n=1
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Genetic operators
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=20.0, low=LOWS, up=HIGHS, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate_individual)
    
    return toolbox

def run_optimization(pop_size=20, generations=15, cxpb=0.7, mutpb=0.2):
    """Run evolutionary optimization."""
    toolbox = setup_deap()
    pop = toolbox.population(n=pop_size)
    
    # Statistics
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
    
    # Run algorithm
    pop, logbook = algorithms.eaSimple(
        pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=generations,
        stats=stats, verbose=True
    )
    
    # Find best feasible individual (lowest mass with zero violations)
    feasible = [ind for ind in pop if ind.fitness.values[1] == 0]
    if feasible:
        best = min(feasible, key=lambda ind: ind.fitness.values[0])
    else:
        best = min(pop, key=lambda ind: ind.fitness.values[0])
    
    return best, logbook, feasible

def save_results(best, log, feasible, filename=None):
    """Save optimization results to JSON file."""
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"piston_opt_results_11krpm_{timestamp}.json"
    
    geo = create_geometry_from_vector(best)
    analyzer = PistonAnalyzer(geo)
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
        "logbook": log
    }
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {filename}")
    return results, filename

def generate_cad(geometry, filename=None):
    """Generate CAD model of piston using CadQuery."""
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"piston_optimized_11krpm_{timestamp}.step"
    
    try:
        from src.cad.piston_cad import create_piston, export_step
        piston = create_piston(geometry)
        export_step(piston, filename)
        print(f"CAD model saved to {filename}")
        
        # Also export STL for 3D printing
        import cadquery as cq
        stl_filename = filename.replace(".step", ".stl")
        cq.exporters.export(piston, stl_filename, "STL")
        print(f"STL model saved to {stl_filename}")
    except ImportError:
        print("CadQuery or piston_cad not installed, skipping CAD generation.")
    except Exception as e:
        print(f"CAD generation failed: {e}")

if __name__ == "__main__":
    print("Starting piston generative design optimization with 11k RPM loads...")
    print(f"Bounds: {BOUNDS}")
    print(f"Population: 20, Generations: 15")
    print(f"Loads: {PEAK_PRESSURE_MPA} MPa peak pressure, {PEAK_FORCE_N/1000:.1f} kN compression, {TENSILE_FORCE_N/1000:.1f} kN tensile")
    
    best, log, feasible = run_optimization(pop_size=20, generations=15)
    
    print("\n=== OPTIMIZATION RESULTS ===")
    print(f"Best individual: {best}")
    print(f"Fitness (mass, violations): {best.fitness.values}")
    print(f"Feasible designs found: {len(feasible)}")
    
    # Evaluate and display detailed metrics
    geo = create_geometry_from_vector(best)
    analyzer = PistonAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(PEAK_PRESSURE_MPA, PEAK_FORCE_N, TENSILE_FORCE_N)
    
    print("\nDetailed metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.3f}")
    print("Constraints satisfied:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    
    # Save results
    results, filename = save_results(best, log, feasible)
    
    # Generate CAD if all constraints satisfied
    if all(cons.values()):
        print("\nAll constraints satisfied. Generating CAD...")
        generate_cad(geo)
    else:
        print("\n⚠️ Not all constraints satisfied. CAD generation skipped.")
    
    print("\n✅ Optimization complete.")