#!/usr/bin/env python3
"""
Testing plan for sidepod‑mounted water‑cooled intercoolers.
"""
print("=== INTERCOOLER TESTING PLAN ===")

print("\n1. CFD Simulation (Pre‑prototype)")
print("   - Sidepod external airflow (100–300 km/h)")
print("   - Internal ducting, pressure drop")
print("   - Heat exchanger core airflow distribution")
print("   - Coolant flow distribution")
print("   Tools: OpenFOAM / ANSYS Fluent")

print("\n2. Thermal Simulation")
print("   - Steady‑state heat transfer (air → coolant)")
print("   - Transient response (load changes)")
print("   - Coolant temperature rise")
print("   Tools: ANSYS Thermal / custom Python")

print("\n3. Prototype Fabrication")
print("   - CNC machined aluminum core (plate‑fin)")
print("   - Welded coolant passages")
print("   - Mounting brackets, ducting")
print("   - Instrumentation: thermocouples, pressure taps")

print("\n4. Wind Tunnel Test")
print("   - Scale model sidepod with intercooler")
print("   - Airflow velocity 20–80 m/s")
print("   - Measure pressure drop Δp vs flow")
print("   - Infrared thermography for surface temps")

print("\n5. Hot‑Air Bench Test")
print("   - Electric heater to simulate turbo outlet (up to 150 °C)")
print("   - Coolant loop with chiller (5 °C inlet)")
print("   - Measure air outlet temperature, heat rejection")
print("   - Validate against CFD")

print("\n6. Vehicle Integration Test")
print("   - Install on engine dyno")
print("   - Full load sweeps (up to 3000 whp)")
print("   - Monitor intake temperature, coolant temps")
print("   - Adjust refrigeration loop setpoints")

print("\n7. Endurance & Reliability")
print("   - Thermal cycling (1000 cycles)")
print("   - Vibration testing (engine mounted)")
print("   - Coolant corrosion / leakage checks")

print("\nTimeline (estimated):")
print("   CFD & design: 2 weeks")
print("   Prototype fabrication: 3 weeks")
print("   Wind tunnel & bench tests: 2 weeks")
print("   Vehicle integration: 2 weeks")
print("   Total: 9 weeks")

print("\n✅ Testing plan defined.")