# CAD Protocol for Manufacturing‑Ready Geometry

## Philosophy

**Math first, CAD second.**  
Never draw a line without calculating its dimensions, tolerances, and interactions with neighboring parts.

**Gradual complexity.**  
Start with the simplest solid that captures the envelope. Add one feature at a time, validate, then proceed.

**Validation at every step.**  
Volume, bounding box, clearance, and stress checks must pass before moving to the next feature.

**Manufacturing awareness.**  
Consider wall thickness, draft angles, tool access, and additive‑manufacturing constraints from the beginning.

---

## 1. Mathematical Verification (Pre‑CAD)

Before opening a CAD tool, compute:

### 1.1. Key dimensions from first principles
- **Envelope dimensions** (length × width × height)
- **Critical interfaces** (bearing diameters, bolt patterns, sealing surfaces)
- **Clearances** (running fits, thermal expansion, assembly tolerance stack‑up)
- **Mass properties** (volume × density, center of mass, moments of inertia)

### 1.2. Load cases and stress margins
- **Peak loads** (pressure, inertia, impact)
- **Material properties** (yield strength, fatigue limit, modulus)
- **Safety factors** (static, fatigue, buckling)
- **Deflection limits** (stiffness requirements)

### 1.3. Manufacturing constraints
- **Minimum wall thickness** (casting: ≥3 mm, AM: ≥0.5 mm)
- **Draft angles** (for molding: ≥1°)
- **Tool access** (machining: tool diameter, reach)
- **Surface finish** (bearing surfaces: Ra ≤ 0.8 µm)

**Output:** A `specs.json` file containing all computed values with tolerances.

---

## 2. Stepwise Construction

### 2.1. Start with the envelope
Create a rectangular block representing the outer bounds of the part.  
Export as `01_envelope.step`.

**Validation:**
- Volume matches calculated envelope volume (tolerance ±0.1%).
- Bounding box matches envelope dimensions (tolerance ±0.01 mm).

### 2.2. Add primary features (holes, bosses, ribs)
One feature per step. Each step must satisfy:
- **Geometric correctness:** dimensions match specs.
- **Volume change:** matches calculated removal/addition.
- **No unintended voids or overlaps.**

Export each step as `02_feature_A.step`, `03_feature_B.step`, etc.

### 2.3. Apply fillets and chamfers
Add edge breaks for stress reduction and manufacturability.
- **Fillet radii:** ≥0.5 mm (AM), ≥1.0 mm (machining).
- **Chamfer angles:** 45° typical for deburring.

Export as `XX_fillets.step`.

### 2.4. Finalize with fine details
- Threads, logos, identification marks.
- Non‑critical aesthetic features.

---

## 3. Validation at Each Step

### 3.1. Automated checks (run after every step)
```python
def validate_step(solid, step_name, expected_volume, expected_bbox):
    # Volume check
    vol = solid.Volume()
    if abs(vol - expected_volume) / expected_volume > 0.01:
        raise ValueError(f"Volume mismatch in {step_name}")
    
    # Bounding‑box check
    bbox = solid.BoundingBox()
    if any(abs(a-b) > 0.01 for a,b in zip(bbox, expected_bbox)):
        raise ValueError(f"Bounding‑box mismatch in {step_name}")
    
    # Wall‑thickness check (minimum)
    min_thick = compute_min_wall_thickness(solid)
    if min_thick < MIN_WALL_THICKNESS:
        raise ValueError(f"Wall too thin in {step_name}: {min_thick} mm")
    
    # Export STEP
    export_step(solid, f"{step_name}.step")
```

### 3.2. Manual visual inspection
Open the STEP file in a viewer, verify:
- No missing faces, inverted normals, or self‑intersections.
- Features are correctly positioned.
- Smooth transitions between surfaces.

### 3.3. Clearance analysis
For assemblies, compute:
- **Running fits** (clearance vs interference).
- **Thermal gaps** (expansion at operating temperature).
- **Kinematic range** (full motion without collision).

---

## 4. Gradual Complexity Increase

**Level 1 – Solid envelope**  
Just the outer block. Validate volume and dimensions.

**Level 2 – Major cutouts**  
Bore holes, bearing seats, mounting faces.

**Level 3 – Secondary features**  
Ribs, lightening pockets, coolant passages.

**Level 4 – Fillets/chamfers**  
Edge breaks for stress and manufacturing.

**Level 5 – Fine details**  
Threads, identification, surface textures.

**Rule:** Do not advance to Level *n*+1 until Level *n* passes all validation.

---

## 5. Manufacturing‑Spec Compliance

### 5.1. Wall‑thickness map
Generate a color‑coded map showing thickness distribution.  
Ensure everywhere ≥ minimum required.

### 5.2. Draft‑angle analysis
For molded parts, verify all vertical faces have sufficient draft.

