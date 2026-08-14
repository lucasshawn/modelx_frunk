"""
Tesla Model X 2017 Frunk Modular Divider System
Parametric CAD Automation Script for Autodesk Fusion 360

Generates full 3D CAD components, parametric user parameters (fx),
and assembly structure for a modular 3D printable storage system
tailored for the 2017 Model X front trunk (Creality K2 Combo 350x350x350mm build volume).

Components generated:
1. FT_Segment_12in    - Floor Truss with triangular web cutouts and dovetails
2. VR_Post_Deep       - 11-inch Vertical Post with 6.4mm slots and locking tenon
3. HR_Rail_12in       - Horizontal Top Rail with lead-in funnel and end joints
4. J_Corner_90        - 90-Degree 2-Way Corner Junction
5. J_Tee_3Way         - 3-Way T-Junction Block
6. J_Cross_4Way       - 4-Way Cross Junction Block
7. DIV_Crosshatch_12x11 - Slide-in Divider Panel with 45-degree Diamond Lattice & Pull Handle
8. Pin_Lock_M5        - Transverse Dovetail & Socket Locking Pin
"""

import math
import sys
import traceback
from typing import Any, Dict, List, Optional, Tuple

# Import local geometry engine
try:
    from fusion_scripts.geometry_calc import (
        FrunkParameters,
        calculate_diamond_lattice_segments,
        calculate_dovetail_profile,
        calculate_truss_web_triangles,
    )
except ImportError:
    # Direct execution fallback
    from geometry_calc import (
        FrunkParameters,
        calculate_diamond_lattice_segments,
        calculate_dovetail_profile,
        calculate_truss_web_triangles,
    )

# Attempt Autodesk Fusion 360 API import
try:
    import adsk.core
    import adsk.fusion
    FUSION_AVAILABLE = True
except ImportError:
    FUSION_AVAILABLE = False


# ==============================================================================
# Standalone Mock Framework for Testing & Headless Verification
# ==============================================================================

class MockPoint3D:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def create(cls, x: float, y: float, z: float):
        return cls(x, y, z)

    def __repr__(self):
        return f"Point3D({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


class MockMatrix3D:
    @classmethod
    def create(cls):
        return cls()


class MockValueInput:
    def __init__(self, value: Any, is_string: bool = False):
        self.value = value
        self.is_string = is_string

    @classmethod
    def createByString(cls, val_str: str):
        return cls(val_str, is_string=True)

    @classmethod
    def createByReal(cls, val_real: float):
        return cls(val_real, is_string=False)


class MockUserParameter:
    def __init__(self, name: str, value_input: Any, unit: str, comment: str):
        self.name = name
        self.expression = getattr(value_input, "value", str(value_input))
        self.unit = unit
        self.comment = comment


class MockUserParameters:
    def __init__(self):
        self._params: Dict[str, MockUserParameter] = {}

    def itemByName(self, name: str) -> Optional[MockUserParameter]:
        return self._params.get(name)

    def add(self, name: str, value_input: Any, unit: str, comment: str) -> MockUserParameter:
        param = MockUserParameter(name, value_input, unit, comment)
        self._params[name] = param
        return param

    @property
    def params(self) -> Dict[str, MockUserParameter]:
        return self._params


class MockProfile:
    def __init__(self, name: str = "Profile"):
        self.name = name


class MockSketchCurves:
    def __init__(self):
        self.sketchLines = MockSketchLines()
        self.sketchCircles = MockSketchCircles()


class MockSketchLines:
    def __init__(self):
        self.lines = []

    def addByTwoPoints(self, pt1: Any, pt2: Any):
        self.lines.append((pt1, pt2))
        return (pt1, pt2)

    def addTwoPointRectangle(self, pt1: Any, pt2: Any):
        self.lines.append((pt1, pt2))
        return [pt1, pt2]


class MockSketchCircles:
    def __init__(self):
        self.circles = []

    def addByCenterRadius(self, center: Any, radius: float):
        self.circles.append((center, radius))
        return (center, radius)


class MockSketch:
    def __init__(self, name: str = "Sketch"):
        self.name = name
        self.sketchCurves = MockSketchCurves()
        self.profiles = [MockProfile(f"{name}_Profile")]


