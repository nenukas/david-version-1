# Crankshaft Design Validation Checklist

*Based on engineering design principles, SAE standards, and industry practice.*

## 1. Dimensional Proportions

### Journal Diameters:
- **Main journal diameter** ≈ 0.65‑0.75 × bore  
  - Bore: 94.5 mm → expected 61‑71 mm  
  - Current: 76.485 mm (0.81× bore) – **slightly large** but acceptable for high‑performance.
- **Crank‑pin diameter** ≈ 0.55‑0.65 × bore  
  - Expected 52‑61 mm  
  - Current: 61.415 mm (0.65× bore) – **within range**.
- **Journal width** ≈ 0.3‑0.4 × journal diameter  
  - Main journal width: 26.709 mm (0.35× diameter) – **OK**.
  - Crank‑pin width: 26.525 mm (0.43× diameter) – **OK**.

### Stroke & Overlap:
- **Stroke radius** = stroke/2 = 47.5 mm  
- **Journal + pin diameters** = 76.485 + 61.415 = 137.9 mm > stroke radius  
  - **Interference:** Cheeks must be notched or curved to avoid overlap.
  - Current model uses rectangular cheeks that intersect journals – **design issue**.
- **Overlap ratio** = (journal_dia + pin_dia) / (2 × stroke_radius) = 1.45 (should be <1.0 for straight cheeks)  
  - **Requires** curved cheeks or undercut.

### Cheek Dimensions:
- **Cheek thickness** ≈ 0.2‑0.3 × stroke radius  
  - Current: 17.15 mm (0.36×) – **acceptable**.
- **Cheek radius** (distance from main‑journal center to outer cheek) ≈ 1.5‑1.8 × stroke radius  
  - Current: 82.651 mm (1.74×) – **acceptable**.
- **Cheek hole radius** (lightening hole) ≈ 0.8‑1.0 × cheek radius  
  - Current: 69.381 mm (0.84×) – **OK**.

### Fillet Radii (critical for fatigue):
- **Main journal fillet** ≥ 0.05 × journal diameter (≈3.8 mm)  
  - Current: 7.088 mm (0.093×) – **OK**.
- **Crank‑pin fillet** ≥ 0.05 × pin diameter (≈3.1 mm)  
  - Current: 2.225 mm (0.036×) – **⚠️ possibly undersized**.
- **Fillet transition smoothness** – no sharp corners.

## 2. Functional Features

### Oil Passages:
- **Main‑journal oil feed** (drilled from main bearing saddle)
- **Crank‑pin oil feed** (cross‑drilled from main journal to pin)
- **Oil‑hole chamfers** (0.5‑1.0 mm) to prevent cracking
- **Current model:** **❌ NOT MODELED** – missing oil passages.

### Balance Weights:
- **Counterweight mass** ≈ 50‑60% of reciprocating mass per cylinder
- **Weight positioning** opposite crank pin
- **Current model:** **❌ NOT MODELED** – simplified rectangular cheeks act as counterweights but not optimized.

### Keyways & Threads:
- **Front snout keyway** (Woodruff or parallel) for timing gear/pulley
- **Rear flange** for flywheel attachment (bolt holes, register)
- **Current model:** **❌ NOT MODELED** – ends are simple cylinders.

### Bearing Surfaces:
- **Journal surface finish** Ra 0.2‑0.4 µm (ground)
- **Hardness** 55‑60 HRC (induction hardened)
- **Current model:** **⚠️ Surface properties not specified**.

## 3. Manufacturing Considerations

### Draft Angles:
- **Sand casting:** ≥ 1‑3° draft on all vertical surfaces
- **Forging:** ≥ 0.5‑1° draft
- **Current model:** **❌ NO DRAFT ANGLES** – all walls vertical.

### Fillets & Chamfers:
- **All sharp edges** must have minimum radius (R0.5‑R2 mm)
- **Transition zones** (journal‑to‑cheek, cheek‑to‑web) require generous fillets
- **Current model:** **⚠️ Fillet radii present but chamfers missing**.

### Machining Allowances:
- **Rough casting/forging** oversize 2‑3 mm on journals
- **Finish machining** tolerance ±0.01 mm on diameters
- **Current model:** **❌ NET‑SHAPE** – no machining allowances.

### Material & Heat Treatment:
- **Common materials:** 4340 steel, 300M, forged steel
- **Heat treatment:** quench & temper, induction hardening of journals
- **Current model:** **⚠️ Material specified (300M) but heat treatment not defined**.

## 4. Assembly & Clearance

### Bearing Clearances:
- **Main bearing clearance** 0.02‑0.05 mm (diameter)
- **Rod bearing clearance** 0.03‑0.06 mm
- **Current model:** **⚠️ Clearances not modeled** – diameters are nominal.

### Axial Clearance:
- **Thrust washers** on one main journal (width +0.1‑0.3 mm)
- **Current model:** **❌ NOT MODELED**.

### Bolt Holes & Threads:
- **Flywheel bolts** (8‑12× M10‑M12)
- **Pulley bolts** (4‑6× M8)
- **Current model:** **❌ NOT MODELED**.

