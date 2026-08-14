# tests/test_standalone_generation.py
import math
import pytest
from fusion_scripts.geometry_calc import (
    FrunkParameters,
    calculate_dovetail_profile,
    calculate_truss_web_triangles,
    calculate_diamond_lattice_segments
)

def test_lattice_strut_polygon_generation():
    params = FrunkParameters()
    inner_w = params.panel_width_mm - 20.0
    inner_h = params.panel_height_mm - 20.0
    segments = calculate_diamond_lattice_segments(
        width=inner_w,
        height=inner_h,
        pitch=params.lattice_pitch_mm,
        strut_w=params.lattice_strut_mm
    )
    assert len(segments) > 0
    w = params.lattice_strut_mm
    # Normal offset for 45 degree strut
    dx = w / (2.0 * math.sqrt(2))
    dy = w / (2.0 * math.sqrt(2))
    
    for (x1, y1), (x2, y2) in segments:
        # Check that segment length is positive
        length = math.hypot(x2 - x1, y2 - y1)
        assert length > 0
