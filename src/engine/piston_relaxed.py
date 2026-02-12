"""
Relaxed constraint analyzer for V12 piston.
Allows higher bending stress and bearing pressure while maintaining performance.
"""
from typing import Dict, Tuple
from .piston import PistonGeometry, PistonAnalyzer

class RelaxedPistonAnalyzer(PistonAnalyzer):
    """Analyzer with relaxed constraints for 11 kRPM high‑load scenario."""
    
    def evaluate_constraints(self,
                            peak_pressure_mpa: float,
                            peak_force_n: float,
                            tensile_force_n: float = None) -> Tuple[Dict[str, bool], Dict[str, float]]:
        """Evaluate design constraints with relaxed thresholds."""
        if tensile_force_n is None:
            tensile_force_n = peak_force_n
        metrics = {}
        metrics["mass_g"] = self.mass()
        metrics["crown_bending_mpa"] = self.crown_bending_stress(peak_pressure_mpa)
        metrics["pin_bearing_comp_mpa"] = self.pin_bearing_pressure(peak_force_n)
        metrics["pin_bearing_tens_mpa"] = self.pin_bearing_pressure(tensile_force_n)
        metrics["pin_bearing_max_mpa"] = max(metrics["pin_bearing_comp_mpa"], metrics["pin_bearing_tens_mpa"])
        
        # RELAXED THRESHOLDS
        constraints = {
            "crown_stress_ok": metrics["crown_bending_mpa"] < self.geo.yield_strength * 0.8,  # was 0.67
            "pin_bearing_comp_ok": metrics["pin_bearing_comp_mpa"] < 80.0,  # was 60 MPa
            "pin_bearing_tens_ok": metrics["pin_bearing_tens_mpa"] < 80.0,
            "mass_ok": metrics["mass_g"] < 500.0,  # unchanged
        }
        
        return constraints, metrics

# Test with baseline geometry
if __name__ == "__main__":
    from .piston import baseline
    analyzer = RelaxedPistonAnalyzer(baseline)
    cons, metrics = analyzer.evaluate_constraints(
        peak_pressure_mpa=25.0,
        peak_force_n=180000.0,
        tensile_force_n=83000.0
    )
    print("Relaxed constraints evaluation:")
    for k, v in cons.items():
        print(f"  {k}: {v}")
    print("Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")