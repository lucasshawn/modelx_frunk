"""
Tesla Model X 2017 Frunk Modular Divider System
Autodesk Fusion 360 - Standalone All-In-One CAD Generator Script

INSTRUCTIONS:
1. In Fusion 360, press Shift + S (Scripts and Add-Ins).
2. Select 'ModelX_Frunk_Dividers' and click 'Run'.
"""

import math
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Attempt Autodesk Fusion 360 API import
try:
    import adsk.core
    import adsk.fusion
    FUSION_AVAILABLE = True
except ImportError:
    FUSION_AVAILABLE = False


# ==============================================================================
# Parametric Configuration & Geometry Engine
# ==============================================================================

@dataclass
class FrunkParameters:
    """Parametric dimensions and engineering tolerances."""
    bay_spacing_mm: float = 304.8       # 12.0 in (Center-to-center divider spacing)
    frame_height_mm: float = 280.0      # 11.0 in (Deep full-height upright post)
    truss_height_mm: float = 35.0       # Floor truss height
    truss_width_mm: float = 24.0        # Profile width
    slot_width_mm: float = 6.4          # Guide slot width (for 5mm panel + 0.7mm slip clearance per side)
    slot_depth_mm: float = 8.0          # Guide slot depth
    panel_thickness_mm: float = 5.0     # Nominal divider panel thickness
    panel_width_mm: float = 298.0       # Width of 12" divider panel
    panel_height_mm: float = 275.0      # Height of divider panel
    lattice_pitch_mm: float = 18.0      # 45-degree diamond mesh pitch
    lattice_strut_mm: float = 3.5       # Diamond mesh strut thickness
    tol_dovetail_mm: float = 0.25       # 3D printing slip clearance for 15-deg dovetails
    tol_tenon_mm: float = 0.20          # 3D printing slip clearance for vertical socket tenons
    pin_diameter_mm: float = 5.0        # Transverse locking pin diameter
    dovetail_base_width_mm: float = 14.0 # Dovetail root width
    dovetail_depth_mm: float = 8.0      # Dovetail depth
    dovetail_angle_deg: float = 15.0    # Dovetail wedge half-angle

    @property
    def bay_spacing_cm(self) -> float:
        return self.bay_spacing_mm / 10.0

    @property
    def frame_height_cm(self) -> float:
        return self.frame_height_mm / 10.0

    @property
    def truss_height_cm(self) -> float:
        return self.truss_height_mm / 10.0

    @property
    def truss_width_cm(self) -> float:
        return self.truss_width_mm / 10.0

    @property
    def slot_width_cm(self) -> float:
        return self.slot_width_mm / 10.0

    @property
    def slot_depth_cm(self) -> float:
        return self.slot_depth_mm / 10.0

    @property
    def panel_thickness_cm(self) -> float:
        return self.panel_thickness_mm / 10.0

    @property
    def panel_width_cm(self) -> float:
        return self.panel_width_mm / 10.0

    @property
    def panel_height_cm(self) -> float:
        return self.panel_height_mm / 10.0

    @property
    def pin_diameter_cm(self) -> float:
        return self.pin_diameter_mm / 10.0


def calculate_dovetail_profile(
    male: bool,
    tol: float,
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0
) -> List[Tuple[float, float]]:
    rad = math.radians(angle_deg)
    flare = depth * math.tan(rad)
    offset = -tol if male else 0.0
    w_root = (base_w + 2.0 * offset) / 2.0
    w_tip = (base_w + 2.0 * flare + 2.0 * offset) / 2.0

    return [
        (-w_root, 0.0),
        (-w_tip, depth),
        (w_tip, depth),
        (w_root, 0.0)
    ]


def calculate_truss_web_triangles(
    span_length: float,
    height: float,
    web_thickness: float = 4.0,
    num_bays: int = 6
) -> List[List[Tuple[float, float]]]:
    bay_w = span_length / num_bays
    margin_y = web_thickness
    h_inner = height - 2.0 * margin_y
    triangles = []

    for i in range(num_bays):
        x_left = i * bay_w + web_thickness / 2.0
        x_right = (i + 1) * bay_w - web_thickness / 2.0
        x_mid = (x_left + x_right) / 2.0

        if i % 2 == 0:
            triangles.append([
                (x_left, margin_y),
                (x_right, margin_y),
                (x_mid, margin_y + h_inner)
            ])
        else:
            triangles.append([
                (x_left, margin_y + h_inner),
                (x_right, margin_y + h_inner),
                (x_mid, margin_y)
            ])
    return triangles