### 5.3. Tool‑access simulation
For machined features, verify tool can reach without collision.

### 5.4. Support‑structure analysis (AM)
Identify overhangs >45° that require supports.

### 5.5. Tolerance stack‑up
Compute worst‑case assembly dimensions using tolerances from specs.

---

## 6. Assembly Verification

### 6.1. Interference detection
Perform Boolean intersection between mated parts.  
Any overlap >0.001 mm indicates interference.

### 6.2. Kinematic simulation
Move parts through full range of motion, check for collisions.

### 6.3. Bolt‑clearance check
Verify wrench access, thread engagement length, washer clearance.

### 6.4. Seal‑groove verification
Check O‑ring or gasket groove dimensions against standards.

---

## 7. Documentation

Each step must be documented in a `log.json`:

```json
{
  "step": "03_bore_hole",
  "timestamp": "2026‑02‑13T14:22:23Z",
  "description": "Cylinder bore, Ø94.5 mm, depth 12 mm",
  "validation": {
    "volume_mm3": {"expected": 2650609.4, "actual": 2650609.4, "ok": true},
    "bbox_mm": {"expected": [194.7, 194.7, 72.14], "actual": [194.7, 194.7, 72.14], "ok": true},
    "min_wall_mm": 4.87,
    "clearance_checks": []
  },
  "files": [
    "cad_steps_20260213_142223/cylinder_block/03_bore_hole.step"
  ],
  "next_step": "04_water_jacket"
}
```

---

## 8. Example: V12 Cylinder Head

### Step 1 – Envelope block
150 × 120 × 40 mm block. Validate volume = 720 000 mm³.

### Step 2 – Combustion chamber
Pent‑roof cutout with 15° taper. Validate volume removal ≈ 68 000 mm³.

### Step 3 – Valve seats
Two circular cutouts Ø46.75 mm (intake) and Ø39.49 mm (exhaust).  
Validate seat contact area > 200 mm² each.

### Step 4 – Valve‑guide holes
Ø8 mm holes, depth 30 mm. Validate guide‑to‑seat concentricity.

### Step 5 – Ports
Intake and exhaust ports with smooth transitions.  
Validate flow area > 800 mm².

### Step 6 – Cam‑bore holes
Ø30 mm through‑holes. Validate bearing‑length‑to‑diameter ratio ≥ 1.0.

### Step 7 – Stiffening ribs
Add ribs between ports. Validate rib‑width‑to‑height ratio ≤ 0.2.

### Step 8 – Fillets
Radius 2 mm on all sharp internal edges. Validate no edge‑break violations.

### Step 9 – Threads
Spark‑plug thread M14×1.25. Validate thread engagement length ≥ 10 mm.

---

## 9. Tools & Automation

### 9.1. Python validation script
`validate_cad.py` – runs all checks on a STEP file.

### 9.2. Clearance calculator
`clearance_check.py` – computes fits for assemblies.

### 9.3. Manufacturing‑check plugin
`manufacturing_check.py` – wall thickness, draft angles, tool access.

### 9.4. Log generator
`log_step.py` – creates JSON log entry for each step.

---

## 10. Common Pitfalls & Solutions

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| **Missing mathematical spec** | CAD dimensions guessed | Compute all dimensions from first principles before drawing |
| **Volume mismatch >1%** | Boolean operations incorrect | Check feature order, use solid‑body modeling |
| **Thin walls** | Stress concentration, manufacturing failure | Increase thickness or add ribs |
| **Interference in assembly** | Parts won’t fit together | Perform interference detection before finalizing |
| **Poor surface continuity** | Gaps in fillets, sharp edges | Use tangent‑continuous blends, larger fillet radii |

---

## 11. Success Criteria

A CAD model is **manufacturing‑ready** when:

1. **All dimensions** are derived from mathematical calculations.
2. **Every step** has passed volume, bounding‑box, and clearance checks.
3. **Wall thicknesses** everywhere ≥ minimum required.
4. **Draft angles** sufficient for chosen process.
5. **No interferences** in assembled state.
6. **Tolerance stack‑up** yields acceptable worst‑case fits.
7. **Full documentation** exists for each construction step.

---

## 12. Next Steps for V12 Hypercar

1. **Fix conrod‑crank interference** – recalculate `big_end_width` vs crank‑cheek gap.
2. **Re‑run step‑by‑step generation** with corrected parameters.
3. **Perform thermal‑expansion analysis** for hot clearances.
4. **Run FEA** on critical components (piston crown, conrod beam, crank pin).
5. **Validate with CFD** (coolant flow, combustion chamber turbulence).

---

**Last updated:** 2026‑02‑13  
**Project:** Slothworks V12 Hypercar  
**Repository:** https://github.com/nenukas/david‑version‑1