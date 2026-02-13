import sys
sys.path.insert(0, 'src')
from engine.cylinder_block import CylinderBlockGeometry, CylinderBlockAnalyzer

geo = CylinderBlockGeometry(
    bore_diameter=94.5,
    stroke=94.5,
    bank_angle=60.0,
    bore_spacing=130.01108949624947,
    deck_thickness=8.778178060314389,
    cylinder_wall_thickness=3.1848708120727753,
    water_jacket_thickness=2.420506591055526,
    main_bearing_width=32.61669814465862,
    main_bearing_height=46.45760374519382,
    skirt_depth=54.947739054659095,
    pan_rail_width=14.74367202455982,
)

analyzer = CylinderBlockAnalyzer(geo, 'A356_T6')
stresses = analyzer.compute_stresses(25.0)
print('Stresses:', stresses)
print('Bearing pressure MPa:', stresses['bearing_pressure_mpa'])
print('Bulkhead bending MPa:', stresses['bulkhead_bending_stress_mpa'])

# compute manually
ri = geo.bore_radius
force = 25.0 * 3.141592653589793 * ri**2
print('Force N:', force)
bearing_area = geo.main_bearing_width * geo.main_bearing_height
print('Bearing area mm2:', bearing_area)
print('Bearing pressure (force/area) MPa:', force / bearing_area)
offset = geo.stroke / 2.0
moment = force * offset
section_modulus = (geo.main_bearing_width * geo.main_bearing_height**2) / 6.0
print('Section modulus mm3:', section_modulus)
print('Bending stress MPa:', moment / section_modulus)