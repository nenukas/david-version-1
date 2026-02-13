# V12 Hypercar – Phase 2: System Testing & Validation

## Overview
This directory contains simulation setups, test plans, and prototyping instructions for validating the V12 8.0 L twin‑charged hypercar engine design at 30 MPa peak pressure and 12 k RPM.

## Test Categories

### 1. Finite Element Analysis (FEA)
**Goal:** Verify structural integrity under combined pressure, thermal, and inertial loads.

#### 1.1 Piston Crown – Coupled Thermo‑Mechanical (Axisymmetric)
- **Geometry:** `fea/piston_crown_15.0mm.step`
- **Solver:** Ansys Mechanical APDL (or CalculiX/Code_Aster)
- **Loads:**
  - Pressure: 30 MPa uniform on crown
  - Heat flux: 3 MW/m² (0.003 W/mm²) typical combustion
  - Convection: water‑jacket h = 8000 W/(m²·K), oil‑jet h = 15000 W/(m²·K)
- **Boundary conditions:** Axisymmetric, bottom fixed in Z, symmetry axis fixed radially
- **Expected outputs:** von‑Mises stress distribution, temperature field, safety factor >1.5
- **Files:**
  - `fea/piston_thermomech_ansys.apdl` – APDL script
  - `fea/piston_thermomech_calculix.inp` – CalculiX input (pressure‑only)

#### 1.2 Single‑Cylinder Assembly – 3D Static Structural
- **Geometry:** `fea/single_cylinder_assembly_v2.step` (piston at TDC)
- **Solver:** Ansys Mechanical
- **Loads:** Pressure 30 MPa on piston crown, bearing preloads, gravity
- **Boundary conditions:** Cylinder‑block bolt holes fixed, symmetry planes
- **Expected outputs:** Stress in block, crank, conrod; contact pressures; deformation
- **Files:**
  - `fea/single_cylinder_ansys.apdl` – APDL script
  - `fea/single_cylinder_mesh.png` – mesh snapshot

#### 1.3 Crankshaft – Dynamic Fatigue
- **Geometry:** `fea/crankshaft_30MPa_unified.step`
- **Solver:** Ansys Mechanical (transient structural)
- **Loads:** Time‑varying conrod force (210 kN peak), torque 3360 Nm
- **Boundary conditions:** Main‑bearing constraints, cyclic symmetry
- **Expected outputs:** Fatigue safety factor, critical fillet stresses, Campbell diagram
- **Files:** `fea/crankshaft_fatigue_ansys.apdl`

### 2. Computational Fluid Dynamics (CFD)
**Goal:** Evaluate airflow, heat transfer, and pressure drops in forced‑induction system.

#### 2.1 Intercooler Sidepod Airflow
- **Geometry:** Simplified sidepod volume + `fea/intercooler_core_placeholder.step`
- **Solver:** OpenFOAM (simpleFoam, buoyantBoussinesqSimpleFoam)
- **Boundary conditions:** Inlet velocity 30 m/s (200 km/h), ambient temperature 35 °C, outlet pressure
- **Expected outputs:** Velocity field, pressure drop across core, heat‑transfer coefficient map
- **Files:**
  - `cfd/sidepod_airflow/` – OpenFOAM case directory
  - `cfd/sidepod_airflow/0/` – initial conditions
  - `cfd/sidepod_airflow/system/` – control dict, fvSchemes, fvSolution

#### 2.2 Intake & Exhaust Flow
- **Geometry:** Plumbing routes from `v12_assembly_with_plumbing_simple.step` (extract intake/exhaust pipes)
- **Solver:** OpenFOAM (rhoSimpleFoam)
- **Boundary conditions:** Mass‑flow inlet 2.036 kg/s, pressure outlet, adiabatic walls
- **Expected outputs:** Pressure loss per component, flow distribution, turbo inlet swirl
- **Files:** `cfd/intake_exhaust/` – OpenFOAM case

#### 2.3 Coolant & Refrigerant Loop
- **Geometry:** Simplified coolant channels, intercooler water passages, refrigerant pipes
- **Solver:** OpenFOAM (chtMultiRegionFoam) or Ansys Fluent
- **Boundary conditions:** Pump mass flow, heat rejection in radiator, compressor work
- **Expected outputs:** Temperature distribution, heat‑exchange effectiveness, required pump power
- **Files:** `cfd/cooling_loop/` – multi‑region setup

