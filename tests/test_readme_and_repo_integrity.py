"""
Automated Repository Integrity & README Test Suite
Tesla Model X (2017) Frunk Modular Divider System

Validates:
- Root README.md existence, length, formatting, and technical coverage.
- All local markdown links and file references resolve to existing files on disk.
- Vehicle (2017 Tesla Model X AWD) and 3D printer (Creality K2 Combo 350x350x350 mm) compatibility.
- Complete 8-component library coverage and 3-tier architecture.
- All 17 parametric CAD variables and alignment with geometry_calc.py.
- Bill of Materials (BOM) for 1x1, 2x1, 2x2, and 2x3 grid configurations with filament weight & print times.
- Visual architecture diagrams (ASCII and Mermaid flowcharts).
- Quick Start workflow (Fusion 360 script, OrcaSlicer/Creality Print, assembly sequence).
- Automotive polymer thermal science (ASA/ABS vs PLA).
- Repository directory structure and submodule importability.
"""

import os
import re
import pytest
from fusion_scripts.geometry_calc import FrunkParameters


README_PATH = "README.md"


@pytest.fixture
def readme_content():
    """Load README.md content."""
    assert os.path.exists(README_PATH), f"Expected {README_PATH} to exist in repo root"
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def test_readme_exists_and_substantial(readme_content):
    """Verify that README.md exists and contains substantial technical depth."""
    assert len(readme_content) > 5000, "README.md is too brief"
    assert "# Tesla Model X Frunk Modular Divider System" in readme_content


def test_readme_all_markdown_file_links_exist(readme_content):
    """
    Extract all markdown links in README.md and verify that
    all relative local filesystem paths exist on disk.
    """
    # Regex to match markdown links: matches [label](path) even when nested or in list items
    link_pattern = r'\]\(([^)\s]+)\)'
    targets = re.findall(link_pattern, readme_content)
    assert len(targets) > 0, "No markdown links found in README.md"

    checked_local_links = []
    for target in targets:
        # Ignore external URLs and internal anchors
        if target.startswith("http://") or target.startswith("https://") or target.startswith("#"):
            continue

        target_clean = target.split("#")[0]
        if not target_clean:
            continue

        normalized_path = os.path.normpath(target_clean)
        assert os.path.exists(normalized_path), (
            f"Broken relative link in README.md: target '{target}' -> '{normalized_path}' not found"
        )
        checked_local_links.append(normalized_path)

    # Ensure multiple core files were checked
    assert len(checked_local_links) >= 8, (
        f"Expected at least 8 local file links checked, found {len(checked_local_links)}: {checked_local_links}"
    )
    assert any("cad_modeling_guide.md" in p for p in checked_local_links)
    assert any("3d_printing_and_slicing_guide.md" in p for p in checked_local_links)
    assert any("generate_modelx_frunk_dividers.py" in p for p in checked_local_links)
    assert any("geometry_calc.py" in p for p in checked_local_links)
    assert any("LICENSE" in p for p in checked_local_links)


def test_readme_covers_vehicle_and_printer_compatibility(readme_content):
    """Verify Tesla Model X frunk tub and Creality K2 printer specifications."""
    # Vehicle specifications
    assert "Tesla" in readme_content
    assert "Model X" in readme_content
    assert "2017" in readme_content
    assert "AWD" in readme_content or "tub" in readme_content.lower()
    assert "frunk" in readme_content.lower()

    # 3D Printer specifications
    assert "Creality K2" in readme_content
    assert "350" in readme_content and ("350 × 350" in readme_content or "350x350" in readme_content or "350×350×350" in readme_content)
    assert "chamber" in readme_content.lower() or "enclosure" in readme_content.lower()


def test_readme_covers_all_components(readme_content):
    """Verify that all 8 distinct modular system components are documented."""
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
        assert comp in readme_content, f"Component {comp} missing from README.md"


def test_readme_covers_all_parameters(readme_content):
    """Verify that all 17 parametric CAD variables are listed in README.md."""
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
        assert param in readme_content, f"Parameter {param} not found in README.md"


def test_readme_covers_bom_and_grid_layouts(readme_content):
    """Verify Bill of Materials for standard configurations and manufacturing metrics."""
    # Standard grid configurations
    assert "1×1" in readme_content or "1x1" in readme_content
    assert "2×1" in readme_content or "2x1" in readme_content
    assert "2×2" in readme_content or "2x2" in readme_content
    assert "2×3" in readme_content or "2x3" in readme_content

    # Bill of Materials / Manufacturing metrics
    assert "Bill of Materials" in readme_content or "BOM" in readme_content
    assert "ASA" in readme_content
    assert "Weight" in readme_content or "weight" in readme_content
    assert "Print Time" in readme_content or "print time" in readme_content.lower()


def test_readme_covers_visual_diagrams(readme_content):
    """Verify ASCII architecture and Mermaid diagram integration."""
    # ASCII diagram elements
    assert "+=============================================================================+" in readme_content
    assert "HR_Rail" in readme_content
    assert "FT_Segment" in readme_content

    # Mermaid diagram element
    assert "```mermaid" in readme_content
    assert "graph TD" in readme_content or "graph LR" in readme_content or "flowchart" in readme_content


def test_readme_covers_quickstart_and_materials(readme_content):
    """Verify Fusion 360 script run guide, slicer profiles, and material science."""
    # Fusion 360 workflow
    assert "generate_modelx_frunk_dividers.py" in readme_content
    assert "Autodesk Fusion 360" in readme_content
    assert "Shift" in readme_content and "S" in readme_content

    # Slicer instructions
    assert "OrcaSlicer" in readme_content or "Creality Print" in readme_content

    # Materials
    assert "ASA" in readme_content
    assert "ABS" in readme_content
    assert "PETG" in readme_content
    assert "PLA" in readme_content
    assert any(t in readme_content for t in ["55°C", "60°C", "70°C", "105°C"])


def test_geometry_calc_parameter_values_match_code():
    """Verify FrunkParameters defaults match documented specifications."""
    params = FrunkParameters()
    assert params.bay_spacing_mm == 304.8
    assert params.frame_height_mm == 280.0
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


def test_repo_directory_structure_integrity():
    """Verify that all core directories and files in the repository exist."""
    required_paths = [
        "README.md",
        "LICENSE",
        "pytest.ini",
        os.path.join("docs", "cad_modeling_guide.md"),
        os.path.join("docs", "3d_printing_and_slicing_guide.md"),
        os.path.join("fusion_scripts", "__init__.py"),
        os.path.join("fusion_scripts", "geometry_calc.py"),
        os.path.join("fusion_scripts", "generate_modelx_frunk_dividers.py"),
        os.path.join("tests", "test_geometry_calc.py"),
        os.path.join("tests", "test_fusion_script_syntax.py"),
        os.path.join("tests", "test_cad_modeling_guide.py"),
        os.path.join("tests", "test_printing_guide.py"),
        os.path.join("tests", "test_readme_and_repo_integrity.py"),
    ]

    for path in required_paths:
        assert os.path.exists(path), f"Required repository file missing: {path}"
        assert os.path.getsize(path) > 0, f"Repository file is empty: {path}"
