# LEARN ENGINE DESIGN

*Studying real engine components to build proper generative design protocol.*

## 1. PISTON DESIGN (from GrabCAD tutorial)

### Key Features:
- **Crown**: Curved surface (arc radius ~300mm) for combustion chamber.
- **Ring lands**: Multiple grooves for compression rings and oil control ring.
- **Ring grooves**: Typically 3 rings (2 compression, 1 oil control).
- **Skirt**: Arched profile trimmed for weight reduction and clearance.
- **Pin bosses**: Reinforced structures with holes for wrist pin (piston pin).
- **Internal cavity**: Hollow interior for weight reduction.
- **Material**: Aluminum 5052 or similar alloy.

### Dimensions (example 85mm bore):
- Overall height: ~90mm
- Crown thickness: ~5mm
- Ring land diameters: 79mm (6mm smaller than bore for clearance)
- Ring groove widths: 4.3mm (compression), 6mm (oil control)
- Ring groove spacing: 11.6mm
- Wrist pin diameter: 33.8mm
- Pin boss outer diameter: 45mm
- Pin boss length: 25mm
- Skirt arc: radius 40mm, height 12mm

### Construction Sequence:
1. **Base cylinder** (bore diameter × height)
2. **Ring lands** via offset planes and cut extrusions
3. **Crown shape** via revolve of arc profile
4. **Internal cavity** via cut extrusion
5. **Pin holes** through both sides
6. **Skirt trimming** with arc profile
7. **Pin bosses** as reinforced cylindrical structures
8. **Fillets** for smooth transitions

## 2. CONNECTING ROD DESIGN (from technical literature)

### Key Features:
- **I‑beam cross‑section**: Optimized for buckling resistance.
- **Tapered profile**: Wider at big end, narrower at small end.
- **Big end**: Split cap with bolts, bearing shell.
- **Small end**: Bush/bearing for wrist pin.
- **Bolt holes**: For big end cap assembly.
- **Radius transitions**: Avoid stress concentrations.
- **Material**: Forged steel or aluminum alloy.

### Typical Proportions (I‑beam):
- Height H = 5t
- Width B = 4t
- Web thickness = t
- Flange thickness = t
- Cross‑section area = 11t²

### Dimensions (example for 100mm bore engine):
- Center‑to‑center length: 300‑350mm
- Big end bore: 58‑76mm (crankpin diameter + clearance)
- Small end bore: 28‑34mm (wrist pin diameter + clearance)
- Big end width: ~76mm (crankpin length + clearance)
- Small end width: ~32mm (wrist pin length + clearance)
- I‑beam cross‑section at big end: 42mm × 28mm
- I‑beam cross‑section at small end: 30mm × 28mm
- Bolt diameter: M10‑M12

## 3. CRANKSHAFT DESIGN

### Key Features:
- **Main journals**: Supported by bearings in block.
- **Crank pins**: Offset for piston connection.
- **Cheeks/webs**: Connect journals to pins, often with counterweights.
- **Fillet radii**: Critical for fatigue life.
- **Oil passages**: Drilled for lubrication.
- **Counterweights**: Balance rotating masses.
- **Material**: Forged or cast steel.

### Typical Proportions:
- Stroke = 2 × crank radius
- Main journal diameter ≈ 0.65‑0.75 × bore
- Crankpin diameter ≈ 0.55‑0.65 × bore
- Cheek thickness ≈ 0.15‑0.20 × stroke
- Fillet radius ≈ 0.05‑0.10 × journal diameter

## 4. GENERATIVE DESIGN PRINCIPLES (learned from mistakes)

### What I did wrong:
1. **Simplistic geometry** – cylinders + blocks, not realistic features.
2. **No functional features** – missing ring lands, bolt holes, fillets.
3. **Wrong coordinate systems** – not aligning with kinematic requirements.
4. **No manufacturing awareness** – draft angles, tool access, wall thickness.
5. **No load‑path optimization** – I‑beam not tapered, no stress concentrations.