### 3. Prototyping & Bench Testing
**Goal:** Fabricate and test critical components before full‑scale engine build.

#### 3.1 Intercooler Core – Brazed Aluminum Plate‑Fin
- **Design:** `prototyping/intercooler_core_detailed.step` (detailed fin geometry)
- **Manufacturing:** CNC‑machined aluminum plates, vacuum brazing
- **Test setup:** Hot‑air blower (200 °C), water‑coolant loop, thermocouples, pressure sensors
- **Measurements:** Heat transfer rate vs. airflow, pressure drop, leakage test
- **Files:**
  - `prototyping/intercooler_core_detailed.step`
  - `prototyping/intercooler_test_plan.txt`

#### 3.2 Piston – Additive Manufacturing (Lattice Infill)
- **Design:** `prototyping/piston_am.step` (lattice‑optimized)
- **Manufacturing:** Laser powder‑bed fusion (316L or maraging steel)
- **Test setup:** Hydraulic pressure test to 45 MPa, thermal‑cycle furnace
- **Measurements:** Dimensional accuracy, microstructure, hardness
- **Files:** `prototyping/piston_am.step`, `prototyping/piston_test_procedure.txt`

#### 3.3 Valve Train – Spring‑Rate Validation
- **Components:** Titanium valves (Ø42.5/35.9 mm), chrome‑silicon springs
- **Test setup:** Servo‑hydraulic fatigue tester, high‑speed camera
- **Measurements:** Spring rate, natural frequency, valve lift vs. cam profile
- **Files:** `prototyping/valvetrain_test_plan.txt`

## Directory Structure
```
v12_testing_phase2/
├── README.md                 (this file)
├── fea/                      (finite element analysis)
│   ├── piston_crown_15.0mm.step
│   ├── single_cylinder_assembly_v2.step
│   ├── crankshaft_30MPa_unified.step
│   ├── piston_thermomech_ansys.apdl
│   ├── single_cylinder_ansys.apdl
│   └── crankshaft_fatigue_ansys.apdl
├── cfd/                      (computational fluid dynamics)
│   ├── sidepod_airflow/      (OpenFOAM case)
│   ├── intake_exhaust/       (OpenFOAM case)
│   └── cooling_loop/         (multi‑region case)
├── prototyping/              (fabrication & bench testing)
│   ├── intercooler_core_detailed.step
│   ├── piston_am.step
│   ├── intercooler_test_plan.txt
│   └── valvetrain_test_plan.txt
└── docs/                     (reference documents)
    ├── ansys_setup_guide.txt
    ├── openfoam_basics.txt
    └── material_properties.csv
```

## Required Software & Resources
- **FEA:** Ansys Mechanical 2024 R2 (or CalculiX 2.21, Code_Aster 15.8)
- **CFD:** OpenFOAM v2312 (or Ansys Fluent, Star‑CCM+)
- **CAD:** FreeCAD 0.21, CadQuery
- **Prototyping:** CNC mill, vacuum brazing oven, LPBF 3D printer, hydraulic test stand
- **Compute:** 64 GB RAM, 16‑core CPU, NVIDIA RTX 6000 Ada (for transient CFD)

## Timeline (Estimated)
| Week | Task |
|------|------|
| 1 | Piston crown FEA + sidepod airflow CFD |
| 2 | Single‑cylinder assembly FEA + intake/exhaust CFD |
| 3 | Crankshaft fatigue + cooling‑loop CFD |
| 4 | Intercooler core prototype fabrication |
| 5 | Bench testing of intercooler & valve springs |
| 6 | Report generation & design iteration |

## Next Steps
1. **Immediate:** Run piston crown thermo‑mechanical FEA (see `fea/piston_thermomech_ansys.apdl`).
2. **Parallel:** Set up OpenFOAM sidepod case (`cfd/sidepod_airflow/`).
3. **Procurement:** Order titanium valves, chrome‑silicon spring wire, York 210 compressor.
4. **Fabrication:** Send intercooler core CAD to machine shop for quoting.

## Contact
- **Repository:** [github.com/nenukas/david‑version‑1](https://github.com/nenukas/david-version-1)
- **CAD files:** `v12_30MPa_design/cad/`
- **Design reports:** `v12_30MPa_design/docs/`

---
*Updated: 2026‑02‑13 13:00 SGT*