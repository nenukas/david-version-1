# Connecting Rod Design Validation Checklist

*Based on engineering design principles, SAE standards, and industry practice.*

## 1. Dimensional Proportions

### Rod Ratio (L/R):
- **Rod length** (center‑to‑center) = L
- **Crank radius** = R = Stroke / 2
- **Rod ratio** = L / R = L / (Stroke/2)
- **Typical ranges:**
  - Passenger cars: 1.5‑1.8
  - High‑performance: 1.8‑2.0
  - Motorcycle: 1.6‑1.9
  - Racing: up to 2.2 (rare)

### Our V12 (check):
- Stroke: 47.5 mm → R = 23.75 mm
- Rod length: 150 mm (from optimization)
- Rod ratio = 150 / 23.75 = **6.32** (❌ **EXTREMELY HIGH**)
  - Likely error: Rod length should be ~2× stroke = 95 mm, not 150 mm
  - Or stroke definition mismatch?

### Beam Proportions (I‑section):
- **Height H** = 5t (typical proportion)
- **Width B** = 4t
- **Web thickness** = t
- **Flange thickness** = t
- **Cross‑section area** = 11t²

### Big‑end vs Small‑end:
- **Big‑end width** ≈ Crank‑pin length + (2‑4 mm clearance)
- **Small‑end width** ≈ Piston‑pin length + (1‑3 mm clearance)
- **Bearing diameters** with clearance (0.02‑0.05 mm radial)

## 2. I‑Beam Design

### Section Modulus (buckling resistance):
- **Critical buckling load** calculated from Rankine formula
- **Factor of safety** ≥ 3‑5 for fatigue

### Taper:
- **Beam height** decreases from big‑end to small‑end (10‑20% reduction)
- **Beam width** may also taper
- **Smooth transitions** avoid stress concentrations

### Our model check:
- Beam height: 50 mm constant (❌ should taper)
- Beam width: 30.22 mm constant (❌ should taper)
- Web thickness: 5.1 mm (reasonable)
- Flange thickness: 4.61 mm (reasonable)
- Taper: ❌ **MISSING** – uniform section inefficient

## 3. Big‑End Design

### Journal Bearing:
- **Bore diameter** = Crank‑pin diameter + clearance
- **Width** = Crank‑pin length + axial clearance
- **Bearing shell** thickness: 1.5‑3.0 mm (steel‑backed babbit)

### Cap & Bolts:
- **Split line** at 90° to beam centerline
- **Bolt diameter** ≈ 0.15‑0.20 × big‑end diameter
- **Bolt spacing** ≈ 1.5‑2.0 × bolt diameter
- **Bolt edge distance** ≥ 1.5 × bolt diameter
- **Cap thickness** ≈ 0.3‑0.4 × big‑end width

### Our model check:
- Big‑end Ø: 61.475 mm (✔️ matches crank‑pin + clearance)
- Big‑end width: 22.522 mm (✔️ reasonable)
- Bolt diameter: 10 mm (✔️ 0.16× big‑end Ø)
- Bolt spacing: 80 mm (❌ too large – should be ~30‑40 mm)
- Cap thickness: 10 mm (✔️ 0.44× width)
- Split line: ❌ **SIMPLIFIED** – no actual cap separation features

## 4. Small‑End Design

### Bush/Bearing:
- **Bore diameter** = Piston‑pin diameter + clearance
- **Width** = Piston‑pin length + axial clearance
- **Bush thickness** = 1.5‑3.0 mm (bronze/phosphor‑bronze)

### Reinforcement:
- **Boss outer diameter** ≈ Bush Ø + (10‑15 mm)
- **Transition radius** to beam ≥ 5 mm
- **Lubrication hole** (if pressure‑fed)

### Our model check:
- Small‑end Ø: 28.060 mm (✔️ matches piston‑pin + clearance)
- Small‑end width: 32.500 mm (✔️ reasonable)
- Bush thickness: not modeled (❌ missing)
- Reinforcement: 42.5 mm OD (✔️ 28 mm + 14.5 mm)
- Lubrication: ❌ **MISSING** – no oil passage

## 5. Manufacturing Considerations

### Forging/Casting:
- **Draft angles** ≥ 1‑3° on all surfaces
- **Parting line** along beam centerline
- **Flash allowance** 1‑2 mm

### Machining:
- **Bore tolerances** H7/g6 for bearings
- **Surface finish** Ra 0.4‑1.6 µm for bearing surfaces
- **Bolt‑hole threads** with adequate engagement

### Our model check:
- Draft angles: ❌ **MISSING** – all walls vertical
- Parting line: not defined
- Machining features: ❌ **MISSING** – no chamfers, radii
- Surface finish: not specified

## 6. Functional Validation

### Assembly Checks:
- **Big‑end fits** around crank‑pin with bearing clearance
- **Small‑end fits** piston pin with bush clearance
- **Bolts clear** cylinder walls at BDC
- **Rod clears** camshaft, cylinder walls, oil squirters

