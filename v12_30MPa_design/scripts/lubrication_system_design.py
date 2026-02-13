#!/usr/bin/env python3
"""
Lubrication system design for V12 8.0 L engine at 12 k RPM.
"""
import math

print("=== LUBRICATION SYSTEM DESIGN ===")
print("Engine: V12 8.0 L, 12 k RPM")

# Oil flow requirements (rule of thumb: 0.5 L/min per liter displacement at high performance)
displacement_l = 8.0
oil_flow_lpm = displacement_l * 0.8  # conservative
oil_flow_m3s = oil_flow_lpm / 60000
print(f"Required oil flow: {oil_flow_lpm:.1f} L/min")

# Oil pressure: typical 4–6 bar at high RPM
pressure_bar = 5.0  # bar
pressure_Pa = pressure_bar * 1e5
print(f"Oil pressure: {pressure_bar} bar")

# Pump displacement (gear pump)
# Assume pump volumetric efficiency 0.85, mechanical efficiency 0.90
eta_vol = 0.85
eta_mech = 0.90
pump_speed_rpm = 0.5 * 12000  # pump driven at half crankshaft speed (typical)
pump_flow_lpm = oil_flow_lpm / eta_vol
pump_displacement_cc_per_rev = pump_flow_lpm * 1000 / pump_speed_rpm
print(f"\nPump speed (half crank): {pump_speed_rpm} rpm")
print(f"Pump displacement: {pump_displacement_cc_per_rev:.2f} cc/rev")

# Pump power
pump_power_w = (oil_flow_m3s * pressure_Pa) / (eta_vol * eta_mech)
print(f"Pump power: {pump_power_w:.1f} W ({pump_power_w/745.7:.2f} hp)")

# Oil gallery sizing (main galleries)
# Flow velocity limit: 3 m/s for pressure galleries
velocity_max = 3.0  # m/s
area_gallery = oil_flow_m3s / velocity_max
dia_gallery = math.sqrt(4 * area_gallery / math.pi) * 1000  # mm
print(f"\nMain gallery diameter (3 m/s): {dia_gallery:.1f} mm")

# Bearing feed holes
# Main bearing feed: assume 4 mm diameter each
bearing_feed_dia = 4.0  # mm
bearing_feed_area = math.pi * (bearing_feed_dia/2)**2
print(f"Bearing feed hole diameter: {bearing_feed_dia} mm")

# Oil cooler sizing
# Heat rejection to oil: ~2% of fuel power
fuel_power = 2237e3  # W (from 3000 whp)
oil_heat = 0.02 * fuel_power
print(f"\nOil heat rejection: {oil_heat/1000:.1f} kW")

# Cooler capacity (air‑to‑oil)
deltaT_oil = 20  # K
cp_oil = 2000  # J/(kg·K) approximate
oil_density = 850  # kg/m³
oil_mass_flow = oil_flow_lpm * oil_density / 60000  # kg/s
cooler_heat_capacity = oil_mass_flow * cp_oil * deltaT_oil
print(f"Oil mass flow: {oil_mass_flow:.3f} kg/s")
print(f"Cooler capacity required: {cooler_heat_capacity/1000:.1f} kW")

# Oil pan volume (typical 8–10 L)
oil_pan_volume_l = 9.0
print(f"Oil pan volume: {oil_pan_volume_l} L")

# Oil filter (standard)
print(f"Oil filter: Dual remote full‑flow filters (e.g., FRAM PH8A equivalent)")

# Oil type: synthetic 5W‑50
print(f"Oil type: Synthetic 5W‑50")

print("\n--- CAD placeholder for oil galleries ---")
import sys
sys.path.insert(0, '/home/nenuka/.openclaw/workspace/david-version-1')
import cadquery as cq

# Create a simple block with gallery holes
block = cq.Workplane("XY").box(200, 300, 150)
# Main gallery hole
gallery = cq.Workplane("YZ").circle(dia_gallery/2).extrude(400)
block = block.cut(gallery.translate((-100,0,0)))
# Bearing feed holes
for i in range(7):  # 7 main bearings
    x = (i - 3) * 60
    hole = cq.Workplane("YZ").circle(bearing_feed_dia/2).extrude(200)
    block = block.cut(hole.translate((x,0,0)))

# Oil pump placeholder
pump = cq.Workplane("XY").cylinder(40, 50)
pump = pump.translate((150, 0, -100))

# Oil cooler placeholder
cooler = cq.Workplane("XY").box(150, 100, 30)
cooler = cooler.translate((0, 200, 0))

assembly = block.union(pump).union(cooler)

output_step = "lubrication_system_placeholder.step"
cq.exporters.export(assembly, output_step, "STEP")
print(f"✅ Lubrication system placeholder exported to {output_step}")

print("\n✅ Lubrication system design complete.")