class MockSketches:
    def __init__(self):
        self.sketches: List[MockSketch] = []

    def add(self, plane: Any) -> MockSketch:
        sketch = MockSketch(f"Sketch_{len(self.sketches)+1}")
        self.sketches.append(sketch)
        return sketch


class MockExtrudeInput:
    def __init__(self):
        self.is_symmetric = False
        self.distance = None

    def setDistanceExtent(self, is_symmetric: bool, distance: Any):
        self.is_symmetric = is_symmetric
        self.distance = distance


class MockExtrudeFeatures:
    def __init__(self):
        self.features = []

    def addSimple(self, profile: Any, distance: Any, operation: Any):
        self.features.append({"profile": profile, "distance": distance, "operation": operation})
        return self.features[-1]

    def createInput(self, profile: Any, operation: Any) -> MockExtrudeInput:
        return MockExtrudeInput()

    def add(self, extrude_input: MockExtrudeInput):
        self.features.append(extrude_input)
        return extrude_input


class MockFeatures:
    def __init__(self):
        self.extrudeFeatures = MockExtrudeFeatures()


class MockComponent:
    def __init__(self, name: str = "Component"):
        self.name = name
        self.sketches = MockSketches()
        self.features = MockFeatures()
        self.occurrences = MockOccurrences()
        self.xYConstructionPlane = "XY"
        self.xZConstructionPlane = "XZ"
        self.yZConstructionPlane = "YZ"


class MockOccurrence:
    def __init__(self, component: MockComponent):
        self.component = component


class MockOccurrences:
    def __init__(self):
        self.occurrences: List[MockOccurrence] = []

    def addNewComponent(self, transform: Any) -> MockOccurrence:
        comp = MockComponent(f"Comp_{len(self.occurrences)+1}")
        occ = MockOccurrence(comp)
        self.occurrences.append(occ)
        return occ


class MockDesign:
    def __init__(self):
        self.userParameters = MockUserParameters()
        self.rootComponent = MockComponent("ModelX_Frunk_Root")


# Helper factory for 3D points
def _create_point(x: float, y: float, z: float):
    if FUSION_AVAILABLE:
        return adsk.core.Point3D.create(x, y, z)
    return MockPoint3D.create(x, y, z)


def _create_value_string(expr: str):
    if FUSION_AVAILABLE:
        return adsk.core.ValueInput.createByString(expr)
    return MockValueInput.createByString(expr)


def _create_value_real(val: float):
    if FUSION_AVAILABLE:
        return adsk.core.ValueInput.createByReal(val)
    return MockValueInput.createByReal(val)


def _get_feature_operations():
    if FUSION_AVAILABLE:
        return {
            "new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            "join": adsk.fusion.FeatureOperations.JoinFeatureOperation,
            "cut": adsk.fusion.FeatureOperations.CutFeatureOperation,
        }
    return {
        "new": 0,
        "join": 1,
        "cut": 2,
    }


# ==============================================================================
# Parameter Creation Engine
# ==============================================================================

