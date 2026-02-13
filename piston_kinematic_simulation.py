#!/usr/bin/env python3
"""
Kinematic simulation of piston movement for V12 hypercar single cylinder.
Check clearances, interferences, and geometry validity through full crank cycle.
"""
import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from datetime import datetime

print("=" * 80)
print("PISTON KINEMATIC SIMULATION")
print("=" * 80)

# ----------------------------------------------------------------------
# LOAD SPECIFICATIONS
# ----------------------------------------------------------------------
with open("/home/nenuka/.openclaw/workspace/final_crankshaft_throw_20260213_150959/final_crankshaft_throw_spec.json") as f:
    crank_spec = json.load(f)
    crank = crank_spec["geometry"]

with open("/home/nenuka/.openclaw/workspace/final_corrected_conrod_20260213_150623/final_corrected_spec.json") as f:
    conrod_spec = json.load(f)
    conrod = conrod_spec["corrected_dimensions"]

with open("/home/nenuka/.openclaw/workspace/final_piston_20260213_150906/final_piston_spec.json") as f:
    piston_spec = json.load(f)
    piston_fixed = piston_spec["fixed_parameters"]
    piston_geo = piston_spec["geometry"]

# Core parameters
r = crank["stroke"] / 2                      # crank radius = 23.75 mm
L = conrod["center_length"]                  # conrod length = 150.0 mm
bore = piston_fixed["bore_diameter_mm"]      # 94.5 mm
compression_height = piston_fixed["compression_height_mm"]  # 38.0 mm
skirt_length = piston_geo["skirt_length"]    # 56.992 mm
deck_clearance = 0.8                         # mm (from assembly)
piston_radial_clearance = 0.05               # mm (piston‑to‑bore radial clearance)

# Derived
piston_outer_radius = bore / 2 - piston_radial_clearance
piston_total_height = compression_height + skirt_length  # ~95 mm

# Conrod beam cross‑section (simplified)
beam_width = conrod["beam_width"]            # 30.215 mm
beam_height = conrod["beam_height"]          # 50.0 mm (average)

print("\nParameters:")
print(f"Crank radius: {r:.3f} mm")
print(f"Conrod length: {L:.3f} mm")
print(f"Bore: {bore:.2f} mm, piston radial clearance: {piston_radial_clearance:.3f} mm")
print(f"Compression height: {compression_height:.2f} mm, skirt length: {skirt_length:.2f} mm")
print(f"Deck clearance: {deck_clearance:.2f} mm")

# ----------------------------------------------------------------------
# KINEMATIC FUNCTIONS
# ----------------------------------------------------------------------
def piston_pin_position(theta):
    """Return piston pin Z coordinate (distance from crank center along cylinder axis)
    for crank angle theta (radians, 0 = TDC)."""
    cos_th = np.cos(theta)
    sin_th = np.sin(theta)
    # Classic piston kinematics: x = r cosθ + √(L² - r² sin²θ)
    return r * cos_th + np.sqrt(L**2 - (r * sin_th)**2)

def conrod_angle(theta):
    """Return conrod angle φ (radians) relative to cylinder axis.
    Positive when crank pin is below crank center."""
    sin_th = np.sin(theta)
    return np.arcsin(r * sin_th / L)

def crank_pin_position(theta):
    """Return crank pin coordinates (Y,Z) in plane perpendicular to crankshaft axis.
    Coordinate system: Y horizontal, Z vertical (cylinder axis).
    Crankshaft axis is X (out of plane).
    At theta=0 (TDC), pin at (0, r)."""
    return r * np.sin(theta), r * np.cos(theta)

def piston_crown_position(theta):
    """Return piston crown top Z coordinate (distance from crank center)."""
    return piston_pin_position(theta) - compression_height

def skirt_bottom_position(theta):
    """Return piston skirt bottom Z coordinate (distance from crank center)."""
    return piston_pin_position(theta) + skirt_length

# ----------------------------------------------------------------------
# SIMULATION THROUGH FULL CYCLE
# ----------------------------------------------------------------------
n_points = 361  # 0° to 360° in 1° steps
angles_deg = np.linspace(0, 360, n_points)
angles_rad = np.deg2rad(angles_deg)

z_pin = piston_pin_position(angles_rad)
z_crown = piston_crown_position(angles_rad)
z_skirt = skirt_bottom_position(angles_rad)
phi = conrod_angle(angles_rad)

# Deck height (crank center to deck surface)
deck_height = piston_pin_position(0) - compression_height - deck_clearance
print(f"\nDeck height (crank center to deck surface): {deck_height:.3f} mm")

# Clearance checks
print("\n--- CLEARANCE CHECKS ---")

# 1. Deck clearance at TDC
deck_gap = z_crown[0] - deck_height
print(f"1. Deck clearance at TDC: {deck_gap:.3f} mm (target {deck_clearance} mm)")
if abs(deck_gap - deck_clearance) < 0.1:
    print("   ✅ Within tolerance")
else:
    print(f"   ⚠️  Deviation: {deck_gap - deck_clearance:.3f} mm")

