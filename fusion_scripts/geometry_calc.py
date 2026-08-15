"""
Parametric Geometry & Coordinate Engine
Tesla Model X 2017 Frunk Modular Divider System

Computes 2D profile coordinates, dovetail joints, truss cutout triangles,
and diamond lattice mesh lines for Autodesk Fusion 360 parametric generation.
"""

from dataclasses import dataclass
import math
from typing import List, Tuple


@dataclass
class FrunkParameters:
    """Parametric dimensions and tolerances for Model X frunk modular dividers."""
    bay_spacing_mm: float = 304.8       # 12.0 inches center-to-center bay spacing
    frame_height_mm: float = 280.0      # 11.0 inches overall frame height
    truss_height_mm: float = 35.0       # Floor truss structure height
    truss_width_mm: float = 24.0        # Floor truss and rail profile width
    slot_width_mm: float = 6.4          # Guide slot width (5.0mm panel + 0.7mm clearance/side)
    slot_depth_mm: float = 8.0          # Guide slot depth
    panel_thickness_mm: float = 5.0     # Nominal divider panel thickness
    panel_width_mm: float = 298.0       # Panel width (sized to engage in vertical slots)
    panel_height_mm: float = 275.0      # Panel height (sized to clear floor truss)
    lattice_pitch_mm: float = 18.0      # 45-degree diamond mesh pitch
    lattice_strut_mm: float = 3.5       # Diamond lattice strut width
    tol_dovetail_mm: float = 0.25       # 3D printing slip clearance for 15-deg dovetail
    tol_tenon_mm: float = 0.20          # 3D printing slip clearance for vertical socket tenon
    pin_diameter_mm: float = 5.0        # Transverse locking pin nominal diameter
    dovetail_base_width_mm: float = 14.0 # Dovetail root width
    dovetail_depth_mm: float = 8.0      # Dovetail tab depth
    dovetail_angle_deg: float = 15.0    # Dovetail wedge half-angle (degrees)
    wall_clearance_mm: float = 12.7     # 0.50 in inward clearance from frunk tub wall
    track_width_mm: float = 30.0        # Base conformal perimeter track width
    track_height_mm: float = 18.0       # Base conformal perimeter track height
    floor_slice_z_mm: float = 10.0      # LiDAR slice elevation above lowest tub floor
    trail_base_width_mm: float = 14.0   # Captive T-rail base width
    trail_neck_width_mm: float = 8.0    # Captive T-rail neck width
    trail_height_mm: float = 5.0        # Captive T-rail guide height
    rigid_guide_width_mm: float = 18.0  # Rigid rectangular top guide width
    rigid_guide_height_mm: float = 8.0  # Rigid rectangular guide wall height
    rigid_wall_thickness_mm: float = 4.0 # Rigid vertical guide wall thickness
    tol_seam_dovetail_mm: float = 0.20  # 3D printing slip clearance for quadrant seams
    seam_dovetail_angle_deg: float = 15.0 # Quadrant interlocking dovetail taper angle
    max_bed_dimension_mm: float = 310.0 # Maximum print bed envelope (Creality K2 350x350)

    @property
    def bay_spacing_in(self) -> float:
        """Bay spacing in inches."""
        return self.bay_spacing_mm / 25.4

    @property
    def frame_height_in(self) -> float:
        """Frame height in inches."""
        return self.frame_height_mm / 25.4

    @property
    def wall_clearance_in(self) -> float:
        """Wall clearance in inches."""
        return self.wall_clearance_mm / 25.4

    @property
    def bay_spacing_cm(self) -> float:
        """Bay spacing in centimeters (Fusion 360 database unit)."""
        return self.bay_spacing_mm / 10.0

    @property
    def frame_height_cm(self) -> float:
        """Frame height in centimeters (Fusion 360 database unit)."""
        return self.frame_height_mm / 10.0

    @property
    def truss_height_cm(self) -> float:
        return self.truss_height_mm / 10.0

    @property
    def truss_width_cm(self) -> float:
        return self.truss_width_mm / 10.0

    @property
    def slot_width_cm(self) -> float:
        return self.slot_width_mm / 10.0

    @property
    def slot_depth_cm(self) -> float:
        return self.slot_depth_mm / 10.0

    @property
    def panel_thickness_cm(self) -> float:
        return self.panel_thickness_mm / 10.0

    @property
    def panel_width_cm(self) -> float:
        return self.panel_width_mm / 10.0

    @property
    def panel_height_cm(self) -> float:
        return self.panel_height_mm / 10.0

    @property
    def pin_diameter_cm(self) -> float:
        return self.pin_diameter_mm / 10.0

    @property
    def wall_clearance_cm(self) -> float:
        return self.wall_clearance_mm / 10.0

    @property
    def track_width_cm(self) -> float:
        return self.track_width_mm / 10.0

    @property
    def track_height_cm(self) -> float:
        return self.track_height_mm / 10.0

    @property
    def trail_base_width_cm(self) -> float:
        return self.trail_base_width_mm / 10.0

    @property
    def trail_neck_width_cm(self) -> float:
        return self.trail_neck_width_mm / 10.0

    @property
    def trail_height_cm(self) -> float:
        return self.trail_height_mm / 10.0

    @property
    def rigid_guide_width_cm(self) -> float:
        return self.rigid_guide_width_mm / 10.0

    @property
    def rigid_guide_height_cm(self) -> float:
        return self.rigid_guide_height_mm / 10.0

    @property
    def rigid_wall_thickness_cm(self) -> float:
        return self.rigid_wall_thickness_mm / 10.0


