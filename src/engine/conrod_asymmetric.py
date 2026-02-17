"""
Asymmetric connecting‑rod model with top/bottom flange thickness.
"""
import numpy as np
from dataclasses import dataclass

@dataclass
class AsymmetricConrodGeometry:
    """Parameters defining a connecting rod with asymmetric flanges."""
    # I‑beam cross‑section (asymmetric)
    beam_height: float      # mm (height of I‑beam)
    beam_width: float       # mm (width of I‑beam flange)
    web_thickness: float    # mm (thickness of vertical web)
    flange_thickness_top: float # mm (top flange thickness)
    flange_thickness_bottom: float # mm (bottom flange thickness)
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

class AsymmetricConrodAnalyzer:
    """Analyze asymmetric connecting rod."""
    
    def __init__(self, geometry: AsymmetricConrodGeometry):
        self.geo = geometry
        # Pre‑compute cross‑section properties
        self._area = None
        self._centroid_z = None
        self._Ix = None
        self._Iy = None
    
    def cross_section_area(self) -> float:
        """Cross‑sectional area of asymmetric I‑beam (mm²)."""
        if self._area is None:
            top = self.geo.beam_width * self.geo.flange_thickness_top
            bottom = self.geo.beam_width * self.geo.flange_thickness_bottom
            web_h = self.geo.beam_height - self.geo.flange_thickness_top - self.geo.flange_thickness_bottom
            web = web_h * self.geo.web_thickness
            self._area = top + bottom + web
        return self._area
    
    def centroid_z(self) -> float:
        """Distance from bottom flange bottom to centroid (mm)."""
        if self._centroid_z is None:
            # Bottom flange: rectangle, centroid at tf_bot/2 from bottom
            A_bot = self.geo.beam_width * self.geo.flange_thickness_bottom
            y_bot = self.geo.flange_thickness_bottom / 2.0
            # Web: rectangle, centroid at tf_bot + web_h/2
            web_h = self.geo.beam_height - self.geo.flange_thickness_top - self.geo.flange_thickness_bottom
            A_web = web_h * self.geo.web_thickness
            y_web = self.geo.flange_thickness_bottom + web_h / 2.0
            # Top flange: rectangle, centroid at tf_bot + web_h + tf_top/2
            A_top = self.geo.beam_width * self.geo.flange_thickness_top
            y_top = self.geo.flange_thickness_bottom + web_h + self.geo.flange_thickness_top / 2.0
            # Combined centroid
            total_A = A_bot + A_web + A_top
            self._centroid_z = (A_bot*y_bot + A_web*y_web + A_top*y_top) / total_A
        return self._centroid_z
    
    def moment_of_inertia(self, axis: str = "x") -> float:
        """Area moment of inertia about centroidal axis (mm⁴)."""
        if axis == "x":
            if self._Ix is None:
                self._compute_inertias()
            return self._Ix
        elif axis == "y":
            if self._Iy is None:
                self._compute_inertias()
            return self._Iy
        else:
            raise ValueError("axis must be 'x' or 'y'")
    
    def _compute_inertias(self):
        """Compute Ix and Iy about centroid."""
        b = self.geo.beam_width
        tw = self.geo.web_thickness
        tf_top = self.geo.flange_thickness_top
        tf_bot = self.geo.flange_thickness_bottom
        h = self.geo.beam_height
        web_h = h - tf_top - tf_bot
        
        # Centroid from bottom (already computed)
        yc = self.centroid_z()
        
        # Bottom flange
        A_bot = b * tf_bot
        Ix_bot = b * tf_bot**3 / 12.0
        dy_bot = yc - tf_bot/2.0
        Ix_bot += A_bot * dy_bot**2
        
        # Web
        A_web = tw * web_h
        Ix_web = tw * web_h**3 / 12.0
        dy_web = yc - (tf_bot + web_h/2.0)
        Ix_web += A_web * dy_web**2
        
        # Top flange
        A_top = b * tf_top
        Ix_top = b * tf_top**3 / 12.0
        dy_top = yc - (tf_bot + web_h + tf_top/2.0)
        Ix_top += A_top * dy_top**2
        
        self._Ix = Ix_bot + Ix_web + Ix_top
        
        # Iy (bending out‑of‑plane) – all rectangles share same centroid in Y direction (centered)
        Iy_bot = tf_bot * b**3 / 12.0
        Iy_web = web_h * tw**3 / 12.0
        Iy_top = tf_top * b**3 / 12.0
        self._Iy = Iy_bot + Iy_web + Iy_top
    
    def section_modulus_top(self) -> float:
        """Section modulus for extreme top fiber (mm³)."""
        y_top = self.geo.beam_height - self.centroid_z()
        return self.moment_of_inertia("x") / y_top
    
    def section_modulus_bottom(self) -> float:
        """Section modulus for extreme bottom fiber (mm³)."""
        y_bot = self.centroid_z()
        return self.moment_of_inertia("x") / y_bot
    
    def axial_stress(self, force_n: float) -> float:
        """Axial stress (MPa)."""
        return force_n / self.cross_section_area()
    
    def bending_stress_top(self, moment_nmm: float) -> float:
        """Bending stress at top fiber (MPa)."""
        return moment_nmm / self.section_modulus_top()
    
    def bending_stress_bottom(self, moment_nmm: float) -> float:
        """Bending stress at bottom fiber (MPa)."""
        return moment_nmm / self.section_modulus_bottom()
    
    def total_stress_top(self, force_n: float, moment_nmm: float) -> float:
        """Total stress at top fiber (axial + bending) (MPa)."""
        sigma_a = self.axial_stress(force_n)
        sigma_b = self.bending_stress_top(moment_nmm)
        return sigma_a + sigma_b  # compression positive? sign depends
    
    def total_stress_bottom(self, force_n: float, moment_nmm: float) -> float:
        """Total stress at bottom fiber (axial + bending) (MPa)."""
        sigma_a = self.axial_stress(force_n)
        sigma_b = self.bending_stress_bottom(moment_nmm)
        return sigma_a - sigma_b  # opposite sign
    
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
    
    # Dynamic loads helper
    @staticmethod
    def compute_dynamic_loads(bore_mm, stroke_mm, rod_length_mm, rpm, peak_pressure_mpa, piston_mass_kg):
        """Return max compression and tension forces (N) over crank cycle."""
        # Simplified: use gas + inertia formulas (as in dynamic_loads.py)
        # For now return static values
        # TODO implement
        comp = 210000.0
        tens = 97000.0
        return comp, tens