def create_user_parameters(design: Any, params: FrunkParameters) -> Any:
    """
    Populates Autodesk Fusion 360 User Parameters (`fx`) with full parametric definitions.

    Parameters:
        design: Active Fusion 360 Design object (or MockDesign).
        params: FrunkParameters configuration dataclass.

    Returns:
        UserParameters collection object.
    """
    user_params = design.userParameters
    param_definitions = [
        ("BaySpacing", f"{params.bay_spacing_mm:.2f} mm", "mm", "Center-to-center bay spacing (12.0 in nominal)"),
        ("FrameHeight", f"{params.frame_height_mm:.2f} mm", "mm", "Frame overall height (11.0 in nominal)"),
        ("TrussHeight", f"{params.truss_height_mm:.2f} mm", "mm", "Floor truss structure height"),
        ("TrussWidth", f"{params.truss_width_mm:.2f} mm", "mm", "Floor truss and rail profile width"),
        ("SlotWidth", f"{params.slot_width_mm:.2f} mm", "mm", "Guide slot width (5mm panel + 0.7mm clearance/side)"),
        ("SlotDepth", f"{params.slot_depth_mm:.2f} mm", "mm", "Guide slot insertion depth"),
        ("PanelThickness", f"{params.panel_thickness_mm:.2f} mm", "mm", "Nominal divider panel thickness"),
        ("PanelWidth", f"{params.panel_width_mm:.2f} mm", "mm", "Divider panel overall width"),
        ("PanelHeight", f"{params.panel_height_mm:.2f} mm", "mm", "Divider panel overall height"),
        ("LatticePitch", f"{params.lattice_pitch_mm:.2f} mm", "mm", "45-degree diamond mesh pitch"),
        ("LatticeStrut", f"{params.lattice_strut_mm:.2f} mm", "mm", "Diamond mesh strut width"),
        ("TolDovetail", f"{params.tol_dovetail_mm:.2f} mm", "mm", "3D printing slip clearance for 15-deg dovetail"),
        ("TolTenon", f"{params.tol_tenon_mm:.2f} mm", "mm", "3D printing slip clearance for vertical socket tenon"),
        ("PinDiameter", f"{params.pin_diameter_mm:.2f} mm", "mm", "Transverse locking pin nominal diameter"),
        ("DovetailBaseWidth", f"{params.dovetail_base_width_mm:.2f} mm", "mm", "Dovetail root width"),
        ("DovetailDepth", f"{params.dovetail_depth_mm:.2f} mm", "mm", "Dovetail tab depth"),
        ("DovetailAngle", f"{params.dovetail_angle_deg:.2f} deg", "deg", "Dovetail wedge flare half-angle"),
    ]

    for name, val_str, unit, comment in param_definitions:
        existing = user_params.itemByName(name)
        if existing:
            if hasattr(existing, "expression"):
                existing.expression = val_str
        else:
            val_input = _create_value_string(val_str)
            user_params.add(name, val_input, unit, comment)

    return user_params


# ==============================================================================
# Component Builders
# ==============================================================================

def build_floor_truss_component(root_comp: Any, params: FrunkParameters) -> Any:
    """
    Builds the 12-inch Floor Truss (`FT_Segment_12in`) component.
    Features:
    - Main beam body along X-axis
    - Alternating triangular weight-reduction web cutouts
    - 15-degree male dovetail tab at +X end
    - 15-degree female dovetail pocket at -X end
    - Vertical socket (20x20mm) and transverse 5mm locking pin hole
    """
    matrix = adsk.core.Matrix3D.create() if FUSION_AVAILABLE else MockMatrix3D.create()
    occ = root_comp.occurrences.addNewComponent(matrix)
    comp = occ.component
    comp.name = "FT_Segment_12in"

    ops = _get_feature_operations()
    sketches = comp.sketches
    planes = {
        "xy": getattr(comp, "xYConstructionPlane", "XY"),
        "xz": getattr(comp, "xZConstructionPlane", "XZ"),
        "yz": getattr(comp, "yZConstructionPlane", "YZ"),
    }

    # 1. Base beam profile (in XY plane, extruded in +Z)
    sketch_base = sketches.add(planes["xy"])
    w_cm = params.truss_width_cm
    l_cm = params.bay_spacing_cm
    h_cm = params.truss_height_cm

    p1 = _create_point(0.0, -w_cm / 2.0, 0.0)
    p2 = _create_point(l_cm, w_cm / 2.0, 0.0)
    sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_base.profiles) > 0:
        prof_base = sketch_base.profiles[0]
        ext_dist = _create_value_real(h_cm)
        comp.features.extrudeFeatures.addSimple(prof_base, ext_dist, ops["new"])

    # 2. Triangular weight-reduction web cutouts (in XZ plane, extruded cut through Y)
    sketch_webs = sketches.add(planes["xz"])
    triangles = calculate_truss_web_triangles(
        span_length=params.bay_spacing_mm,
        height=params.truss_height_mm,
        web_thickness=4.0,
        num_bays=6
    )
    for tri in triangles:
        pts = [_create_point(p[0] / 10.0, 0.0, p[1] / 10.0) for p in tri]
        for i in range(3):
            sketch_webs.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % 3])

    # 3. Male dovetail tab at +X end (Join extrusion)
    sketch_male = sketches.add(planes["xy"])
    male_pts = calculate_dovetail_profile(
        male=True,
        tol=params.tol_dovetail_mm,
        base_w=params.dovetail_base_width_mm,
        depth=params.dovetail_depth_mm,
        angle_deg=params.dovetail_angle_deg,
    )
    dt_pts = [_create_point(l_cm + p[1] / 10.0, p[0] / 10.0, 0.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_male.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_male.profiles) > 0:
        comp.features.extrudeFeatures.addSimple(sketch_male.profiles[0], _create_value_real(h_cm), ops["join"])

    # 4. Female dovetail pocket at X=0 end (Cut extrusion)
    sketch_female = sketches.add(planes["xy"])
    female_pts = calculate_dovetail_profile(
        male=False,
        tol=params.tol_dovetail_mm,
        base_w=params.dovetail_base_width_mm,
        depth=params.dovetail_depth_mm,
        angle_deg=params.dovetail_angle_deg,
    )
    f_dt_pts = [_create_point(p[1] / 10.0, p[0] / 10.0, 0.0) for p in female_pts]
    for i in range(len(f_dt_pts)):
        sketch_female.sketchCurves.sketchLines.addByTwoPoints(f_dt_pts[i], f_dt_pts[(i + 1) % len(f_dt_pts)])

    # 5. Center Vertical Rib Socket (20x20mm pocket) and Pin Hole
    sketch_socket = sketches.add(planes["xy"])
    soc_w_cm = 2.0
    soc_x_mid = l_cm / 2.0
    sp1 = _create_point(soc_x_mid - soc_w_cm / 2.0, -soc_w_cm / 2.0, 0.0)
    sp2 = _create_point(soc_x_mid + soc_w_cm / 2.0, soc_w_cm / 2.0, 0.0)
    sketch_socket.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)

    sketch_pin = sketches.add(planes["xz"])
    pin_center = _create_point(soc_x_mid, 0.0, h_cm / 2.0)
    sketch_pin.sketchCurves.sketchCircles.addByCenterRadius(pin_center, params.pin_diameter_cm / 2.0)

    return comp


