"""
Additive‑manufacturing‑aware piston model for V12 twin‑charged engine.
Uses forged steel with lattice‑infill for mass reduction.
Gibson‑Ashby scaling for effective properties.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict

@dataclass
class PistonGeometryAM:
    """Parameters defining an additive‑manufactured piston with lattice infill."""
    # Primary dimensions (solid outer shell)
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
    # Lattice relative density (0.2–1.0) for internal volume
    lattice_relative_density: float  # ρ_rel = ρ_eff / ρ_solid
    
    # Material properties (forged steel, e.g., 4340)
    density: float = 7.85e-3         # g/mm³ (7.85 g/cm³)
    youngs_modulus: float = 210.0e3  # MPa
    poisson: float = 0.29
    yield_strength: float = 800.0    # MPa (tensile yield)
    thermal_conductivity: float = 50.0  # W/(m·K)

class PistonAnalyzerAM:
    """Analyze AM piston with lattice‑infill scaling."""
    
    def __init__(self, geometry: PistonGeometryAM):
        self.geo = geometry
    
    def effective_properties(self) -> Dict[str, float]:
        """Compute effective material properties using Gibson‑Ashby scaling.
        Returns dict with keys: density_eff, modulus_eff, yield_strength_eff."""
        ρ = self.geo.lattice_relative_density
        # Scaling exponents for bending‑dominated lattice (same as conrod)
        return {
            "density_eff": self.geo.density * ρ,
            "modulus_eff": self.geo.youngs_modulus * ρ**2,
            "yield_strength_eff": self.geo.yield_strength * ρ**(1.5),
        }
    
    def crown_surface_area(self) -> float:
        """Crown surface area exposed to combustion (mm²)."""
        return np.pi * (self.geo.bore_diameter / 2)**2
    
    def crown_volume(self) -> float:
        """Volume of crown material (mm³)."""
        area = self.crown_surface_area()
        return area * self.geo.crown_thickness
    
    def pin_boss_volume(self) -> float:
        """Volume of pin boss region (simplified as two blocks)."""
        boss_height = self.geo.compression_height * 0.6
        boss_depth = self.geo.pin_boss_width
        boss_width = self.geo.pin_diameter + 2 * self.geo.pin_boss_width
        return 2 * boss_height * boss_depth * boss_width
    
    def skirt_volume(self) -> float:
        """Volume of skirt (simplified as cylindrical shell)."""
        outer_radius = self.geo.bore_diameter / 2 - 0.5  # clearance
        inner_radius = outer_radius - self.geo.skirt_thickness
        skirt_area = np.pi * (outer_radius**2 - inner_radius**2)
        return skirt_area * self.geo.skirt_length
    
    def total_solid_volume(self) -> float:
        """Total solid outer‑shell volume (mm³)."""
        return (self.crown_volume() + self.pin_boss_volume() +
                self.skirt_volume())
    
    def mass(self) -> float:
        """Piston mass (g) accounting for lattice infill."""
        eff = self.effective_properties()
        ρ_eff = eff["density_eff"]  # g/mm³
        return self.total_solid_volume() * ρ_eff
    
    def crown_bending_stress(self, peak_pressure_mpa: float) -> float:
        """Bending stress in crown due to gas pressure (MPa)."""
        p = peak_pressure_mpa
        r = self.geo.bore_diameter / 2
        t = self.geo.crown_thickness
        return (3 * p * r**2) / (4 * t**2)
    
    def pin_bearing_pressure(self, peak_force_n: float) -> float:
        """Bearing pressure on piston pin (MPa)."""
        area = 2 * self.geo.pin_diameter * self.geo.pin_boss_width
        return peak_force_n / area
    
    def evaluate_constraints(self,
                            peak_pressure_mpa: float,
                            peak_force_n: float,
                            tensile_force_n: float = None) -> Tuple[Dict[str, bool], Dict[str, float]]:
        """Evaluate design constraints with relaxed limits for steel."""
        if tensile_force_n is None:
            tensile_force_n = peak_force_n
        eff = self.effective_properties()
        Sy_eff = eff["yield_strength_eff"]
        
        metrics = {}
        metrics["mass_g"] = self.mass()
        metrics["crown_bending_mpa"] = self.crown_bending_stress(peak_pressure_mpa)
        metrics["pin_bearing_comp_mpa"] = self.pin_bearing_pressure(peak_force_n)
        metrics["pin_bearing_tens_mpa"] = self.pin_bearing_pressure(tensile_force_n)
        metrics["pin_bearing_max_mpa"] = max(metrics["pin_bearing_comp_mpa"], metrics["pin_bearing_tens_mpa"])
        
        # Constraints with relaxed thresholds for steel
        constraints = {
            "crown_stress_ok": metrics["crown_bending_mpa"] < Sy_eff * 0.8,  # 0.8×yield
            "pin_bearing_comp_ok": metrics["pin_bearing_comp_mpa"] < 100.0,  # increased limit for steel
            "pin_bearing_tens_ok": metrics["pin_bearing_tens_mpa"] < 100.0,
            "mass_ok": metrics["mass_g"] < 800.0,  # up to 800 g (steel heavier)
            "lattice_density_ok": 0.2 <= self.geo.lattice_relative_density <= 1.0,
        }
        
        # Add effective properties to metrics
        metrics["effective_yield_strength_mpa"] = Sy_eff
        metrics["effective_modulus_mpa"] = eff["modulus_eff"]
        metrics["lattice_relative_density"] = self.geo.lattice_relative_density
        
        return constraints, metrics

# Baseline geometry with lattice infill (forged steel)
baseline = PistonGeometryAM(
    bore_diameter=94.5,
    compression_height=38.0,
    pin_diameter=28.0,
    pin_boss_width=12.0,
    crown_thickness=8.0,
    ring_land_height=2.5,
    ring_groove_depth=3.0,
    skirt_length=45.0,
    skirt_thickness=3.5,
    lattice_relative_density=0.5,
)

if __name__ == "__main__":
    analyzer = PistonAnalyzerAM(baseline)
    cons, metrics = analyzer.evaluate_constraints(
        peak_pressure_mpa=25.0,
        peak_force_n=180000.0,
        tensile_force_n=83000.0
    )
    print("AM piston (forged steel with lattice infill):")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        else:
            print(f"  {k}: {v}")
    print("Constraints satisfied:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    print(f"Mass: {metrics['mass_g']:.1f} g")