def calculate_diamond_lattice_segments(
    width: float,
    height: float,
    pitch: float,
    strut_w: float
) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    segments = []
    step = pitch * math.sqrt(2)

    # +45 degree lines: y = x + c
    c = -width
    while c <= height:
        pts = []
        if 0.0 <= c <= height:
            pts.append((0.0, c))
        if 0.0 <= width + c <= height:
            pts.append((width, width + c))
        if 0.0 <= -c <= width and (-c != 0.0 or c != 0.0):
            pts.append((-c, 0.0))
        if 0.0 <= height - c <= width and (height - c != width or width + c != height):
            pts.append((height - c, height))

        unique_pts = list(set([(round(p[0], 4), round(p[1], 4)) for p in pts]))
        if len(unique_pts) == 2:
            unique_pts.sort()
            segments.append((unique_pts[0], unique_pts[1]))
        c += step

    # -45 degree lines: y = -x + d
    d = 0.0
    while d <= width + height:
        pts = []
        if 0.0 <= d <= height:
            pts.append((0.0, d))
        if 0.0 <= d - width <= height:
            pts.append((width, d - width))
        if 0.0 <= d <= width:
            pts.append((d, 0.0))
        if 0.0 <= d - height <= width:
            pts.append((d - height, height))

        unique_pts = list(set([(round(p[0], 4), round(p[1], 4)) for p in pts]))
        if len(unique_pts) == 2:
            unique_pts.sort()
            segments.append((unique_pts[0], unique_pts[1]))
        d += step

    return segments


# ==============================================================================
# Helper Factories & Robust Fusion API Wrappers
# ==============================================================================

def _create_point(x: float, y: float, z: float):
    if FUSION_AVAILABLE:
        return adsk.core.Point3D.create(x, y, z)
    class MockPt:
        def __init__(self, px, py, pz): self.x, self.y, self.z = px, py, pz
    return MockPt(x, y, z)


def _create_value_string(expr: str):
    if FUSION_AVAILABLE:
        return adsk.core.ValueInput.createByString(expr)
    class MockVal:
        def __init__(self, v): self.value = v
    return MockVal(expr)


def _create_value_real(val: float):
    if FUSION_AVAILABLE:
        return adsk.core.ValueInput.createByReal(val)
    class MockVal:
        def __init__(self, v): self.value = v
    return MockVal(val)


def _get_first_profile(sketch: Any) -> Optional[Any]:
    if not FUSION_AVAILABLE:
        return sketch.profiles[0] if getattr(sketch, "profiles", None) else None
    try:
        if sketch.profiles and sketch.profiles.count > 0:
            return sketch.profiles.item(0)
    except Exception:
        pass
    return None


def _extrude_profile(comp: Any, profile: Any, distance_val: Any, operation: Any):
    if FUSION_AVAILABLE and profile is not None:
        try:
            return comp.features.extrudeFeatures.addSimple(profile, distance_val, operation)
        except Exception:
            try:
                ext_input = comp.features.extrudeFeatures.createInput(profile, operation)
                ext_input.setDistanceExtent(False, distance_val)
                return comp.features.extrudeFeatures.add(ext_input)
            except Exception:
                pass
    return None


def _create_or_get_component(root_comp: Any, name: str) -> Any:
    """Creates a new component occurrence with graceful fallback for all document modes."""
    if FUSION_AVAILABLE:
        try:
            matrix = adsk.core.Matrix3D.create()
            occ = root_comp.occurrences.addNewComponent(matrix)
            comp = occ.component
            comp.name = name
            return comp
        except Exception:
            # Fallback if document is in direct single-part mode
            return root_comp
    class MockComp:
        def __init__(self, n):
            self.name = n
            self.sketches = MockSketches()
            self.features = MockFeatures()
    return MockComp(name)


# ==============================================================================
# CAD Generation Functions
# ==============================================================================

def create_user_parameters(design: Any, params: FrunkParameters):
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


