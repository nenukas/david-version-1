#!/usr/bin/env python3
"""
Revised forced‑induction cooling with passive airflow + active refrigeration.
Assume intercoolers are air‑to‑air (plate‑fin) with ram‑air cooling.
Active bus compressor only supplements to reach target intake temperature.
Goal: use one engine‑driven compressor, avoid electrics.
"""
import math

# Air side parameters
air_flow_kg_s = 2.036  # kg/s
T_ambient_C = 30.0
T_ambient = T_ambient_C + 273.15

# Stage 1: post‑turbo
turbo_pr = 2.0
turbo_efficiency = 0.78
gamma = 1.4
T_in_turbo = T_ambient
T_out_turbo_ideal = T_in_turbo * turbo_pr**((gamma-1)/gamma)
T_out_turbo = T_in_turbo + (T_out_turbo_ideal - T_in_turbo) / turbo_efficiency
print(f"Stage 1: Turbo outlet temperature = {T_out_turbo-273.15:.1f}°C")

# Target after intercooler stage 1 (with combined passive+active)
T_target_stage1_C = 50.0
T_target_stage1 = T_target_stage1_C + 273.15
deltaT_stage1 = T_out_turbo - T_target_stage1
print(f"  Required ΔT = {deltaT_stage1:.1f} K")

# Stage 2: post‑supercharger
supercharger_pr = 1.24
supercharger_efficiency = 0.70
T_in_super = T_target_stage1
T_out_super_ideal = T_in_super * supercharger_pr**((gamma-1)/gamma)
T_out_super = T_in_super + (T_out_super_ideal - T_in_super) / supercharger_efficiency
print(f"Stage 2: Supercharger outlet temperature = {T_out_super-273.15:.1f}°C")
T_target_stage2_C = 50.0  # ideal intake temperature
T_target_stage2 = T_target_stage2_C + 273.15
deltaT_stage2 = T_out_super - T_target_stage2
print(f"  Required ΔT = {deltaT_stage2:.1f} K")

# Heat rejection each stage (total)
cp_air = 1005  # J/(kg·K)
Q1_total = air_flow_kg_s * cp_air * deltaT_stage1
Q2_total = air_flow_kg_s * cp_air * deltaT_stage2
print(f"\nTotal heat rejection:")
print(f"  Stage 1: {Q1_total/1000:.1f} kW")
print(f"  Stage 2: {Q2_total/1000:.1f} kW")
print(f"  Total: {(Q1_total+Q2_total)/1000:.1f} kW")

# Passive air‑to‑air intercooler effectiveness
# Assume vehicle speed 100 km/h (27.8 m/s), frontal airflow through intercooler.
# Ram‑air mass flow through intercooler core:
core_frontal_area = 0.2  # m² each (assumed)
air_density = 1.2  # kg/m³
ram_air_flow = core_frontal_area * 27.8 * air_density  # kg/s
print(f"\nRam‑air flow per intercooler (0.2 m² frontal, 100 km/h): {ram_air_flow:.2f} kg/s")

# Heat transfer coefficient for plate‑fin with forced air: ~100 W/m²·K
U_passive = 100  # W/(m²·K)
# Effectiveness of air‑to‑air intercooler (counterflow)
# We'll assume passive cooling can achieve ΔT_passive = 0.7 * (T_hot - T_ambient)
# Actually, we need to compute NTU method. Let's approximate.
# For simplicity, assume passive cooling reduces required active cooling by 60%.
passive_fraction = 0.6
Q1_active = Q1_total * (1 - passive_fraction)
Q2_active = Q2_total * (1 - passive_fraction)
print(f"\nAssuming passive air‑to‑air cooling handles {passive_fraction*100:.0f}% of heat.")
print(f"Active refrigeration load:")
print(f"  Stage 1: {Q1_active/1000:.1f} kW")
print(f"  Stage 2: {Q2_active/1000:.1f} kW")
print(f"  Total active: {(Q1_active+Q2_active)/1000:.1f} kW")

# Combined intercooler: air‑to‑air core with internal refrigerant tubes (cold plate).
# Active refrigeration cools the coolant that circulates through intercooler cold plate.
# Coolant (water‑glycol) temperature set by refrigerant evaporator.
coolant_inlet_C = 5.0  # °C (from evaporator)
coolant_inlet = coolant_inlet_C + 273.15
coolant_deltaT = 5.0  # K (small ΔT for better heat transfer)
coolant_cp = 3800
coolant_flow_total = (Q1_active + Q2_active) / (coolant_cp * coolant_deltaT)
print(f"\nCoolant system (coolant at {coolant_inlet_C}°C, ΔT={coolant_deltaT} K):")
print(f"  Total coolant flow: {coolant_flow_total:.3f} kg/s")