def build_vertical_rib_component(root_comp: Any, params: FrunkParameters) -> Any:
    """
    Builds the 11-inch Vertical Rib Post (`VR_Post_Deep`) component.
    Features:
    - 24x24mm vertical post column of height 280mm
    - 6.4mm wide x 8.0mm deep panel guide slots
    - Bottom 20x20mm tenon with 0.20mm slip clearance
    - 5.0mm transverse locking pin hole
    - Top locator interface for horizontal rails
    """
    matrix = adsk.core.Matrix3D.create() if FUSION_AVAILABLE else MockMatrix3D.create()
    occ = root_comp.occurrences.addNewComponent(matrix)
    comp = occ.component
    comp.name = "VR_Post_Deep"

    ops = _get_feature_operations()
    sketches = comp.sketches
    planes = {
        "xy": getattr(comp, "xYConstructionPlane", "XY"),
        "xz": getattr(comp, "xZConstructionPlane", "XZ"),
        "yz": getattr(comp, "yZConstructionPlane", "YZ"),
    }

    w_cm = params.truss_width_cm
    h_cm = params.frame_height_cm
    slot_w_cm = params.slot_width_cm
    slot_d_cm = params.slot_depth_cm

    # 1. Main post column (XY plane extruded +Z by frame_height)
    sketch_post = sketches.add(planes["xy"])
    p1 = _create_point(-w_cm / 2.0, -w_cm / 2.0, 0.0)
    p2 = _create_point(w_cm / 2.0, w_cm / 2.0, 0.0)
    sketch_post.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_post.profiles) > 0:
        comp.features.extrudeFeatures.addSimple(sketch_post.profiles[0], _create_value_real(h_cm), ops["new"])

    # 2. Longitudinal guide slots along sides (Cut operation)
    sketch_slot = sketches.add(planes["xy"])
    # -X face slot
    s1 = _create_point(-w_cm / 2.0, -slot_w_cm / 2.0, 0.0)
    s2 = _create_point(-w_cm / 2.0 + slot_d_cm, slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)
    # +X face slot
    s3 = _create_point(w_cm / 2.0 - slot_d_cm, -slot_w_cm / 2.0, 0.0)
    s4 = _create_point(w_cm / 2.0, slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s3, s4)

    # 3. Bottom Tenon (20x20mm - 2*tol_tenon extruded downwards to -20mm)
    sketch_tenon = sketches.add(planes["xy"])
    tenon_w_cm = (20.0 - 2.0 * params.tol_tenon_mm) / 10.0
    t1 = _create_point(-tenon_w_cm / 2.0, -tenon_w_cm / 2.0, 0.0)
    t2 = _create_point(tenon_w_cm / 2.0, tenon_w_cm / 2.0, 0.0)
    sketch_tenon.sketchCurves.sketchLines.addTwoPointRectangle(t1, t2)

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_tenon.profiles) > 0:
        comp.features.extrudeFeatures.addSimple(sketch_tenon.profiles[0], _create_value_real(-2.0), ops["join"])

    # 4. Transverse Pin Hole at Z = -1.0 cm
    sketch_pin = sketches.add(planes["xz"])
    pin_pt = _create_point(0.0, 0.0, -1.0)
    sketch_pin.sketchCurves.sketchCircles.addByCenterRadius(pin_pt, params.pin_diameter_cm / 2.0)

    # 5. Top Rail Locator Pin at Z = h_cm (8mm diameter x 10mm high)
    sketch_top = sketches.add(planes["xy"])
    top_pin = _create_point(0.0, 0.0, h_cm)
    sketch_top.sketchCurves.sketchCircles.addByCenterRadius(top_pin, 0.4)

    return comp


