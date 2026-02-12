"""
Analytical connecting‑rod model for V12 twin‑charged engine.
Ti‑6Al‑4V titanium, optimized for buckling, fatigue, and bearing pressure.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict

@dataclass
class ConrodGeometry:
    """Parameters defining a connecting rod."""
    # I‑beam cross‑section (simplified)
    beam_height: float      # mm (height of I‑beam)
    beam_width: float       # mm (width of I‑beam flange)
    web_thickness: float    # mm (thickness of vertical web)
    flange_thickness: float # mm (thickness of top/bottom flange)
    # Lengths
    center_length: float    # mm (distance between bearing centers)
    big_end_width: float    # mm (width of big‑end bearing)
    small_end_width: float  # mm (width of small‑end bearing)
    # Bearing diameters (crank pin / piston pin)
    big_end_diameter: float   # mm (must match crankshaft pin diameter)
    small_end_diameter: float # mm (piston pin diameter)
    # Fillet radii
    fillet_big: float       # mm (transition at big end)
    fillet_small: float     # mm (transition at small end)
    # Material properties (Ti‑6Al‑4V titanium)
    density: float = 4.43e-3      # g/mm³ (4.43 g/cm³)
    youngs_modulus: float = 113.0e3  # MPa
    poisson: float = 0.34
    yield_strength: float = 880.0   # MPa (tensile yield)
    fatigue_limit: float = 450.0    # MPa (fully reversed, polished)

class ConrodAnalyzer:
    """Analyze connecting rod for buckling, stress, fatigue, bearing pressure."""
    
    def __init__(self, geometry: ConrodGeometry):
        self.geo = geometry
    
    def cross_section_area(self) -> float:
        """Cross‑sectional area of I‑beam (mm²)."""
        # Simplified: rectangular approximation
        # Area = 2 × flange_area + web_area
        flange_area = self.geo.beam_width * self.geo.flange_thickness
        web_height = self.geo.beam_height - 2 * self.geo.flange_thickness
        web_area = web_height * self.geo.web_thickness
        return 2 * flange_area + web_area
    
    def moment_of_inertia(self, axis: str = "x") -> float:
        """Area moment of inertia about bending axis (mm⁴).
        axis='x': bending in plane of motion (strongest)
        axis='y': buckling out‑of‑plane (weaker)
        """
        h = self.geo.beam_height
        b = self.geo.beam_width
        tw = self.geo.web_thickness
        tf = self.geo.flange_thickness
        
        if axis == "x":
            # I_x = (b·h³ - (b‑tw)·(h‑2tf)³)/12
            return (b * h**3 - (b - tw) * (h - 2*tf)**3) / 12
        else:
            # I_y = 2·tf·b³/12 + (h‑2tf)·tw³/12
            return (2 * tf * b**3 + (h - 2*tf) * tw**3) / 12
    
    def radius_of_gyration(self, axis: str = "y") -> float:
        """Radius of gyration for buckling (mm)."""
        I = self.moment_of_inertia(axis)
        A = self.cross_section_area()
        return np.sqrt(I / A)
    
    def slenderness_ratio(self, axis: str = "y") -> float:
        """Slenderness ratio (λ) = effective length / radius of gyration."""
        # Effective length factor K = 1.0 (both ends pinned)
        K = 1.0
        Le = K * self.geo.center_length
        r = self.radius_of_gyration(axis)
        return Le / r
    
    def buckling_stress(self, axis: str = "y") -> float:
        """Critical buckling stress (Euler‑Johnson) in MPa."""
        λ = self.slenderness_ratio(axis)
        E = self.geo.youngs_modulus
        Sy = self.geo.yield_strength
        # Transition slenderness
        λ_c = np.sqrt(2 * np.pi**2 * E / Sy)
        
        if λ >= λ_c:
            # Euler buckling (long column)
            return np.pi**2 * E / λ**2
        else:
            # Johnson parabolic (intermediate)
            return Sy * (1 - (Sy * λ**2) / (4 * np.pi**2 * E))
    
    def axial_stress(self, force_n: float) -> float:
        """Compressive/tensile stress due to axial force (MPa)."""
        return force_n / self.cross_section_area()
    
    def bending_stress(self, force_n: float, eccentricity_mm: float = 0.0) -> float:
        """Bending stress due to eccentric loading (MPa)."""
        if eccentricity_mm == 0.0:
            return 0.0
        M = force_n * eccentricity_mm
        c = self.geo.beam_height / 2
        I = self.moment_of_inertia("x")
        return M * c / I
    
    def bearing_pressure(self, force_n: float, end: str = "big") -> float:
        """Bearing pressure on crank/piston pin (MPa)."""
        if end == "big":
            area = self.geo.big_end_diameter * self.geo.big_end_width
        else:
            area = self.geo.small_end_diameter * self.geo.small_end_width
        return force_n / area
    
    def mass(self) -> float:
        """Estimated mass in kg."""
        # Volume = area × length + bearing ends (approximated as cylinders)
        main_volume = self.cross_section_area() * self.geo.center_length
        # Big‑end: cylindrical shell around crank pin
        big_end_volume = np.pi * self.geo.big_end_diameter * self.geo.big_end_width * self.geo.beam_width
        # Small‑end: similar
        small_end_volume = np.pi * self.geo.small_end_diameter * self.geo.small_end_width * self.geo.beam_width
        total_volume = main_volume + big_end_volume + small_end_volume
        return total_volume * self.geo.density / 1000  # kg
    
    def evaluate_constraints(self,
                             compression_force_n: float,
                             tensile_force_n: float,
                             eccentricity_mm: float = 0.5) -> Tuple[Dict, Dict]:
        """Evaluate all constraints for given load cases.
        Returns (constraints_dict, metrics_dict).
        """
        # Load cases
        sigma_axial_comp = self.axial_stress(compression_force_n)
        sigma_axial_tens = self.axial_stress(tensile_force_n)
        sigma_bending = self.bending_stress(compression_force_n, eccentricity_mm)
        sigma_total_comp = sigma_axial_comp + sigma_bending
        sigma_total_tens = sigma_axial_tens + sigma_bending
        
        # Buckling safety (out‑of‑plane is critical)
        sigma_crit = self.buckling_stress("y")
        buckling_sf = sigma_crit / sigma_axial_comp if sigma_axial_comp > 0 else 1e6
        
        # Bearing pressures
        p_big = self.bearing_pressure(compression_force_n, "big")
        p_small = self.bearing_pressure(compression_force_n, "small")
        
        # Fatigue (Goodman diagram)
        sigma_mean = (sigma_total_comp + sigma_total_tens) / 2
        sigma_amp = abs(sigma_total_comp - sigma_total_tens) / 2
        Se = self.geo.fatigue_limit
        Sy = self.geo.yield_strength
        goodman_sf = 1 / (sigma_amp / Se + sigma_mean / Sy) if sigma_amp > 0 else 1e6
        
        constraints = {
            "buckling_ok": buckling_sf >= 2.0,
            "compressive_stress_ok": sigma_total_comp < Sy * 0.5,  # safety factor 2
            "tensile_stress_ok": sigma_total_tens < Sy * 0.5,
            "bearing_pressure_ok": max(p_big, p_small) < 60.0,  # MPa (typical limit)
            "fatigue_ok": goodman_sf >= 2.0,
            "mass_ok": self.mass() < 1.0,  # kg (target for titanium rod)
        }
        
        metrics = {
            "mass_kg": self.mass(),
            "axial_stress_comp_mpa": sigma_axial_comp,
            "axial_stress_tens_mpa": sigma_axial_tens,
            "bending_stress_mpa": sigma_bending,
            "total_stress_comp_mpa": sigma_total_comp,
            "total_stress_tens_mpa": sigma_total_tens,
            "buckling_critical_stress_mpa": sigma_crit,
            "buckling_safety_factor": buckling_sf,
            "bearing_pressure_big_mpa": p_big,
            "bearing_pressure_small_mpa": p_small,
            "fatigue_safety_factor": goodman_sf,
            "slenderness_ratio": self.slenderness_ratio("y"),
        }
        
        return constraints, metrics

# Baseline geometry (matching crankshaft pin 86.5 mm, piston pin ~28 mm)
baseline = ConrodGeometry(
    beam_height=45.0,
    beam_width=35.0,
    web_thickness=8.0,
    flange_thickness=6.0,
    center_length=150.0,  # typical rod length for 95 mm stroke
    big_end_width=35.6,   # matches crankshaft pin width
    small_end_width=25.0,
    big_end_diameter=86.5,
    small_end_diameter=28.0,
    fillet_big=5.0,
    fillet_small=3.0,
)

if __name__ == "__main__":
    analyzer = ConrodAnalyzer(baseline)
    # Loads: overdrive compression 180 kN, tensile (inertia) 83 kN (11 kRPM)
    cons, metrics = analyzer.evaluate_constraints(
        compression_force_n=180000.0,
        tensile_force_n=83000.0,
        eccentricity_mm=0.5
    )
    print("Baseline connecting rod (Ti‑6Al‑4V):")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    print("Constraints satisfied:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    print(f"Mass: {metrics['mass_kg']:.3f} kg")