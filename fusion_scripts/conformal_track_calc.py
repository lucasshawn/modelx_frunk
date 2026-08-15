"""
LiDAR-Matched Conformal Floor Track Geometry Engine
Tesla Model X 2017 Frunk Modular Cargo System

Extracts 2D floor contours from calibrated LiDAR STL scans, computes
exact 0.50 in (12.7 mm) inward perimeter offsets, constructs constant-width
continuous track profiles (captive T-rail and rigid anti-tip rectangular cross-sections),
and prepares quadrant segments for Autodesk Fusion 360 solid generation.
"""

from dataclasses import dataclass
import math
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np


@dataclass
class ConformalTrackParameters:
    """Parametric dimensions and clearances for conformal floor track system."""

    wall_clearance_mm: float = 12.7       # 0.50 in inward clearance from frunk tub wall
    track_width_mm: float = 30.0          # Base track width
    track_height_mm: float = 18.0         # Base track height
    floor_slice_z_mm: float = 10.0        # Scan slicing elevation above lowest tub floor
    trail_base_width_mm: float = 14.0     # Captive T-rail base width
    trail_neck_width_mm: float = 8.0      # Captive T-rail neck width
    trail_height_mm: float = 5.0          # Captive T-rail guide height
    rigid_guide_width_mm: float = 18.0    # Rigid rectangular top guide width
    rigid_guide_height_mm: float = 8.0    # Rigid rectangular guide wall height
    rigid_wall_thickness_mm: float = 4.0  # Rigid vertical guide wall thickness
    tol_seam_dovetail_mm: float = 0.20    # 3D printing slip clearance for quadrant seams
    seam_dovetail_angle_deg: float = 15.0 # Quadrant interlocking dovetail taper angle
    max_bed_dimension_mm: float = 310.0   # Maximum print bed envelope (Creality K2 350x350)
    resample_spacing_mm: float = 4.0      # Arc-length resampling pitch for smooth splines
    smooth_window_size: int = 5           # Moving average smoothing window size

    @property
    def wall_clearance_in(self) -> float:
        """Wall clearance in inches."""
        return self.wall_clearance_mm / 25.4

    @property
    def wall_clearance_cm(self) -> float:
        """Wall clearance in centimeters (Fusion 360 database unit)."""
        return self.wall_clearance_mm / 10.0

    @property
    def track_width_cm(self) -> float:
        """Track width in centimeters."""
        return self.track_width_mm / 10.0

    @property
    def track_height_cm(self) -> float:
        """Track height in centimeters."""
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


@dataclass
class SeamJoint:
    """Descriptor for an interlocking quadrant seam joint."""


    name: str  # e.g., "Front_Seam", "Left_Seam", "Rear_Seam", "Right_Seam"
    location: str  # "front", "left", "rear", "right"
    center: Tuple[float, float]  # (X, Y) seam center midpoint
    p_outer: Tuple[float, float]  # (X, Y) point on outer loop
    p_inner: Tuple[float, float]  # (X, Y) point on inner loop
    normal: Tuple[float, float]  # (nx, ny) unit normal vector pointing along CCW track forward
    seam_vector: Tuple[float, float]  # (ux, uy) unit vector from p_outer to p_inner
    width_mm: float  # Seam width across track (nominal 30.0 mm)
    male_quadrant: str  # Name of quadrant with male tab
    female_quadrant: str  # Name of quadrant with female pocket


@dataclass
class QuadrantGeometry:
    """Geometry descriptor for a single printable track quadrant."""

    name: str  # "TRK_Front_L", "TRK_Front_R", "TRK_Rear_L", "TRK_Rear_R"
    polygon: List[Tuple[float, float]]  # Closed 2D boundary polygon including dovetail seam tabs/pockets
    nominal_polygon: List[Tuple[float, float]]  # Closed 2D boundary polygon with flat nominal seam cuts
    outer_points: List[Tuple[float, float]]  # Outer boundary arc points
    inner_points: List[Tuple[float, float]]  # Inner boundary arc points
    start_seam: str  # Name of start seam (e.g. "Front_Seam")
    start_joint_type: str  # "male" or "female"
    end_seam: str  # Name of end seam (e.g. "Left_Seam")
    end_joint_type: str  # "male" or "female"
    bounds: Dict[str, float]  # {"min_x": ..., "max_x": ..., "min_y": ..., "max_y": ...}
    width: float  # AABB width
    height: float  # AABB height
    max_dimension: float  # Min oriented bounding box max dimension (< 310 mm)
    area_mm2: float  # Planar area of closed polygon
    perimeter_mm: float  # Perimeter of closed polygon



# ---------------------------------------------------------------------------
# Core 2D Polygon Geometric Utilities
# ---------------------------------------------------------------------------

