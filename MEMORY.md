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

## Milestones
- [ ] Environment setup (Python env, CAD tools, simulation solvers)
- [ ] Conceptual design: target specifications & constraints
- [ ] Generative design of first component (e.g., suspension upright)
- [ ] FEA validation of component
- [ ] CFD of external aerodynamics
- [ ] Full vehicle CAD assembly
- [ ] Multibody dynamics simulation (lap time prediction)
- [ ] Manufacturing‑ready drawings & BOM

## Notes
*Daily logs are stored in `memory/YYYY‑MM‑DD.md`.*