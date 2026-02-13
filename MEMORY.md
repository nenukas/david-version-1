# MEMORY.md – Slothworks (V12 Hypercar Engineering)

## Project Identity
- **Name:** Slothworks (V12 Hypercar Project)
- **Engineering Assistant:** DAVID (Design Assistant for Vehicle Innovation & Development)
- **Version:** 1.0
- **Created:** 2026‑02‑12 09:31 SGT
- **Renamed:** 2026‑02‑12 18:28 SGT (per user request)
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
- **11 kRPM iteration** (expanded bounds, 30‑population × 20‑generations):
  - **Result:** No feasible design found under current constraints.
  - Best infeasible design mass: **1.04 kg**.
  - Critical violations:
    - Buckling safety factor: **0.48** (needs ≥2)
    - Compressive stress: **1024 MPa** (>440 MPa limit)
    - Small‑end bearing pressure: **275 MPa** (>60 MPa)
    - Fatigue safety factor: **0.69** (needs ≥2)
  - **Implication:** At 11 kRPM with 180 kN compression + 83 kN tensile inertia, the current constraints (mass <1 kg, bearing pressure <60 MPa, buckling SF ≥2) may be too strict. Need to relax constraints (allow higher mass, higher bearing pressure, lower buckling safety factor) or increase geometry bounds further.
- **Relaxed constraints defined** (17:54 SGT) per user request "Relax constraints without losing performance":
  - **Connecting rod:**
    - Mass limit: **1.5 kg** (was 1.0 kg)
    - Bearing pressure limit: **120 MPa** (was 60 MPa)
    - Buckling safety factor: **≥1.5** (was ≥2.0)
    - Fatigue safety factor: **≥1.5** (was ≥2.0)
    - Stress limit: **0.6×yield** (528 MPa, was 0.5×yield 440 MPa)
  - **Piston:**
    - Crown bending stress limit: **0.8×yield** (248 MPa, was 0.67×yield 208 MPa)
    - Pin bearing pressure limit: **80 MPa** (was 60 MPa)
    - Crown thickness bounds expanded: **8‑20 mm** (was 6‑15 mm)
    - Pin boss width bounds expanded: **10‑25 mm** (was 8‑20 mm)
- **Next:** Run generative design optimization with relaxed constraints (two sub‑agents launched).

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

## Piston Generative Design Progress (2026‑02‑12 17:47 SGT)
- **First optimization** (20‑population × 15‑generations, 11 kRPM loads):
  - Mass: **229 g** (<500 g target ✅)
  - Crown bending stress: **1113 MPa** (>208 MPa limit ❌) – crown too thin.
  - Pin bearing pressure (compression): **349 MPa** (>60 MPa ❌) – pin boss too narrow.
  - Constraints satisfied: mass only.
  - **Implication:** To handle 25 MPa peak pressure and 180 kN force, piston needs thicker crown (>10 mm) and wider pin boss (>15 mm). Optimization prioritized mass minimization over stress constraints.

- **Relaxed‑constraint optimization** (18:03 SGT, crown stress <248 MPa, pin bearing <80 MPa, expanded bounds):
  - Mass: **285 g** (<500 g target ✅)
  - Crown bending stress: **630 MPa** (>248 MPa limit ❌) – still too high.
  - Pin bearing pressure: **313 MPa** (>80 MPa ❌) – still too high.
  - Constraints satisfied: mass only.
  - **Interpretation:** Even with relaxed stress limits and expanded geometry bounds, the piston cannot satisfy stress and bearing constraints while staying under 500 g. Likely need either:
    1. **Higher‑strength material** (forged steel, yield ~800 MPa, allowing crown stress ~640 MPa)
    2. **Increased crown thickness** beyond 20 mm (requires larger compression height)
    3. **Increased pin boss width** beyond 25 mm (limited by piston diameter)
    4. **Additive‑manufactured lattice infill** to reduce mass while maintaining stiffness.

- **Next steps:** Explore additive‑manufacturing‑enabled generative design (lattice/hollow sections) or switch to forged steel material.

## Additive‑Manufacturing‑Aware Design Shift (2026‑02‑12 18:13 SGT)
**User directive:** Switch to higher‑strength materials and use additive‑manufacturing‑aware designs.

### New Material Selection
- **Connecting rod:** 300M high‑strength steel (yield 1800 MPa, density 7.85 g/cm³) with lattice infill.
- **Piston:** Forged steel (yield 800 MPa, density 7.85 g/cm³) with lattice infill.

### Gibson‑Ashby Scaling for Lattice Infill
- **Relative density ρ_rel** (0.2–1.0) as design variable.
- **Effective modulus:** E_eff = E_solid × ρ_rel²
- **Effective yield strength:** σ_y_eff = σ_y_solid × ρ_rel¹·⁵
- **Effective density:** ρ_eff = ρ_solid × ρ_rel