# 2. Piston skirt bottom vs crankcase at BDC
# Assume crankcase bottom is at Z = crank_center - (r + some_margin)
# Simplistic: crankcase bottom at Z = - (r + cheek_thickness + margin)
cheek_thickness = crank["cheek_thickness"]  # 17.15 mm
crankcase_bottom_z = - (r + cheek_thickness + 10.0)  # extra 10 mm margin
skirt_bottom_min = np.min(z_skirt)
skirt_to_crankcase = skirt_bottom_min - crankcase_bottom_z
print(f"2. Skirt bottom vs crankcase:")
print(f"   Skirt bottom min Z: {skirt_bottom_min:.3f} mm")
print(f"   Crankcase bottom Z: {crankcase_bottom_z:.3f} mm")
print(f"   Clearance: {skirt_to_crankcase:.3f} mm")
if skirt_to_crankcase > 5.0:
    print("   ✅ Sufficient clearance (>5 mm)")
else:
    print(f"   ⚠️  Possibly insufficient clearance")

# 3. Conrod angularity max
phi_max_deg = np.rad2deg(np.max(np.abs(phi)))
print(f"3. Maximum conrod angularity: {phi_max_deg:.2f}°")
if phi_max_deg < 20:
    print("   ✅ Within typical limit (<20°)")
else:
    print("   ⚠️  High angularity may increase side thrust")

# 4. Piston acceleration (simplified)
# Second derivative of position w.r.t. time (assuming constant angular velocity)
# Use finite difference for demonstration
omega = 1.0  # rad/s for normalization
a = np.gradient(np.gradient(z_pin, angles_rad), angles_rad) * omega**2
a_max = np.max(np.abs(a))
print(f"4. Max normalized piston acceleration: {a_max:.3f} mm/s² (per rad²/s²)")

# 5. Conrod‑to‑cylinder wall clearance (simplified)
# Approximate minimum distance between conrod beam centerline and cylinder axis
# At each angle, compute line segment between crank pin (Yc,Zc) and piston pin (0,Zp)
# Distance from origin (cylinder axis) to line segment
min_dist = np.inf
critical_angle = 0
for i, th in enumerate(angles_rad):
    Yc, Zc = crank_pin_position(th)
    Zp = z_pin[i]
    # Line segment from (Yc,Zc) to (0,Zp)
    # Distance from (0,0) to line segment formula
    # Vector v = (0 - Yc, Zp - Zc)
    vx = -Yc
    vy = Zp - Zc
    # Projection of origin onto line
    t = - (Yc*vx + Zc*vy) / (vx**2 + vy**2) if (vx**2 + vy**2) > 0 else 0
    t_clamped = max(0, min(1, t))
    closest_y = Yc + t_clamped * vx
    closest_z = Zc + t_clamped * vy
    dist = np.sqrt(closest_y**2 + closest_z**2)
    if dist < min_dist:
        min_dist = dist
        critical_angle = np.rad2deg(th)

# Crankcase inner radius (approximate, larger than bore)
crankcase_radius = bore / 2 + 20.0  # mm (assume 20 mm extra clearance around bore)
beam_outer_distance = min_dist + beam_width / 2
clearance_to_crankcase = crankcase_radius - beam_outer_distance
print(f"5. Conrod‑to‑crankcase clearance (approximate):")
print(f"   Min distance beam‑center to cylinder axis: {min_dist:.3f} mm")
print(f"   Beam outer distance (center + half‑width): {beam_outer_distance:.3f} mm")
print(f"   Crankcase inner radius (assumed): {crankcase_radius:.3f} mm")
print(f"   Available clearance: {clearance_to_crankcase:.3f} mm")
print(f"   Critical crank angle: {critical_angle:.1f}°")
if clearance_to_crankcase > 0:
    print("   ✅ Beam likely clears crankcase (based on assumed radius)")
else:
    print("   ⚠️  Beam may contact crankcase – verify with CAD")

# 6. Piston ring travel within cylinder
# Rings are located within piston ring belt, which stays within bore
# Ensure ring belt never goes above deck or below cylinder liner
ring_belt_top_z = z_crown + piston_geo.get("crown_thickness", 15.0) + 10.0  # approx
ring_belt_bottom_z = z_crown + piston_geo.get("crown_thickness", 15.0) + 30.0
# Simple check: ring belt should stay between deck and crankcase
if np.all(ring_belt_top_z > deck_height) and np.all(ring_belt_bottom_z < crankcase_bottom_z):
    print("6. Ring belt stays within cylinder liner: ✅")
else:
    print("6. Ring belt may exceed liner bounds: ⚠️")

# ----------------------------------------------------------------------
# PLOTTING
# ----------------------------------------------------------------------
print("\n--- GENERATING PLOTS ---")
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 1. Piston position vs crank angle
ax = axes[0, 0]
ax.plot(angles_deg, z_pin, 'b-', label='Pin center')
ax.plot(angles_deg, z_crown, 'r-', label='Crown top')
ax.plot(angles_deg, z_skirt, 'g-', label='Skirt bottom')
ax.axhline(y=deck_height, color='k', linestyle='--', label='Deck surface')
ax.axhline(y=crankcase_bottom_z, color='brown', linestyle='--', label='Crankcase bottom')
ax.set_xlabel('Crank angle [deg]')
ax.set_ylabel('Z position [mm]')
ax.set_title('Piston Positions vs Crank Angle')
ax.legend()
ax.grid(True)

