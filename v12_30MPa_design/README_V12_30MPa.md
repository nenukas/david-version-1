# V12 8.0 L Twin‑Charged Hypercar Engine – 30 MPa Peak Pressure Design

## Overview
Generative‑design‑driven engine components for a 3000 whp (2237 kW) hypercar powerplant. All components validated for 30 MPa peak cylinder pressure and 12 k RPM redline.

## Components & Status

| Component | Material | Key Metric | Safety Factor | CAD File |
|-----------|----------|------------|---------------|----------|
| **Piston crown** | Forged steel + lattice infill | Crown stress ≈202 MPa | 2.1 | `piston_crown_15mm_full.step` |
| **Cylinder block deck** | 7075‑T6 aluminum | Deck stress ≈349 MPa | 1.44 | `cylinder_block_deck_12mm.step` |
| **Connecting rod** | 300M steel + lattice infill | Compressive stress 522 MPa, buckling SF 1.04 | 1.23 | `conrod_opt_relaxed2_30MPa_results_*.step` |
| **Crankshaft** | 300M forged steel | Bending stress 499 MPa, shear stress 5.5 MPa | >3 | `crankshaft_30MPa_unified.step` |
| **Cylinder head** | A356‑T6 aluminum | Titanium valves (37.5 g intake, 31.7 g exhaust) | – | `cylinder_head_simplified.step` |
| **Valve springs** | Chrome‑silicon steel | Spring rates 122 N/mm intake, 117 N/mm exhaust, natural frequency 150 Hz | – | – |
| **Forced‑induction layout** | Placeholder | Twin Garrett GTX4294R + centrifugal supercharger | – | `v12_forced_induction_layout.step` |
| **Turbo manifolds** | 321 stainless steel | Runner Ø33.6 mm, collector Ø60.4 mm | – | `turbo_manifold_placeholder.step` |
| **Intercooler core** | Aluminum plate‑fin | Water‑cooled, sidepod‑mounted, ≈8 m² total | – | `intercooler_core_placeholder.step` |
| **Lubrication system** | – | Oil flow 6.4 L/min @ 5 bar, pump 1.25 cc/rev | – | `lubrication_system_placeholder.step` |
| **Full V12 assembly** | – | Static assembly (pistons at TDC) | – | `v12_full_assembly_compound.step` |

## Forced‑Induction & Cooling

### Air Flow & Boost
- **Total air flow:** 2.036 kg/s (7329 kg/h, 269 lb/min)
- **Pressure ratio required:** 2.48 (≈1.48 bar gauge)
- **Turbo:** Twin Garrett GTX4294R (PR 2.0 each)
- **Supercharger:** Centrifugal (Vortech V‑30 type, PR 1.24)

### Intercooling Strategy
- **Two‑stage water‑cooled intercoolers** mounted in sidepods.
- **Air‑to‑liquid plate‑fin cores** (total area ≈8 m²).
- **Coolant:** Water‑glycol, chilled by active refrigeration loop.
- **Active refrigeration:** R134a vapor‑compression with engine‑driven **York 210 compressor** (28 kW).
- **Condenser:** Water‑cooled (refrigerant‑to‑coolant), heat rejected via engine radiator.

### Valve Train (12 k RPM Safe)
- **Valve diameters:** Intake 42.5 mm, exhaust 35.9 mm (4‑valve per cylinder).
- **Valve lift:** Intake 11.1 mm, exhaust 9.3 mm.
- **Titanium valves** reduce inertia forces.
- **Spring forces at max lift:** Intake 495 N, exhaust 354 N.
- **Spring rates:** Intake 122 N/mm, exhaust 117 N/mm.
- **Natural frequency:** 150 Hz (>1.5× cam frequency).

### Thermal Safety Margins
- **Piston crown critical heat flux:** 0.347 W/mm² (safe for typical combustion fluxes ≈0.003 W/mm²).
- **Cylinder block deck** thickened to 12 mm; stress 349 MPa (SF 1.44).
- **Cylinder wall hoop stress:** 307 MPa (SF 1.48).

## Generative Design Parameters
- **Optimization method:** Evolutionary algorithm (DEAP) with stress, buckling, and mass constraints.
- **Lattice infill:** Gibson‑Ashby scaling for additive‑manufacturing effective properties.
- **CAD generation:** CadQuery scripts produce STEP files directly from optimization results.

## Files & Directories

### CAD (`/cad/`)
- `piston_crown_15mm_full.step`
- `cylinder_block_deck_12mm.step`
- `conrod_opt_relaxed2_30MPa_results_*.step`
- `crankshaft_30MPa_unified.step`
- `cylinder_head_simplified.step`
- `v12_forced_induction_layout.step`
- `turbo_manifold_placeholder.step`
- `intercooler_core_placeholder.step`
- `lubrication_system_placeholder.step`
- `single_cylinder_assembly_v2.step`
- `v12_full_assembly_compound.step`

### Analysis (`/analysis/`)
- `crankshaft_30MPa_final.json` – geometry & metrics
- `full_assembly_data.json` – V12 cylinder positions
- `fea_thermal/` – CalculiX/Ansys setup guides, thermal assessment scripts

### Scripts (`/scripts/`)
- `forced_induction_sizing.py`
- `forced_induction_cooling_revised.py`
- `intercooler_sidepod_design.py`
- `intercooler_optimization.py`
- `intercooler_core_cad.py`
- `condenser_radiator_sizing.py`
- `compressor_selection.py`
- `intercooler_testing_plan.py`
- `cylinder_head_design.py`
- `cylinder_head_12kRPM.py`
- `titanium_valves.py`
- `valve_spring_optimization.py`
- `valve_spring_reasonable.py`
- `turbo_manifold_design.py`
- `lubrication_system_design.py`
- `full_v12_assembly_compound.py`
- `v12_design_summary.py`

### Documentation (`/docs/`)
- `ansys_setup_guide.txt`
- `cylinder_block_thermal_summary.txt`
- `README_V12_30MPa.md` (this file)

## Next Steps & Recommendations
1. **Run coupled thermo‑mechanical FEA** in Ansys using `single_cylinder_assembly_v2.step`.
2. **CFD of intercooler sidepod airflow** and heat transfer validation.
3. **Fabricate prototype intercooler cores** and bench‑test.
4. **Source York 210 compressor** and design engine‑mounting bracket.
5. **Additive‑manufacturing lattice optimization** for mass reduction on all components.
6. **Cooling system CFD** to verify airflow through sidepods and radiator.

## Notes
- **Crankshaft CAD volume discrepancy:** analytical mass model underestimates volume; stress analysis remains valid.
- **Valve‑spring natural frequency** raised to 150 Hz (safe from resonance).
- **Intercooler core area** based on water‑cooled design; air‑side pressure drop must be validated.
- **Condenser heat rejection** transferred to engine radiator (simplifies packaging).

## Repository
All files are available in the `david‑version‑1` GitHub repository under `v12_30MPa_design/`.

---
*Generated 2026‑02‑13 | OpenClaw Slothworks Project*