def calculate_polygon_signed_area(polygon: Sequence[Tuple[float, float]]) -> float:
    """
    Computes signed area of a 2D closed polygon using Shoelace formula.
    Positive indicates counter-clockwise (CCW) winding, negative indicates clockwise (CW).
    """
    pts = np.asarray(polygon, dtype=float)
    if len(pts) < 3:
        return 0.0
    x = pts[:, 0]
    y = pts[:, 1]
    return float(0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def calculate_polygon_area(polygon: Sequence[Tuple[float, float]]) -> float:
    """Computes absolute 2D planar area of a closed polygon."""
    return abs(calculate_polygon_signed_area(polygon))


def calculate_polygon_perimeter(polygon: Sequence[Tuple[float, float]]) -> float:
    """Computes total perimeter path length of a closed polygon."""
    pts = np.asarray(polygon, dtype=float)
    if len(pts) < 2:
        return 0.0
    diffs = np.roll(pts, -1, axis=0) - pts
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


def ensure_ccw(polygon: Sequence[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Ensures polygon vertices are in counter-clockwise (CCW) winding order."""
    pts = list(polygon)
    if len(pts) >= 2 and math.isclose(pts[0][0], pts[-1][0], abs_tol=1e-6) and math.isclose(pts[0][1], pts[-1][1], abs_tol=1e-6):
        pts = pts[:-1]
    if calculate_polygon_signed_area(pts) < 0:
        pts = pts[::-1]
    return [(float(p[0]), float(p[1])) for p in pts]


def resample_polygon_2d(
    pts: Sequence[Tuple[float, float]],
    target_spacing: float = 4.0,
) -> List[Tuple[float, float]]:
    """
    Resamples a 2D closed polygon along its arc length to achieve uniform vertex pitch.
    """
    arr = np.asarray(pts, dtype=float)
    if len(arr) < 3:
        return [(float(p[0]), float(p[1])) for p in arr]

    diffs = np.roll(arr, -1, axis=0) - arr
    segment_lens = np.linalg.norm(diffs, axis=1)
    cum_dist = np.concatenate([[0.0], np.cumsum(segment_lens)])
    total_len = cum_dist[-1]

    if total_len < 1e-6:
        return [(float(p[0]), float(p[1])) for p in arr]

    num_samples = max(20, int(round(total_len / max(target_spacing, 0.1))))
    sample_dists = np.linspace(0.0, total_len, num_samples, endpoint=False)

    loop = np.vstack([arr, arr[0:1]])
    new_x = np.interp(sample_dists, cum_dist, loop[:, 0])
    new_y = np.interp(sample_dists, cum_dist, loop[:, 1])

    return [(float(x), float(y)) for x, y in zip(new_x, new_y)]


def smooth_polygon_2d(
    pts: Sequence[Tuple[float, float]],
    window_size: int = 5,
) -> List[Tuple[float, float]]:
    """
    Applies circular moving-average filter to smooth tessellated LiDAR scan polylines.
    """
    arr = np.asarray(pts, dtype=float)
    n = len(arr)
    if n < window_size or window_size <= 1:
        return [(float(p[0]), float(p[1])) for p in arr]

    if window_size % 2 == 0:
        window_size += 1

    pad = window_size // 2
    padded = np.vstack([arr[-pad:], arr, arr[:pad]])
    kernel = np.ones(window_size) / window_size

    smooth_x = np.convolve(padded[:, 0], kernel, mode="valid")
    smooth_y = np.convolve(padded[:, 1], kernel, mode="valid")

    return [(float(x), float(y)) for x, y in zip(smooth_x, smooth_y)]


# ---------------------------------------------------------------------------
# Mathematical 2D Polygon Inward / Outward Offset
# ---------------------------------------------------------------------------

def offset_polygon_2d(
    polygon: Sequence[Tuple[float, float]],
    offset_distance_mm: float,
    inward: bool = True,
    max_miter: float = 2.0,
) -> List[Tuple[float, float]]:
    """
    Computes an exact normal-vector offset of a 2D closed polygon.

    Parameters:
        polygon: Closed loop of (X, Y) coordinates.
        offset_distance_mm: Perpendicular offset distance in millimeters.
        inward: True for inward offset (inset), False for outward offset.
        max_miter: Maximum miter extension factor to prevent spikes at acute corners.

    Returns:
        List of offset (X, Y) coordinate tuples.
    """
    ccw_pts = np.asarray(ensure_ccw(polygon), dtype=float)
    n = len(ccw_pts)
    if n < 3:
        return [(float(p[0]), float(p[1])) for p in ccw_pts]

    # Inward offset in CCW polygon is along left normal: (-dy, dx)
    d = -abs(offset_distance_mm) if not inward else abs(offset_distance_mm)

    tangents = np.roll(ccw_pts, -1, axis=0) - ccw_pts
    t_lens = np.linalg.norm(tangents, axis=1, keepdims=True)
    t_unit = tangents / np.maximum(t_lens, 1e-9)

    # Inward edge normal is 90 deg CCW rotation of edge tangent
    edge_normals = np.column_stack([-t_unit[:, 1], t_unit[:, 0]])

    # Vertex normal = normalized sum of adjacent edge normals (angle bisector)
    prev_normals = np.roll(edge_normals, 1, axis=0)
    v_normals = prev_normals + edge_normals
    v_lens = np.linalg.norm(v_normals, axis=1, keepdims=True)
    v_unit = v_normals / np.maximum(v_lens, 1e-9)

    # Miter length factor: 1.0 / cos(theta / 2) = 1.0 / dot(prev_normals, v_unit)
    cos_half = np.sum(prev_normals * v_unit, axis=1)
    miter_factor = np.clip(1.0 / np.maximum(cos_half, 0.05), 0.5, max_miter)

    offset_arr = ccw_pts + d * (v_unit * miter_factor[:, None])
    return [(float(x), float(y)) for x, y in offset_arr]


# ---------------------------------------------------------------------------
# LiDAR Scan Planar Section Extraction
# ---------------------------------------------------------------------------

def extract_calibrated_floor_polygon(
    stl_path: str = "docs/scans/frunk_scan_calibrated.stl",
    z_height: float = 10.0,
    target_spacing: float = 4.0,
    smooth_window: int = 5,
) -> List[Tuple[float, float]]:
    """
    Extracts the 2D planar floor perimeter cross-section from the calibrated LiDAR scan STL.

    Parameters:
        stl_path: Path to the calibrated STL file.
        z_height: Height in millimeters above tub floor at which to slice the mesh.
        target_spacing: Arc-length resampling pitch (mm).
        smooth_window: Moving average filter window size.

    Returns:
        List of continuous (X, Y) coordinates representing the closed floor boundary loop.
    """
    if not os.path.isabs(stl_path):
        # Resolve relative to repo root if possible
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate = os.path.join(repo_root, stl_path)
        if os.path.exists(candidate):
            stl_path = candidate

    if not os.path.exists(stl_path):
        raise FileNotFoundError(f"LiDAR scan file not found: {stl_path}")

    import trimesh

    mesh = trimesh.load(stl_path)
    section = mesh.section(plane_origin=[0.0, 0.0, float(z_height)], plane_normal=[0.0, 0.0, 1.0])

    if section is None or len(section.entities) == 0:
        raise ValueError(f"No cross-section entities found in scan at Z = {z_height} mm")

    # Find the entity that represents the main frunk tub perimeter.
    # We select the entity with the largest closed bounding area or longest perimeter.
    best_pts: Optional[np.ndarray] = None
    best_metric = -1.0

    for entity in section.entities:
        disc = entity.discrete(section.vertices)
        if len(disc) < 10:
            continue
        # Check if points reside within the frunk tub lateral/longitudinal region
        pts_xy = disc[:, :2]
        if np.all(np.abs(pts_xy[:, 0]) < 650) and np.all(np.abs(pts_xy[:, 1]) < 550):
            # Calculate perimeter or area metric
            diffs = np.diff(pts_xy, axis=0)
            length = float(np.sum(np.linalg.norm(diffs, axis=1)))
            if length > best_metric:
                best_metric = length
                best_pts = pts_xy

    if best_pts is None:
        # Fallback to the entity with the most vertices
        entity_sizes = [len(e.discrete(section.vertices)) for e in section.entities]
        max_idx = int(np.argmax(entity_sizes))
        best_pts = section.entities[max_idx].discrete(section.vertices)[:, :2]

    # Convert to CCW loop
    raw_loop = ensure_ccw([(float(p[0]), float(p[1])) for p in best_pts])

    # Resample and smooth
    resampled = resample_polygon_2d(raw_loop, target_spacing=target_spacing)
    smoothed = smooth_polygon_2d(resampled, window_size=smooth_window)

    return ensure_ccw(smoothed)


# ---------------------------------------------------------------------------
# Track Boundary Loops Generation
# ---------------------------------------------------------------------------

def generate_track_boundary_loops(
    floor_polygon: Sequence[Tuple[float, float]],
    wall_clearance_mm: float = 12.7,
    track_width_mm: float = 30.0,
) -> Dict[str, List[Tuple[float, float]]]:
    """
    Generates outer boundary, inner boundary, and centerline closed polygon loops for the track.

    Parameters:
        floor_polygon: Floor tub perimeter polygon from LiDAR scan.
        wall_clearance_mm: Inward offset from floor tub to track outer edge (default 12.7mm = 0.50 in).
        track_width_mm: Width of track profile (default 30.0mm).

    Returns:
        Dictionary with keys:
            - 'outer_loop': Outer perimeter of track body.
            - 'inner_loop': Inner perimeter of track body.
            - 'centerline': Centerline path along track ring.
    """
    base_poly = ensure_ccw(floor_polygon)

    outer_loop = offset_polygon_2d(base_poly, offset_distance_mm=wall_clearance_mm, inward=True)
    centerline = offset_polygon_2d(
        base_poly, offset_distance_mm=wall_clearance_mm + track_width_mm / 2.0, inward=True
    )
    inner_loop = offset_polygon_2d(
        base_poly, offset_distance_mm=wall_clearance_mm + track_width_mm, inward=True
    )

    return {
        "outer_loop": outer_loop,
        "centerline": centerline,
        "inner_loop": inner_loop,
    }


# ---------------------------------------------------------------------------
# Track Cross-Section Profiles
# ---------------------------------------------------------------------------

def calculate_captive_trail_profile(
    base_width: float = 14.0,
    neck_width: float = 8.0,
    height: float = 5.0,
    lip_height: float = 2.0,
) -> List[Tuple[float, float]]:
    """
    Calculates 2D profile coordinates for top captive T-rail / dovetail guide.

    Parameters:
        base_width: Full base width of the T-rail (mm).
        neck_width: Narrow neck width (mm).
        height: Total T-rail height (mm).
        lip_height: Thickness of the top captive flanges (mm).

    Returns:
        List of 2D coordinates (X, Y) relative to rail centerline bottom at (0, 0).
    """
    w_base_half = base_width / 2.0
    w_neck_half = neck_width / 2.0
    y_neck = height - lip_height

    return [
        (-w_neck_half, 0.0),
        (-w_neck_half, y_neck),
        (-w_base_half, y_neck),
        (-w_base_half, height),
        (w_base_half, height),
        (w_base_half, y_neck),
        (w_neck_half, y_neck),
        (w_neck_half, 0.0),
    ]


def calculate_rigid_rectangular_profile(
    track_width: float = 30.0,
    track_height: float = 18.0,
    guide_width: float = 18.0,
    guide_height: float = 8.0,
    wall_thickness: float = 4.0,
) -> List[Tuple[float, float]]:
    """
    Calculates 2D profile coordinates for rigid rectangular track with vertical anti-tip guide walls.
    Provides wide moment support against post tilting under lateral loads.

    Parameters:
        track_width: Total base track width (mm, default 30.0).
        track_height: Total track height (mm, default 18.0).
        guide_width: Inner guide channel width (mm, default 18.0).
        guide_height: Height of vertical guide channel walls (mm, default 8.0).
        wall_thickness: Thickness of outer retaining guide walls (mm, default 4.0).

    Returns:
        List of 2D profile coordinates (X, Y) centered at X=0 with bottom at Y=0.
    """
    w_half = track_width / 2.0
    inner_w_half = guide_width / 2.0
    base_floor_y = track_height - guide_height

    return [
        (-w_half, 0.0),
        (-w_half, track_height),
        (-w_half + wall_thickness, track_height),
        (-inner_w_half, base_floor_y),
        (inner_w_half, base_floor_y),
        (w_half - wall_thickness, track_height),
        (w_half, track_height),
        (w_half, 0.0),
    ]


def calculate_track_cross_section_profile(
    profile_type: str = "rigid_rectangular",
    params: Optional[ConformalTrackParameters] = None,
) -> List[Tuple[float, float]]:
    """
    Profile calculation dispatcher for track cross-section geometry.

    Parameters:
        profile_type: Either 'rigid_rectangular' or 'captive_trail'.
        params: Optional ConformalTrackParameters instance.

    Returns:
        List of 2D coordinate tuples.
    """
    if params is None:
        params = ConformalTrackParameters()

    if profile_type == "rigid_rectangular":
        return calculate_rigid_rectangular_profile(
            track_width=params.track_width_mm,
            track_height=params.track_height_mm,
            guide_width=params.rigid_guide_width_mm,
            guide_height=params.rigid_guide_height_mm,
            wall_thickness=params.rigid_wall_thickness_mm,
        )
    elif profile_type == "captive_trail":
        return calculate_captive_trail_profile(
            base_width=params.trail_base_width_mm,
            neck_width=params.trail_neck_width_mm,
            height=params.trail_height_mm,
        )
    else:
        raise ValueError(
            f"Unknown track profile_type '{profile_type}'. Expected 'rigid_rectangular' or 'captive_trail'."
        )


# ---------------------------------------------------------------------------
# Interlocking Seam Dovetail Joint Engine
# ---------------------------------------------------------------------------

def calculate_seam_dovetail_profile(
    male: bool,
    tol: float = 0.20,
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0,
) -> List[Tuple[float, float]]:
    """
    Calculates 2D profile coordinates for 15-degree sliding dovetail joint.

    Parameters:
        male: True for male tab (nominal width and depth), False for female pocket (oversized by tol).
        tol: Slip clearance tolerance in mm (default 0.20 mm).
        base_w: Dovetail root base width at y=0 in mm (default 14.0 mm).
        depth: Dovetail projection/depth along y in mm (default 8.0 mm).
        angle_deg: Wedge flare half-angle in degrees (default 15.0 deg).

    Returns:
        List of 4 (x, y) coordinate tuples defining the closed dovetail trapezoid profile.
    """
    rad = math.radians(angle_deg)
    if male:
        w_root_half = base_w / 2.0
        w_tip_half = w_root_half + depth * math.tan(rad)
        return [
            (-w_root_half, 0.0),
            (-w_tip_half, depth),
            (w_tip_half, depth),
            (w_root_half, 0.0),
        ]
    else:
        w_root_half = (base_w + 2.0 * tol) / 2.0
        d_pocket = depth + tol
        w_tip_half = w_root_half + d_pocket * math.tan(rad)
        return [
            (-w_root_half, 0.0),
            (-w_tip_half, d_pocket),
            (w_tip_half, d_pocket),
            (w_root_half, 0.0),
        ]


def calculate_seam_dovetail_joint(
    seam_center: Optional[Tuple[float, float]] = None,
    seam_normal: Optional[Tuple[float, float]] = None,
    male: bool = True,
    tol: float = 0.20,
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0,
    p_outer: Optional[Tuple[float, float]] = None,
    p_inner: Optional[Tuple[float, float]] = None,
) -> List[Tuple[float, float]]:
    """
    Generates 2D profile coordinates for male tab or female pocket at an interlocking seam.

    If `p_outer` and `p_inner` are provided, generates the full cut path starting at `p_outer`,
    forming the dovetail feature centered along the seam, and ending at `p_inner`.
    If only `seam_center` and `seam_normal` are provided, generates the 4 dovetail trapezoid vertices.
    """
    rad = math.radians(angle_deg)

    if p_outer is not None and p_inner is not None:
        p_out = np.asarray(p_outer, dtype=float)
        p_in = np.asarray(p_inner, dtype=float)
        p_mid = (p_out + p_in) / 2.0
        seam_vec = p_in - p_out
        seam_w = float(np.linalg.norm(seam_vec))
        u = seam_vec / max(seam_w, 1e-9)

        if seam_normal is not None:
            n = np.asarray(seam_normal, dtype=float)
            n_len = float(np.linalg.norm(n))
            n = n / max(n_len, 1e-9)
        else:
            n = np.array([u[1], -u[0]])

        if male:
            w_root_half = base_w / 2.0
            w_tip_half = w_root_half + depth * math.tan(rad)
            pt_root1 = p_mid - w_root_half * u
            pt_tip1 = p_mid - w_tip_half * u + depth * n
            pt_tip2 = p_mid + w_tip_half * u + depth * n
            pt_root2 = p_mid + w_root_half * u
            return [
                (float(p_out[0]), float(p_out[1])),
                (float(pt_root1[0]), float(pt_root1[1])),
                (float(pt_tip1[0]), float(pt_tip1[1])),
                (float(pt_tip2[0]), float(pt_tip2[1])),
                (float(pt_root2[0]), float(pt_root2[1])),
                (float(p_in[0]), float(p_in[1])),
            ]
        else:
            w_root_half = (base_w + 2.0 * tol) / 2.0
            d_pocket = depth + tol
            w_tip_half = w_root_half + d_pocket * math.tan(rad)
            pt_root1 = p_mid - w_root_half * u
            pt_tip1 = p_mid - w_tip_half * u + d_pocket * n
            pt_tip2 = p_mid + w_tip_half * u + d_pocket * n
            pt_root2 = p_mid + w_root_half * u
            return [
                (float(p_out[0]), float(p_out[1])),
                (float(pt_root1[0]), float(pt_root1[1])),
                (float(pt_tip1[0]), float(pt_tip1[1])),
                (float(pt_tip2[0]), float(pt_tip2[1])),
                (float(pt_root2[0]), float(pt_root2[1])),
                (float(p_in[0]), float(p_in[1])),
            ]

    center = np.asarray(seam_center if seam_center is not None else (0.0, 0.0), dtype=float)
    if seam_normal is not None:
        n = np.asarray(seam_normal, dtype=float)
        n_len = float(np.linalg.norm(n))
        n = n / max(n_len, 1e-9)
    else:
        n = np.array([0.0, 1.0])
    u = np.array([-n[1], n[0]])

    local_pts = calculate_seam_dovetail_profile(male=male, tol=tol, base_w=base_w, depth=depth, angle_deg=angle_deg)
    global_pts = []
    for x_loc, y_loc in local_pts:
        p_glob = center + x_loc * u + y_loc * n
        global_pts.append((float(p_glob[0]), float(p_glob[1])))
    return global_pts


def calculate_min_oriented_bounding_box_dimension(points: Sequence[Tuple[float, float]]) -> float:
    """
    Computes the minimum maximum-extent of the oriented bounding box of a 2D point set.
    Used to determine the minimum square bed size needed to print the part flat.
    """
    pts = np.asarray(points, dtype=float)
    if len(pts) < 3:
        return 0.0
    angles = np.linspace(0, np.pi, 90, endpoint=False)
    min_max_dim = float("inf")
    for a in angles:
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        rot_x = pts[:, 0] * cos_a - pts[:, 1] * sin_a
        rot_y = pts[:, 0] * sin_a + pts[:, 1] * cos_a
        extent_x = float(rot_x.max() - rot_x.min())
        extent_y = float(rot_y.max() - rot_y.min())
        max_extent = max(extent_x, extent_y)
        if max_extent < min_max_dim:
            min_max_dim = max_extent
    return min_max_dim


# ---------------------------------------------------------------------------
# Quadrant Segmentation Engine
# ---------------------------------------------------------------------------

def _get_arc_indices(start_idx: int, end_idx: int, total_len: int) -> List[int]:
    """Returns circular index slice along a closed loop from start_idx to end_idx."""
    if start_idx <= end_idx:
        return list(range(start_idx, end_idx + 1))
    else:
        return list(range(start_idx, total_len)) + list(range(0, end_idx + 1))


def slice_track_quadrants(
    outer_poly: Sequence[Tuple[float, float]],
    inner_poly: Sequence[Tuple[float, float]],
    params: Optional[ConformalTrackParameters] = None,
    x_split: Optional[float] = None,
    y_split: Optional[float] = None,
) -> Dict[str, QuadrantGeometry]:
    """
    Slices continuous 2D track boundary loops into 4 printable quadrants with 15° interlocking dovetail seam joints.

    Parameters:
        outer_poly: Outer boundary loop of track body (CCW).
        inner_poly: Inner boundary loop of track body (CCW).
        params: Optional ConformalTrackParameters instance.
        x_split: Optional vehicle lateral split coordinate (defaults to optimal balanced split).
        y_split: Optional vehicle longitudinal split coordinate (defaults to midpoint of outer Y extent).

    Returns:
        Dict mapping quadrant names ("TRK_Front_L", "TRK_Front_R", "TRK_Rear_L", "TRK_Rear_R")
        to QuadrantGeometry dataclass instances.
    """
    if params is None:
        params = ConformalTrackParameters()

    outer = ensure_ccw(outer_poly)
    inner = ensure_ccw(inner_poly)
    if len(outer) < 60:
        outer = resample_polygon_2d(outer, target_spacing=params.resample_spacing_mm)
    if len(inner) < 60:
        inner = resample_polygon_2d(inner, target_spacing=params.resample_spacing_mm)

    n_out = len(outer)
    n_in = len(inner)

    outer_arr = np.asarray(outer, dtype=float)
    inner_arr = np.asarray(inner, dtype=float)

    if y_split is None:
        y_split = float((outer_arr[:, 1].min() + outer_arr[:, 1].max()) / 2.0)

    # If x_split is not provided, perform local neighborhood search to balance quadrant dimensions
    if x_split is None:
        x_mid = float((outer_arr[:, 0].min() + outer_arr[:, 0].max()) / 2.0)
        candidate_splits = [x_mid + float(delta) for delta in np.linspace(-15.0, 15.0, 31)]
        best_x_split = x_mid
        best_worst_dim = float("inf")

        for cand_x in candidate_splits:
            f_cands = [i for i in range(n_out) if outer_arr[i, 1] > y_split]
            f_idx = min(f_cands, key=lambda i: abs(outer_arr[i, 0] - cand_x)) if f_cands else 0

            r_cands = [i for i in range(n_out) if outer_arr[i, 1] < y_split]
            r_idx = min(r_cands, key=lambda i: abs(outer_arr[i, 0] - cand_x)) if r_cands else n_out // 2

            l_cands = [i for i in range(n_out) if outer_arr[i, 0] <= outer_arr[:, 0].min() + 8.0]
            l_idx = min(l_cands, key=lambda i: abs(outer_arr[i, 1] - y_split)) if l_cands else 0

            rg_cands = [i for i in range(n_out) if outer_arr[i, 0] >= outer_arr[:, 0].max() - 8.0]
            rg_idx = min(rg_cands, key=lambda i: abs(outer_arr[i, 1] - y_split)) if rg_cands else n_out // 2

            worst_dim = 0.0
            for s_i, e_i in [(f_idx, l_idx), (l_idx, r_idx), (r_idx, rg_idx), (rg_idx, f_idx)]:
                o_pts = [outer[i] for i in _get_arc_indices(s_i, e_i, n_out)]
                in_s = int(np.argmin(np.linalg.norm(inner_arr - outer_arr[s_i], axis=1)))
                in_e = int(np.argmin(np.linalg.norm(inner_arr - outer_arr[e_i], axis=1)))
                i_pts = [inner[i] for i in reversed(_get_arc_indices(in_s, in_e, n_in))]
                dim = calculate_min_oriented_bounding_box_dimension(o_pts + i_pts)
                if dim > worst_dim:
                    worst_dim = dim

            if worst_dim < best_worst_dim:
                best_worst_dim = worst_dim
                best_x_split = cand_x

        x_split = best_x_split

    # Find the 4 seam indices on outer loop
    front_candidates = [i for i in range(n_out) if outer_arr[i, 1] > y_split]
    front_idx = min(front_candidates, key=lambda i: abs(outer_arr[i, 0] - x_split)) if front_candidates else 0

    rear_candidates = [i for i in range(n_out) if outer_arr[i, 1] < y_split]
    rear_idx = min(rear_candidates, key=lambda i: abs(outer_arr[i, 0] - x_split)) if rear_candidates else n_out // 2

    left_candidates = [i for i in range(n_out) if outer_arr[i, 0] <= outer_arr[:, 0].min() + 8.0]
    left_idx = min(left_candidates, key=lambda i: abs(outer_arr[i, 1] - y_split)) if left_candidates else 0

    right_candidates = [i for i in range(n_out) if outer_arr[i, 0] >= outer_arr[:, 0].max() - 8.0]
    right_idx = min(right_candidates, key=lambda i: abs(outer_arr[i, 1] - y_split)) if right_candidates else n_out // 2

    seam_outer_indices = {
        "Front_Seam": front_idx,
        "Left_Seam": left_idx,
        "Rear_Seam": rear_idx,
        "Right_Seam": right_idx,
    }

    # Find matching inner loop indices
    seam_inner_indices = {}
    for seam_name, out_idx in seam_outer_indices.items():
        if n_in == n_out:
            seam_inner_indices[seam_name] = out_idx
        else:
            p_out = outer_arr[out_idx]
            dists = np.linalg.norm(inner_arr - p_out, axis=1)
            seam_inner_indices[seam_name] = int(np.argmin(dists))

    # Compute forward tangent and unit normal vector for each seam
    seam_normals = {}
    seam_joints = {}
    for seam_name, out_idx in seam_outer_indices.items():
        in_idx = seam_inner_indices[seam_name]
        p_out = outer_arr[out_idx]
        p_in = inner_arr[in_idx]
        seam_vec = p_in - p_out
        seam_w = float(np.linalg.norm(seam_vec))
        u = seam_vec / max(seam_w, 1e-9)

        # Tangent along outer loop in CCW direction
        t_vec = outer_arr[(out_idx + 1) % n_out] - outer_arr[(out_idx - 1) % n_out]
        t_len = float(np.linalg.norm(t_vec))
        t_unit = t_vec / max(t_len, 1e-9)

        # Forward normal n perpendicular to u
        n_cand = np.array([-u[1], u[0]])
        if np.dot(n_cand, t_unit) < 0:
            n_cand = -n_cand

        seam_normals[seam_name] = n_cand
        p_mid = (p_out + p_in) / 2.0
        seam_joints[seam_name] = SeamJoint(
            name=seam_name,
            location=seam_name.split("_")[0].lower(),
            center=(float(p_mid[0]), float(p_mid[1])),
            p_outer=(float(p_out[0]), float(p_out[1])),
            p_inner=(float(p_in[0]), float(p_in[1])),
            normal=(float(n_cand[0]), float(n_cand[1])),
            seam_vector=(float(u[0]), float(u[1])),
            width_mm=seam_w,
            male_quadrant="",
            female_quadrant="",
        )

    # Quadrant topologies:
    # TRK_Front_L: Front_Seam (Female) -> Left_Seam (Male)
    # TRK_Rear_L:  Left_Seam (Female)  -> Rear_Seam (Male)
    # TRK_Rear_R:  Rear_Seam (Female)  -> Right_Seam (Male)
    # TRK_Front_R: Right_Seam (Female) -> Front_Seam (Male)
    quad_defs = [
        {
            "name": "TRK_Front_L",
            "start_seam": "Front_Seam",
            "start_joint_type": "female",
            "end_seam": "Left_Seam",
            "end_joint_type": "male",
        },
        {
            "name": "TRK_Rear_L",
            "start_seam": "Left_Seam",
            "start_joint_type": "female",
            "end_seam": "Rear_Seam",
            "end_joint_type": "male",
        },
        {
            "name": "TRK_Rear_R",
            "start_seam": "Rear_Seam",
            "start_joint_type": "female",
            "end_seam": "Right_Seam",
            "end_joint_type": "male",
        },
        {
            "name": "TRK_Front_R",
            "start_seam": "Right_Seam",
            "start_joint_type": "female",
            "end_seam": "Front_Seam",
            "end_joint_type": "male",
        },
    ]

    for q_def in quad_defs:
        if q_def["end_joint_type"] == "male":
            seam_joints[q_def["end_seam"]].male_quadrant = q_def["name"]
        else:
            seam_joints[q_def["end_seam"]].female_quadrant = q_def["name"]

        if q_def["start_joint_type"] == "male":
            seam_joints[q_def["start_seam"]].male_quadrant = q_def["name"]
        else:
            seam_joints[q_def["start_seam"]].female_quadrant = q_def["name"]

    rad = math.radians(params.seam_dovetail_angle_deg)
    base_w = params.trail_base_width_mm
    depth = 8.0
    tol = params.tol_seam_dovetail_mm

    def _dovetail_cut(
        p_from: Sequence[float],
        p_to: Sequence[float],
        is_male: bool,
        outward_n: np.ndarray,
    ) -> List[Tuple[float, float]]:
        p_a = np.asarray(p_from, dtype=float)
        p_b = np.asarray(p_to, dtype=float)
        p_m = (p_a + p_b) / 2.0
        s_vec = p_b - p_a
        s_len = float(np.linalg.norm(s_vec))
        u_vec = s_vec / max(s_len, 1e-9)

        if is_male:
            w_r_half = base_w / 2.0
            w_t_half = w_r_half + depth * math.tan(rad)
            r1 = p_m - w_r_half * u_vec
            t1 = p_m - w_t_half * u_vec + depth * outward_n
            t2 = p_m + w_t_half * u_vec + depth * outward_n
            r2 = p_m + w_r_half * u_vec
            return [
                (float(r1[0]), float(r1[1])),
                (float(t1[0]), float(t1[1])),
                (float(t2[0]), float(t2[1])),
                (float(r2[0]), float(r2[1])),
            ]
        else:
            w_r_half = (base_w + 2.0 * tol) / 2.0
            d_p = depth + tol
            w_t_half = w_r_half + d_p * math.tan(rad)
            r1 = p_m - w_r_half * u_vec
            t1 = p_m - w_t_half * u_vec - d_p * outward_n
            t2 = p_m + w_t_half * u_vec - d_p * outward_n
            r2 = p_m + w_r_half * u_vec
            return [
                (float(r1[0]), float(r1[1])),
                (float(t1[0]), float(t1[1])),
                (float(t2[0]), float(t2[1])),
                (float(r2[0]), float(r2[1])),
            ]

    results: Dict[str, QuadrantGeometry] = {}

    for q_def in quad_defs:
        q_name = q_def["name"]
        s_seam = q_def["start_seam"]
        e_seam = q_def["end_seam"]
        s_out_idx = seam_outer_indices[s_seam]
        e_out_idx = seam_outer_indices[e_seam]
        s_in_idx = seam_inner_indices[s_seam]
        e_in_idx = seam_inner_indices[e_seam]

        outer_idxs = _get_arc_indices(s_out_idx, e_out_idx, n_out)
        inner_idxs = _get_arc_indices(s_in_idx, e_in_idx, n_in)

        outer_pts = [outer[i] for i in outer_idxs]
        inner_pts = [inner[i] for i in inner_idxs]
        inner_pts_rev = list(reversed(inner_pts))

        nominal_poly = outer_pts + inner_pts_rev

        end_cut_pts = _dovetail_cut(
            p_from=outer[e_out_idx],
            p_to=inner[e_in_idx],
            is_male=(q_def["end_joint_type"] == "male"),
            outward_n=seam_normals[e_seam],
        )

        start_cut_pts = _dovetail_cut(
            p_from=inner[s_in_idx],
            p_to=outer[s_out_idx],
            is_male=(q_def["start_joint_type"] == "male"),
            outward_n=-seam_normals[s_seam],
        )

        full_poly = outer_pts + end_cut_pts + inner_pts_rev + start_cut_pts

        all_arr = np.asarray(full_poly, dtype=float)
        min_x, max_x = float(all_arr[:, 0].min()), float(all_arr[:, 0].max())
        min_y, max_y = float(all_arr[:, 1].min()), float(all_arr[:, 1].max())
        w = max_x - min_x
        h = max_y - min_y

        max_dim = calculate_min_oriented_bounding_box_dimension(full_poly)
        area = calculate_polygon_area(full_poly)
        perim = calculate_polygon_perimeter(full_poly)

        results[q_name] = QuadrantGeometry(
            name=q_name,
            polygon=full_poly,
            nominal_polygon=nominal_poly,
            outer_points=outer_pts,
            inner_points=inner_pts,
            start_seam=s_seam,
            start_joint_type=q_def["start_joint_type"],
            end_seam=e_seam,
            end_joint_type=q_def["end_joint_type"],
            bounds={"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y},
            width=w,
            height=h,
            max_dimension=max_dim,
            area_mm2=area,
            perimeter_mm=perim,
        )

    return results


def generate_track_quadrant_polygons(
    perimeter_pts: Sequence[Tuple[float, float]],
    track_width_mm: float = 30.0,
    wall_clearance_mm: float = 12.7,
) -> Dict[str, Dict[str, Any]]:
    """
    Partitions the continuous conformal floor track ring into 4 printable quadrants
    (TRK_Front_L, TRK_Front_R, TRK_Rear_L, TRK_Rear_R) sized to fit within 310mm print bed envelope.

    Parameters:
        perimeter_pts: Floor boundary polygon or track centerline polygon.
        track_width_mm: Track profile width.
        wall_clearance_mm: Clearance offset from frunk tub wall.

    Returns:
        Dict of 4 quadrant descriptors with points, bounds, and maximum dimension.
    """
    loops = generate_track_boundary_loops(
        perimeter_pts,
        wall_clearance_mm=wall_clearance_mm,
        track_width_mm=track_width_mm,
    )
    quadrants = slice_track_quadrants(
        outer_poly=loops["outer_loop"],
        inner_poly=loops["inner_loop"],
    )

    result: Dict[str, Dict[str, Any]] = {}
    for name, q in quadrants.items():
        result[name] = {
            "points": q.polygon,
            "polygon": q.polygon,
            "nominal_polygon": q.nominal_polygon,
            "bounds": q.bounds,
            "width": q.width,
            "height": q.height,
            "max_dimension": q.max_dimension,
            "geometry": q,
        }

    return result