### What real generative design should include:
1. **Functional requirements** – must accommodate rings, pins, bearings, bolts.
2. **Manufacturing constraints** – minimum wall thickness, draft angles, tool access.
3. **Load‑path optimization** – material follows principal stress directions.
4. **Assembly constraints** – clearances, fits, bolt patterns.
5. **Aesthetic/ergonomic considerations** – smooth transitions, brand identity.

## 5. NEW PROTOCOL OUTLINE

### Phase 1: Requirements Definition
- List all functional features (ring grooves, pin holes, bolt holes, etc.)
- Define manufacturing constraints (min wall thickness, draft angles)
- Set performance targets (weight, stiffness, safety factors)
- Establish kinematic constraints (stroke, rod length, deck height)

### Phase 2: Parametric Skeleton
- Create master sketch with critical dimensions
- Establish coordinate systems and datums
- Define cross‑section profiles at key stations
- Create taper/transition laws for smooth variation

### Phase 3: Feature‑Based Construction
- Build base geometry (envelope)
- Add functional features (cuts, holes, grooves)
- Apply fillets and radii
- Verify clearances and interferences

### Phase 4: Validation
- Check volume, mass, center of gravity
- Verify manufacturing constraints
- Perform FEA for stress, deflection
- Kinematic simulation for motion clearance

### Phase 5: Optimization Loop
- Adjust parameters to meet targets
- Iterate on cross‑section, taper, feature sizes
- Use generative algorithms (topology optimization) within constraints

## 6. IMMEDIATE ACTION ITEMS

1. **Create parametric piston model** based on tutorial.
2. **Study connecting rod CAD models** from GrabCAD library.
3. **Develop script** that constructs realistic piston with all features.
4. **Apply same approach** to connecting rod, then crankshaft.
5. **Build assembly** with proper kinematics and clearances.

## 7. MOTORCYCLE VS CAR ENGINE DIFFERENCES (Key Insights)

### Scale & Proportions:
- **Motorcycle**: smaller bore (50‑100 mm), higher RPM (8,000‑14,000), oversquare bore/stroke.
- **Car**: larger bore (75‑105 mm), lower RPM (5,000‑7,000), more square/undersquare.

### Piston Design:
- **Motorcycle**: slipper pistons (reduced skirt), higher ring placement, deeper valve reliefs.
- **Car**: full/slipper skirts, lower ring placement, shallower valve reliefs.

### Connecting Rod:
- **Motorcycle**: I‑beam/H‑beam lightweight, smaller big‑end, needle bearings (2‑stroke).
- **Car**: I‑beam robust, larger big‑end, plain bearings, two‑piece bolted cap.

### Crankshaft:
- **Motorcycle**: one‑piece pressed, smaller journals, minimal counterweights.
- **Car**: forged/cast one‑piece, larger journals, full counterweights.

### Manufacturing:
- **Motorcycle**: cylinder barrels replaceable, integrated transmission, easy rebuild.
- **Car**: monoblock construction, separate transmission, serviceability secondary.

### Implications for V12 Hypercar:
- Blend motorcycle‑style lightweight components for high RPM with car‑style robust bearings for high torque.
- Use hypercar‑level materials (titanium, additive manufacturing).

## 8. RESOURCES

- GrabCAD Piston Tutorial: https://grabcad.com/tutorials/piston-head
- Connecting Rod Design Slides: https://www.slideshare.net/slideshow/u3-design-of-connecting-rodi-section-bigampsmall-eng-bolt-whipping-stress/163897732
- Engine Builder's Guide: H‑Beam vs. I‑Beam Rods: https://www.speedwaymotors.com/the-toolbox/engine-builder-s-guide-h-beam-vs-i-beam-rods-explained/145858
- V12 Engine CAD Models: https://grabcad.com/library/v12-engine-assembly-4
- Motorcycle Engine Technical Drawings: Pinterest collections, GrabCAD library.

---

*Last updated: 2026‑02‑13*