# Refrigeration loop (R134a)
Te_C = 0.0  # evaporator temperature 0°C (to cool coolant to 5°C)
Te = Te_C + 273.15
Tc_C = 60.0  # condenser temperature
Tc = Tc_C + 273.15
COP_carnot = Te / (Tc - Te)
COP_real = COP_carnot * 0.6
print(f"\nRefrigeration loop:")
print(f"  Evaporator temp: {Te_C}°C, Condenser temp: {Tc_C}°C")
print(f"  Carnot COP: {COP_carnot:.2f}")
print(f"  Estimated real COP: {COP_real:.2f}")

W_comp = (Q1_active + Q2_active) / COP_real
print(f"  Compressor power required: {W_comp/1000:.1f} kW")

# Select engine‑driven compressor
# Bus compressor capacity ~25 kW at 0°C evaporator.
if W_comp <= 25000:
    print(f"  ✅ Single bus compressor (25 kW) suffices.")
else:
    # Need larger compressor, maybe truck A/C compressor up to 40 kW.
    # Use a larger engine‑driven compressor (e.g., York 210).
    print(f"  ⚠️  Requires larger compressor (≥{W_comp/1000:.1f} kW).")
    print(f"     Consider York 210 or similar engine‑driven compressor.")

# Refrigerant mass flow (approx)
hg = 400e3  # J/kg
hf = 280e3
delta_h = hg - hf
m_ref = (Q1_active + Q2_active) / delta_h
print(f"  Refrigerant mass flow: {m_ref:.4f} kg/s ({m_ref*3600:.1f} kg/h)")

# Condenser (radiator) sizing with ram‑air cooling
U_rad = 50  # W/(m²·K)
deltaT_air = 30  # K
Q_cond = (Q1_active + Q2_active) + W_comp
A_rad = Q_cond / (U_rad * deltaT_air)
print(f"\nCondenser radiator (air‑cooled):")
print(f"  Heat rejected: {Q_cond/1000:.1f} kW")
print(f"  Required area: {A_rad:.2f} m²")
if A_rad > 0:
    side_cm = math.sqrt(A_rad) * 100
    print(f"  Approx dimensions: {side_cm:.0f} cm square, or 800 x 500 mm.")

# Intercooler core sizing (air‑to‑air part)
# For passive fraction, need sufficient frontal area.
# Assume U_passive = 100 W/m²·K, ΔT_mean ≈ (T_hot - T_ambient) / 2
T_hot_avg1 = (T_out_turbo + T_target_stage1) / 2
T_hot_avg2 = (T_out_super + T_target_stage2) / 2
deltaT_mean1 = T_hot_avg1 - T_ambient
deltaT_mean2 = T_hot_avg2 - T_ambient
A_passive1 = (Q1_total * passive_fraction) / (U_passive * deltaT_mean1)
A_passive2 = (Q2_total * passive_fraction) / (U_passive * deltaT_mean2)
print(f"\nPassive intercooler core area (U={U_passive} W/m²·K):")
print(f"  Stage 1: {A_passive1:.2f} m²")
print(f"  Stage 2: {A_passive2:.2f} m²")
print(f"  Total passive area: {A_passive1+A_passive2:.2f} m²")

# Weight estimate
print(f"\nWeight estimate (revised):")
print(f"  Passive intercoolers (Al): {(A_passive1+A_passive2)*2.5:.1f} kg")
print(f"  Coolant (water‑glycol): {coolant_flow_total*2*10:.1f} kg")
print(f"  Compressor (engine‑driven): 15 kg")
print(f"  Condenser radiator: {A_rad*1.5:.1f} kg")
print(f"  Piping, valves, accumulator: 10 kg")
total_weight = (A_passive1+A_passive2)*2.5 + coolant_flow_total*2*10 + 15 + A_rad*1.5 + 10
print(f"  Total added weight: ~{total_weight:.1f} kg")

# Packaging: intercoolers mounted in airstream (front or side ducts)
print(f"\nPackaging notes:")
print(f"  Intercoolers can be front‑mounted or side‑ducted.")
print(f"  Refrigeration compressor driven by engine accessory belt.")
print(f"  Condenser radiator mounted behind front grille.")
print(f"  Coolant‑refrigerant heat exchanger (chiller) near intercoolers.")

print("\n✅ Revised cooling analysis complete.")