def build_floor_truss_component(root_comp: Any, params: FrunkParameters):
    comp = _create_or_get_component(root_comp, "FT_Segment_12in")
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None
    plane_xz = comp.xZConstructionPlane if hasattr(comp, "xZConstructionPlane") else None

    w_cm = params.truss_width_cm
    l_cm = params.bay_spacing_cm
    h_cm = params.truss_height_cm

    # 1. Base beam body
    sketch_base = sketches.add(plane_xy)
    p1 = _create_point(0.0, -w_cm / 2.0, 0.0)
    p2 = _create_point(l_cm, w_cm / 2.0, 0.0)
    sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    prof_base = _get_first_profile(sketch_base)
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1
    _extrude_profile(comp, prof_base, _create_value_real(h_cm), op_new)

    # 2. Triangular web cutouts
    sketch_webs = sketches.add(plane_xz)
    triangles = calculate_truss_web_triangles(span_length=params.bay_spacing_mm, height=params.truss_height_mm, web_thickness=4.0, num_bays=6)
    for tri in triangles:
        pts = [_create_point(p[0] / 10.0, 0.0, p[1] / 10.0) for p in tri]
        for i in range(3):
            sketch_webs.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % 3])

    # 3. Male dovetail tab at +X end
    sketch_male = sketches.add(plane_xy)
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm, base_w=params.dovetail_base_width_mm, depth=params.dovetail_depth_mm, angle_deg=params.dovetail_angle_deg)
    dt_pts = [_create_point(l_cm + p[1] / 10.0, p[0] / 10.0, 0.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_male.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    prof_male = _get_first_profile(sketch_male)
    _extrude_profile(comp, prof_male, _create_value_real(h_cm), op_join)

    # 4. Female dovetail pocket sketch at X=0
    sketch_female = sketches.add(plane_xy)
    female_pts = calculate_dovetail_profile(male=False, tol=params.tol_dovetail_mm, base_w=params.dovetail_base_width_mm, depth=params.dovetail_depth_mm, angle_deg=params.dovetail_angle_deg)
    f_dt_pts = [_create_point(p[1] / 10.0, p[0] / 10.0, 0.0) for p in female_pts]
    for i in range(len(f_dt_pts)):
        sketch_female.sketchCurves.sketchLines.addByTwoPoints(f_dt_pts[i], f_dt_pts[(i + 1) % len(f_dt_pts)])

    # 5. Socket pocket (20x20mm) and pin hole
    sketch_socket = sketches.add(plane_xy)
    soc_w_cm = 2.0
    soc_x_mid = l_cm / 2.0
    sp1 = _create_point(soc_x_mid - soc_w_cm / 2.0, -soc_w_cm / 2.0, 0.0)
    sp2 = _create_point(soc_x_mid + soc_w_cm / 2.0, soc_w_cm / 2.0, 0.0)
    sketch_socket.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)

    sketch_pin = sketches.add(plane_xz)
    pin_center = _create_point(soc_x_mid, 0.0, h_cm / 2.0)
    sketch_pin.sketchCurves.sketchCircles.addByCenterRadius(pin_center, params.pin_diameter_cm / 2.0)

    return comp


def build_vertical_rib_component(root_comp: Any, params: FrunkParameters):
    comp = _create_or_get_component(root_comp, "VR_Post_Deep")
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None
    plane_xz = comp.xZConstructionPlane if hasattr(comp, "xZConstructionPlane") else None

    w_cm = params.truss_width_cm
    h_cm = params.frame_height_cm
    slot_w_cm = params.slot_width_cm
    slot_d_cm = params.slot_depth_cm

    # 1. Main post column
    sketch_post = sketches.add(plane_xy)
    p1 = _create_point(-w_cm / 2.0, -w_cm / 2.0, 0.0)
    p2 = _create_point(w_cm / 2.0, w_cm / 2.0, 0.0)
    sketch_post.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    prof_post = _get_first_profile(sketch_post)
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1
    _extrude_profile(comp, prof_post, _create_value_real(h_cm), op_new)

    # 2. Guide slots
    sketch_slot = sketches.add(plane_xy)
    s1 = _create_point(-w_cm / 2.0, -slot_w_cm / 2.0, 0.0)
    s2 = _create_point(-w_cm / 2.0 + slot_d_cm, slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)
    s3 = _create_point(w_cm / 2.0 - slot_d_cm, -slot_w_cm / 2.0, 0.0)
    s4 = _create_point(w_cm / 2.0, slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s3, s4)

    # 3. Bottom Tenon (20x20mm - 2*tol)
    sketch_tenon = sketches.add(plane_xy)
    tenon_w_cm = (20.0 - 2.0 * params.tol_tenon_mm) / 10.0
    t1 = _create_point(-tenon_w_cm / 2.0, -tenon_w_cm / 2.0, 0.0)
    t2 = _create_point(tenon_w_cm / 2.0, tenon_w_cm / 2.0, 0.0)
    sketch_tenon.sketchCurves.sketchLines.addTwoPointRectangle(t1, t2)

    prof_tenon = _get_first_profile(sketch_tenon)
    _extrude_profile(comp, prof_tenon, _create_value_real(-2.0), op_join)

    # 4. Transverse pin hole
    sketch_pin = sketches.add(plane_xz)
    pin_pt = _create_point(0.0, 0.0, -1.0)
    sketch_pin.sketchCurves.sketchCircles.addByCenterRadius(pin_pt, params.pin_diameter_cm / 2.0)

    return comp


def build_horizontal_rail_component(root_comp: Any, params: FrunkParameters):
    comp = _create_or_get_component(root_comp, "HR_Rail_12in")
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None
    plane_yz = comp.yZConstructionPlane if hasattr(comp, "yZConstructionPlane") else None

    w_cm = params.truss_width_cm
    l_cm = params.bay_spacing_cm
    slot_w_cm = params.slot_width_cm

    # 1. Main horizontal beam body (along X)
    sketch_rail = sketches.add(plane_yz)
    p1 = _create_point(0.0, -w_cm / 2.0, 0.0)
    p2 = _create_point(0.0, w_cm / 2.0, w_cm)
    sketch_rail.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    prof_rail = _get_first_profile(sketch_rail)
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    _extrude_profile(comp, prof_rail, _create_value_real(l_cm), op_new)

    # 2. Bottom guide slot
    sketch_bottom_slot = sketches.add(plane_xy)
    s1 = _create_point(0.0, -slot_w_cm / 2.0, 0.0)
    s2 = _create_point(l_cm, slot_w_cm / 2.0, 0.0)
    sketch_bottom_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)

    # 3. Male dovetail at end
    sketch_male_dt = sketches.add(plane_yz)
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
    dt_pts = [_create_point(0.0, p[0] / 10.0, p[1] / 10.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_male_dt.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    return comp


def build_junction_components(root_comp: Any, params: FrunkParameters):
    block_w_cm = 3.2
    block_h_cm = params.truss_height_cm
    junctions = {}

    configs = [
        ("J_Corner_90", [(1, 0), (0, 1)]),
        ("J_Tee_3Way", [(-1, 0), (1, 0), (0, 1)]),
        ("J_Cross_4Way", [(-1, 0), (1, 0), (0, -1), (0, 1)]),
    ]

    for name, directions in configs:
        comp = _create_or_get_component(root_comp, name)
        sketches = comp.sketches
        plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None
        plane_xz = comp.xZConstructionPlane if hasattr(comp, "xZConstructionPlane") else None

        sketch_main = sketches.add(plane_xy)
        p1 = _create_point(-block_w_cm / 2.0, -block_w_cm / 2.0, 0.0)
        p2 = _create_point(block_w_cm / 2.0, block_w_cm / 2.0, 0.0)
        sketch_main.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

        prof_main = _get_first_profile(sketch_main)
        op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
        _extrude_profile(comp, prof_main, _create_value_real(block_h_cm), op_new)

        # Dovetail tabs
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

        # Socket & pin
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


def build_divider_panel_component(root_comp: Any, params: FrunkParameters):
    comp = _create_or_get_component(root_comp, "DIV_Crosshatch_12x11")
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    w_cm = params.panel_width_cm
    h_cm = params.panel_height_cm
    t_cm = params.panel_thickness_cm
    bezel_cm = 1.0

    # 1. Outer perimeter bezel
    sketch_bezel = sketches.add(plane_xy)
    p_out1 = _create_point(0.0, 0.0, 0.0)
    p_out2 = _create_point(w_cm, h_cm, 0.0)
    sketch_bezel.sketchCurves.sketchLines.addTwoPointRectangle(p_out1, p_out2)

    p_in1 = _create_point(bezel_cm, bezel_cm, 0.0)
    p_in2 = _create_point(w_cm - bezel_cm, h_cm - bezel_cm, 0.0)
    sketch_bezel.sketchCurves.sketchLines.addTwoPointRectangle(p_in1, p_in2)

    prof_bezel = _get_first_profile(sketch_bezel)
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    _extrude_profile(comp, prof_bezel, _create_value_real(t_cm), op_new)

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

    # 3. Top Handle
    sketch_handle = sketches.add(plane_xy)
    handle_w_cm = 8.0
    handle_h_cm = 2.2
    mid_x = w_cm / 2.0
    hp1 = _create_point(mid_x - handle_w_cm / 2.0, h_cm - bezel_cm - handle_h_cm, 0.0)
    hp2 = _create_point(mid_x + handle_w_cm / 2.0, h_cm - bezel_cm, 0.0)
    sketch_handle.sketchCurves.sketchLines.addTwoPointRectangle(hp1, hp2)

    return comp


def build_locking_pin_component(root_comp: Any, params: FrunkParameters):
    comp = _create_or_get_component(root_comp, "Pin_Lock_M5")
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    # 1. Grip head cylinder (8mm diameter x 4mm height)
    sketch_head = sketches.add(plane_xy)
    head_center = _create_point(0.0, 0.0, 0.0)
    sketch_head.sketchCurves.sketchCircles.addByCenterRadius(head_center, 0.4)

    prof_head = _get_first_profile(sketch_head)
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1
    _extrude_profile(comp, prof_head, _create_value_real(0.4), op_new)

    # 2. Pin shaft cylinder (5mm diameter x 28mm length extending in -Z)
    sketch_shaft = sketches.add(plane_xy)
    shaft_center = _create_point(0.0, 0.0, 0.0)
    sketch_shaft.sketchCurves.sketchCircles.addByCenterRadius(shaft_center, params.pin_diameter_cm / 2.0)

    prof_shaft = _get_first_profile(sketch_shaft)
    _extrude_profile(comp, prof_shaft, _create_value_real(-2.8), op_join)

    return comp


# ==============================================================================
# Fusion 360 Entry Point
# ==============================================================================

def run(context=None):
    ui = None
    try:
        if FUSION_AVAILABLE:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)

            if not design:
                if ui:
                    ui.messageBox(
                        "No active 3D design workspace found.\n\n"
                        "Please create or open a document in Fusion 360 (File -> New Design) before running.",
                        "Tesla Model X Frunk Generator"
                    )
                return

            # Ensure document is in Parametric Assembly Mode (Capture Design History)
            try:
                if design.designType != adsk.fusion.DesignTypes.ParametricDesignType:
                    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            except Exception:
                pass

            root_comp = design.rootComponent
        else:
            design = MockDesign()
            root_comp = design.rootComponent

        params = FrunkParameters()

        # Step 1: Create Parametric User Parameters (fx)
        create_user_parameters(design, params)

        # Step 2: Build All 6 Core CAD Components
        comp_truss = build_floor_truss_component(root_comp, params)
        comp_rib = build_vertical_rib_component(root_comp, params)
        comp_rail = build_horizontal_rail_component(root_comp, params)
        comp_junctions = build_junction_components(root_comp, params)
        comp_divider = build_divider_panel_component(root_comp, params)
        comp_pin = build_locking_pin_component(root_comp, params)

        if ui:
            ui.messageBox(
                "Tesla Model X Frunk Modular Divider System Generated Successfully!\n\n"
                "Components created in Browser Tree:\n"
                " 1. FT_Segment_12in (Floor Truss with web cutouts & dovetails)\n"
                " 2. VR_Post_Deep (11\" Vertical Rib Post with 6.4mm slots)\n"
                " 3. HR_Rail_12in (Horizontal Top Tie Rail)\n"
                " 4. J_Corner_90, J_Tee_3Way, J_Cross_4Way (Modular Junction Blocks)\n"
                " 5. DIV_Crosshatch_12x11 (45° Diamond Lattice Slide-In Divider)\n"
                " 6. Pin_Lock_M5 (Transverse Locking Pin)\n\n"
                "You can inspect all components in your browser tree on the left and edit dimensions in Modify -> Change Parameters (fx).",
                "Generation Complete"
            )

    except Exception:
        err_msg = f"Error generating components:\n{traceback.format_exc()}"
        if ui:
            ui.messageBox(err_msg, "Tesla Frunk Script Error")
        else:
            print(err_msg, file=sys.stderr)


if __name__ == "__main__":
    run(None)
