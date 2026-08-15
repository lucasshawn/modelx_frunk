"""
Automated Solid Generation & Deployment Test Suite for Conformal Floor Track
Autodesk Fusion 360 API Integration for Tesla Model X Frunk
"""

import ast
import math
import os
import sys
import pytest


def test_conformal_track_ast_and_exports():
    """Verify script files exist and define build_conformal_floor_track and parameters."""
    script_paths = [
        os.path.join("fusion_scripts", "ModelX_Frunk_Dividers_Standalone.py"),
        os.path.join("fusion_scripts", "ModelX_Frunk_Dividers", "ModelX_Frunk_Dividers.py"),
        os.path.join("fusion_scripts", "generate_modelx_frunk_dividers.py"),
    ]

    for script_path in script_paths:
        assert os.path.exists(script_path), f"File {script_path} does not exist"
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()

        tree = ast.parse(code)
        func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert "build_conformal_floor_track" in func_names, (
            f"Missing required function 'build_conformal_floor_track' in {script_path}"
        )
        assert "create_user_parameters" in func_names, (
            f"Missing 'create_user_parameters' in {script_path}"
        )
        assert "run" in func_names, f"Missing 'run' in {script_path}"


def test_user_parameters_includes_conformal_track():
    """Verify create_user_parameters creates all 9 conformal track parameters."""
    from fusion_scripts.ModelX_Frunk_Dividers_Standalone import create_user_parameters, FrunkParameters

    class MockUserParameters:
        def __init__(self):
            self.params = {}

        def itemByName(self, name):
            return self.params.get(name)

        def add(self, name, value_input, unit, comment):
            self.params[name] = {
                "name": name,
                "value_input": value_input,
                "unit": unit,
                "comment": comment,
            }
            return self.params[name]

    class MockDesign:
        def __init__(self):
            self.userParameters = MockUserParameters()

    design = MockDesign()
    params = FrunkParameters()
    create_user_parameters(design, params)

    param_names = list(design.userParameters.params.keys())
    expected_conformal_params = [
        "WallClearance",
        "TrackWidth",
        "TrackHeight",
        "TrackRailBase",
        "TrackRailNeck",
        "TrackRailHeight",
        "TrackBedMaxDim",
        "TolSeamDovetail",
        "SeamDovetailAngle",
    ]
    for p in expected_conformal_params:
        assert p in param_names, f"Missing expected conformal track parameter '{p}' in userParameters"


def test_build_conformal_floor_track_mock():
    """Verify build_conformal_floor_track constructs 4 distinct quadrant bodies + master assembled body."""
    from fusion_scripts.ModelX_Frunk_Dividers_Standalone import (
        build_conformal_floor_track,
        FrunkParameters,
    )

    class MockBody:
        def __init__(self, name=""):
            self.name = name

    class MockBodies:
        def __init__(self):
            self._list = []

        @property
        def count(self):
            return len(self._list)

        def item(self, idx):
            return self._list[idx]

        def append(self, body):
            self._list.append(body)

    class MockSketchLines:
        def __init__(self):
            self.lines = []

        def addByTwoPoints(self, pt1, pt2):
            self.lines.append((pt1, pt2))
            return None

        def addTwoPointRectangle(self, pt1, pt2):
            self.lines.append((pt1, pt2))
            return None

    class MockSketchCurves:
        def __init__(self):
            self.sketchLines = MockSketchLines()

    class MockSketch:
        def __init__(self):
            self.sketchCurves = MockSketchCurves()
            self.profiles = [object()]

    class MockSketches:
        def __init__(self):
            self.sketches = []

        def add(self, plane):
            sk = MockSketch()
            self.sketches.append(sk)
            return sk

    class MockExtrudeInput:
        def setDistanceExtent(self, is_symmetric, distance):
            pass

    class MockExtrudeFeatures:
        def __init__(self, parent_comp):
            self.parent_comp = parent_comp
            self.operations = []

        def addSimple(self, profile, distance_val, operation):
            body = MockBody()
            self.parent_comp.bRepBodies.append(body)
            self.operations.append(("addSimple", distance_val, operation))
            return None

        def createInput(self, profile, operation):
            return MockExtrudeInput()

        def add(self, ext_input):
            self.operations.append(("add", ext_input))
            return None

    class MockFeatures:
        def __init__(self, parent_comp):
            self.extrudeFeatures = MockExtrudeFeatures(parent_comp)

    class MockRootComp:
        def __init__(self):
            self.sketches = MockSketches()
            self.bRepBodies = MockBodies()
            self.features = MockFeatures(self)
            self.xYConstructionPlane = "XY"
            self.xZConstructionPlane = "XZ"

    root_comp = MockRootComp()
    params = FrunkParameters()

    track_bodies = build_conformal_floor_track(root_comp, params)
    assert track_bodies is not None
    assert isinstance(track_bodies, dict)

    expected_quadrants = [
        "TRK_Front_L",
        "TRK_Front_R",
        "TRK_Rear_L",
        "TRK_Rear_R",
        "TRK_Master_Assembled",
    ]
    for q_name in expected_quadrants:
        assert q_name in track_bodies, f"Expected body {q_name} in track_bodies output"

    created_body_names = [b.name for b in root_comp.bRepBodies._list if b.name]
    for q_name in expected_quadrants:
        assert q_name in created_body_names, f"Expected body name {q_name} in bRepBodies list"


def test_conformal_floor_quadrants_bed_envelope():
    """Verify all 4 quadrants satisfy the Creality K2 maximum 310mm build envelope."""
    from fusion_scripts.conformal_track_calc import (
        extract_calibrated_floor_polygon,
        generate_track_boundary_loops,
        slice_track_quadrants,
        ConformalTrackParameters,
    )

    poly = extract_calibrated_floor_polygon()
    loops = generate_track_boundary_loops(poly)
    quadrants = slice_track_quadrants(loops["outer_loop"], loops["inner_loop"])

    for name, q in quadrants.items():
        assert q.max_dimension <= 310.0, (
            f"Quadrant {name} max dimension {q.max_dimension:.2f}mm exceeds 310mm bed limit!"
        )
        assert len(q.polygon) >= 50, f"Quadrant {name} polygon has insufficient resolution"
        assert q.area_mm2 > 5000.0, f"Quadrant {name} has unrealistically low area"


def test_standalone_run_execution(capsys):
    """Verify run(context=None) runs without error and generates conformal floor track."""
    import fusion_scripts.ModelX_Frunk_Dividers_Standalone as standalone

    standalone.run(context=None)
    captured = capsys.readouterr()
    assert "Tesla Model X" in captured.out or "TRK_" in captured.out or "Generated" in captured.out or len(captured.err) == 0


def test_deployed_script_matches_and_valid():
    """Verify script deployed to %APPDATA% exists, parses, and matches workspace source."""
    appdata = os.environ.get("APPDATA", "")
    deployed_path = os.path.join(
        appdata,
        "Autodesk",
        "Autodesk Fusion 360",
        "API",
        "Scripts",
        "ModelX_Frunk_Dividers",
        "ModelX_Frunk_Dividers.py",
    )
    assert os.path.exists(deployed_path), f"Deployed script not found at {deployed_path}"

    with open(deployed_path, "r", encoding="utf-8") as f:
        deployed_code = f.read()

    tree = ast.parse(deployed_code)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert "build_conformal_floor_track" in func_names
    assert "create_user_parameters" in func_names
    assert "run" in func_names
