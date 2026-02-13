"""
Analytical model for V12 cylinder block (simplified).
Supports multiple material options: CGI‑450 cast iron, forged aluminum A356‑T6, billet aluminum 7075‑T6.
Geometry: cylinder bore spacing, deck thickness, cylinder wall thickness, main bearing bulkhead dimensions.
Loads: peak cylinder pressure, inertial forces, main bearing reactions.
"""
import math
from dataclasses import dataclass
from typing import Dict, Tuple, List

# Material database (yield strength MPa, density g/cm³, Young's modulus GPa)
MATERIALS = {
    "CGI_450": {
        "name": "Compacted Graphite Iron 450",
        "yield_strength": 450.0,      # MPa
        "density": 7.1,               # g/cm³
        "youngs_modulus": 165.0,      # GPa
        "poisson": 0.28,
        "fatigue_limit": 200.0,       # MPa (approx)
    },
    "A356_T6": {
        "name": "Forged Aluminum A356‑T6",
        "yield_strength": 230.0,
        "density": 2.7,
        "youngs_modulus": 71.0,
        "poisson": 0.33,
        "fatigue_limit": 90.0,
    },
    "7075_T6": {
        "name": "Billet Aluminum 7075‑T6",
        "yield_strength": 503.0,      # MPa (high)
        "density": 2.81,
        "youngs_modulus": 71.7,
        "poisson": 0.33,
        "fatigue_limit": 160.0,
    },
}

@dataclass
class CylinderBlockGeometry:
    """Simplified geometry parameters for a V12 block."""
    # Engine fixed parameters (no defaults)
    bore_diameter: float          # mm
    stroke: float                 # mm
    bank_angle: float             # degrees (V‑angle)
    # Design variables (no defaults)
    bore_spacing: float           # center‑to‑center distance between adjacent cylinders (mm)
    deck_thickness: float         # thickness of cylinder head deck (mm)
    cylinder_wall_thickness: float  # thickness of cylinder wall (mm)
    water_jacket_thickness: float # thickness of water jacket around cylinder (mm)
    main_bearing_width: float     # width of main bearing bulkhead (mm)
    main_bearing_height: float    # height of main bearing bulkhead (mm)
    skirt_depth: float            # depth of block skirt below crank centerline (mm)
    pan_rail_width: float         # width of oil‑pan rail (mm)
    # Fixed constants (defaults)
    cylinder_count: int = 12
    bank_count: int = 2
    
    # Derived dimensions
    @property
    def bore_radius(self) -> float:
        return self.bore_diameter / 2.0
    
    @property
    def cylinder_center_distance(self) -> float:
        """Distance between cylinder centers along bank (same as bore_spacing)."""
        return self.bore_spacing
    
    @property
    def bank_offset(self) -> float:
        """Offset between banks in transverse direction (simplified)."""
        # For V‑engine, banks are offset by some distance; approximate.
        return self.bore_spacing * math.sin(math.radians(self.bank_angle / 2.0))
    
    def validate(self) -> Tuple[bool, str]:
        """Check geometric feasibility."""
        # Outer diameter of water jacket cavity (hole in block)
        outer_diameter = self.bore_diameter + 2*self.cylinder_wall_thickness + 2*self.water_jacket_thickness
        clearance = 10.0  # mm
        
        if self.bore_spacing < outer_diameter + clearance:
            return False, f"Bore spacing {self.bore_spacing:.1f} mm too small for outer diameter {outer_diameter:.1f} mm"
        # Bank offset must be at least half outer diameter (cylinders in opposite banks are separated by 2*bank_offset)
        if self.bank_offset < outer_diameter/2 + clearance:
            return False, f"Bank offset {self.bank_offset:.1f} mm too small for outer diameter {outer_diameter:.1f} mm"
        # Ensure metal volume per cylinder is positive (cell volume > bore + jacket volumes)
        cell_height = self.deck_thickness + self.stroke/2.0 + self.skirt_depth
        cell_volume = self.bore_spacing * self.bank_offset * cell_height
        bore_volume = math.pi * (self.bore_radius ** 2) * cell_height
        jacket_outer_radius = self.bore_radius + self.cylinder_wall_thickness + self.water_jacket_thickness
        jacket_volume = math.pi * (jacket_outer_radius ** 2 - (self.bore_radius + self.cylinder_wall_thickness) ** 2) * cell_height
        if cell_volume <= bore_volume + jacket_volume:
            return False, f"Metal volume per cylinder non-positive (cell {cell_volume:.0f} <= bore+jacket {bore_volume+jacket_volume:.0f})"
        if self.deck_thickness < 5.0:
            return False, f"Deck thickness {self.deck_thickness:.1f} mm too thin"
        if self.cylinder_wall_thickness < 3.0:
            return False, f"Cylinder wall thickness {self.cylinder_wall_thickness:.1f} mm too thin"
        if self.water_jacket_thickness < 2.0:
            return False, f"Water jacket thickness {self.water_jacket_thickness:.1f} mm too thin"
        if self.main_bearing_width < 10.0:
            return False, f"Main bearing width {self.main_bearing_width:.1f} mm too narrow"
        if self.main_bearing_height < 15.0:
            return False, f"Main bearing height {self.main_bearing_height:.1f} mm too short"
        if self.skirt_depth < 10.0:
            return False, f"Skirt depth {self.skirt_depth:.1f} mm too shallow"
        if self.pan_rail_width < 5.0:
            return False, f"Pan rail width {self.pan_rail_width:.1f} mm too narrow"
        return True, "OK"