### Updated Analytical Models
- **`conrod_am.py`** – AM‑aware connecting rod analyzer with lattice scaling.
- **`piston_am.py`** – AM‑aware piston analyzer with lattice scaling.
- **`conrod_opt_am.py`** – Generative design optimization with 10 variables (geometry + ρ_rel), population 40, generations 25.
- **`piston_opt_am.py`** – Generative design optimization with 5 variables (geometry + ρ_rel), population 30, generations 20.

### Relaxed Constraints (AM‑enabled)
- **Connecting rod:** mass <2 kg, bearing pressure <200 MPa, buckling SF ≥1.2, fatigue SF ≥1.2, stress limit 0.6×yield_eff.
- **Piston:** mass <800 g, crown stress <0.8×yield_eff, pin bearing pressure <100 MPa.

### AM‑Aware Optimization Results (2026‑02‑12 18:26 SGT)
- **Connecting rod (300M steel + lattice infill):** No feasible designs (0/40 population). Best design mass **54 g**, but critical violations:
  - Buckling safety factor: **0.102** (needs ≥1.2)
  - Fatigue safety factor: **0.158** (needs ≥1.2)
  - Compressive stress: **854 MPa** > 0.6×yield_eff (≈102 MPa)
- **Piston (forged steel + lattice infill):** No feasible designs (0/30 population). Best design mass **156 g**, violations:
  - Crown bending stress: **648 MPa** > 0.8×yield_eff (≈59 MPa at ρ=0.2)
  - Pin bearing pressure: **318 MPa** > 100 MPa limit

**Interpretation:** Even with high‑strength steels and lattice infill, the 11 kRPM loads (180 kN compression + 83 kN tensile) are too severe for the current constraint thresholds.

### Options to Proceed
1. **Further relax constraints** – e.g., buckling SF ≥0.8, bearing pressure ≤250 MPa, crown stress ≤0.9×yield, fatigue SF ≥0.8.
2. **Increase lattice density lower bound** to 0.5–1.0 (sacrifice mass reduction for strength).
3. **Expand geometry bounds** – pin‑boss width up to 40 mm, beam height up to 200 mm, small‑end width up to 200 mm.
4. **Accept infeasible designs** – proceed with CAD of best‑infeasible geometries, note violations.
5. **Adjust loads** – reduce peak pressure (e.g., 200 bar → 144 kN) or RPM (e.g., 9000 RPM → 61 kN tensile).

**User direction (2026‑02‑12 19:03 SGT):** “Expand geometry and try iterating from best seed.”

### Updated Optimization Runs
- **Connecting rod v2 (expanded geometry bounds, lattice density lower bound 0.5):** ✅ **Feasible design found!**
  - Mass: **0.280 kg** (well under 2 kg limit)
  - Buckling safety factor: **1.63** (≥1.2)
  - Bearing pressure: big end 17.8 MPa, small end 30.1 MPa (<200 MPa)
  - Fatigue safety factor: **1.34** (≥1.2)
  - Compressive stress: **412.6 MPa** (<0.6×yield_eff)
  - Lattice relative density: **0.531** (within 0.5–1.0)
  - Geometry within expanded bounds (beam height 56.3 mm, beam width 45.7 mm, web thickness 3.3 mm, flange thickness 3.1 mm, big‑end width 116.7 mm, small‑end width 140.1 mm).
  - **CAD generated:** `conrod_opt_am_v2_results_20260212_184007.step` (STEP) and STL.

- **Piston v3 (further expanded geometry bounds, seed 2):** ❌ **No feasible designs found**
  - Expanded bounds: crown thickness 8–35 mm, pin‑boss width 10–60 mm, skirt length 30–100 mm, skirt thickness 2–15 mm, lattice density 0.5–1.0.
  - Population 30, generations 20, random seed 2.
  - Best design: mass 425 g, crown stress 639 MPa (>0.8×yield), pin bearing pressure 300 MPa (>100 MPa).
  - Bottleneck: mass constraint (800 g) conflicts with required pin‑boss width ≥32 mm & crown thickness ≥13.6 mm.

- **Piston v4 (relaxed mass limit, increased lattice density lower bound):** ❌ **No feasible designs found**
  - Relaxed constraints: mass <1500 g, lattice density lower bound 0.6.
  - Geometry bounds same as v3.
  - Population 30, generations 20, seed 2.
  - Best design: mass 550 g, crown stress 557 MPa (>0.8×yield), pin bearing 282 MPa (>100 MPa), pin‑boss width 11.4 mm.
  - Algorithm still avoided wider pin‑boss width to minimize mass, ignoring stress/bearing penalties.

