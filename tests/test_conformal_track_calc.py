"""
Unit Tests for Conformal Floor Track Geometry Engine
Tesla Model X 2017 Frunk LiDAR-Matched Perimeter Floor Track
"""

import math
import os
import pytest
import numpy as np

from fusion_scripts.conformal_track_calc import (
    ConformalTrackParameters,
    extract_calibrated_floor_polygon,
    offset_polygon_2d,
    resample_polygon_2d,
    smooth_polygon_2d,
    generate_track_boundary_loops,
    calculate_captive_trail_profile,
    calculate_rigid_rectangular_profile,
    calculate_track_cross_section_profile,
    generate_track_quadrant_polygons,
    calculate_polygon_area,
    calculate_polygon_perimeter,
)


def test_conformal_track_parameters_defaults():
    """Verify default dimensions, clearances, and profile parameters."""
    params = ConformalTrackParameters()
    assert params.wall_clearance_mm == pytest.approx(12.7, abs=0.01)  # 0.50 in
    assert params.track_width_mm == 30.0
    assert params.track_height_mm == 18.0
    assert params.trail_base_width_mm == 14.0
    assert params.trail_neck_width_mm == 8.0
    assert params.trail_height_mm == 5.0
    assert params.rigid_guide_width_mm == 18.0
    assert params.rigid_guide_height_mm == 8.0
    assert params.rigid_wall_thickness_mm == 4.0
    assert params.tol_seam_dovetail_mm == 0.20
    assert params.seam_dovetail_angle_deg == 15.0
    assert params.max_bed_dimension_mm == 310.0

    # Conversions
    assert params.wall_clearance_in == pytest.approx(0.50, abs=0.01)
    assert params.track_width_cm == pytest.approx(3.0, abs=0.01)
    assert params.track_height_cm == pytest.approx(1.8, abs=0.01)


def test_offset_polygon_2d_rectangle():
    """Verify mathematical inward offset on a rectangular polygon."""
    rect = [
        (0.0, 0.0),
        (400.0, 0.0),
        (400.0, 300.0),
        (0.0, 300.0),
    ]
    inset_rect = offset_polygon_2d(rect, offset_distance_mm=12.7, inward=True)
    assert len(inset_rect) == 4

    expected = [
        (12.7, 12.7),
        (387.3, 12.7),
        (387.3, 287.3),
        (12.7, 287.3),
    ]
    for pt, exp in zip(inset_rect, expected):
        assert pt[0] == pytest.approx(exp[0], abs=1e-3)
        assert pt[1] == pytest.approx(exp[1], abs=1e-3)

    orig_area = calculate_polygon_area(rect)
    inset_area = calculate_polygon_area(inset_rect)
    expected_area = (400.0 - 25.4) * (300.0 - 25.4)
    assert orig_area == pytest.approx(120000.0, abs=1e-3)
    assert inset_area == pytest.approx(expected_area, abs=1e-3)


def test_offset_polygon_2d_circle():
    """Verify uniform radial offset on a circular polygon."""
    r = 100.0
    n = 120
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    circle_pts = [(float(r * np.cos(t)), float(r * np.sin(t))) for t in theta]

    offset_d = 12.7
    inset_pts = offset_polygon_2d(circle_pts, offset_distance_mm=offset_d, inward=True)

    expected_r = r - offset_d
    for x, y in inset_pts:
        curr_r = math.hypot(x, y)
        assert curr_r == pytest.approx(expected_r, abs=0.1)


def test_extract_calibrated_floor_polygon_from_stl():
    """Extract floor boundary polygon from LiDAR scan at Z=10mm."""
    stl_path = "docs/scans/frunk_scan_calibrated.stl"
    assert os.path.exists(stl_path), f"Scan file not found: {stl_path}"

    floor_poly = extract_calibrated_floor_polygon(stl_path=stl_path, z_height=10.0)
    assert len(floor_poly) >= 20

    xs = [p[0] for p in floor_poly]
    ys = [p[1] for p in floor_poly]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    depth = max_y - min_y

    # Calibrated scan floor section bounds: width ~ 800mm, depth ~ 260mm
    assert width > 700.0
    assert depth > 200.0

    area = calculate_polygon_area(floor_poly)
    perimeter = calculate_polygon_perimeter(floor_poly)
    assert area > 100000.0  # > 1000 cm^2
    assert perimeter > 1500.0


def test_lidar_floor_inward_offset_clearance():
    """Verify 0.50 in (12.7 mm) inward offset from calibrated scan boundary."""
    stl_path = "docs/scans/frunk_scan_calibrated.stl"
    floor_poly = extract_calibrated_floor_polygon(stl_path=stl_path, z_height=10.0)
    inset_poly = offset_polygon_2d(floor_poly, offset_distance_mm=12.7, inward=True)

    assert len(inset_poly) == len(floor_poly)

    # Inset area must be strictly smaller than original
    area_orig = calculate_polygon_area(floor_poly)
    area_inset = calculate_polygon_area(inset_poly)
    assert area_inset < area_orig

    # Point-to-segment distance check: every inset point is approx 12.7mm from boundary
    def point_to_segment_dist(p, a, b):
        ab = (b[0] - a[0], b[1] - a[1])
        ab_sq = ab[0]**2 + ab[1]**2
        if ab_sq < 1e-9:
            return math.hypot(p[0] - a[0], p[1] - a[1])
        t = max(0.0, min(1.0, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / ab_sq))
        proj = (a[0] + t * ab[0], a[1] + t * ab[1])
        return math.hypot(p[0] - proj[0], p[1] - proj[1])

    dists = []
    n = len(floor_poly)
    for p in inset_poly:
        d_min = min(point_to_segment_dist(p, floor_poly[i], floor_poly[(i + 1) % n]) for i in range(n))
        dists.append(d_min)

    mean_dist = sum(dists) / len(dists)
    assert mean_dist == pytest.approx(12.7, abs=0.5)


