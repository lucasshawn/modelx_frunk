"""
Unit test for CAD Modeling Guide & Parameter Reference documentation.
Verifies file existence, structure, parameter completeness, component coverage,
assembly layouts, and export guidelines.
"""

import os
import pytest
from fusion_scripts.geometry_calc import FrunkParameters


def test_cad_guide_exists_and_nonempty():
    guide_path = os.path.join("docs", "cad_modeling_guide.md")
    assert os.path.exists(guide_path), f"Expected {guide_path} to exist"
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content) > 1000, "CAD modeling guide content is too brief"


def test_cad_guide_covers_all_parameters():
    guide_path = os.path.join("docs", "cad_modeling_guide.md")
    assert os.path.exists(guide_path)
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()

    # All 17 parameters created in create_user_parameters must be documented
    expected_params = [
        "BaySpacing",
        "FrameHeight",
        "TrussHeight",
        "TrussWidth",
        "SlotWidth",
        "SlotDepth",
        "PanelThickness",
        "PanelWidth",
        "PanelHeight",
        "LatticePitch",
        "LatticeStrut",
        "TolDovetail",
        "TolTenon",
        "PinDiameter",
        "DovetailBaseWidth",
        "DovetailDepth",
        "DovetailAngle",
    ]

    for param in expected_params:
        assert f"`{param}`" in content or param in content, f"Parameter {param} not found in CAD guide"


def test_cad_guide_covers_all_components():
    guide_path = os.path.join("docs", "cad_modeling_guide.md")
    assert os.path.exists(guide_path)
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()

    expected_components = [
        "FT_Segment_12in",
        "VR_Post_Deep",
        "HR_Rail_12in",
        "J_Corner_90",
        "J_Tee_3Way",
        "J_Cross_4Way",
        "DIV_Crosshatch_12x11",
        "Pin_Lock_M5",
    ]

    for comp in expected_components:
        assert comp in content, f"Component {comp} not documented in CAD guide"


def test_cad_guide_covers_assembly_layouts_and_bom():
    guide_path = os.path.join("docs", "cad_modeling_guide.md")
    assert os.path.exists(guide_path)
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for grid layouts
    assert "1x1" in content or "1×1" in content
    assert "2x1" in content or "2×1" in content
    assert "2x2" in content or "2×2" in content
    assert "2x3" in content or "2×3" in content

    # Check for Bill of Materials / BOM mentions
    assert "Bill of Materials" in content or "BOM" in content

    # Check for Joint assembly methods
    assert "Rigid Joint" in content or "Joint" in content


def test_cad_guide_covers_installation_and_export():
    guide_path = os.path.join("docs", "cad_modeling_guide.md")
    assert os.path.exists(guide_path)
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Installation paths
    assert "Autodesk Fusion 360" in content
    assert "Scripts" in content
    assert "Shift + S" in content or "Shift+S" in content

    # Export formats
    assert "3MF" in content
    assert "STEP" in content
    assert "Creality K2" in content or "K2" in content