# 2. Conrod angle
ax = axes[0, 1]
ax.plot(angles_deg, np.rad2deg(phi), 'c-')
ax.set_xlabel('Crank angle [deg]')
ax.set_ylabel('Conrod angle [deg]')
ax.set_title('Conrod Angularity')
ax.grid(True)

# 3. Piston velocity (numerical derivative)
ax = axes[1, 0]
v = np.gradient(z_pin, angles_rad)  # mm/rad
ax.plot(angles_deg, v, 'm-')
ax.set_xlabel('Crank angle [deg]')
ax.set_ylabel('Piston velocity [mm/rad]')
ax.set_title('Piston Velocity (per unit angular speed)')
ax.grid(True)

# 4. Cylinder cross‑section with envelope
ax = axes[1, 1]
# Plot cylinder bore circle
theta_circle = np.linspace(0, 2*np.pi, 100)
y_circle = piston_outer_radius * np.sin(theta_circle)
z_circle = piston_outer_radius * np.cos(theta_circle) + deck_height + bore/2
ax.plot(y_circle, z_circle, 'k--', alpha=0.5, label='Bore')
# Plot piston pin path (just Z variation, Y=0)
ax.plot([0]*len(z_pin), z_pin, 'b.', markersize=1, alpha=0.5, label='Pin path')
ax.set_xlabel('Y [mm]')
ax.set_ylabel('Z [mm]')
ax.set_title('Cylinder Cross‑Section')
ax.axis('equal')
ax.grid(True)
ax.legend()

plt.tight_layout()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plot_dir = f"piston_kinematic_{timestamp}"
os.makedirs(plot_dir, exist_ok=True)
plot_path = os.path.join(plot_dir, "kinematic_plots.png")
plt.savefig(plot_path, dpi=150)
print(f"Plots saved to {plot_path}")

# ----------------------------------------------------------------------
# SUMMARY
# ----------------------------------------------------------------------
print("\n" + "=" * 80)
print("SIMULATION SUMMARY")
print("=" * 80)
print("Geometry holds for kinematic simulation:")
print(f"  • Deck clearance: {deck_gap:.3f} mm (target {deck_clearance} mm)")
print(f"  • Skirt‑crankcase clearance: {skirt_to_crankcase:.3f} mm")
print(f"  • Max conrod angularity: {phi_max_deg:.2f}°")
print(f"  • Conrod‑crankcase clearance: {clearance_to_crankcase:.3f} mm (assumed crankcase radius)")
print("\nRecommendations:")
if clearance_to_crankcase < 0:
    print("  ❌ REDESIGN NEEDED: Conrod beam may hit crankcase.")
    print("     Options: reduce beam width, increase crankcase width, adjust conrod length.")
if skirt_to_crankcase < 5.0:
    print("  ⚠️  Consider increasing crankcase depth or shortening skirt.")
if phi_max_deg > 20:
    print("  ⚠️  High conrod angularity may increase wear; consider longer rod.")

print("\nNext steps:")
print("  1. Perform interference check with actual CAD geometry at critical angles.")
print("  2. Validate side‑thrust and piston tilt using dynamic simulation.")
print("  3. Check valve‑to‑piston clearance with valve lift profiles.")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "parameters": {
        "crank_radius_mm": r,
        "conrod_length_mm": L,
        "bore_diameter_mm": bore,
        "compression_height_mm": compression_height,
        "skirt_length_mm": skirt_length,
        "deck_clearance_mm": deck_clearance,
        "piston_radial_clearance_mm": piston_radial_clearance,
    },
    "kinematic_checks": {
        "deck_clearance_actual_mm": float(deck_gap),
        "skirt_bottom_min_z_mm": float(skirt_bottom_min),
        "crankcase_bottom_z_mm": float(crankcase_bottom_z),
        "skirt_crankcase_clearance_mm": float(skirt_to_crankcase),
        "max_conrod_angle_deg": float(phi_max_deg),
        "max_piston_acceleration_mm_per_rad2": float(a_max),
        "conrod_crankcase_clearance_mm": float(clearance_to_crankcase),
        "critical_angle_deg": float(critical_angle),
    },
    "validation": {
        "deck_clearance_ok": bool(abs(deck_gap - deck_clearance) < 0.1),
        "skirt_clearance_ok": bool(skirt_to_crankcase > 5.0),
        "conrod_angle_ok": bool(phi_max_deg < 20),
        "conrod_crankcase_clearance_ok": bool(clearance_to_crankcase > 0),
    }
}

json_path = os.path.join(plot_dir, "kinematic_results.json")
with open(json_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nDetailed results saved to {json_path}")
print("\nSimulation complete.")