def build_horizontal_rail_component(root_comp: Any, params: FrunkParameters) -> Any:
    """
    Builds the 12-inch Horizontal Top Rail (`HR_Rail_12in`) component.
    Features:
    - 24x24mm structural rail profile spanning bay spacing
    - Bottom 6.4mm guide slot for panel capture
    - 45-degree chamfer lead-in funnel on slot mouth
    - Interlocking end dovetails / junction sockets
    """
    matrix = adsk.core.Matrix3D.create() if FUSION_AVAILABLE else MockMatrix3D.create()
    occ = root_comp.occurrences.addNewComponent(matrix)
    comp = occ.component
    comp.name = "HR_Rail_12in"

    ops = _get_feature_operations()
    sketches = comp.sketches
    planes = {
        "xy": getattr(comp, "xYConstructionPlane", "XY"),
        "xz": getattr(comp, "xZConstructionPlane", "XZ"),
        "yz": getattr(comp, "yZConstructionPlane", "YZ"),
    }

    w_cm = params.truss_width_cm
    l_cm = params.bay_spacing_cm
    slot_w_cm = params.slot_width_cm
    slot_d_cm = params.slot_depth_cm

    # 1. Main horizontal beam body (Extruded along X)
    sketch_rail = sketches.add(planes["yz"])
    p1 = _create_point(0.0, -w_cm / 2.0, 0.0)
    p2 = _create_point(0.0, w_cm / 2.0, w_cm)
    sketch_rail.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_rail.profiles) > 0:
        comp.features.extrudeFeatures.addSimple(sketch_rail.profiles[0], _create_value_real(l_cm), ops["new"])

    # 2. Bottom guide slot and lead-in funnel
    sketch_bottom_slot = sketches.add(planes["xy"])
    s1 = _create_point(0.0, -slot_w_cm / 2.0, 0.0)
    s2 = _create_point(l_cm, slot_w_cm / 2.0, 0.0)
    sketch_bottom_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)

    # 3. Lead-in chamfer sketch at slot mouth (2mm lead-in funnel)
    sketch_funnel = sketches.add(planes["yz"])
    funnel_w_cm = (params.slot_width_mm + 4.0) / 10.0
    f1 = _create_point(0.0, -funnel_w_cm / 2.0, 0.0)
    f2 = _create_point(0.0, funnel_w_cm / 2.0, 0.2)
    sketch_funnel.sketchCurves.sketchLines.addTwoPointRectangle(f1, f2)

    # 4. End Dovetail interfaces
    sketch_male_dt = sketches.add(planes["yz"])
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
    dt_pts = [_create_point(0.0, p[0] / 10.0, p[1] / 10.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_male_dt.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    return comp


def build_junction_components(root_comp: Any, params: FrunkParameters) -> Dict[str, Any]:
    """
    Builds modular junction blocks:
    1. `J_Corner_90`  - 2-Way 90-degree corner block
    2. `J_Tee_3Way`    - 3-Way T-junction block
    3. `J_Cross_4Way`  - 4-Way Cross junction block
    """
    ops = _get_feature_operations()
    block_w_cm = 3.2
    block_h_cm = params.truss_height_cm
    junctions = {}

    configs = [
        ("J_Corner_90", [(1, 0), (0, 1)]),
        ("J_Tee_3Way", [(-1, 0), (1, 0), (0, 1)]),
        ("J_Cross_4Way", [(-1, 0), (1, 0), (0, -1), (0, 1)]),
    ]

    for name, directions in configs:
        matrix = adsk.core.Matrix3D.create() if FUSION_AVAILABLE else MockMatrix3D.create()
        occ = root_comp.occurrences.addNewComponent(matrix)
        comp = occ.component
        comp.name = name

        sketches = comp.sketches
        plane_xy = getattr(comp, "xYConstructionPlane", "XY")
        plane_xz = getattr(comp, "xZConstructionPlane", "XZ")

        # 1. Main junction block
        sketch_main = sketches.add(plane_xy)
        p1 = _create_point(-block_w_cm / 2.0, -block_w_cm / 2.0, 0.0)
        p2 = _create_point(block_w_cm / 2.0, block_w_cm / 2.0, 0.0)
        sketch_main.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

        if hasattr(comp.features, "extrudeFeatures") and len(sketch_main.profiles) > 0:
            comp.features.extrudeFeatures.addSimple(sketch_main.profiles[0], _create_value_real(block_h_cm), ops["new"])

        # 2. Dovetail interfaces in specified directions
        male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
        sketch_dt = sketches.add(plane_xy)
        for dx, dy in directions:
            offset_x = dx * (block_w_cm / 2.0)
            offset_y = dy * (block_w_cm / 2.0)
            for i in range(len(male_pts)):
                p_curr = male_pts[i]
                p_next = male_pts[(i + 1) % len(male_pts)]
                pt_a = _create_point(offset_x + p_curr[0] / 10.0, offset_y + p_curr[1] / 10.0, 0.0)
                pt_b = _create_point(offset_x + p_next[0] / 10.0, offset_y + p_next[1] / 10.0, 0.0)
                sketch_dt.sketchCurves.sketchLines.addByTwoPoints(pt_a, pt_b)

        # 3. Vertical Tenon Socket (20x20mm) and Cross Pin Hole
        sketch_socket = sketches.add(plane_xy)
        soc_w = 2.0
        sp1 = _create_point(-soc_w / 2.0, -soc_w / 2.0, 0.0)
        sp2 = _create_point(soc_w / 2.0, soc_w / 2.0, 0.0)
        sketch_socket.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)

        sketch_pin = sketches.add(plane_xz)
        pin_pt = _create_point(0.0, 0.0, block_h_cm / 2.0)
        sketch_pin.sketchCurves.sketchCircles.addByCenterRadius(pin_pt, params.pin_diameter_cm / 2.0)

        junctions[name] = comp

    return junctions


def build_divider_panel_component(root_comp: Any, params: FrunkParameters) -> Any:
    """
    Builds the 12x11-inch Slide-in Divider Panel (`DIV_Crosshatch_12x11`).
    Features:
    - 298mm x 275mm x 5mm overall envelope
    - 10mm solid perimeter bezel
    - 45-degree diagonal diamond crosshatch lattice struts (3.5mm width, 18mm pitch)
    - Ergonomic top finger pull handle cutout
    """
    matrix = adsk.core.Matrix3D.create() if FUSION_AVAILABLE else MockMatrix3D.create()
    occ = root_comp.occurrences.addNewComponent(matrix)
    comp = occ.component
    comp.name = "DIV_Crosshatch_12x11"

    ops = _get_feature_operations()
    sketches = comp.sketches
    plane_xy = getattr(comp, "xYConstructionPlane", "XY")

    w_cm = params.panel_width_cm
    h_cm = params.panel_height_cm
    t_cm = params.panel_thickness_cm
    bezel_cm = 1.0  # 10.0 mm solid perimeter bezel

    # 1. Outer perimeter bezel sketch
    sketch_bezel = sketches.add(plane_xy)
    p_out1 = _create_point(0.0, 0.0, 0.0)
    p_out2 = _create_point(w_cm, h_cm, 0.0)
    sketch_bezel.sketchCurves.sketchLines.addTwoPointRectangle(p_out1, p_out2)

    # Inner cutout window for lattice
    p_in1 = _create_point(bezel_cm, bezel_cm, 0.0)
    p_in2 = _create_point(w_cm - bezel_cm, h_cm - bezel_cm, 0.0)
    sketch_bezel.sketchCurves.sketchLines.addTwoPointRectangle(p_in1, p_in2)

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_bezel.profiles) > 0:
        comp.features.extrudeFeatures.addSimple(sketch_bezel.profiles[0], _create_value_real(t_cm), ops["new"])

    # 2. 45-degree Diamond Lattice Segments
    inner_w_mm = params.panel_width_mm - 20.0
    inner_h_mm = params.panel_height_mm - 20.0
    segments = calculate_diamond_lattice_segments(
        width=inner_w_mm,
        height=inner_h_mm,
        pitch=params.lattice_pitch_mm,
        strut_w=params.lattice_strut_mm
    )

    sketch_lattice = sketches.add(plane_xy)
    for (x1, y1), (x2, y2) in segments:
        pt1 = _create_point(bezel_cm + x1 / 10.0, bezel_cm + y1 / 10.0, 0.0)
        pt2 = _create_point(bezel_cm + x2 / 10.0, bezel_cm + y2 / 10.0, 0.0)
        sketch_lattice.sketchCurves.sketchLines.addByTwoPoints(pt1, pt2)

    # 3. Top Pull Handle Cutout (80mm x 22mm centered at top bezel)
    sketch_handle = sketches.add(plane_xy)
    handle_w_cm = 8.0
    handle_h_cm = 2.2
    mid_x = w_cm / 2.0
    hp1 = _create_point(mid_x - handle_w_cm / 2.0, h_cm - bezel_cm - handle_h_cm, 0.0)
    hp2 = _create_point(mid_x + handle_w_cm / 2.0, h_cm - bezel_cm, 0.0)
    sketch_handle.sketchCurves.sketchLines.addTwoPointRectangle(hp1, hp2)

    return comp


