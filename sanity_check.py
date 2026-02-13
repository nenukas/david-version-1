import sys
sys.path.insert(0, 'src')
from engine.cylinder_block import CylinderBlockGeometry, CylinderBlockAnalyzer

# Use geometry from JSON that gave negative mass
geo = CylinderBlockGeometry(
    bore_diameter=94.5,
    stroke=94.5,
    bank_angle=60.0,
    bore_spacing=105.96053102040175,
    deck_thickness=29.485533225725383,
    cylinder_wall_thickness=9.143492706457245,
    water_jacket_thickness=7.632123698772921,
    main_bearing_width=25.545176422723692,
    main_bearing_height=38.27698470392114,
    skirt_depth=133.2826304528826,
    pan_rail_width=30.0,
)

analyzer = CylinderBlockAnalyzer(geo, 'CGI_450')
print('Geometry:', geo)
print('Bore radius:', geo.bore_radius)
print('Wall outer radius:', geo.bore_radius + geo.cylinder_wall_thickness)
print('Water jacket outer radius:', geo.bore_radius + geo.cylinder_wall_thickness + geo.water_jacket_thickness)
print('Bank offset:', geo.bank_offset)

# compute mass
mass_g = analyzer.compute_mass()
print('Mass g:', mass_g)
print('Mass kg:', mass_g/1000.0)

# compute stresses
stresses = analyzer.compute_stresses(25.0)
print('Stresses:', stresses)

# evaluate constraints
cons, metrics = analyzer.evaluate_constraints(25.0)
print('Constraints:', cons)
print('Metrics:', metrics)