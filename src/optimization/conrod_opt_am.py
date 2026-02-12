"""
Generative design optimization for V12 connecting rod with additive‑manufacturing.
Uses high‑strength steel (300M) with lattice infill, relaxed constraints.
Variables: geometry + lattice relative density (0.2–1.0).
Constraints: mass <2 kg, bearing pressure <200 MPa, buckling SF ≥1.2, fatigue SF ≥1.2.
"""
import numpy as np
import random
import json
import datetime
from deap import base, creator, tools, algorithms
from src.engine.conrod_am import ConrodGeometryAM, ConrodAnalyzerAM

# Fixed parameters (matching crankshaft & piston)
CRANK_PIN_DIAMETER = 86.5   # mm (from optimized crankshaft)
PISTON_PIN_DIAMETER = 28.0  # mm (typical for high‑power V12)
CENTER_LENGTH = 150.0       # mm (rod length for 95 mm stroke)

# Load cases (11k RPM worst‑case)
COMPRESSION_FORCE = 180000.0  # N (250 bar peak pressure)
TENSILE_FORCE = 83000.0       # N (inertia at 11k RPM)
ECCENTRICITY = 0.5            # mm (manufacturing misalignment)

# Expanded design variable bounds (mm) + lattice density
BOUNDS = {
    "beam_height": (25.0, 150.0),          # further expanded
    "beam_width": (15.0, 120.0),           # further expanded
    "web_thickness": (3.0, 40.0),          # further expanded
    "flange_thickness": (2.0, 30.0),       # further expanded
    "big_end_width": (25.0, 150.0),        # further expanded
    "small_end_width": (15.0, 150.0),      # further expanded
    "small_end_diameter": (25.0, 100.0),   # further expanded
    "fillet_big": (1.0, 25.0),             # further expanded
    "fillet_small": (0.5, 20.0),           # further expanded
    "lattice_relative_density": (0.2, 1.0),  # lattice density
}

LOWS = [b[0] for b in BOUNDS.values()]
HIGHS = [b[1] for b in BOUNDS.values()]

def create_geometry_from_vector(vec):
    """Convert DEAP individual vector to ConrodGeometryAM."""
    return ConrodGeometryAM(
        beam_height=vec[0],
        beam_width=vec[1],
        web_thickness=vec[2],
        flange_thickness=vec[3],
        center_length=CENTER_LENGTH,
        big_end_width=vec[4],
        small_end_width=vec[5],
        big_end_diameter=CRANK_PIN_DIAMETER,
        small_end_diameter=vec[6],  # variable
        fillet_big=vec[7],
        fillet_small=vec[8],
        lattice_relative_density=vec[9],
    )

def geometric_feasibility(geo):
    """Check geometry for manufacturability, return violation count."""
    violations = 0
    # 1. Web thickness < beam width
    if geo.web_thickness >= geo.beam_width - 2:
        violations += 10
    # 2. Flange thickness reasonable relative to beam height
    if geo.flange_thickness >= geo.beam_height * 0.4:
        violations += 5
    # 3. Positive cross‑section area
    if geo.beam_height <= 2 * geo.flange_thickness:
        violations += 10
    # 4. Bearing widths positive
    if geo.big_end_width < 5 or geo.small_end_width < 5:
        violations += 5
    # 5. Fillet radii positive
    if geo.fillet_big < 0.5 or geo.fillet_small < 0.5:
        violations += 5
    # 6. Aspect ratios (avoid extreme shapes)
    if geo.beam_width / geo.beam_height > 3.0:
        violations += 3
    if geo.beam_height / geo.beam_width > 3.0:
        violations += 3
    # 7. Lattice density within bounds (already bounded by variable)
    if not (0.2 <= geo.lattice_relative_density <= 1.0):
        violations += 10
    return violations

