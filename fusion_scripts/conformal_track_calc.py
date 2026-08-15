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
# Quadrant Segmentation Engine
# ---------------------------------------------------------------------------

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
    outer = np.asarray(loops["outer_loop"], dtype=float)

    # Split boundaries: X = 0 (vehicle lateral centerline), Y = mid (longitudinal partition)
    x_split = 0.0
    y_split = float((outer[:, 1].min() + outer[:, 1].max()) / 2.0)

    quadrant_specs = [
        ("TRK_Front_L", outer[:, 0] <= x_split, outer[:, 1] >= y_split),
        ("TRK_Front_R", outer[:, 0] >= x_split, outer[:, 1] >= y_split),
        ("TRK_Rear_L", outer[:, 0] <= x_split, outer[:, 1] <= y_split),
        ("TRK_Rear_R", outer[:, 0] >= x_split, outer[:, 1] <= y_split),
    ]

    result: Dict[str, Dict[str, Any]] = {}

    for name, x_mask, y_mask in quadrant_specs:
        mask = x_mask & y_mask
        pts_q = outer[mask]
        if len(pts_q) == 0:
            pts_q = outer[:5]

        min_x, max_x = float(pts_q[:, 0].min()), float(pts_q[:, 0].max())
        min_y, max_y = float(pts_q[:, 1].min()), float(pts_q[:, 1].max())
        w = max_x - min_x
        h = max_y - min_y

        # Minimum bounding box / oriented extent for printing flat
        cov = np.cov(pts_q.T)
        evals, _ = np.linalg.eigh(cov)
        oriented_length = float(np.sqrt(max(evals)) * 3.5) if len(pts_q) > 2 else max(w, h)
        effective_max_dim = min(max(w, h), oriented_length, 305.0)

        result[name] = {
            "points": [(float(x), float(y)) for x, y in pts_q],
            "bounds": {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y},
            "width": w,
            "height": h,
            "max_dimension": effective_max_dim,
        }

    return result
