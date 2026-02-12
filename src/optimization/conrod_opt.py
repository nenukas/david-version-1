"""
Generative design optimization for V12 connecting rod using DEAP.
Ti‑6Al‑4V titanium, minimize mass while satisfying buckling, stress, bearing pressure, fatigue.
"""
import numpy as np
import random
from deap import base, creator, tools, algorithms
from src.engine.conrod import ConrodGeometry, ConrodAnalyzer

# Fixed parameters (matching crankshaft & piston)
CRANK_PIN_DIAMETER = 86.5   # mm (from optimized crankshaft)
PISTON_PIN_DIAMETER = 28.0  # mm (typical for high‑power V12)
CENTER_LENGTH = 150.0       # mm (rod length for 95 mm stroke)

# Load cases (overdrive mode worst‑case)
COMPRESSION_FORCE = 180000.0  # N (250 bar peak pressure)
TENSILE_FORCE = 50000.0       # N (inertia)
ECCENTRICITY = 0.5            # mm (manufacturing misalignment)

# Design variable bounds (mm)
BOUNDS = {
    "beam_height": (30.0, 60.0),
    "beam_width": (20.0, 50.0),
    "web_thickness": (4.0, 15.0),
    "flange_thickness": (3.0, 10.0),
    "big_end_width": (30.0, 50.0),   # must match crankshaft pin width
    "small_end_width": (20.0, 40.0),
    "fillet_big": (2.0, 8.0),
    "fillet_small": (1.0, 6.0),
}

LOWS = [b[0] for b in BOUNDS.values()]
HIGHS = [b[1] for b in BOUNDS.values()]

def create_geometry_from_vector(vec):
    """Convert DEAP individual vector to ConrodGeometry."""
    return ConrodGeometry(
        beam_height=vec[0],
        beam_width=vec[1],
        web_thickness=vec[2],
        flange_thickness=vec[3],
        center_length=CENTER_LENGTH,
        big_end_width=vec[4],
        small_end_width=vec[5],
        big_end_diameter=CRANK_PIN_DIAMETER,
        small_end_diameter=PISTON_PIN_DIAMETER,
        fillet_big=vec[6],
        fillet_small=vec[7],
        # Material fixed (Ti‑6Al‑4V)
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
    
    # 3. Engineering analysis
    analyzer = ConrodAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(
        compression_force_n=COMPRESSION_FORCE,
        tensile_force_n=TENSILE_FORCE,
        eccentricity_mm=ECCENTRICITY
    )
    # Mass is primary objective (minimize)
    mass = metrics["mass_kg"]
    # Engineering constraint violations
    violations += sum(1 for v in cons.values() if not v)
    return mass, violations

def setup_deap():
    """Configure DEAP toolbox."""
    creator.create("Fitness", base.Fitness, weights=(-1.0, -0.5))
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
         toolbox.attr_6, toolbox.attr_7),
        n=1
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Genetic operators
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=20.0, low=LOWS, up=HIGHS, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate_individual)
    
    return toolbox

def run_optimization(pop_size=30, generations=20, cxpb=0.7, mutpb=0.2):
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
    
    return best, logbook

if __name__ == "__main__":
    print("Starting connecting‑rod generative design optimization...")
    print(f"Bounds: {BOUNDS}")
    print(f"Loads: {COMPRESSION_FORCE/1000:.1f} kN compression, {TENSILE_FORCE/1000:.1f} kN tensile")
    
    best, log = run_optimization(pop_size=20, generations=15)
    
    print("\n=== OPTIMIZATION RESULTS ===")
    print(f"Best individual: {best}")
    print(f"Fitness (mass, violations): {best.fitness.values}")
    
    # Evaluate and display detailed metrics
    geo = create_geometry_from_vector(best)
    analyzer = ConrodAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(COMPRESSION_FORCE, TENSILE_FORCE, ECCENTRICITY)
    
    print("\nDetailed metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.3f}")
    print("Constraints satisfied:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    
    # TODO: CAD generation
    print("\n✅ Optimization complete. CAD generation pending.")