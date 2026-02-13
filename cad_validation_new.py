#!/usr/bin/env python3
"""
CAD validation module for step‑by‑step construction.
Checks volume, bounding box, interference, connection, wall thickness.
"""
import cadquery as cq
import numpy as np
from typing import Tuple, List, Optional

# ----------------------------------------------------------------------
# VOLUME & BOUNDING BOX
# ----------------------------------------------------------------------
def check_volume(solid: cq.Workplane, expected_mm3: float, tolerance: float = 0.01) -> Tuple[bool, float]:
    """Check solid volume against expected value.
    Returns (ok, actual_volume_mm3)."""
    try:
        vol = solid.val().Volume()
        diff = abs(vol - expected_mm3) / expected_mm3
        ok = diff <= tolerance
        return ok, vol
    except Exception as e:
        print(f"Volume check failed: {e}")
        return False, 0.0

def check_bounding_box(solid: cq.Workplane, expected_dimensions: Tuple[float, float, float],
                       tolerance: float = 0.01) -> Tuple[bool, Tuple[float, float, float]]:
    """Check bounding box dimensions (dx, dy, dz).
    Returns (ok, (actual_dx, actual_dy, actual_dz))."""
    try:
        bbox = solid.val().BoundingBox()
        dx = bbox.xmax - bbox.xmin
        dy = bbox.ymax - bbox.ymin
        dz = bbox.zmax - bbox.zmin
        exp_dx, exp_dy, exp_dz = expected_dimensions
        ok = (abs(dx - exp_dx) <= tolerance and
              abs(dy - exp_dy) <= tolerance and
              abs(dz - exp_dz) <= tolerance)
        return ok, (dx, dy, dz)
    except Exception as e:
        print(f"Bounding‑box check failed: {e}")
        return False, (0.0, 0.0, 0.0)

# ----------------------------------------------------------------------
# INTERFERENCE & CONNECTION
# ----------------------------------------------------------------------
def check_interference(solid1: cq.Workplane, solid2: cq.Workplane,
                       tolerance_mm3: float = 0.001) -> Tuple[bool, float]:
    """Check if two solids interfere (intersect).
    Returns (interference_exists, intersection_volume_mm3).
    interference_exists = True if intersection volume > tolerance."""
    try:
        intersect = solid1.intersect(solid2)
        vol = intersect.val().Volume() if intersect.val() is not None else 0.0
        return vol > tolerance_mm3, vol
    except Exception as e:
        print(f"Interference check failed: {e}")
        return False, 0.0

def check_connection(solid1: cq.Workplane, solid2: cq.Workplane,
                     tolerance_mm: float = 0.001) -> Tuple[bool, float]:
    """Check if two solids are connected (touch within tolerance).
    Returns (connected, min_distance_mm).
    Computes distance between bounding boxes as approximation."""
    try:
        b1 = solid1.val().BoundingBox()
        b2 = solid2.val().BoundingBox()
        # Distance between boxes along each axis
        dx = max(b1.xmin - b2.xmax, b2.xmin - b1.xmax, 0)
        dy = max(b1.ymin - b2.ymax, b2.ymin - b1.ymax, 0)
        dz = max(b1.zmin - b2.zmax, b2.zmin - b1.zmax, 0)
        distance = np.sqrt(dx*dx + dy*dy + dz*dz)
        connected = distance <= tolerance_mm
        return connected, distance
    except Exception as e:
        print(f"Connection check failed: {e}")
        return False, float('inf')

# ----------------------------------------------------------------------
# WALL THICKNESS (approximate)
# ----------------------------------------------------------------------
def estimate_wall_thickness(solid: cq.Workplane, sample_points: int = 10) -> float:
    """Estimate minimum wall thickness by sampling bounding box.
    Very approximate – for manufacturability screening."""
    try:
        bbox = solid.val().BoundingBox()
        # Simple approach: assume solid is convex and wall thickness
        # is roughly min dimension / 4. For actual use, implement
        # ray‑casting or use dedicated library.
        dx = bbox.xmax - bbox.xmin
        dy = bbox.ymax - bbox.ymin
        dz = bbox.zmax - bbox.zmin
        return min(dx, dy, dz) * 0.25
    except Exception as e:
        print(f"Wall‑thickness estimate failed: {e}")
        return 0.0

def check_wall_thickness(solid: cq.Workplane, min_thickness_mm: float) -> bool:
    """Check if estimated wall thickness >= minimum."""
    thickness = estimate_wall_thickness(solid)
    return thickness >= min_thickness_mm

