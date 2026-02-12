# MEMORY.md – DAVID Engineering Assistant

## Project Identity
- **Name:** DAVID (Design Assistant for Vehicle Innovation & Development)
- **Version:** 1.0
- **Created:** 2026‑02‑12 09:31 SGT
- **Primary Goal:** Design, simulate, and produce CAD for a working sports car/hypercar.
- **Secondary Goal:** Evolve into a general‑purpose engineering assistant (JARVIS‑like).

## Core Principles
1. **Generative‑first:** Use optimization algorithms to explore design spaces.
2. **Simulation‑driven:** Validate every design with physics‑based simulation.
3. **Modular architecture:** Each subsystem (suspension, powertrain, aerodynamics) is independently modeled and tested.
4. **Open‑source toolchain:** Prefer FreeCAD, Calculix, OpenFOAM, Modelica.
5. **Real‑time interaction:** Voice/chat control, live dashboards, progressive disclosure.

## Key Decisions
**2026‑02‑12 09:50 SGT – V12 Twin‑Charged Hypercar Engine**
- **Architecture:** 8.0 L V12 (95 mm bore × 95 mm stroke), 60° bank angle, DOHC 4‑valve.
- **Dual‑mode operation:** 
  - **Standard mode:** 6‑cylinder active, lean‑burn, Euro‑6 compliant, ~500–600 WHP.
  - **Overdrive mode:** All 12 cylinders, 5 bar boost, water‑injection, bus‑compressor intercooling, 3000 WHP short‑burst (<30 s).
- **Materials:**
  - Block: CGI‑450/500 iron (cast).
  - Crankshaft: 300M forged steel (nitrided).
  - Connecting rods: Ti‑6Al‑4V titanium.
  - Pistons: Forged 2618 aluminum with ceramic‑thermal‑barrier coating.
  - Cylinder head: A356‑T6 aluminum with copper‑beryllium valve seats.
- **Emissions:** Euro‑6 compliance in standard mode via cylinder deactivation, lean‑burn, likely secondary‑air injection & dual‑catalyst.
- **Vehicle layout:** Mid‑engine, rear‑wheel‑drive with mechanical Torsen differential.
- **Generative design focus:** Crankshaft first (dual‑mode load cases), then block, conrod, piston.

## Progress & Results
**2026‑02‑12 10:05 SGT – Crankshaft Generative Design Completed**
- **Method:** Evolutionary algorithm (DEAP) with 30 individuals × 20 generations.
- **Objectives:** Minimize mass while satisfying stress, stiffness, and geometric constraints.
- **Load cases:** Overdrive mode (2800 Nm torque, 180 kN conrod force, 11000 rpm).
- **Optimal design:**
  - Mass: **13.03 kg** (300M forged steel)
  - Main journal: 70.0 mm diameter × 26.6 mm width
  - Crank pin: 69.2 mm diameter × 26.2 mm width
  - Cheek: 80.3 mm outer radius, 69.6 mm hole radius, 17.6 mm thickness (33 % sector)
  - Fillet radii: 5.3 mm (main), 4.5 mm (pin)
- **Constraints satisfied:** Shear stress (5.9 MPa < 500 MPa), bending stress (310 MPa < 500 MPa), torsional stiffness (504 kHz > 212 Hz), mass (<50 kg).
- **CAD exported:** `crankshaft_optimized.step` (881 KB) and STL.

**2026‑02‑12 11:51 SGT – Enhanced Geometric Feasibility Checks**
- **Added checks:** Minimum wall thickness (5 mm), aspect ratios (cheek thickness/radius > 0.1, pin width/diameter > 0.3, journal width/diameter > 0.3), positive fillet radii (>1 mm), positive volumes for all components.
- **CAD validation:** Volume > 0, single‑solid check, mass comparison between analytical and CAD.
- **Re‑optimization result** (with enhanced checks):
  - Mass: **26.43 kg** (stricter geometric constraints)
  - Main journal: 80.2 mm diameter × 28.8 mm width
  - Crank pin: 86.5 mm diameter × 35.6 mm width
  - Cheek: 80.8 mm outer radius, 38.0 mm hole radius, 17.3 mm thickness
  - Fillet radii: 4.3 mm (main), 5.2 mm (pin)
