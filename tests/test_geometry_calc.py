import math
import pytest

from fusion_scripts.geometry_calc import (
    FrunkParameters,
    calculate_dovetail_profile,
    calculate_truss_web_triangles,
    calculate_diamond_lattice_segments,
)


def test_frunk_parameters_defaults():
    """Verify all default parameter values for Model X 2017 frunk divider system."""
    params = FrunkParameters()
    assert params.bay_spacing_mm == pytest.approx(304.8, abs=0.1)
    assert params.frame_height_mm == pytest.approx(280.0, abs=0.1)
    assert params.truss_height_mm == 35.0
    assert params.truss_width_mm == 24.0
    assert params.slot_width_mm == 6.4
    assert params.slot_depth_mm == 8.0
    assert params.panel_thickness_mm == 5.0
    assert params.panel_width_mm == 298.0
    assert params.panel_height_mm == 275.0
    assert params.lattice_pitch_mm == 18.0
    assert params.lattice_strut_mm == 3.5
    assert params.tol_dovetail_mm == 0.25
    assert params.tol_tenon_mm == 0.20
    assert params.pin_diameter_mm == 5.0
    assert params.dovetail_base_width_mm == 14.0
    assert params.dovetail_depth_mm == 8.0
    assert params.dovetail_angle_deg == 15.0


def test_frunk_parameters_conversions():
    """Verify metric-to-imperial and metric-to-cm conversion properties."""
    params = FrunkParameters()
    assert params.bay_spacing_in == pytest.approx(12.0, abs=0.01)
    assert params.frame_height_in == pytest.approx(11.02, abs=0.05)
    assert params.bay_spacing_cm == pytest.approx(30.48, abs=0.01)
    assert params.frame_height_cm == pytest.approx(28.0, abs=0.01)
    assert params.truss_height_cm == pytest.approx(3.5, abs=0.01)
    assert params.truss_width_cm == pytest.approx(2.4, abs=0.01)
    assert params.slot_width_cm == pytest.approx(0.64, abs=0.001)
    assert params.slot_depth_cm == pytest.approx(0.8, abs=0.001)
    assert params.panel_thickness_cm == pytest.approx(0.5, abs=0.001)
    assert params.panel_width_cm == pytest.approx(29.8, abs=0.01)
    assert params.panel_height_cm == pytest.approx(27.5, abs=0.01)
    assert params.pin_diameter_cm == pytest.approx(0.5, abs=0.01)


def test_dovetail_profile_clearance():
    """Verify slip clearance and geometry of dovetail male tab vs female pocket."""
    params = FrunkParameters()
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
    female_pts = calculate_dovetail_profile(male=False, tol=params.tol_dovetail_mm)

    # Male width should be narrower than female width by exactly 2 * tolerance
    male_root_w = max(p[0] for p in male_pts) - min(p[0] for p in male_pts)
    female_root_w = max(p[0] for p in female_pts) - min(p[0] for p in female_pts)
    assert female_root_w - male_root_w == pytest.approx(2 * params.tol_dovetail_mm, abs=0.01)

    # Both profiles should have 4 vertices
    assert len(male_pts) == 4
    assert len(female_pts) == 4

    # Verify symmetry about X=0
    for pts in (male_pts, female_pts):
        assert pts[0][0] == pytest.approx(-pts[3][0], abs=1e-5)
        assert pts[1][0] == pytest.approx(-pts[2][0], abs=1e-5)
        assert pts[0][1] == 0.0 and pts[3][1] == 0.0
        assert pts[1][1] == 8.0 and pts[2][1] == 8.0

    # Verify 15-degree flare angle
    # flare = depth * tan(15 deg)
    male_w_root = abs(male_pts[3][0] - male_pts[0][0])
    male_w_tip = abs(male_pts[2][0] - male_pts[1][0])
    expected_flare = 2.0 * 8.0 * math.tan(math.radians(15.0))
    assert (male_w_tip - male_w_root) == pytest.approx(expected_flare, abs=0.01)