## 5. Dynamic Validation

### Torsional Stiffness:
- **Natural frequency** > 1.5× firing frequency at redline
- **Current analysis:** 600,808 Hz (extremely high) – **OK**.

### Stress Concentration:
- **Max bending stress** at fillet under peak combustion load
- **Allowable** < 0.7× yield strength
- **Current:** 499 MPa bending, yield ≈ 1500 MPa → SF ≈ 3 – **OK**.

### Fatigue Safety Factor:
- **Minimum** ≥ 1.5 for high‑reliability applications
- **Current:** Not calculated explicitly but stress levels low.

## 6. Common Design Errors

### ❌ **My current crankshaft errors (`crankshaft_30MPa_final.step`):**
1. **Cheek interference** – rectangular cheeks intersect journal/pin diameters due to insufficient stroke radius.
2. **Missing oil passages** – no drilled oil feeds for main/rod bearings.
3. **Missing balance weights** – cheeks not shaped as counterweights.
4. **Missing keyways/threads** – no attachment features for timing gear/flywheel.
5. **No draft angles** – cannot be cast/forged.
6. **Undersized pin fillet** – 2.225 mm (<5% of pin diameter).
7. **No chamfers** on sharp edges (stress concentrators).
8. **No machining allowances** – net‑shape geometry unrealistic.

### ✅ **Correct design would include:**
1. Curved cheeks or undercuts to clear journals/pins.
2. Drilled oil passages from main journals to crank pins.
3. Counterweight masses optimized for balance.
4. Keyway on front snout, bolt holes on rear flange.
5. Draft angles (1‑3°) on all vertical surfaces.
6. Generous fillets (R5‑R10 mm) at stress‑critical transitions.
7. Chamfers (0.5×45°) on all sharp edges.
8. Machining allowances (2 mm oversize on journals).

## 7. Validation Procedure

### Step 1: Kinematic Check
- Verify journal/pin diameters fit within stroke radius (curved cheeks if needed).
- Check counterweight clearance with block/pan.

### Step 2: Functional Check
- Ensure oil passages connect main bearings to rod bearings.
- Verify keyway/bolt‑hole dimensions match standard components.

### Step 3: Manufacturing Check
- Apply draft angles to all vertical faces.
- Add fillets/chamfers to sharp edges.
- Include machining allowances.

### Step 4: Dynamic Check (FEA)
- Stress concentration at fillets under peak load.
- Torsional vibration natural frequency.
- Fatigue life estimation.

## 8. Our Specific Issues

### Critical Issue: Cheek Interference
- **Problem:** Journal Ø76.485 mm + pin Ø61.415 mm = 137.9 mm > 2× stroke radius (95 mm).
- **Solution:** Curved cheeks (circular arcs) that wrap around journals, or reduce journal/pin diameters.
- **Action:** Redesign cheek profile as circular sector with notch clearance.

### Missing Oil Passages:
- **Requirement:** Ø6‑8 mm drilled hole from main journal center to crank‑pin center.
- **Action:** Add cross‑drilled holes in CAD.

### Balance Weights:
- **Requirement:** Counterweight mass ≈ 0.55× reciprocating mass (piston+pin+rings+small‑end).
- **Action:** Shape cheeks as eccentric masses opposite crank pin.

### Draft Angles:
- **Requirement:** 1° taper on all vertical walls for forging.
- **Action:** Apply taper to cheek sides, journal ends.

## 9. Next Actions

### Immediate corrections:
1. **Redesign cheek geometry** – circular arcs with clearance notches.
2. **Add oil passages** – cross‑drilled holes.
3. **Increase pin fillet radius** to ≥3 mm (5% of pin diameter).
4. **Add chamfers** to all sharp edges.

### Medium‑term improvements:
5. **Add balance‑weight profiling** (eccentric mass).
6. **Add keyway & bolt holes** for flywheel/pulley.
7. **Apply draft angles** (1°) to all vertical surfaces.
8. **Include machining allowances** (2 mm oversize).

### Validation:
9. **Run FEA** on corrected geometry (stress at fillets).
10. **Check torsional stiffness** with actual length (V12 crankshaft).

---

## Summary

My current crankshaft (`crankshaft_30MPa_final.step`) has **geometric interference** (cheeks intersect journals) and **lacks essential functional features** for a real engine. It fails on:

- **❌ Geometric feasibility** – cheek interference due to large journal/pin diameters.
- **❌ Lubrication** – no oil passages.
- **❌ Balancing** – no counterweight design.
- **❌ Assembly** – no keyways, bolt holes.
- **❌ Manufacturing** – no draft angles, chamfers.

**Root cause:** Optimization focused on stress constraints but neglected geometric packaging and functional requirements.

**Self‑validation capability:** I can now identify these errors by checking against engineering principles. The next step is to correct the cheek interference, add oil passages, and incorporate missing features.

---

*Last updated: 2026‑02‑13*  
*References: SAE standards, engine design textbooks, crankshaft design guides.*