"""
Analytical piston model for V12 twin‑charged engine.
Forged aluminum (2618‑T6), optimized for strength‑to‑weight and thermal fatigue.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict

@dataclass
class PistonGeometry:
    """Parameters defining a piston."""
    # Primary dimensions
    bore_diameter: float        # mm (cylinder bore)
    compression_height: float   # mm (pin center to crown)
    pin_diameter: float         # mm (piston pin)
    pin_boss_width: float       # mm (boss thickness)
    crown_thickness: float      # mm (crown thickness at center)
    # Ring pack
    ring_land_height: float     # mm (height of each ring land)
    ring_groove_depth: float    # mm (depth of ring groove)
    # Skirt
    skirt_length: float         # mm (length of skirt)
    skirt_thickness: float      # mm (wall thickness)
    # Material properties (2618‑T6 forged aluminum)
    density: float = 2.73e-3      # g/mm³
    youngs_modulus: float = 73.0e3  # MPa
    poisson: float = 0.33
    yield_strength: float = 310.0   # MPa at 150°C
    thermal_conductivity: float = 130.0  # W/(m·K)

class PistonAnalyzer:
    """Analyze piston for mechanical stress, thermal stress, and mass."""
    
    def __init__(self, geometry: PistonGeometry):
        self.geo = geometry
    
    def crown_surface_area(self) -> float:
        """Crown surface area exposed to combustion (mm²)."""
        # Approximate as flat circle (ignoring dome/dish)
        return np.pi * (self.geo.bore_diameter / 2)**2
    
    def crown_volume(self) -> float:
        """Volume of crown material (mm³)."""
        area = self.crown_surface_area()
        return area * self.geo.crown_thickness
    
    def pin_boss_volume(self) -> float:
        """Volume of pin boss region (simplified as two blocks)."""
        # Boss approximated as rectangular block around pin
        boss_height = self.geo.compression_height * 0.6  # guess
        boss_depth = self.geo.pin_boss_width
        boss_width = self.geo.pin_diameter + 2 * self.geo.pin_boss_width
        return 2 * boss_height * boss_depth * boss_width
    
    def skirt_volume(self) -> float:
        """Volume of skirt (simplified as cylindrical shell)."""
        outer_radius = self.geo.bore_diameter / 2 - 0.5  # clearance
        inner_radius = outer_radius - self.geo.skirt_thickness
        skirt_area = np.pi * (outer_radius**2 - inner_radius**2)
        return skirt_area * self.geo.skirt_length
    
    def total_volume(self) -> float:
        """Total piston volume (mm³)."""
        # Approximate sum of main components
        return (self.crown_volume() + self.pin_boss_volume() +
                self.skirt_volume())
    
    def mass(self) -> float:
        """Piston mass (g)."""
        return self.total_volume() * self.geo.density
    
    def crown_bending_stress(self, peak_pressure_mpa: float) -> float:
        """Bending stress in crown due to gas pressure (MPa)."""
        # Simplified: clamped circular plate with uniform pressure
        # σ_max = (3 * p * r²) / (4 * t²)  (for clamped edges)
        p = peak_pressure_mpa
        r = self.geo.bore_diameter / 2
        t = self.geo.crown_thickness
        return (3 * p * r**2) / (4 * t**2)
    
    def pin_bearing_pressure(self, peak_force_n: float) -> float:
        """Bearing pressure on piston pin (MPa)."""
        # Projected area = pin_diameter × pin_boss_width (for one boss, ×2 for two)
        area = 2 * self.geo.pin_diameter * self.geo.pin_boss_width
        return peak_force_n / area
    
    def evaluate_constraints(self, peak_pressure_mpa: float,
                            peak_force_n: float,
                            tensile_force_n: float = None) -> Tuple[Dict[str, bool], Dict[str, float]]:
        """Evaluate design constraints and return metrics."""
        if tensile_force_n is None:
            tensile_force_n = peak_force_n  # default to same as compression
        metrics = {}
        metrics["mass_g"] = self.mass()
        metrics["crown_bending_mpa"] = self.crown_bending_stress(peak_pressure_mpa)
        metrics["pin_bearing_comp_mpa"] = self.pin_bearing_pressure(peak_force_n)
        metrics["pin_bearing_tens_mpa"] = self.pin_bearing_pressure(tensile_force_n)
        metrics["pin_bearing_max_mpa"] = max(metrics["pin_bearing_comp_mpa"], metrics["pin_bearing_tens_mpa"])
        
        constraints = {}
        constraints["crown_stress_ok"] = metrics["crown_bending_mpa"] < self.geo.yield_strength * 0.67
        constraints["pin_bearing_comp_ok"] = metrics["pin_bearing_comp_mpa"] < 60.0  # typical limit for aluminum
        constraints["pin_bearing_tens_ok"] = metrics["pin_bearing_tens_mpa"] < 60.0
        constraints["mass_ok"] = metrics["mass_g"] < 500.0  # target <500g
        
        return constraints, metrics

# Baseline geometry for 8.0 L V12 (bore ≈ 94.5 mm, stroke 95 mm)
baseline = PistonGeometry(
    bore_diameter=94.5,
    compression_height=38.0,
    pin_diameter=28.0,
    pin_boss_width=12.0,
    crown_thickness=8.0,
    ring_land_height=2.5,
    ring_groove_depth=3.0,
    skirt_length=45.0,
    skirt_thickness=3.5,
)