# ----------------------------------------------------------------------
# STEPWISE CONSTRUCTION LOGGER (UPDATED)
# ----------------------------------------------------------------------
class StepwiseBuilder:
    """Helper for step‑by‑step CAD with validation."""
    
    def __init__(self, name: str, output_dir: str = "."):
        self.name = name
        self.output_dir = output_dir
        self.solids = []  # list of (step_name, solid)
        self.log = []
    
    def _get_solid(self, step_name: str) -> cq.Workplane:
        """Retrieve solid by step name."""
        for name, solid in self.solids:
            if name == step_name:
                return solid
        raise ValueError(f"Step '{step_name}' not found")
    
    def add_step(self, step_name: str, solid: cq.Workplane,
                 expected_volume: Optional[float] = None,
                 expected_bbox: Optional[Tuple[float, float, float]] = None,
                 check_interference_with: Optional[List[str]] = None,
                 allow_interference_with: Optional[List[str]] = None,
                 check_connection_with: Optional[List[str]] = None,
                 allow_disconnection_with: Optional[List[str]] = None):
        """Add a construction step, validate, export STEP.
        
        Parameters:
        - check_interference_with: list of step names that must NOT interfere.
        - allow_interference_with: list of step names where interference is allowed (e.g., cuts).
        - check_connection_with: list of step names that must be connected.
        - allow_disconnection_with: list of step names where disconnection is allowed.
        """
        # Store
        self.solids.append((step_name, solid))
        
        # Validate volume
        if expected_volume is not None:
            ok, vol = check_volume(solid, expected_volume)
            self.log.append(f"{step_name}: volume {vol:.1f} mm³ ({'✅' if ok else '❌'})")
            if not ok:
                print(f"⚠️  Volume mismatch in {step_name}: expected {expected_volume:.1f}, got {vol:.1f}")
        
        # Validate bounding box
        if expected_bbox is not None:
            ok, dims = check_bounding_box(solid, expected_bbox)
            self.log.append(f"{step_name}: bbox {dims[0]:.1f}×{dims[1]:.1f}×{dims[2]:.1f} mm ({'✅' if ok else '❌'})")
        
        # Check interference with previous steps
        if check_interference_with:
            for other_name in check_interference_with:
                if allow_interference_with and other_name in allow_interference_with:
                    continue  # skip, interference allowed
                other_solid = self._get_solid(other_name)
                interferes, vol = check_interference(solid, other_solid)
                if interferes:
                    print(f"❌ Interference detected between {step_name} and {other_name}: {vol:.6f} mm³")
                else:
                    self.log.append(f"{step_name} – {other_name}: no interference ✅")
        
        # Check connection with previous steps
        if check_connection_with:
            for other_name in check_connection_with:
                if allow_disconnection_with and other_name in allow_disconnection_with:
                    continue  # skip, disconnection allowed
                other_solid = self._get_solid(other_name)
                connected, dist = check_connection(solid, other_solid)
                if connected:
                    self.log.append(f"{step_name} – {other_name}: connected ✅")
                else:
                    print(f"⚠️  {step_name} not connected to {other_name}: distance {dist:.3f} mm")
        
        # Export STEP
        import os
        step_path = os.path.join(self.output_dir, f"{step_name}.step")
        cq.exporters.export(solid, step_path, "STEP")
        self.log.append(f"{step_name}: exported to {step_path}")
        
        return solid
    
    def get_final(self) -> cq.Workplane:
        """Return union of all solids."""
        if not self.solids:
            return cq.Workplane()
        final = self.solids[0][1]
        for _, solid in self.solids[1:]:
            final = final.union(solid)
        return final
    
    def print_log(self):
        """Print validation log."""
        print("\n".join(self.log))

# ----------------------------------------------------------------------
# QUICK TEST
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example: two cubes that intersect
    cube1 = cq.Workplane("XY").box(10, 10, 10)
    cube2 = cq.Workplane("XY").box(10, 10, 10).translate((5, 0, 0))
    
    interferes, vol = check_interference(cube1, cube2)
    print(f"Cubes intersect: {interferes}, volume {vol:.3f} mm³")
    
    # Example: two separate cubes
    cube3 = cube2.translate((20, 0, 0))
    connected, dist = check_connection(cube1, cube3)
    print(f"Cubes connected: {connected}, distance {dist:.3f} mm")
    
    print("✅ CAD validation module ready.")