def evaluate_individual(vec):
    """Evaluate one design candidate. Returns (mass, constraint_violations)."""
    # 1. Bounds checking
    violations = 0
    for i, (low, high) in enumerate(zip(LOWS, HIGHS)):
        if vec[i] < low or vec[i] > high:
            violations += 5
    
    if violations > 0:
        return 1e6, violations
    
    # 2. Create geometry and geometric feasibility
    geo = create_geometry_from_vector(vec)
    geom_violations = geometric_feasibility(geo)
    if geom_violations > 0:
        return 1e6, geom_violations
    
    # 3. Engineering analysis with AM‑aware constraints
    analyzer = ConrodAnalyzerAM(geo)
    cons, metrics = analyzer.evaluate_constraints(
        compression_force_n=COMPRESSION_FORCE,
        tensile_force_n=TENSILE_FORCE,
        eccentricity_mm=ECCENTRICITY
    )
    # Mass is primary objective (minimize)
    mass = metrics["mass_kg"]
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
        (toolbox.attr_0, toolbox.attr_1, toolbox.attr_2,
         toolbox.attr_3, toolbox.attr_4, toolbox.attr_5,
         toolbox.attr_6, toolbox.attr_7, toolbox.attr_8,
         toolbox.attr_9),
        n=1
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Genetic operators
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=20.0, low=LOWS, up=HIGHS, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate_individual)
    
    return toolbox

def run_optimization(pop_size=40, generations=25, cxpb=0.7, mutpb=0.2):
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
        filename = f"conrod_opt_am_results_{timestamp}.json"
    
    geo = create_geometry_from_vector(best)
    analyzer = ConrodAnalyzerAM(geo)
    cons, metrics = analyzer.evaluate_constraints(COMPRESSION_FORCE, TENSILE_FORCE, ECCENTRICITY)
    
    results = {
        "best_individual": best,
        "fitness_mass": best.fitness.values[0],
        "fitness_violations": best.fitness.values[1],
        "geometry": {
            "beam_height": geo.beam_height,
            "beam_width": geo.beam_width,
            "web_thickness": geo.web_thickness,
            "flange_thickness": geo.flange_thickness,
            "big_end_width": geo.big_end_width,
            "small_end_width": geo.small_end_width,
            "small_end_diameter": geo.small_end_diameter,
            "fillet_big": geo.fillet_big,
            "fillet_small": geo.fillet_small,
            "lattice_relative_density": geo.lattice_relative_density,
        },
        "metrics": metrics,
        "constraints_satisfied": cons,
        "feasible_count": len(feasible),
        "bounds": BOUNDS,
        "loads": {
            "compression_force_n": COMPRESSION_FORCE,
            "tensile_force_n": TENSILE_FORCE,
            "eccentricity_mm": ECCENTRICITY
        },
        "logbook": log
    }
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {filename}")
    return results, filename

if __name__ == "__main__":
    print("Starting connecting‑rod generative design with ADDITIVE MANUFACTURING...")
    print(f"Material: 300M steel with lattice infill (ρ_rel 0.2–1.0)")
    print(f"Relaxed thresholds: mass <2 kg, bearing pressure <200 MPa, buckling SF ≥1.2, fatigue SF ≥1.2")
    print(f"Bounds: {BOUNDS}")
    print(f"Population: 40, Generations: 25")
    print(f"Loads: {COMPRESSION_FORCE/1000:.1f} kN compression, {TENSILE_FORCE/1000:.1f} kN tensile")
    
    best, log, feasible = run_optimization(pop_size=40, generations=25)
    
    print("\n=== OPTIMIZATION RESULTS ===")
    print(f"Best individual: {best}")
    print(f"Fitness (mass, violations): {best.fitness.values}")
    print(f"Feasible designs found: {len(feasible)}")
    
    # Evaluate and display detailed metrics
    geo = create_geometry_from_vector(best)
    analyzer = ConrodAnalyzerAM(geo)
    cons, metrics = analyzer.evaluate_constraints(COMPRESSION_FORCE, TENSILE_FORCE, ECCENTRICITY)
    
    print("\nDetailed metrics:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.3f}")
        else:
            print(f"  {k}: {v}")
    print("Constraints satisfied:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    
    # Save results
    results, filename = save_results(best, log, feasible)
    
    # TODO: CAD generation if all constraints satisfied
    if all(cons.values()):
        print("\nAll constraints satisfied. Generating CAD...")
        # Use existing CAD generation function
        # generate_cad(geo, filename.replace('.json', '.step'))
        print("CAD generation placeholder.")
    else:
        print("\n⚠️ Not all constraints satisfied. CAD generation skipped.")
    
    print("\n✅ Optimization complete.")