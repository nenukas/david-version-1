import math
import json

# load the JSON
with open('cylinder_block_A356_T6_results_20260212_205808.json') as f:
    data = json.load(f)

geo = data['geometry']
bore_diameter = 94.5
ri = bore_diameter / 2.0
print('bore radius', ri)
peak_pressure_mpa = 25.0
force = peak_pressure_mpa * math.pi * ri**2
print('force N', force)
bearing_area = geo['main_bearing_width'] * geo['main_bearing_height']
print('bearing area mm2', bearing_area)
bearing_pressure = force / bearing_area
print('bearing pressure MPa', bearing_pressure)
print('JSON bearing pressure', data['metrics']['bearing_pressure_mpa'])
print('ratio', data['metrics']['bearing_pressure_mpa'] / bearing_pressure)

# compute bending stress
offset = 94.5 / 2.0  # stroke/2
moment = force * offset
section_modulus = (geo['main_bearing_width'] * geo['main_bearing_height']**2) / 6.0
bending_stress = moment / section_modulus
print('bending stress MPa', bending_stress)
print('JSON bending stress', data['metrics']['bulkhead_bending_stress_mpa'])
print('ratio', data['metrics']['bulkhead_bending_stress_mpa'] / bending_stress)