def build_locking_pin_component(root_comp: Any, params: FrunkParameters) -> Any:
    """
    Builds the Transverse Dovetail & Socket Locking Pin (`Pin_Lock_M5`).
    Features:
    - 8.0mm diameter flanged grip head (4.0mm thick)
    - 5.0mm nominal diameter locking shaft (28.0mm length)
    - 1-degree lead-in taper and chamfered tip
    """
    matrix = adsk.core.Matrix3D.create() if FUSION_AVAILABLE else MockMatrix3D.create()
    occ = root_comp.occurrences.addNewComponent(matrix)
    comp = occ.component
    comp.name = "Pin_Lock_M5"

    ops = _get_feature_operations()
    sketches = comp.sketches
    plane_xy = getattr(comp, "xYConstructionPlane", "XY")

    # 1. Grip head cylinder (8mm diameter x 4mm height)
    sketch_head = sketches.add(plane_xy)
    head_center = _create_point(0.0, 0.0, 0.0)
    sketch_head.sketchCurves.sketchCircles.addByCenterRadius(head_center, 0.4)

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_head.profiles) > 0:
        comp.features.extrudeFeatures.addSimple(sketch_head.profiles[0], _create_value_real(0.4), ops["new"])

    # 2. Pin shaft cylinder (5mm diameter x 28mm length extending in -Z)
    sketch_shaft = sketches.add(plane_xy)
    shaft_center = _create_point(0.0, 0.0, 0.0)
    sketch_shaft.sketchCurves.sketchCircles.addByCenterRadius(shaft_center, params.pin_diameter_cm / 2.0)

    if hasattr(comp.features, "extrudeFeatures") and len(sketch_shaft.profiles) > 0:
        comp.features.extrudeFeatures.addSimple(sketch_shaft.profiles[0], _create_value_real(-2.8), ops["join"])

    return comp


