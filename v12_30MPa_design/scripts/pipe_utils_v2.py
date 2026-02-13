#!/usr/bin/env python3
"""
Robust pipe/tube generation utilities - fixed version.
"""
import cadquery as cq
from cadquery import Vector
import numpy as np

def create_pipe_sweep(points, diameter, thickness=0):
    """
    Create a pipe using sweep along polyline Edge (method that works).
    
    Args:
        points: List of (x,y,z) tuples or Vector objects
        diameter: Outer diameter (mm)
        thickness: Wall thickness (mm). 0 = solid rod.
    
    Returns:
        CadQuery Workplane object or None if failed.
    """
    if len(points) < 2:
        return None
    
    # Convert to tuples
    point_tuples = []
    for p in points:
        if isinstance(p, Vector):
            point_tuples.append((p.x, p.y, p.z))
        else:
            point_tuples.append(p)
    
    print(f"  Creating pipe with {len(point_tuples)} points, diameter={diameter}mm")
    
    # Create path as Edge (not Wire) - this works
    try:
        path = cq.Workplane().polyline(point_tuples).val()
    except Exception as e:
        print(f"  Failed to create polyline: {e}")
        return None
    
    # Create profile (circle) at origin
    # Note: Profile should be at origin; sweep will position it along path
    if thickness > 0 and thickness < diameter/2:
        # Tube: two concentric circles
        profile = (cq.Workplane()
                   .circle(diameter/2)
                   .circle(diameter/2 - thickness))
    else:
        # Solid rod
        profile = cq.Workplane().circle(diameter/2)
    
    # Sweep profile along path
    try:
        pipe = profile.sweep(path, multisection=False, combine=False)
        return pipe
    except Exception as e:
        print(f"  Sweep failed: {e}")
        # Try alternative: simple extrude fallback for straight segments
        return create_pipe_segmented(points, diameter, thickness)

def create_pipe_segmented(points, diameter, thickness=0):
    """
    Fallback: create pipe as series of straight cylinders between points.
    Good for debugging or when sweep fails.
    """
    if len(points) < 2:
        return None
    
    pipe = None
    for i in range(len(points)-1):
        p1 = points[i]
        p2 = points[i+1]
        
        if isinstance(p1, Vector):
            start = (p1.x, p1.y, p1.z)
            end = (p2.x, p2.y, p2.z)
        else:
            start = p1
            end = p2
        
        # Create straight cylinder between points
        # Calculate vector and length
        dx, dy, dz = end[0]-start[0], end[1]-start[1], end[2]-start[2]
        length = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        if length < 1e-6:
            continue
        
        # Create cylinder along Z axis
        if thickness > 0 and thickness < diameter/2:
            # Tube
            outer = cq.Workplane("XY").circle(diameter/2).extrude(length)
            inner = cq.Workplane("XY").circle(diameter/2 - thickness).extrude(length)
            segment = outer.cut(inner)
        else:
            # Solid
            segment = cq.Workplane("XY").circle(diameter/2).extrude(length)
        
        # Rotate to align with direction (dx, dy, dz)
        # Default cylinder is along Z axis
        if abs(dz - length) > 1e-6:  # Not already aligned with Z
            # Normalize direction
            dir_norm = np.array([dx/length, dy/length, dz/length])
            z_axis = np.array([0, 0, 1])
            
            # Rotation axis: cross product
            rot_axis = np.cross(z_axis, dir_norm)
            rot_axis_norm = np.linalg.norm(rot_axis)
            
            if rot_axis_norm > 1e-6:
                rot_axis = rot_axis / rot_axis_norm
                # Rotation angle
                rot_angle = np.arccos(np.dot(z_axis, dir_norm)) * 180 / np.pi
                
                # Apply rotation
                segment = segment.rotate(
                    startVector=(0,0,0),
                    endVector=tuple(rot_axis),
                    angleDegrees=rot_angle
                )
        
        # Translate to correct position (center of cylinder)
        segment = segment.translate((
            (start[0] + end[0])/2,
            (start[1] + end[1])/2,
            (start[2] + end[2])/2
        ))
        
        # Combine
        if pipe is None:
            pipe = segment
        else:
            pipe = pipe.union(segment)
    
    return pipe

def test_all():
    """Test pipe creation methods."""
    print("Testing pipe creation...")
    
    # Test 1: Simple straight line
    points1 = [Vector(0,0,0), Vector(50,0,0)]
    pipe1 = create_pipe_sweep(points1, 10)
    print(f"  Test 1 (straight): {'Success' if pipe1 else 'Failed'}")
    
    # Test 2: Curved path
    points2 = [
        Vector(0,0,0),
        Vector(30,0,0),
        Vector(30,30,0),
        Vector(30,30,30)
    ]
    pipe2 = create_pipe_sweep(points2, 8, thickness=1)
    print(f"  Test 2 (curved): {'Success' if pipe2 else 'Failed'}")
    
    # Test 3: More complex path (like intake routing)
    points3 = [
        Vector(-500, -200, 100),
        Vector(-400, -222, 80),
        Vector(-350, -222, 60),
        Vector(-350, -372, 60),
        Vector(-350, -372, 150)
    ]
    pipe3 = create_pipe_sweep(points3, 80)
    print(f"  Test 3 (intake segment): {'Success' if pipe3 else 'Failed'}")
    
    # Export successful tests
    if pipe1:
        cq.exporters.export(pipe1, "test_pipe_straight.step", "STEP")
        print("  Exported test_pipe_straight.step")
    if pipe2:
        cq.exporters.export(pipe2, "test_pipe_curved.step", "STEP")
        print("  Exported test_pipe_curved.step")
    
    return pipe1, pipe2, pipe3

if __name__ == "__main__":
    test_all()