class CylinderBlockAnalyzer:
    """Perform stress, stiffness, and mass analysis of cylinder block."""
    def __init__(self, geometry: CylinderBlockGeometry, material_key: str = "CGI_450"):
        self.geo = geometry
        self.material = MATERIALS[material_key]
    
    def compute_mass(self) -> float:
        """Estimate block mass (grams) using simplified volume model."""
        ri = self.geo.bore_radius
        wall_outer_radius = ri + self.geo.cylinder_wall_thickness
        # Height of cylinder wall (deck to skirt bottom)
        wall_height = self.geo.deck_thickness + self.geo.stroke/2.0 + self.geo.skirt_depth
        # Volume of cylinder walls (12 cylinders)
        wall_volume = math.pi * (wall_outer_radius**2 - ri**2) * wall_height * self.geo.cylinder_count
        
        # Deck volume (simplified as rectangular plate covering both banks)
        deck_length = self.geo.bore_spacing * 6  # length of one bank
        deck_width = self.geo.bank_offset * 2    # width across both banks
        deck_volume = deck_length * deck_width * self.geo.deck_thickness
        
        # Main bearing bulkhead volume (7 bulkheads)
        bulkhead_volume = self.geo.main_bearing_width * self.geo.main_bearing_height * self.geo.bore_spacing * 7
        
        # Total material volume (ignore water jacket cavities, oil passages, etc.)
        total_volume = wall_volume + deck_volume + bulkhead_volume  # mm³
        # Convert to grams: mm³ → cm³ (divide by 1000), then multiply by density g/cm³
        mass_g = total_volume * 1e-3 * self.material["density"]
        return mass_g
    
    def compute_stresses(self, peak_pressure_mpa: float) -> Dict[str, float]:
        """Compute key stresses (MPa)."""
        # 1. Cylinder wall hoop stress (thick‑cylinder formula)
        ri = self.geo.bore_radius
        ro = ri + self.geo.cylinder_wall_thickness
        hoop_stress = peak_pressure_mpa * (ri**2 + ro**2) / (ro**2 - ri**2)
        
        # 2. Deck bending stress (simplified as clamped circular plate under uniform pressure)
        # Using formula for stress at center of clamped circular plate: σ = 0.75 * p * (r/t)^2
        deck_stress = 0.75 * peak_pressure_mpa * (ri / self.geo.deck_thickness) ** 2
        
        # 3. Main bearing bulkhead bearing pressure (force distributed over bearing area)
        # 1 MPa = 1 N/mm², area = π * ri² (mm²), force (N) = peak_pressure_mpa * area
        peak_force_n = peak_pressure_mpa * math.pi * ri**2  # N
        bearing_area = self.geo.main_bearing_width * self.geo.main_bearing_height  # mm²
        bearing_pressure = peak_force_n / bearing_area  # MPa (since 1 N/mm² = 1 MPa)
        
        # 4. Bulkhead bending stress (simplified cantilever)
        offset = self.geo.stroke / 2.0  # moment arm (mm)
        moment = peak_force_n * offset  # N·mm
        section_modulus = (self.geo.main_bearing_width * self.geo.main_bearing_height**2) / 6.0  # mm³
        bending_stress = moment / section_modulus  # MPa
        
        return {
            "hoop_stress_mpa": hoop_stress,
            "deck_stress_mpa": deck_stress,
            "bearing_pressure_mpa": bearing_pressure,
            "bulkhead_bending_stress_mpa": bending_stress,
        }
    
    def evaluate_constraints(self, peak_pressure_mpa: float = 25.0) -> Tuple[Dict[str, bool], Dict[str, float]]:
        """Evaluate design against constraints. Returns (constraint_satisfied, metrics)."""
        mass_g = self.compute_mass()
        stresses = self.compute_stresses(peak_pressure_mpa)
        
        # Constraint limits (relaxed per user request)
        yield_strength = self.material["yield_strength"]
        constraints = {
            "hoop_stress_ok": stresses["hoop_stress_mpa"] < 0.8 * yield_strength,
            "deck_stress_ok": stresses["deck_stress_mpa"] < 1.0 * yield_strength,
            "bearing_pressure_ok": stresses["bearing_pressure_mpa"] < 120.0,  # increased bearing pressure limit (MPa)
            "bulkhead_bending_ok": stresses["bulkhead_bending_stress_mpa"] < 0.8 * yield_strength,
            "mass_ok": mass_g < 200000.0,  # 200 kg limit (reasonable for V12 block)
            "geometric_ok": self.geo.validate()[0],
        }
        
        metrics = {
            "mass_g": mass_g,
            "mass_kg": mass_g / 1000.0,
            **stresses,
            "material": self.material["name"],
        }
        return constraints, metrics
    
    def print_report(self, peak_pressure_mpa: float = 25.0):
        """Print a human‑readable analysis report."""
        constraints, metrics = self.evaluate_constraints(peak_pressure_mpa)
        print("=== CYLINDER BLOCK ANALYSIS ===")
        print(f"Material: {self.material['name']}")
        print(f"Geometry:")
        print(f"  Bore spacing: {self.geo.bore_spacing:.1f} mm")
        print(f"  Deck thickness: {self.geo.deck_thickness:.1f} mm")
        print(f"  Cylinder wall thickness: {self.geo.cylinder_wall_thickness:.1f} mm")
        print(f"  Water jacket thickness: {self.geo.water_jacket_thickness:.1f} mm")
        print(f"  Main bearing: {self.geo.main_bearing_width:.1f} × {self.geo.main_bearing_height:.1f} mm")
        print(f"  Skirt depth: {self.geo.skirt_depth:.1f} mm")
        print(f"  Pan rail width: {self.geo.pan_rail_width:.1f} mm")
        print(f"Mass: {metrics['mass_kg']:.1f} kg")
        print(f"Stresses (MPa):")
        print(f"  Hoop (cylinder wall): {metrics['hoop_stress_mpa']:.1f}")
        print(f"  Deck bending: {metrics['deck_stress_mpa']:.1f}")
        print(f"  Bearing pressure: {metrics['bearing_pressure_mpa']:.1f}")
        print(f"  Bulkhead bending: {metrics['bulkhead_bending_stress_mpa']:.1f}")
        print(f"Constraints satisfied:")
        for k, v in constraints.items():
            print(f"  {k}: {v}")
        print("=" * 40)

# Example usage
if __name__ == "__main__":
    # Default geometry (approximate)
    geo = CylinderBlockGeometry(
        bore_diameter=94.5,
        stroke=94.5,
        bank_angle=60.0,
        bore_spacing=110.0,
        deck_thickness=12.0,
        cylinder_wall_thickness=5.0,
        water_jacket_thickness=4.0,
        main_bearing_width=30.0,
        main_bearing_height=50.0,
        skirt_depth=80.0,
        pan_rail_width=15.0,
    )
    
    for mat in ["CGI_450", "A356_T6", "7075_T6"]:
        analyzer = CylinderBlockAnalyzer(geo, mat)
        analyzer.print_report(peak_pressure_mpa=25.0)
        print()