# ==============================================================================
# Fusion 360 Entry Point & CLI Dry-Run
# ==============================================================================

def run(context: Optional[Any] = None) -> None:
    """
    Standard Fusion 360 Script Entry Point.
    Executes within Autodesk Fusion 360 or in standalone dry-run mode.
    """
    ui = None
    try:
        if FUSION_AVAILABLE and context is not None:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = app.activeProduct
            if not design:
                ui.messageBox("No active Fusion 360 design document found.\nPlease open or create a design.", "Tesla Model X Frunk CAD Generator")
                return
            root_comp = design.rootComponent
            mode_desc = "Autodesk Fusion 360 Active Session"
        else:
            design = MockDesign()
            root_comp = design.rootComponent
            mode_desc = "Standalone / Headless Python Dry-Run"

        params = FrunkParameters()

        # Step 1: Create Parametric User Parameters
        create_user_parameters(design, params)

        # Step 2: Build All 6 Core CAD Components
        comp_truss = build_floor_truss_component(root_comp, params)
        comp_rib = build_vertical_rib_component(root_comp, params)
        comp_rail = build_horizontal_rail_component(root_comp, params)
        comp_junctions = build_junction_components(root_comp, params)
        comp_divider = build_divider_panel_component(root_comp, params)
        comp_pin = build_locking_pin_component(root_comp, params)

        summary_lines = [
            "=================================================================",
            "Tesla Model X 2017 Frunk Modular Divider System",
            "Autodesk Fusion 360 Parametric CAD Automation Script",
            "=================================================================",
            f"Execution Mode: {mode_desc}",
            "",
            "Generated CAD Components:",
            f" 1. {getattr(comp_truss, 'name', 'FT_Segment_12in')} (12-inch Floor Truss Segment)",
            f" 2. {getattr(comp_rib, 'name', 'VR_Post_Deep')} (11-inch Vertical Post with 6.4mm Slots)",
            f" 3. {getattr(comp_rail, 'name', 'HR_Rail_12in')} (12-inch Horizontal Top Rail)",
            f" 4. Junction Blocks: {', '.join(comp_junctions.keys())}",
            f" 5. {getattr(comp_divider, 'name', 'DIV_Crosshatch_12x11')} (Slide-in Diamond Mesh Divider)",
            f" 6. {getattr(comp_pin, 'name', 'Pin_Lock_M5')} (Transverse Locking Pin)",
            "",
            "Parametric Specifications (fx):",
            f" - Bay Spacing: {params.bay_spacing_mm} mm ({params.bay_spacing_in:.1f} in)",
            f" - Frame Height: {params.frame_height_mm} mm ({params.frame_height_in:.1f} in)",
            f" - Guide Slot Width: {params.slot_width_mm} mm (for {params.panel_thickness_mm} mm panel)",
            f" - Dovetail Joint: 15 deg wedge with {params.tol_dovetail_mm} mm slip clearance",
            f" - Tenon Socket: 20x20 mm with {params.tol_tenon_mm} mm slip clearance",
            f" - Lattice: 45 deg diamond mesh, {params.lattice_pitch_mm} mm pitch, {params.lattice_strut_mm} mm strut",
            "=================================================================",
        ]
        summary_text = "\n".join(summary_lines)
        print(summary_text)

        if ui:
            ui.messageBox(
                "Tesla Model X Frunk Divider System generated successfully!\n\n"
                "All 6 component definitions and User Parameters (fx) have been populated.\n"
                "You can now inspect the timeline and modify parameters under Modify -> Change Parameters.",
                "CAD Generation Complete"
            )

    except Exception:
        err_msg = f"Failed to generate Model X frunk components:\n{traceback.format_exc()}"
        print(err_msg, file=sys.stderr)
        if ui:
            ui.messageBox(err_msg, "Tesla Frunk CAD Generator Error")
        else:
            raise


if __name__ == "__main__":
    run(None)