- **All constraints satisfied**, geometric feasibility validated, CAD exported.

**2026‑02‑12 16:45 SGT – Connecting‑Rod Generative Design Started**
- **Material:** Ti‑6Al‑4V titanium (density 4.43 g/cm³, yield 880 MPa).
- **Load cases:** Overdrive compression 180 kN, tensile 83 kN (11 kRPM), eccentricity 0.5 mm.
- **Analytical model:** Euler‑Johnson buckling, fatigue (Goodman), bearing pressure, I‑beam cross‑section.
- **Optimization pipeline:** DEAP evolutionary algorithm with 8 design variables (beam dimensions, bearing widths, fillets).
- **Initial result** (20‑population × 15‑generations):
  - Mass: **1.32 kg** (target <1 kg)
  - Buckling safety factor: 2.12 (≥2 ✅)
  - Compressive stress: 344 MPa (<440 MPa ✅)
  - Bearing pressure (small end): 311 MPa (>60 MPa ❌) – needs larger small‑end width/diameter.
  - Fatigue safety factor: 1.92 (<2 ❌) – close.
- **Second iteration** (variable small‑end diameter added, 20‑population × 15‑generations):
  - Mass: **1.31 kg** (target <1 kg)
  - Buckling safety factor: 1.66 (≥2 ❌) – insufficient.
  - Compressive stress: 433 MPa (<440 MPa ✅)
  - Bearing pressure (small end): 233 MPa (>60 MPa ❌) – improved but still high.
  - Fatigue safety factor: 1.53 (<2 ❌).
  - Small‑end diameter increased to 30.9 mm (from fixed 28 mm).
- **Next:** Further adjust bounds (increase big‑end width, beam height), re‑optimize, generate CAD.

## Technical Stack
**Generative Design & Optimization:**
- `pyOpt` (0.84) – gradient‑based optimization
- `OpenMDAO` (3.42) – multidisciplinary optimization framework
- `DEAP` (1.4.3) – evolutionary algorithms

**CAD & Geometry:**
- `CadQuery` (parametric CAD via Python)
- `OpenCASCADE` kernel (via CadQuery)
- `meshio` (mesh conversion)

**Simulation (planned):**
- `Calculix` (ccx) – FEA (to be installed)
- `OpenFOAM` – CFD (optional, later)
- `PyTorch` – surrogate ML models (optional)

**Visualization & Interface:**
- `Matplotlib`, `Plotly`
- `Gradio` (web dashboards)
- OpenClaw integration (real‑time chat control)

## CAD Generation Progress (2026‑02‑12 17:20 SGT)
- **Connecting rod CAD** generated from optimized design (mass 1.42 kg, constraints partially satisfied). File: `conrod_test.step`.
- **Piston CAD** generated from baseline geometry (bore 94.5 mm, forged aluminum). File: `piston_baseline.step`.
- **Crankshaft CAD** already available (`crankshaft_optimized.step`).
- **FEA validation paused** due to Calculix output parsing issues; proceeding with generative design of remaining components.

## Milestones
- [x] Environment setup (Python env, CAD tools, simulation solvers)
- [x] Conceptual design: target specifications & constraints
- [x] Generative design of first component (crankshaft)
- [~] FEA validation of crankshaft (Calculix integration) – paused
- [~] Generative design of connecting rod – CAD generated, optimization ongoing
- [~] Generative design of piston – CAD generated, optimization pending
- [ ] Generative design of cylinder block
- [ ] Assembly of full engine CAD
- [ ] Multibody dynamics simulation (lap time prediction)
- [ ] Manufacturing‑ready drawings & BOM

## Notes
*Daily logs are stored in `memory/YYYY‑MM‑DD.md`.*