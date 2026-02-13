#!/usr/bin/env python3
"""
Generative design optimization for V12 crankshaft at 30 MPa peak pressure.
Based on original crankshaft_opt.py with updated loads.
"""
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')

import numpy as np
import random
import json
import datetime
from deap import base, creator, tools, algorithms
from src.engine.crankshaft import CrankshaftGeometry, CrankshaftAnalyzer

# Fixed parameters (from engine specification)
STROKE = 47.5  # mm (half of 95 mm engine stroke)
MATERIAL_DENSITY = 7.85e-3  # g/mm³
MATERIAL_SHEAR_MODULUS = 79.3e3  # MPa
MATERIAL_YIELD_SHEAR = 1000.0  # MPa
MATERIAL_FATIGUE_LIMIT = 500.0  # MPa

# Load cases at 30 MPa (bore 94.5 mm)
BORE_DIAMETER = 94.5  # mm
BORE_AREA = np.pi * (BORE_DIAMETER / 2.0)**2  # mm²
PEAK_PRESSURE = 30.0  # MPa
PEAK_CONROD_FORCE = PEAK_PRESSURE * BORE_AREA  # N
# Original torque at 250 bar (25 MPa) was 2800 Nm. Scale linearly with pressure.
PEAK_TORQUE = 2800.0 * (PEAK_PRESSURE / 25.0)  # N·m
REDLINE_RPM = 11000.0

print(f"Bore area: {BORE_AREA:.1f} mm²")
print(f"Peak conrod force: {PEAK_CONROD_FORCE/1000:.1f} kN")
print(f"Peak torque: {PEAK_TORQUE:.0f} N·m")

# Design variable bounds (mm) – same as original
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

def geometric_feasibility(geo):
    """Check geometry for physical manufacturability, return violation count."""
    violations = 0
    # 1. Cheek hole must be smaller than cheek radius with minimum wall thickness
    min_wall = 5.0  # mm
    if geo.cheek_hole_radius >= geo.cheek_radius - min_wall:
        violations += 10
    # 2. Fillet radii positive and not too small relative to diameter
    if geo.fillet_main <= 1.0 or geo.fillet_pin <= 1.0:
        violations += 5
    # 3. Minimum cheek thickness (avoid paper‑thin)
    if geo.cheek_thickness < 5.0:
        violations += 5
    # 4. Aspect ratios (avoid extreme geometries)
    # Cheek thickness / radius > 0.1 (avoid too thin disks)
    if geo.cheek_thickness / geo.cheek_radius < 0.1:
        violations += 3
    # Pin width / diameter > 0.3 (avoid too slender)
    if geo.pin_width / geo.pin_diameter < 0.3:
        violations += 3
    # Main journal width / diameter > 0.3
    if geo.main_journal_width / geo.main_journal_diameter < 0.3:
        violations += 3
    # 5. Ensure positive volumes (analytical)
    vol_main = np.pi * (geo.main_journal_diameter/2)**2 * geo.main_journal_width
    if vol_main <= 0:
        violations += 20
    vol_pin = np.pi * (geo.pin_diameter/2)**2 * geo.pin_width
    if vol_pin <= 0:
        violations += 20
    cheek_area = geo.cheek_sector_factor * np.pi * (geo.cheek_radius**2 - geo.cheek_hole_radius**2)
    vol_cheek = cheek_area * geo.cheek_thickness
    if vol_cheek <= 0:
        violations += 20
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
    
    # 2. Create geometry and check geometric feasibility
    geo = create_geometry_from_vector(vec)
    geom_violations = geometric_feasibility(geo)
    if geom_violations > 0:
        return 1e6, geom_violations
    
    # 3. Engineering analysis
    analyzer = CrankshaftAnalyzer(geo)
    cons, metrics = analyzer.evaluate_constraints(
        max_torque_nm=PEAK_TORQUE,
        max_conrod_force_n=PEAK_CONROD_FORCE,
        redline_rpm=REDLINE_RPM
    )
    mass = metrics["mass_kg"]
    violations += sum(1 for v in cons.values() if not v)
    return mass, violations

