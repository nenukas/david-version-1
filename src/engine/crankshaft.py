"""
Analytical crankshaft model for V12 twin‑charged engine.
Generates geometry, calculates stress, weight, and constraints.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class CrankshaftGeometry:
    """Parameters defining a V12 crankshaft."""
    # Main journal (supports block)
    main_journal_diameter: float  # mm
    main_journal_width: float     # mm
    # Crank pin (connects conrod)
    pin_diameter: float           # mm
    pin_width: float              # mm
    # Stroke (radius from main to pin center)
    stroke: float                 # mm (half of engine stroke)
    # Cheek dimensions (counterweight)
    cheek_thickness: float        # mm
    cheek_radius: float           # mm (outer radius)
    cheek_hole_radius: float      # mm (lightening hole)
    # Fillet radii
    fillet_main: float            # mm
    fillet_pin: float             # mm
    # Cheek sector (fraction of full disk, e.g., 0.33 for 120°)
    cheek_sector_factor: float = 0.33
    # Material properties (300M forged steel)
    density: float = 7.85e-3      # g/mm³ (7.85 g/cm³)
    shear_modulus: float = 79.3e3 # MPa
    yield_shear: float = 1000.0   # MPa (shear yield ~0.577 × 1800 MPa tensile)
    fatigue_limit: float = 500.0  # MPa (fully reversed, high‑strength steel)

class CrankshaftAnalyzer:
    """Analyze crankshaft for stress, weight, vibration."""
    
    def __init__(self, geometry: CrankshaftGeometry):
        self.geo = geometry
        
    def mass(self) -> float:
        """Estimated mass in kg."""
        # Simplified: cylindrical journals + cheek disks
        vol_main = np.pi * (self.geo.main_journal_diameter/2)**2 * self.geo.main_journal_width * 7  # 7 mains for V12
        vol_pin = np.pi * (self.geo.pin_diameter/2)**2 * self.geo.pin_width * 6  # 6 pins (shared for each pair)
        # Cheek: annular disk (outer radius - inner hole) × thickness × 12 cheeks
        cheek_area = self.geo.cheek_sector_factor * np.pi * (self.geo.cheek_radius**2 - self.geo.cheek_hole_radius**2)
        vol_cheek = cheek_area * self.geo.cheek_thickness * 12
        total_vol = vol_main + vol_pin + vol_cheek  # mm³
        return total_vol * self.geo.density / 1000  # kg
    
    def shear_stress(self, torque_nm: float) -> float:
        """Maximum shear stress in main journal under pure torsion (MPa)."""
        # Assume torque distributed evenly across 7 mains
        torque_per_main = torque_nm * 1000 / 7  # N·mm
        r = self.geo.main_journal_diameter / 2
        j = np.pi * r**4 / 2  # polar moment of circular section
        tau = torque_per_main * r / j  # MPa
        return tau
    
    def bending_stress(self, force_n: float, location: str = "pin") -> float:
        """Bending stress at fillet due to conrod force."""
        # Simplified cantilever beam model
        if location == "pin":
            d = self.geo.pin_diameter
            fillet = self.geo.fillet_pin
        else:
            d = self.geo.main_journal_diameter
            fillet = self.geo.fillet_main
        # Stress concentration factor (approximate for shoulder fillet)
        # Guard against division by zero or negative values
        ratio = fillet / max(0.001, d/2)
        kt = 1 + 0.5 * np.sqrt(max(0.001, ratio))
        bending_moment = force_n * self.geo.stroke  # N·mm
        i = np.pi * d**4 / 64  # area moment of inertia
        sigma_nominal = bending_moment * (d/2) / i
        sigma_max = kt * sigma_nominal
        return sigma_max
    
    def torsional_stiffness(self) -> float:
        """Torsional stiffness in N·m/rad."""
        g = self.geo.shear_modulus
        l = self.geo.main_journal_width * 7  # total length of mains
        j = np.pi * (self.geo.main_journal_diameter/2)**4 / 2
        k = (g * j) / (l / 1000)  # convert mm to m
        return k
    
    def natural_frequency(self, inertia_kgm2: float = 0.1) -> float:
        """First torsional natural frequency (Hz)."""
        k = self.torsional_stiffness()
        fn = (1 / (2 * np.pi)) * np.sqrt(k / inertia_kgm2)
        return fn
    
    def evaluate_constraints(self, 
                             max_torque_nm: float, 
                             max_conrod_force_n: float,
                             redline_rpm: float) -> dict:
        """Evaluate all constraints for given load cases."""
        # Load cases
        tau = self.shear_stress(max_torque_nm)
        sigma_bend = self.bending_stress(max_conrod_force_n, "pin")
        freq = self.natural_frequency()
        
        constraints = {
            "shear_stress_ok": tau < self.geo.yield_shear * 0.5,  # safety factor 2
            "bending_stress_ok": sigma_bend < self.geo.fatigue_limit,
            "torsional_stiffness_ok": freq > redline_rpm / 60 * 1.5,  # >1.5× engine order
            "mass_ok": self.mass() < 50.0,  # arbitrary limit (kg)
        }
        metrics = {
            "shear_stress_mpa": tau,
            "bending_stress_mpa": sigma_bend,
            "torsional_stiffness_nm_per_rad": self.torsional_stiffness(),
            "natural_frequency_hz": freq,
            "mass_kg": self.mass(),
        }
        return constraints, metrics

# Example baseline geometry (300M steel) – realistic V12 dimensions
baseline = CrankshaftGeometry(
    main_journal_diameter=80.0,   # mm
    main_journal_width=30.0,
    pin_diameter=70.0,
    pin_width=30.0,
    stroke=47.5,                  # half of 95 mm stroke
    cheek_thickness=20.0,
    cheek_radius=90.0,
    cheek_hole_radius=60.0,
    fillet_main=5.0,
    fillet_pin=5.0,
    cheek_sector_factor=0.33,
)

if __name__ == "__main__":
    analyzer = CrankshaftAnalyzer(baseline)
    # Loads for 3000 WHP overdrive mode:
    # Peak torque ≈ 2800 Nm, conrod force ≈ 180 kN (250 bar peak cylinder pressure)
    cons, metrics = analyzer.evaluate_constraints(
        max_torque_nm=2800.0,
        max_conrod_force_n=180000.0,
        redline_rpm=11000.0
    )
    print("Baseline crankshaft (V12, 8.0 L, 3000 WHP):")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    print("Constraints:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    print(f"\nMass: {metrics['mass_kg']:.2f} kg")