- **Piston v5 (enforced geometric bounds):** ✅ **Feasible design found**
  - Enforced geometry: pin‑boss width ≥32 mm (actual 32.20 mm), crown thickness ≥12 mm (actual 12.29 mm).
  - Mass limit 1500 g satisfied (mass 1394.87 g), lattice density 0.615.
  - Crown bending stress 276.95 MPa (<0.8×yield), pin bearing pressure 99.81 MPa (<100 MPa).
  - **All constraints satisfied** – feasible designs: 12.
  - **CAD generated:** `piston_opt_am_v5_results_20260212_194740.step` and `.stl`.

## Cylinder Block Generative Design (2026‑02‑12 20:50 SGT)
- **Objective:** Compare materials (CGI‑450 cast iron, forged aluminum A356‑T6, billet aluminum 7075‑T6) for lightweight feasible design.
- **Analytical model:** `src/engine/cylinder_block.py` – simplified stress analysis (hoop stress, deck bending, bearing pressure). **Fixed unit error** (force calculation) that previously gave unrealistic stresses.
- **Optimization script:** `src/optimization/cylinder_block_opt.py` – DEAP evolutionary algorithm, population 30, generations 20 per material. Updated bounds: main bearing width 30–80 mm, height 40–120 mm.
- **Design variables:** Bore spacing (125–300 mm), deck thickness (8–30 mm), cylinder wall thickness (3–10 mm), water jacket thickness (2–8 mm), main bearing dimensions, skirt depth, pan rail width.
- **Previous results (2026‑02‑12 21:10 SGT):** ❌ No feasible designs found (all four stress constraints violated). Lightest infeasible: forged aluminum A356‑T6 (10.3 kg). Violated constraints: hoop stress (>0.6×yield), deck bending (>0.8×yield), bearing pressure (>80 MPa), bulkhead bending (>0.6×yield).
- **Updated optimization (2026‑02‑12 21:20 SGT):** ✅ **Constraints relaxed & geometry bounds expanded** (hoop stress <0.8×yield, deck bending <1.0×yield, bearing pressure <120 MPa, bulkhead bending <0.8×yield; bore spacing 100–350 mm, deck thickness 5–40 mm, cylinder wall 3–15 mm, water jacket 2–12 mm, main bearing width 20–100 mm, height 30–150 mm, skirt depth 40–200 mm, pan rail 8–40 mm).
- **Bug fix (2026‑02‑12 23:57 SGT):** Fixed `IndexError` in `save_results` (fitness_violations index out of range). Script now runs successfully.
- **New results (2026‑02‑12 23:58 SGT):** ✅ **Feasible designs found** for forged aluminum A356‑T6. Best feasible design mass **26.32 kg**, all constraints satisfied (hoop stress 177.5 MPa, deck bending 180.6 MPa, bearing pressure 43.3 MPa, bulkhead bending 165.8 MPa). Feasible designs in final population: **21**.
- **Next:** Run full material comparison (CGI‑450, forged A356‑T6, billet 7075‑T6) with full population (30) and generations (20) to determine lightest feasible block.

## CAD Generation Progress (2026‑02‑12 19:10 SGT)
- **Crankshaft CAD** – `crankshaft_optimized.step` (generative design, mass 26.43 kg, all constraints satisfied).
- **Connecting rod CAD (AM‑aware)** – `conrod_opt_am_v2_results_20260212_184007.step` (feasible design, mass 0.28 kg, all constraints satisfied).
- **Connecting rod CAD (baseline)** – `conrod_test.step` (previous infeasible design).
- **Piston CAD (baseline)** – `piston_baseline.step` (forged aluminum baseline).
- **Piston CAD (AM‑aware)** – pending v3 optimization results.
- **FEA validation paused** due to Calculix output parsing issues; proceeding with generative design of remaining components.

## Milestones
- [x] Environment setup (Python env, CAD tools, simulation solvers)
- [x] Conceptual design: target specifications & constraints
- [x] Generative design of first component (crankshaft)
- [~] FEA validation of crankshaft (Calculix integration) – paused
- [x] Generative design of connecting rod – **feasible AM‑aware design found, CAD generated**
- [x] Generative design of piston – **feasible AM‑aware design found, CAD generated**
- [~] Generative design of cylinder block – **re‑running with relaxed constraints & expanded bounds**
- [ ] Assembly of full engine CAD
- [ ] Multibody dynamics simulation (lap time prediction)
- [ ] Manufacturing‑ready drawings & BOM

## Notes
*Daily logs are stored in `memory/YYYY‑MM‑DD.md`.*