def setup_deap():
    """Configure DEAP toolbox."""
    # Define a single‑objective minimization with penalty for constraints
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
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
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

def convert_to_serializable(obj):
    """Convert numpy types and nested dicts/lists to JSON‑serializable Python types."""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_to_serializable(v) for v in obj]
    # Default (str, int, float, bool, None)
    return obj

def save_results_json(geo, cons, metrics, filename):
    """Save optimization results in JSON format."""
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "loads": {
            "peak_pressure_mpa": PEAK_PRESSURE,
            "peak_conrod_force_n": PEAK_CONROD_FORCE,
            "peak_torque_nm": PEAK_TORQUE,
            "redline_rpm": REDLINE_RPM,
        },
        "geometry": {
            "main_journal_diameter": geo.main_journal_diameter,
            "main_journal_width": geo.main_journal_width,
            "pin_diameter": geo.pin_diameter,
            "pin_width": geo.pin_width,
            "stroke": geo.stroke,
            "cheek_thickness": geo.cheek_thickness,
            "cheek_radius": geo.cheek_radius,
            "cheek_hole_radius": geo.cheek_hole_radius,
            "fillet_main": geo.fillet_main,
            "fillet_pin": geo.fillet_pin,
            "cheek_sector_factor": geo.cheek_sector_factor,
        },
        "metrics": convert_to_serializable(metrics),
        "constraints_satisfied": convert_to_serializable(cons),
        "bounds": BOUNDS,
    }
    data = convert_to_serializable(data)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    print("Starting crankshaft generative design optimization at 30 MPa...")
    print(f"Bounds: {BOUNDS}")
    print(f"Loads: {PEAK_TORQUE:.0f} Nm torque, {PEAK_CONROD_FORCE/1000:.1f} kN conrod force")
    
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
    
    # Save JSON results
    json_filename = f"crankshaft_30MPa_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_results_json(geo, cons, metrics, json_filename)
    print(f"✅ Results saved to {json_filename}")
    
    # CAD validation & export
    try:
        from src.cad.crankshaft_cad import create_crankshaft, export_step
        crankshaft = create_crankshaft(geo)
        
        # Check volume > 0
        cad_volume = crankshaft.volume()  # mm³
        if cad_volume <= 0:
            print("⚠️  CAD volume is zero or negative – geometry may be degenerate.")
        else:
            cad_mass = cad_volume * geo.density / 1000  # kg
            anal_mass = metrics["mass_kg"]
            mass_diff_pct = abs(cad_mass - anal_mass) / anal_mass * 100
            print(f"CAD volume: {cad_volume:.0f} mm³ → mass: {cad_mass:.2f} kg")
            print(f"Analytical mass: {anal_mass:.2f} kg (difference: {mass_diff_pct:.1f}%)")
            if mass_diff_pct > 10:
                print("⚠️  Large mass discrepancy – analytical model may be inaccurate.")
        
        # Check if single solid (connected)
        solids = crankshaft.solids()
        if solids.size() != 1:
            print(f"⚠️  CAD contains {solids.size()} separate solids – may be disconnected.")
        else:
            print("✅ CAD is a single connected solid.")
        
        # Export STEP
        step_name = "crankshaft_30MPa_optimized.step"
        export_step(crankshaft, step_name)
        print(f"✅ Optimized CAD exported to '{step_name}'")
        
        # Export STL
        import cadquery as cq
        cq.exporters.export(crankshaft, "crankshaft_30MPa_optimized.stl", "STL")
        print("✅ STL exported as 'crankshaft_30MPa_optimized.stl'")
        
    except Exception as e:
        print(f"❌ CAD validation/export failed: {e}")
        import traceback
        traceback.print_exc()