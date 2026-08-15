"""
Unit tests for Creality K2 3D Printing, Infill & Slicing Guide.
Verifies file existence, material selection criteria, slicer parameter coverage,
Creality K2 hardware profiles, print orientation strategies, assembly instructions,
and Tesla Model X frunk installation procedures.
"""

import os
import pytest


GUIDE_PATH = os.path.join("docs", "3d_printing_and_slicing_guide.md")


@pytest.fixture
def guide_content():
    """Fixture to load the 3D printing and slicing guide content."""
    assert os.path.exists(GUIDE_PATH), f"Expected {GUIDE_PATH} to exist"
    with open(GUIDE_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def test_printing_guide_exists_and_substantial(guide_content):
    """Verify that the guide file exists and has comprehensive technical depth."""
    assert len(guide_content) > 5000, "3D printing and slicing guide content is too brief"
    assert "Creality K2" in guide_content
    assert "Tesla Model X" in guide_content


def test_material_selection_and_thermal_comparison(guide_content):
    """
    Verify material comparison covers ASA, ABS, PETG, and PLA,
    specifically addressing automotive thermal conditions (55°C - 70°C).
    """
    # Materials required
    assert "ASA" in guide_content
    assert "ABS" in guide_content
    assert "PETG" in guide_content
    assert "PLA" in guide_content

    # Thermal properties
    assert "Glass Transition" in guide_content or "Tg" in guide_content
    assert "Heat Deflection" in guide_content or "HDT" in guide_content
    assert "UV" in guide_content

    # Check vehicle frunk thermal context (PLA failure explanation)
    assert any(temp in guide_content for temp in ["55°C", "60°C", "65°C", "70°C"])
    assert "creep" in guide_content.lower() or "warp" in guide_content.lower() or "deform" in guide_content.lower()


def test_slicer_infill_and_wall_strategy(guide_content):
    """
    Verify infill patterns and wall thicknesses for structural vs divider components.
    """
    # Wall/perimeter settings (4 perimeters / walls, 1.6 mm shell)
    assert "4 perimeters" in guide_content or "4 walls" in guide_content or "4 Walls" in guide_content or "4 Perimeters" in guide_content
    assert "1.6" in guide_content or "1.6 mm" in guide_content or "1.6mm" in guide_content

    # Structural infill (30% Hexagonal or Gyroid)
    assert "30%" in guide_content
    assert "Gyroid" in guide_content or "Hexagonal" in guide_content

    # Divider panels (100% solid struts / no sparse infill inside thin struts)
    assert "100%" in guide_content
    assert "strut" in guide_content.lower() or "lattice" in guide_content.lower()

    # Top/Bottom solid layers
    assert "top" in guide_content.lower() and "bottom" in guide_content.lower()


def test_creality_k2_specific_slicer_settings(guide_content):
    """
    Verify Creality K2 Combo specific parameters:
    - 350x350x350 mm build volume
    - Active chamber heating
    - Extruder/Bed temperatures
    - Cooling and fan control
    - Volumetric flow rate & acceleration
    """
    # Build volume
    assert "350" in guide_content and ("350 x 350" in guide_content or "350×350" in guide_content or "350mm" in guide_content or "350 mm" in guide_content)

    # Chamber heater / enclosure
    assert "Chamber" in guide_content or "chamber" in guide_content

    # Temperature parameters
    assert "Nozzle" in guide_content or "Extruder" in guide_content or "Print Temperature" in guide_content
    assert "Bed Temperature" in guide_content or "Bed Temp" in guide_content

    # Slicer profiles (OrcaSlicer / Creality Print)
    assert "OrcaSlicer" in guide_content or "Creality Print" in guide_content

    # Speed / Flow / Acceleration
    assert "Acceleration" in guide_content or "acceleration" in guide_content
    assert "Volumetric" in guide_content or "Flow Rate" in guide_content or "mm³/s" in guide_content or "mm3/s" in guide_content


def test_print_bed_orientation_and_layout_matrix(guide_content):
    """
    Verify orientation guidance for all modular system components
    to maximize layer adhesion and mechanical strength.
    """
    components = [
        "FT_Segment_12in",
        "VR_Post_Deep",
        "HR_Rail_12in",
        "J_Corner_90",
        "J_Tee_3Way",
        "J_Cross_4Way",
        "DIV_Crosshatch_12x11",
        "Pin_Lock_M5",
        "TRK_Front_L",
        "TRK_Front_R",
        "TRK_Rear_L",
        "TRK_Rear_R",
    ]

    for comp in components:
        assert comp in guide_content, f"Component {comp} must be detailed in the print orientation matrix"

    # Support-free 45-degree angle rationale
    assert "45" in guide_content
    assert "support" in guide_content.lower()


def test_dimensional_tolerances_and_tuning(guide_content):
    """
    Verify horizontal expansion, shrinkage compensation, and fit calibration.
    """
    assert "Horizontal Expansion" in guide_content or "XY Size Compensation" in guide_content or "tolerance" in guide_content.lower()
    assert "Dovetail" in guide_content or "dovetail" in guide_content
    assert "Shrinkage" in guide_content or "shrinkage" in guide_content or "Scaling" in guide_content or "scaling" in guide_content


def test_assembly_and_modelx_frunk_installation(guide_content):
    """
    Verify step-by-step assembly instructions and Model X frunk tub placement.
    """
    # Assembly sequence
    assert "Assembly" in guide_content or "assembly" in guide_content
    assert "Locking Pin" in guide_content or "Pin_Lock_M5" in guide_content or "pin" in guide_content.lower()

    # Model X frunk tub
    assert "2017" in guide_content
    assert "Model X" in guide_content
    assert "Frunk" in guide_content or "frunk" in guide_content
    assert "Carpet" in guide_content or "carpet" in guide_content or "tub" in guide_content.lower()
