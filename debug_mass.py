import sys
sys.path.insert(0, '.')
from src.engine.cylinder_block import CylinderBlockGeometry, CylinderBlockAnalyzer, MATERIALS
import math

# best individual from CGI_450
best = [
    105.96053102040175,
    29.485533225725383,
    9.143492706457245,
    7.632123698772921,
    25.545176422723692,
    38.27698470392114,
    133.2826304528826,
    30.0
]

geo = CylinderBlockGeometry(
    bore_diameter=94.5,
    stroke=94.5,
    bank_angle=60.0,
    bore_spacing=best[0],
    deck_thickness=best[1],
    cylinder_wall_thickness=best[2],
    water_jacket_thickness=best[3],
    main_bearing_width=best[4],
    main_bearing_height=best[5],
    skirt_depth=best[6],
    pan_rail_width=best[7],
)

analyzer = CylinderBlockAnalyzer(geo, "CGI_450")
# manually compute mass
cell_height = geo.deck_thickness + geo.stroke/2.0 + geo.skirt_depth
print(f"cell_height = {cell_height} mm")
bore_radius = geo.bore_radius
cell_volume = geo.bore_spacing * geo.bank_offset * cell_height
print(f"bore_spacing = {geo.bore_spacing}")
print(f"bank_offset = {geo.bank_offset}")
print(f"cell_volume = {cell_volume} mm^3")
bore_volume = math.pi * (bore_radius ** 2) * cell_height
print(f"bore_volume = {bore_volume} mm^3")
jacket_outer_radius = bore_radius + geo.cylinder_wall_thickness + geo.water_jacket_thickness
jacket_volume = math.pi * (jacket_outer_radius ** 2 - (bore_radius + geo.cylinder_wall_thickness) ** 2) * cell_height
print(f"jacket_volume = {jacket_volume} mm^3")
bulkhead_volume = geo.main_bearing_width * geo.main_bearing_height * geo.bore_spacing
print(f"bulkhead_volume = {bulkhead_volume} mm^3")
total_volume = (cell_volume - bore_volume - jacket_volume) * geo.cylinder_count + bulkhead_volume * 7
print(f"total_volume = {total_volume} mm^3")
mass_g = total_volume * 1e-3 * MATERIALS["CGI_450"]["density"]
print(f"mass_g = {mass_g} g")
print(f"mass_kg = {mass_g/1000} kg")
# compare with analyzer
mass_g2 = analyzer.compute_mass()
print(f"analyzer.compute_mass() = {mass_g2}")