def test_dovetail_custom_parameters():
    """Verify dovetail generation with non-default geometric parameters."""
    pts = calculate_dovetail_profile(male=True, tol=0.1, base_w=20.0, depth=10.0, angle_deg=20.0)
    flare = 10.0 * math.tan(math.radians(20.0))
    expected_w_root = (20.0 - 0.2) / 2.0
    expected_w_tip = (20.0 + 2.0 * flare - 0.2) / 2.0
    assert pts[0] == pytest.approx((-expected_w_root, 0.0))
    assert pts[1] == pytest.approx((-expected_w_tip, 10.0))
    assert pts[2] == pytest.approx((expected_w_tip, 10.0))
    assert pts[3] == pytest.approx((expected_w_root, 0.0))


def test_truss_web_triangles():
    """Verify triangular cutout generation for floor truss structures."""
    triangles = calculate_truss_web_triangles(span_length=304.8, height=35.0, web_thickness=4.0)
    assert len(triangles) == 6  # 6 bays by default
    for tri in triangles:
        assert len(tri) == 3
        # Ensure all vertices are strictly inside bounding box
        for x, y in tri:
            assert 0.0 <= x <= 304.8
            assert 0.0 <= y <= 35.0

    # Verify alternating apex orientation
    # Bay 0: upright -> apex is at y = height - web_thickness = 31.0
    assert triangles[0][2][1] == pytest.approx(31.0, abs=0.01)
    # Bay 1: inverted -> apex is at y = web_thickness = 4.0
    assert triangles[1][2][1] == pytest.approx(4.0, abs=0.01)


def test_truss_web_custom_bays():
    """Verify truss generation with custom bay counts."""
    triangles_4 = calculate_truss_web_triangles(span_length=200.0, height=40.0, web_thickness=5.0, num_bays=4)
    assert len(triangles_4) == 4
    for tri in triangles_4:
        assert len(tri) == 3


def test_diamond_lattice_45_degree():
    """Verify 45-degree lattice line segment angle, intersection bounds, and distribution."""
    width = 278.0
    height = 255.0
    pitch = 18.0
    segments = calculate_diamond_lattice_segments(width=width, height=height, pitch=pitch, strut_w=3.5)
    assert len(segments) > 10

    for (x1, y1), (x2, y2) in segments:
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        # 45-degree angle check: dx should equal dy
        angle = math.degrees(math.atan2(dy, dx))
        assert angle == pytest.approx(45.0, abs=1.0) or math.isclose(dx, 0) or math.isclose(dy, 0)
        # Verify points are within bounding box
        assert 0.0 <= x1 <= width and 0.0 <= x2 <= width
        assert 0.0 <= y1 <= height and 0.0 <= y2 <= height

        # Verify endpoints lie on boundary
        on_boundary_1 = (math.isclose(x1, 0.0, abs_tol=1e-3) or math.isclose(x1, width, abs_tol=1e-3) or
                         math.isclose(y1, 0.0, abs_tol=1e-3) or math.isclose(y1, height, abs_tol=1e-3))
        on_boundary_2 = (math.isclose(x2, 0.0, abs_tol=1e-3) or math.isclose(x2, width, abs_tol=1e-3) or
                         math.isclose(y2, 0.0, abs_tol=1e-3) or math.isclose(y2, height, abs_tol=1e-3))
        assert on_boundary_1 and on_boundary_2


def test_diamond_lattice_square_and_aspect_ratios():
    """Verify lattice calculation on square and high aspect ratio rectangles."""
    square_segs = calculate_diamond_lattice_segments(width=100.0, height=100.0, pitch=15.0)
    assert len(square_segs) > 5
    for (x1, y1), (x2, y2) in square_segs:
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        assert math.isclose(dx, dy, abs_tol=1e-4)

    tall_segs = calculate_diamond_lattice_segments(width=50.0, height=200.0, pitch=15.0)
    assert len(tall_segs) > 5
    for (x1, y1), (x2, y2) in tall_segs:
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        assert math.isclose(dx, dy, abs_tol=1e-4)
