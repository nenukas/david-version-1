#!/usr/bin/env python3
"""
Detailed sizing of two‑stage intercooler & refrigeration loop for V12 3000 whp engine.
CORRECTED with proper Kelvin temperatures.
"""
import math

# Air side parameters (from forced_induction_sizing.py)
air_flow_kg_s = 2.036  # kg/s
T_ambient_C = 30.0
T_ambient = T_ambient_C + 273.15
# Stage 1: post‑turbo (turbo outlet temp)
turbo_pr = 2.0
turbo_efficiency = 0.78
gamma = 1.4
T_in_turbo = T_ambient  # after air filter
T_out_turbo_ideal = T_in_turbo * turbo_pr**((gamma-1)/gamma)
T_out_turbo = T_in_turbo + (T_out_turbo_ideal - T_in_turbo) / turbo_efficiency
print(f"Stage 1: Turbo outlet temperature = {T_out_turbo-273.15:.1f}°C")
# Target after intercooler stage 1
T_target_stage1_C = 50.0
T_target_stage1 = T_target_stage1_C + 273.15
deltaT_stage1 = T_out_turbo - T_target_stage1
print(f"  Desired ΔT = {deltaT_stage1:.1f} K")

# Stage 2: post‑supercharger
supercharger_pr = 1.24
supercharger_efficiency = 0.70
T_in_super = T_target_stage1
T_out_super_ideal = T_in_super * supercharger_pr**((gamma-1)/gamma)
T_out_super = T_in_super + (T_out_super_ideal - T_in_super) / supercharger_efficiency
print(f"Stage 2: Supercharger outlet temperature = {T_out_super-273.15:.1f}°C")
# Target after intercooler stage 2 (intake manifold)
T_target_stage2_C = 50.0
T_target_stage2 = T_target_stage2_C + 273.15
deltaT_stage2 = T_out_super - T_target_stage2
print(f"  Desired ΔT = {deltaT_stage2:.1f} K")

# Heat rejection each stage
cp_air = 1005  # J/(kg·K)
Q1 = air_flow_kg_s * cp_air * deltaT_stage1  # watts
Q2 = air_flow_kg_s * cp_air * deltaT_stage2
print(f"\nHeat rejection:")
print(f"  Stage 1 (post‑turbo): {Q1/1000:.1f} kW")
print(f"  Stage 2 (post‑supercharger): {Q2/1000:.1f} kW")
print(f"  Total: {(Q1+Q2)/1000:.1f} kW")

# Intercooler sizing (plate‑fin air‑to‑liquid)
# Assume water‑glycol coolant at 30 °C inlet (from refrigerant chiller)
coolant_inlet_C = 30.0
coolant_inlet = coolant_inlet_C + 273.15
coolant_deltaT = 10.0  # K
coolant_outlet = coolant_inlet + coolant_deltaT
coolant_cp = 3800  # J/(kg·K) for 50/50 glycol‑water
# Required coolant mass flow per stage
m_coolant1 = Q1 / (coolant_cp * coolant_deltaT)
m_coolant2 = Q2 / (coolant_cp * coolant_deltaT)
print(f"\nCoolant ({coolant_inlet_C} °C inlet, ΔT={coolant_deltaT} K):")
print(f"  Stage 1 coolant flow: {m_coolant1:.3f} kg/s")
print(f"  Stage 2 coolant flow: {m_coolant2:.3f} kg/s")
print(f"  Total coolant flow: {m_coolant1 + m_coolant2:.3f} kg/s")

# Heat exchanger effectiveness method
epsilon = 0.85
C_air = air_flow_kg_s * cp_air
C_coolant1 = m_coolant1 * coolant_cp
C_coolant2 = m_coolant2 * coolant_cp
C_min1 = min(C_air, C_coolant1)
C_min2 = min(C_air, C_coolant2)
NTU1 = -math.log(1 - epsilon)
NTU2 = -math.log(1 - epsilon)
U = 300  # W/(m²·K)
A1 = NTU1 * C_min1 / U
A2 = NTU2 * C_min2 / U
print(f"\nIntercooler heat‑transfer area (U≈{U} W/m²·K):")
print(f"  Stage 1 area: {A1:.2f} m²")
print(f"  Stage 2 area: {A2:.2f} m²")
print(f"  Total area: {A1+A2:.2f} m²")