def calculate_dovetail_profile(
    male: bool,
    tol: float,
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0,
) -> List[Tuple[float, float]]:
    """
    Calculates 2D polygon vertices for 15-degree sliding dovetail joint.

    Parameters:
        male: True for male tab (undersized by tolerance), False for female pocket (nominal).
        tol: Slip clearance tolerance (mm).
        base_w: Dovetail root width at y=0 (mm).
        depth: Dovetail projection/depth along y (mm).
        angle_deg: Wedge flare angle in degrees.

    Returns:
        List of (x, y) coordinate tuples defining the closed 4-point trapezoid profile.
    """
    rad = math.radians(angle_deg)
    flare = depth * math.tan(rad)
    # Male tab is offset inward by tol on each side (-tol)
    # Female pocket is nominal (offset = 0.0)
    # Result: female_width - male_width = 2 * tol
    offset = -tol if male else 0.0

    w_root = (base_w + 2.0 * offset) / 2.0
    w_tip = (base_w + 2.0 * flare + 2.0 * offset) / 2.0

    return [
        (-w_root, 0.0),
        (-w_tip, depth),
        (w_tip, depth),
        (w_root, 0.0),
    ]


def calculate_truss_web_triangles(
    span_length: float,
    height: float,
    web_thickness: float,
    num_bays: int = 6,
) -> List[List[Tuple[float, float]]]:
    """
    Generates triangular cutout coordinates for floor truss weight-reduction webs.

    Parameters:
        span_length: Total span length along X (mm).
        height: Total truss height along Y (mm).
        web_thickness: Perimeter and strut web wall thickness (mm).
        num_bays: Number of alternating triangular bays (default 6).

    Returns:
        List of triangles, where each triangle is a list of 3 (x, y) vertex tuples.
    """
    bay_w = span_length / num_bays
    margin_y = web_thickness
    h_inner = height - 2.0 * margin_y
    triangles = []

    for i in range(num_bays):
        x_left = i * bay_w + web_thickness / 2.0
        x_right = (i + 1) * bay_w - web_thickness / 2.0
        x_mid = (x_left + x_right) / 2.0

        if i % 2 == 0:
            # Upright triangle: base on bottom margin, apex at top margin
            triangles.append([
                (x_left, margin_y),
                (x_right, margin_y),
                (x_mid, margin_y + h_inner),
            ])
        else:
            # Inverted triangle: base on top margin, apex at bottom margin
            triangles.append([
                (x_left, margin_y + h_inner),
                (x_right, margin_y + h_inner),
                (x_mid, margin_y),
            ])
    return triangles


def calculate_diamond_lattice_segments(
    width: float,
    height: float,
    pitch: float,
    strut_w: float = 3.5,
) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Computes 45-degree intersecting diamond lattice centerlines within a rectangular boundary.

    Parameters:
        width: Boundary rectangle width (mm).
        height: Boundary rectangle height (mm).
        pitch: Perpendicular pitch between adjacent parallel struts (mm).
        strut_w: Strut width (mm).

    Returns:
        List of ((x1, y1), (x2, y2)) tuples representing 45-degree line segments.
    """
    segments: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
    step = pitch * math.sqrt(2)

    # Generate +45 degree lines: y - x = c => y = x + c
    c_min = -width
    c_max = height
    c = c_min + step / 2.0
    while c < c_max:
        pts: List[Tuple[float, float]] = []
        # Intersection with x = 0 (left edge): y = c
        if 0.0 <= c <= height:
            pts.append((0.0, c))
        # Intersection with x = width (right edge): y = width + c
        if 0.0 <= width + c <= height:
            pts.append((width, width + c))
        # Intersection with y = 0 (bottom edge): x = -c
        if 0.0 <= -c <= width:
            pts.append((-c, 0.0))
        # Intersection with y = height (top edge): x = height - c
        if 0.0 <= height - c <= width:
            pts.append((height - c, height))

        unique_pts = sorted(list(set([(round(p[0], 6), round(p[1], 6)) for p in pts])))
        if len(unique_pts) == 2:
            segments.append((unique_pts[0], unique_pts[1]))
        c += step

    # Generate -45 degree lines: y + x = d => y = -x + d
    d_min = 0.0
    d_max = width + height
    d = d_min + step / 2.0
    while d < d_max:
        pts = []
        # Intersection with x = 0 (left edge): y = d
        if 0.0 <= d <= height:
            pts.append((0.0, d))
        # Intersection with x = width (right edge): y = d - width
        if 0.0 <= d - width <= height:
            pts.append((width, d - width))
        # Intersection with y = 0 (bottom edge): x = d
        if 0.0 <= d <= width:
            pts.append((d, 0.0))
        # Intersection with y = height (top edge): x = d - height
        if 0.0 <= d - height <= width:
            pts.append((d - height, height))

        unique_pts = sorted(list(set([(round(p[0], 6), round(p[1], 6)) for p in pts])))
        if len(unique_pts) == 2:
            segments.append((unique_pts[0], unique_pts[1]))
        d += step

    return segments
