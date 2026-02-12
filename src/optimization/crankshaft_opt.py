"""
Generative design optimization for V12 crankshaft using DEAP.
Minimizes mass while satisfying stress, stiffness, and geometric constraints.
"""
import numpy as np
import random
from deap import base, creator, tools, algorithms
from src.engine.crankshaft import CrankshaftGeometry, CrankshaftAnalyzer

# Fixed parameters (from engine specification)
STROKE = 47.5  # mm (half of 95 mm engine stroke)
MATERIAL_DENSITY = 7.85e-3  # g/mm³
MATERIAL_SHEAR_MODULUS = 79.3e3  # MPa
MATERIAL_YIELD_SHEAR = 1000.0  # MPa
MATERIAL_FATIGUE_LIMIT = 500.0  # MPa

# Load cases (overdrive mode, worst‑case)
PEAK_TORQUE = 2800.0  # N·m
PEAK_CONROD_FORCE = 180000.0  # N (250 bar peak pressure)
REDLINE_RPM = 8500.0

# Design variable bounds (mm)
BOUNDS = {
    "main_journal_diameter": (70.0, 100.0),
    "main_journal_width": (25.0, 45.0),
    "pin_diameter": (60.0, 90.0),
    "pin_width": (25.0, 45.0),
    "cheek_thickness": (15.0, 35.0),
    "cheek_radius": (80.0, 130.0),
    "cheek_hole_radius": (30.0, 70.0),
    "fillet_main": (2.0, 8.0),
    "fillet_pin": (2.0, 8.0),
}
# Lists for bounded mutation
LOWS = [b[0] for b in BOUNDS.values()]
HIGHS = [b[1] for b in BOUNDS.values()]

def create_geometry_from_vector(vec):
    """Convert DEAP individual vector to CrankshaftGeometry."""
    return CrankshaftGeometry(
        main_journal_diameter=vec[0],
        main_journal_width=vec[1],
        pin_diameter=vec[2],
        pin_width=vec[3],
        stroke=STROKE,
        cheek_thickness=vec[4],
        cheek_radius=vec[5],
        cheek_hole_radius=vec[6],
        fillet_main=vec[7],
        fillet_pin=vec[8],
        cheek_sector_factor=0.33,
        density=MATERIAL_DENSITY,
        shear_modulus=MATERIAL_SHEAR_MODULUS,
        yield_shear=MATERIAL_YIELD_SHEAR,
        fatigue_limit=MATERIAL_FATIGUE_LIMIT,
    )

def evaluate_individual(vec):
    """Evaluate one design candidate. Returns (mass, constraint_violations)."""
    # Geometric feasibility checks
    violations = 0
    # 1. Cheek hole must be smaller than cheek radius (with margin)
    if vec[6] >= vec[5] - 5.0:
        violations += 10  # large penalty
    # 2. Fillet radii positive
    if vec[7] <= 0.1 or vec[8] <= 0.1:
        violations += 10
    # 3. Check bounds (should be satisfied by mutation, but guard)
    for i, (low, high) in enumerate(zip(LOWS, HIGHS)):
        if vec[i] < low or vec[i] > high:
            violations += 5
    
    # If severe geometric violations, return high mass and violation count
    if violations > 0:
        return 1e6, violations
    
    # Create geometry and analyze
    geo = create_geometry_from_vector(vec)
    analyzer = CrankshaftAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(
        max_torque_nm=PEAK_TORQUE,
        max_conrod_force_n=PEAK_CONROD_FORCE,
        redline_rpm=REDLINE_RPM
    )
    # Mass is primary objective (minimize)
    mass = metrics["mass_kg"]
    # Engineering constraint violations
    violations += sum(1 for v in cons.values() if not v)
    return mass, violations

def setup_deap():
    """Configure DEAP toolbox."""
    # Define a single‑objective minimization with penalty for constraints
    creator.create("Fitness", base.Fitness, weights=(-1.0, -0.5))  # weight for violations
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
         toolbox.attr_6, toolbox.attr_7, toolbox.attr_8),
        n=1
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Genetic operators
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=20.0, low=LOWS, up=HIGHS, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate_individual)
    
    return toolbox

def run_optimization(pop_size=50, generations=30, cxpb=0.7, mutpb=0.2):
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
    print("Starting crankshaft generative design optimization...")
    print(f"Bounds: {BOUNDS}")
    print(f"Loads: {PEAK_TORQUE} Nm torque, {PEAK_CONROD_FORCE/1000:.1f} kN conrod force")
    
    best, log = run_optimization(pop_size=30, generations=20)
    
    print("\n=== OPTIMIZATION RESULTS ===")
    print(f"Best individual: {best}")
    print(f"Fitness (mass, violations): {best.fitness.values}")
    
    # Evaluate and display detailed metrics
    geo = create_geometry_from_vector(best)
    analyzer = CrankshaftAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(PEAK_TORQUE, PEAK_CONROD_FORCE, REDLINE_RPM)
    
    print("\nDetailed metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    print("Constraints satisfied:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    
    # Export CAD of best design
    from src.cad.crankshaft_cad import create_crankshaft, export_step
    crankshaft = create_crankshaft(geo)
    export_step(crankshaft, "crankshaft_optimized.step")
    print("\nOptimized CAD exported to 'crankshaft_optimized.step'")