# Core dimensions (typical plate‑fin)
frontal_area = 0.2  # m²
core_depth1 = A1 / frontal_area / 2
core_depth2 = A2 / frontal_area / 2
print(f"  Assuming frontal area {frontal_area*10000:.0f} cm²:")
print(f"    Stage 1 core depth ≈{core_depth1*1000:.0f} mm")
print(f"    Stage 2 core depth ≈{core_depth2*1000:.0f} mm")

# Refrigeration loop (vapor‑compression) to cool coolant
Q_total = Q1 + Q2
print(f"\nRefrigeration loop:")
print(f"  Coolant heat load: {Q_total/1000:.1f} kW")

# Refrigerant R134a
Te_C = 5.0
Te = Te_C + 273.15
Tc_C = 60.0
Tc = Tc_C + 273.15
COP_carnot = Te / (Tc - Te)
COP_real = COP_carnot * 0.6
print(f"  Evaporator temp: {Te_C} °C, Condenser temp: {Tc_C} °C")
print(f"  Carnot COP: {COP_carnot:.2f}")
print(f"  Estimated real COP: {COP_real:.2f}")

# Compressor power
W_comp = Q_total / COP_real
print(f"  Compressor power required: {W_comp/1000:.1f} kW")

# Bus compressor selection
print(f"  Typical bus compressor capacity: 20‑25 kW at 0 °C evaporator.")
if W_comp <= 25000:
    print("  ✅ Single bus compressor may suffice.")
else:
    print("  ⚠️  May require two compressors or larger unit.")

# Refrigerant mass flow (using enthalpy difference)
hg = 400e3  # J/kg (approx at 5°C)
hf = 280e3  # J/kg (approx at 60°C)
delta_h = hg - hf
m_ref = Q_total / delta_h
print(f"  Refrigerant mass flow: {m_ref:.4f} kg/s ({m_ref*3600:.1f} kg/h)")

# Condenser (radiator) sizing
U_rad = 50  # W/(m²·K)
air_flow_rad = 2.0  # kg/s
cp_air = 1005
deltaT_air = 30  # K
Q_cond = Q_total + W_comp
A_rad = Q_cond / (U_rad * deltaT_air)
print(f"\nCondenser (radiator) sizing:")
print(f"  Heat rejected: {Q_cond/1000:.1f} kW")
print(f"  Required area (U≈{U_rad} W/m²·K, ΔT={deltaT_air} K): {A_rad:.2f} m²")
if A_rad > 0:
    side_cm = math.sqrt(A_rad) * 100
    print(f"  Approx dimensions: {side_cm:.0f} cm square, or 600 x 400 mm.")
else:
    print("  Area negative (check heat load).")

# Coolant reservoir and pump
print(f"\nCoolant system:")
coolant_total_flow = m_coolant1 + m_coolant2
print(f"  Total coolant flow: {coolant_total_flow:.3f} kg/s ({coolant_total_flow*3600:.1f} kg/h)")
print(f"  Pump power (ΔP=2 bar, η=0.7): {coolant_total_flow*2e5/0.7/1000:.1f} W")

# Weight estimate
print(f"\nWeight estimate:")
print(f"  Intercoolers (plate‑fin Al): { (A1+A2)*2.5 :.1f} kg")
print(f"  Coolant (water‑glycol): { (m_coolant1+m_coolant2)*2*10 :.1f} kg")
print(f"  Bus compressor: 12 kg")
print(f"  Condenser radiator: { A_rad*1.5 :.1f} kg")
print(f"  Piping, valves, accumulator: 8 kg")
total_weight = (A1+A2)*2.5 + (m_coolant1+m_coolant2)*2*10 + 12 + A_rad*1.5 + 8
print(f"  Total added weight: ~{total_weight:.1f} kg")

# Packaging notes
print(f"\nPackaging notes:")
print(f"  Intercoolers can be mounted on sides of engine bay (each ~{frontal_area*10000:.0f} cm² frontal).")
print(f"  Condenser radiator mounted forward of engine (front of bay).")
print(f"  Bus compressor mounted on engine accessory drive (belt‑driven).")
print(f"  Coolant‑refrigerant heat exchanger (chiller) mounted near intercoolers.")
print(f"  Refrigerant lines routed with insulation.")

print("\n✅ Intercooler & refrigeration loop sizing complete.")