"""
Generative design optimization for V12 cylinder block.
Supports multiple materials: CGI‑450, forged aluminum A356‑T6, billet aluminum 7075‑T6.
Objective: minimize mass while satisfying stress and geometric constraints.
"""
import numpy as np
import random
import json
import datetime
from deap import base, creator, tools, algorithms
from src.engine.cylinder_block import CylinderBlockGeometry, CylinderBlockAnalyzer, MATERIALS

# Fixed engine parameters
BORE_DIAMETER = 94.5      # mm
STROKE = 94.5             # mm
BANK_ANGLE = 60.0         # degrees
PEAK_PRESSURE_MPA = 25.0  # MPa (250 bar)

# Design variable bounds (mm) – expanded per user request
BOUNDS = {
    "bore_spacing": (100.0, 350.0),
    "deck_thickness": (5.0, 40.0),
    "cylinder_wall_thickness": (3.0, 15.0),
    "water_jacket_thickness": (2.0, 12.0),
    "main_bearing_width": (20.0, 100.0),      # expanded lower bound to 20 mm, upper to 100 mm
    "main_bearing_height": (30.0, 150.0),     # expanded lower bound to 30 mm, upper to 150 mm
    "skirt_depth": (40.0, 200.0),
    "pan_rail_width": (8.0, 40.0),
}

LOWS = [b[0] for b in BOUNDS.values()]
HIGHS = [b[1] for b in BOUNDS.values()]

def create_geometry_from_vector(vec):
    """Convert DEAP individual vector to CylinderBlockGeometry."""
    return CylinderBlockGeometry(
        bore_diameter=BORE_DIAMETER,
        stroke=STROKE,
        bank_angle=BANK_ANGLE,
        bore_spacing=vec[0],
        deck_thickness=vec[1],
        cylinder_wall_thickness=vec[2],
        water_jacket_thickness=vec[3],
        main_bearing_width=vec[4],
        main_bearing_height=vec[5],
        skirt_depth=vec[6],
        pan_rail_width=vec[7],
    )

def evaluate_individual(vec, material_key):
    """Evaluate one design candidate. Returns (fitness,) where fitness = mass + penalty*violations."""
    # Bounds checking
    violations = 0
    for i, (low, high) in enumerate(zip(LOWS, HIGHS)):
        if vec[i] < low or vec[i] > high:
            violations += 5
    
    if violations > 0:
        return (1e9 + violations * 1e6,)
    
    # Create geometry and check geometric feasibility
    geo = create_geometry_from_vector(vec)
    geo_ok, msg = geo.validate()
    if not geo_ok:
        violations += 10
        return (1e9 + violations * 1e6,)
    
    # Engineering analysis
    analyzer = CylinderBlockAnalyzer(geo, material_key)
    cons, metrics = analyzer.evaluate_constraints(PEAK_PRESSURE_MPA)
    mass = metrics["mass_g"]
    # Count constraint violations
    violations += sum(1 for v in cons.values() if not v)
    # Penalty per violation
    penalty = 1e6
    fitness = mass + penalty * violations
    return (fitness,)


def count_violations(vec, material_key):
    """Return number of constraint violations (0-5) and geometric feasibility."""
    # Bounds checking
    violations = 0
    for i, (low, high) in enumerate(zip(LOWS, HIGHS)):
        if vec[i] < low or vec[i] > high:
            violations += 5
    if violations > 0:
        return violations, False
    geo = create_geometry_from_vector(vec)
    geo_ok, msg = geo.validate()
    if not geo_ok:
        return 10, False
    analyzer = CylinderBlockAnalyzer(geo, material_key)
    cons, metrics = analyzer.evaluate_constraints(PEAK_PRESSURE_MPA)
    violations = sum(1 for v in cons.values() if not v)
    return violations, violations == 0

def setup_deap(material_key, seed=1):
    """Configure DEAP toolbox for given material."""
    random.seed(seed)
    np.random.seed(seed)
    
    creator.create("Fitness", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.Fitness)
    
    toolbox = base.Toolbox()
    
    # Attribute generators
    for i, (key, (low, high)) in enumerate(BOUNDS.items()):
        toolbox.register(f"attr_{i}", random.uniform, low, high)
    
    # Structure initializers
    toolbox.register(
        "individual",
        tools.initCycle,
        creator.Individual,
        (toolbox.attr_0, toolbox.attr_1, toolbox.attr_2, toolbox.attr_3,
         toolbox.attr_4, toolbox.attr_5, toolbox.attr_6, toolbox.attr_7),
        n=1
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Genetic operators
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutPolynomialBounded, eta=20.0, low=LOWS, up=HIGHS, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=3)
    # Partial evaluation with material key
    toolbox.register("evaluate", lambda ind: evaluate_individual(ind, material_key))
    
    return toolbox