### Load Paths:
- **Combustion force** → piston pin → small‑end → beam → big‑end → crank‑pin
- **Inertia forces** (tension) at TDC
- **Buckling** (compression) at firing TDC
- **Bending** from piston side thrust

### Dynamic Clearances:
- **Rod angularity** maximum at mid‑stroke
- **Big‑end bearing** oil film thickness
- **Small‑end bushing** rotation clearance

## 7. Common Design Errors

### ❌ **My current conrod errors:**
1. **Rod ratio unrealistic** – 6.32 vs typical 1.5‑2.2 (likely dimension error)
2. **No beam taper** – uniform section inefficient for weight/stress
3. **Bolt spacing excessive** – 80 mm vs typical 30‑40 mm
4. **No bearing bushes** – solid material instead of replaceable bush
5. **No lubrication passages** – oil cannot reach bearing surfaces
6. **No draft angles** – cannot be forged/cast
7. **Sharp transitions** – stress concentrations at beam‑end junctions
8. **No cap features** – simplified split, no locating dowels, no serrations

### ✅ **Correct design would include:**
1. Realistic rod ratio (re‑check L and stroke)
2. Tapered I‑beam (height reduces 10‑20% to small‑end)
3. Proper bolt pattern with edge distances
4. Bronze bush in small‑end, bearing shells in big‑end
5. Oil passage from big‑end to small‑end (drilled or external)
6. Draft angles for forging (1‑3°)
7. Generous fillets (R3‑R10 mm) at stress concentrations
8. Cap with dowel/serrations, bolt‑head recesses, balance pads

## 8. Validation Procedure

### Step 1: Kinematic Check
- Verify rod ratio within realistic range (1.5‑2.2)
- Check piston‑to‑valve clearance at max lift
- Verify rod doesn't interfere with cylinder/crankcase

### Step 2: Structural Check
- Calculate buckling safety factor (Rankine/Johnson)
- Verify bearing pressures (<20 MPa for big‑end, <30 MPa for small‑end)
- Check bolt pre‑load for cap separation

### Step 3: Feature Check
- All required features present (bolts, bush, oil passages)
- Proper clearances for assembly
- Manufacturable geometry (draft, fillets)

### Step 4: Dynamic Check (FEA)
- Stress under peak combustion pressure
- Fatigue life at maximum RPM
- Bearing oil film thickness simulation

## 9. Our Specific Issues

### Critical Issue: Rod Length vs Stroke
- Current: L = 150 mm, Stroke = 47.5 mm → Ratio = 6.32
- **Likely error:** Optimized rod length may be incorrect, or stroke definition wrong
- **Check:** Rod length should be ~2× stroke = 95 mm for ratio ~2.0
- **Action:** Re‑examine optimization constraints and kinematic requirements

### Beam Geometry:
- Current: Constant 50 × 30.2 mm I‑beam
- **Improvement:** Taper height from ~55 mm at big‑end to ~45 mm at small‑end
- **Reason:** Moment distribution favors larger section near big‑end

### Manufacturing Readiness:
- Current: Simple extruded shapes, sharp edges
- **Required:** Draft angles, fillets, machining allowances
- **Cost impact:** Adds complexity but essential for production

## 10. Next Actions

### Immediate investigation:
1. **Re‑check rod length optimization** – likely constraint error
2. **Verify stroke definition** – 47.5 mm seems short for 94.5 mm bore
3. **Calculate realistic rod ratio** based on engine architecture

### Design corrections:
4. **Add taper** to I‑beam (10‑20% height reduction)
5. **Add bearing bushes/shells** with proper clearances
6. **Design proper cap** with bolts, dowels, serrations
7. **Add oil passages** for lubrication
8. **Apply draft angles & fillets** for manufacturability

### Validation:
9. **Run buckling calculation** with corrected dimensions
10. **Check bearing pressures** with actual loads
11. **Verify assembly clearance** in engine block

---

## Summary

My current connecting rod (`conrod_realistic.step`) has **fundamental kinematic issues** (unrealistic rod ratio) and **lacks critical features** for a functional component. It fails on:

- **❌ Kinematic validity** – rod ratio 6.32 vs typical 1.5‑2.2
- **❌ Structural efficiency** – no beam taper
- **❌ Bearing design** – no replaceable bushes/shells
- **❌ Manufacturing readiness** – no draft, sharp edges
- **❌ Lubrication** – no oil passages

**Root cause:** Likely optimization constraint error leading to unrealistic rod length. Must re‑examine before proceeding.

**Self‑validation capability:** I can now identify these errors by checking against engineering principles. The next step is to correct the fundamental dimensions, then add missing features.

---

*Last updated: 2026‑02‑13*  
*References: SAE standards, engine design textbooks, industry articles on rod ratios.*