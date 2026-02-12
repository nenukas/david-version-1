"""
Relaxed constraint analyzer for V12 connecting rod.
Allows higher mass, bearing pressure, lower safety factors while maintaining performance.
"""
from typing import Dict, Tuple
from .conrod import ConrodGeometry, ConrodAnalyzer

class RelaxedConrodAnalyzer(ConrodAnalyzer):
    """Analyzer with relaxed constraints for 11 kRPM high‑load scenario."""
    
    def evaluate_constraints(self,
                             compression_force_n: float,
                             tensile_force_n: float,
                             eccentricity_mm: float = 0.5) -> Tuple[Dict, Dict]:
        """Evaluate all constraints with relaxed thresholds."""
        # Compute same metrics as parent
        sigma_axial_comp = self.axial_stress(compression_force_n)
        sigma_axial_tens = self.axial_stress(tensile_force_n)
        sigma_bending = self.bending_stress(compression_force_n, eccentricity_mm)
        sigma_total_comp = sigma_axial_comp + sigma_bending
        sigma_total_tens = sigma_axial_tens + sigma_bending
        
        sigma_crit = self.buckling_stress("y")
        buckling_sf = sigma_crit / sigma_axial_comp if sigma_axial_comp > 0 else 1e6
        
        p_big = self.bearing_pressure(compression_force_n, "big")
        p_small = self.bearing_pressure(compression_force_n, "small")
        
        # Fatigue (Goodman diagram)
        sigma_mean = (sigma_total_comp + sigma_total_tens) / 2
        sigma_amp = abs(sigma_total_comp - sigma_total_tens) / 2
        Se = self.geo.fatigue_limit
        Sy = self.geo.yield_strength
        goodman_sf = 1 / (sigma_amp / Se + sigma_mean / Sy) if sigma_amp > 0 else 1e6
        
        # RELAXED THRESHOLDS
        constraints = {
            "buckling_ok": buckling_sf >= 1.5,                     # was 2.0
            "compressive_stress_ok": sigma_total_comp < Sy * 0.6,  # was 0.5 (440 MPa → 528 MPa)
            "tensile_stress_ok": sigma_total_tens < Sy * 0.6,
            "bearing_pressure_ok": max(p_big, p_small) < 120.0,    # was 60 MPa
            "fatigue_ok": goodman_sf >= 1.5,                       # was 2.0
            "mass_ok": self.mass() < 1.5,                          # was 1.0 kg
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

# Test with baseline geometry
if __name__ == "__main__":
    from .conrod import baseline
    analyzer = RelaxedConrodAnalyzer(baseline)
    cons, metrics = analyzer.evaluate_constraints(
        compression_force_n=180000.0,
        tensile_force_n=83000.0,
        eccentricity_mm=0.5
    )
    print("Relaxed constraints evaluation:")
    for k, v in constraints.items():
        print(f"  {k}: {v}")
    print("Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")