def run_optimization_for_material(material_key, pop_size=30, generations=20, seed=1):
    """Run evolutionary optimization for a specific material."""
    print(f"\n{'='*60}")
    print(f"Optimizing cylinder block with material: {MATERIALS[material_key]['name']}")
    print(f"{'='*60}")
    
    toolbox = setup_deap(material_key, seed)
    pop = toolbox.population(n=pop_size)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
    
    pop, logbook = algorithms.eaSimple(
        pop, toolbox, cxpb=0.7, mutpb=0.3, ngen=generations,
        stats=stats, verbose=True
    )
    
    # Find best feasible individual (zero violations)
    feasible = []
    for ind in pop:
        violations, feasible_flag = count_violations(ind, material_key)
        if feasible_flag:
            feasible.append(ind)
    if feasible:
        best = min(feasible, key=lambda ind: ind.fitness.values[0])
    else:
        best = min(pop, key=lambda ind: ind.fitness.values[0])
    
    return best, logbook, feasible

def save_results(material_key, best, log, feasible, filename=None):
    """Save optimization results to JSON file."""
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cylinder_block_{material_key}_results_{timestamp}.json"
    
    geo = create_geometry_from_vector(best)
    analyzer = CylinderBlockAnalyzer(geo, material_key)
    cons, metrics = analyzer.evaluate_constraints(PEAK_PRESSURE_MPA)
    total_violations = count_violations(best, material_key)[0]
    
    results = {
        "material": material_key,
        "material_name": MATERIALS[material_key]["name"],
        "best_individual": best,
        "fitness_mass": metrics["mass_g"],
        "violations": total_violations,
        "geometry": {
            "bore_spacing": geo.bore_spacing,
            "deck_thickness": geo.deck_thickness,
            "cylinder_wall_thickness": geo.cylinder_wall_thickness,
            "water_jacket_thickness": geo.water_jacket_thickness,
            "main_bearing_width": geo.main_bearing_width,
            "main_bearing_height": geo.main_bearing_height,
            "skirt_depth": geo.skirt_depth,
            "pan_rail_width": geo.pan_rail_width,
        },
        "metrics": metrics,
        "constraints_satisfied": cons,
        "feasible_count": len(feasible),
        "bounds": BOUNDS,
        "loads": {
            "peak_pressure_mpa": PEAK_PRESSURE_MPA,
        },
        "logbook": log
    }
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {filename}")
    return results, filename

def compare_materials(materials=None):
    """Run optimization for each material and compare results."""
    if materials is None:
        materials = ["CGI_450", "A356_T6", "7075_T6"]
    
    best_results = {}
    for mat in materials:
        best, log, feasible = run_optimization_for_material(mat, pop_size=30, generations=20, seed=1)
        results, filename = save_results(mat, best, log, feasible)
        best_results[mat] = {
            "mass_kg": results["metrics"]["mass_kg"],
            "feasible": len(feasible) > 0,
            "filename": filename,
            "geometry": results["geometry"],
        }
    
    print("\n" + "="*60)
    print("MATERIAL COMPARISON (best feasible design mass)")
    print("="*60)
    for mat, res in best_results.items():
        print(f"{MATERIALS[mat]['name']:30s} mass = {res['mass_kg']:.1f} kg  feasible = {res['feasible']}")
    print("="*60)
    
    # Select best (lowest mass feasible)
    feasible_results = {k: v for k, v in best_results.items() if v["feasible"]}
    if feasible_results:
        best_mat = min(feasible_results.keys(), key=lambda k: feasible_results[k]["mass_kg"])
        print(f"\n✅ Best material: {MATERIALS[best_mat]['name']} (mass {feasible_results[best_mat]['mass_kg']:.1f} kg)")
    else:
        print("\n⚠️ No feasible designs found for any material.")
        # pick least violation
        best_mat = min(best_results.keys(), key=lambda k: best_results[k]["mass_kg"])
        print(f"   Least‑mass infeasible: {MATERIALS[best_mat]['name']}")
    
    return best_results

if __name__ == "__main__":
    print("Cylinder Block Generative Design Optimization")
    print(f"Engine: {BORE_DIAMETER} mm bore × {STROKE} mm stroke, V{BANK_ANGLE}°")
    print(f"Peak pressure: {PEAK_PRESSURE_MPA} MPa")
    print(f"Design variables: {list(BOUNDS.keys())}")
    print(f"Materials to compare: CGI‑450 cast iron, forged aluminum A356‑T6, billet aluminum 7075‑T6")
    print(f"Population: 30, Generations: 20 per material")
    
    results = compare_materials()
    
    # TODO: CAD generation for best feasible design
    # If feasible designs exist, generate CAD using cylinder_block_cad.py (to be created)
    print("\n✅ Optimization complete. Results saved to JSON files.")