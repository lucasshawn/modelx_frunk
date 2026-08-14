"""
Unit and syntax tests for Fusion 360 automation script.
Validates AST structure, parameter generation, component builders, and headless dry-run execution.
"""

import ast
import os
import pytest
from fusion_scripts.geometry_calc import FrunkParameters


def test_script_syntax_and_ast():
    """Verify script exists, parses without syntax errors, and defines all required API functions."""
    script_path = os.path.join("fusion_scripts", "generate_modelx_frunk_dividers.py")
    assert os.path.exists(script_path), f"File {script_path} does not exist"
    
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    tree = ast.parse(code)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    required_functions = [
        "run",
        "create_user_parameters",
        "build_floor_truss_component",
        "build_vertical_rib_component",
        "build_horizontal_rail_component",
        "build_junction_components",
        "build_divider_panel_component",
        "build_locking_pin_component",
    ]
    
    for fn in required_functions:
        assert fn in func_names, f"Missing required function '{fn}' in {script_path}"


def test_module_import_and_exports():
    """Verify the module can be cleanly imported in standalone Python environments."""
    import fusion_scripts.generate_modelx_frunk_dividers as fscript
    
    assert hasattr(fscript, "run")
    assert hasattr(fscript, "create_user_parameters")
    assert hasattr(fscript, "build_floor_truss_component")
    assert hasattr(fscript, "build_vertical_rib_component")
    assert hasattr(fscript, "build_horizontal_rail_component")
    assert hasattr(fscript, "build_junction_components")
    assert hasattr(fscript, "build_divider_panel_component")
    assert hasattr(fscript, "build_locking_pin_component")


def test_create_user_parameters_mock():
    """Verify create_user_parameters adds all required parametric dimensions."""
    from fusion_scripts.generate_modelx_frunk_dividers import create_user_parameters
    
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
                "comment": comment
            }
            return self.params[name]
            
    class MockDesign:
        def __init__(self):
            self.userParameters = MockUserParameters()
            
    design = MockDesign()
    params = FrunkParameters()
    result = create_user_parameters(design, params)
    
    assert result is not None
    param_names = design.userParameters.params.keys()
    
    expected_params = [
        "BaySpacing",
        "FrameHeight",
        "TrussHeight",
        "TrussWidth",
        "SlotWidth",
        "SlotDepth",
        "PanelThickness",
        "TolDovetail",
        "TolTenon",
        "PinDiameter",
    ]
    for p in expected_params:
        assert p in param_names, f"Expected parameter '{p}' was not added to design"


def test_component_builders_mock():
    """Verify each component builder executes cleanly with mock/standalone root component."""
    import fusion_scripts.generate_modelx_frunk_dividers as fscript
    
    class MockOccurrences:
        def __init__(self):
            self.occurrences = []
            
        def addNewComponent(self, transform):
            comp = MockComponent()
            occ = MockOccurrence(comp)
            self.occurrences.append(occ)
            return occ
            
    class MockOccurrence:
        def __init__(self, component):
            self.component = component
            
    class MockComponent:
        def __init__(self, name="MockComp"):
            self.name = name
            self.occurrences = MockOccurrences()
            self.sketches = MockSketches()
            self.features = MockFeatures()
            
    class MockSketches:
        def add(self, plane):
            return MockSketch()
            
    class MockSketch:
        def __init__(self):
            self.sketchCurves = MockSketchCurves()
            self.profiles = [MockProfile()]
            
    class MockSketchCurves:
        def __init__(self):
            self.sketchLines = MockSketchLines()
            self.sketchCircles = MockSketchCircles()
            
    class MockSketchLines:
        def addByTwoPoints(self, pt1, pt2):
            return None
        def addTwoPointRectangle(self, pt1, pt2):
            return None
            
    class MockSketchCircles:
        def addByCenterRadius(self, pt, radius):
            return None
            
    class MockProfile:
        pass
        
    class MockFeatures:
        def __init__(self):
            self.extrudeFeatures = MockExtrudeFeatures()
            
    class MockExtrudeFeatures:
        def addSimple(self, profile, distance, operation):
            return None
        def createInput(self, profile, operation):
            return MockExtrudeInput()
        def add(self, extrude_input):
            return None
            
    class MockExtrudeInput:
        def setDistanceExtent(self, is_symmetric, distance):
            pass
            
    root_comp = MockComponent("RootComponent")
    params = FrunkParameters()
    
    # 1. Floor truss
    ft = fscript.build_floor_truss_component(root_comp, params)
    assert ft is not None
    
    # 2. Vertical rib
    vr = fscript.build_vertical_rib_component(root_comp, params)
    assert vr is not None
    
    # 3. Horizontal rail
    hr = fscript.build_horizontal_rail_component(root_comp, params)
    assert hr is not None
    
    # 4. Junctions
    juncs = fscript.build_junction_components(root_comp, params)
    assert isinstance(juncs, (list, tuple, dict))
    
    # 5. Divider panel
    div = fscript.build_divider_panel_component(root_comp, params)
    assert div is not None
    
    # 6. Locking pin
    pin = fscript.build_locking_pin_component(root_comp, params)
    assert pin is not None


def test_run_standalone_execution(capsys):
    """Verify run(context=None) executes safely in standalone mode without raising unhandled errors."""
    import fusion_scripts.generate_modelx_frunk_dividers as fscript
    
    # Executing run outside Fusion 360 should detect headless/standalone environment gracefully
    fscript.run(context=None)
    captured = capsys.readouterr()
    assert "Tesla Model X" in captured.out or "Standalone" in captured.out or "Fusion 360" in captured.out
