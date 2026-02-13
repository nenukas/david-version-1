import json
import glob
import os

files = glob.glob('cylinder_block_*_results_20260212_211018.json')
if not files:
    files = glob.glob('cylinder_block_*_results_*.json')
    
results = []
for f in files:
    with open(f) as fp:
        data = json.load(fp)
    material = data['material_name']
    mass_kg = data['metrics']['mass_kg']
    feasible = data['feasible_count'] > 0
    violations = data['fitness_violations']
    cons = data['constraints_satisfied']
    violated = [k for k, v in cons.items() if not v]
    results.append({
        'material': material,
        'mass_kg': mass_kg,
        'feasible': feasible,
        'violations': violations,
        'violated_constraints': violated,
        'file': os.path.basename(f)
    })
    print(f'{material}: mass {mass_kg:.1f} kg, feasible {feasible}, violations {violations}')
    print('  Violated:', violated)

# Sort by mass
results.sort(key=lambda x: x['mass_kg'])
print('\nRanked by mass (lowest first):')
for r in results:
    print(f"  {r['material']}: {r['mass_kg']:.1f} kg")
    
if results:
    with open('cylinder_block_material_comparison_summary.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('\nSummary saved to cylinder_block_material_comparison_summary.json')