def test_generate_track_boundary_loops():
    """Verify outer and inner closed track boundary generation with constant 30mm width."""
    # 1. Exact synthetic geometry test (30.0 mm constant track width)
    rect = [(0.0, 0.0), (400.0, 0.0), (400.0, 300.0), (0.0, 300.0)]
    rect_loops = generate_track_boundary_loops(rect, wall_clearance_mm=12.7, track_width_mm=30.0)
    assert "outer_loop" in rect_loops
    assert "inner_loop" in rect_loops
    assert "centerline" in rect_loops

    def point_to_segment_dist(p, a, b):
        ab = (b[0] - a[0], b[1] - a[1])
        ab_sq = ab[0]**2 + ab[1]**2
        if ab_sq < 1e-9:
            return math.hypot(p[0] - a[0], p[1] - a[1])
        t = max(0.0, min(1.0, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / ab_sq))
        proj = (a[0] + t * ab[0], a[1] + t * ab[1])
        return math.hypot(p[0] - proj[0], p[1] - proj[1])

    outer_rect = rect_loops["outer_loop"]
    inner_rect = rect_loops["inner_loop"]
    for p in inner_rect:
        d_min = min(point_to_segment_dist(p, outer_rect[i], outer_rect[(i + 1) % len(outer_rect)]) for i in range(len(outer_rect)))
        assert d_min == pytest.approx(30.0, abs=1e-3)

    # 2. Calibrated scan geometry test
    stl_path = "docs/scans/frunk_scan_calibrated.stl"
    floor_poly = extract_calibrated_floor_polygon(stl_path=stl_path, z_height=10.0)

    loops = generate_track_boundary_loops(floor_poly, wall_clearance_mm=12.7, track_width_mm=30.0)
    outer_loop = loops["outer_loop"]
    inner_loop = loops["inner_loop"]
    centerline = loops["centerline"]

    assert len(outer_loop) == len(inner_loop) == len(centerline)

    area_outer = calculate_polygon_area(outer_loop)
    area_inner = calculate_polygon_area(inner_loop)
    assert area_outer > area_inner

    # Track width check on scan
    dists = []
    n = len(outer_loop)
    for p in inner_loop:
        d_min = min(point_to_segment_dist(p, outer_loop[i], outer_loop[(i + 1) % n]) for i in range(n))
        dists.append(d_min)

    mean_dist = sum(dists) / len(dists)
    assert mean_dist == pytest.approx(30.0, abs=2.0)


def test_calculate_captive_trail_profile():
    """Verify top captive T-rail / dovetail profile coordinates."""
    params = ConformalTrackParameters()
    pts = calculate_captive_trail_profile(
        base_width=params.trail_base_width_mm,
        neck_width=params.trail_neck_width_mm,
        height=params.trail_height_mm,
    )
    assert len(pts) >= 4

    # Profile must be symmetric about X=0
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    assert min(xs) == pytest.approx(-params.trail_base_width_mm / 2.0, abs=1e-3)
    assert max(xs) == pytest.approx(params.trail_base_width_mm / 2.0, abs=1e-3)
    assert min(ys) == 0.0
    assert max(ys) == pytest.approx(params.trail_height_mm, abs=1e-3)


def test_calculate_rigid_rectangular_profile():
    """Verify rigid rectangular track cross-section with vertical anti-tip guide walls."""
    params = ConformalTrackParameters()
    pts = calculate_rigid_rectangular_profile(
        track_width=params.track_width_mm,
        track_height=params.track_height_mm,
        guide_width=params.rigid_guide_width_mm,
        guide_height=params.rigid_guide_height_mm,
        wall_thickness=params.rigid_wall_thickness_mm,
    )
    assert len(pts) >= 6

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    # Full width and height checks
    assert min(xs) == pytest.approx(-params.track_width_mm / 2.0, abs=1e-3)
    assert max(xs) == pytest.approx(params.track_width_mm / 2.0, abs=1e-3)
    assert min(ys) == 0.0
    assert max(ys) == pytest.approx(params.track_height_mm, abs=1e-3)


def test_calculate_track_cross_section_profile_dispatch():
    """Verify profile calculation dispatcher supports both profile styles."""
    trail_pts = calculate_track_cross_section_profile(profile_type="captive_trail")
    rect_pts = calculate_track_cross_section_profile(profile_type="rigid_rectangular")

    assert len(trail_pts) > 0
    assert len(rect_pts) > 0

    with pytest.raises(ValueError):
        calculate_track_cross_section_profile(profile_type="unknown_type")


def test_generate_track_quadrant_polygons():
    """Verify splitting full track perimeter into 4 printable quadrant segments under 310mm."""
    stl_path = "docs/scans/frunk_scan_calibrated.stl"
    floor_poly = extract_calibrated_floor_polygon(stl_path=stl_path, z_height=10.0)

    quadrants = generate_track_quadrant_polygons(floor_poly, track_width_mm=30.0)
    assert len(quadrants) == 4
    for key in ["TRK_Front_L", "TRK_Front_R", "TRK_Rear_L", "TRK_Rear_R"]:
        assert key in quadrants
        q = quadrants[key]
        assert "points" in q
        assert "bounds" in q
        assert "max_dimension" in q
        assert q["max_dimension"] < 310.0, f"Quadrant {key} exceeds 310mm bed limit: {q['max_dimension']}"
