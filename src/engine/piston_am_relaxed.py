"""
Relaxed‑constraint additive‑manufacturing‑aware piston model for V12.
Mass limit increased to 1500 g, lattice density lower bound 0.6.
"""
from .piston_am import PistonGeometryAM, PistonAnalyzerAM
from typing import Dict, Tuple

class PistonAnalyzerAMRelaxed(PistonAnalyzerAM):
    """AM piston analyzer with relaxed mass constraint and higher lattice density."""
    
    def evaluate_constraints(self, peak_pressure_mpa: float, peak_force_n: float, tensile_force_n: float) -> Tuple[Dict[str, bool], Dict[str, float]]:
        """Evaluate constraints with relaxed mass (1500 g) and lattice density ≥0.6."""
        # Call parent to get metrics
        constraints, metrics = super().evaluate_constraints(peak_pressure_mpa, peak_force_n, tensile_force_n)
        # Override mass constraint
        constraints["mass_ok"] = metrics["mass_g"] < 1500.0  # relaxed from 800 g
        # Override lattice density lower bound
        constraints["lattice_density_ok"] = 0.6 <= self.geo.lattice_relative_density <= 1.0
        return constraints, metrics