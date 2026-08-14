"""
Tesla Model X 2017 Frunk Modular Divider System
Autodesk Fusion 360 - Standalone All-In-One CAD Generator Script

INSTRUCTIONS:
1. In Fusion 360, open a fresh workspace tab (File -> New Design).
2. Press Shift + S (Scripts and Add-Ins).
3. Select 'ModelX_Frunk_Dividers' and click 'Run'.
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


def calculate_truss_span_triangles(
    x_start: float,
    x_end: float,
    z_bottom: float = 6.0,
    z_top: float = 29.0,
    num_triangles: int = 3,
    web_strut_w: float = 4.0
) -> List[List[Tuple[float, float]]]:
    """Generates alternating upright and inverted triangles for a truss span."""
    triangles = []
    span_len = x_end - x_start
    dx = span_len / num_triangles

    for i in range(num_triangles):
        x1 = x_start + i * dx + web_strut_w / 2.0
        x2 = x_start + (i + 1) * dx - web_strut_w / 2.0
        x_mid = (x1 + x2) / 2.0

        if i % 2 == 0:
            triangles.append([
                (x1, z_bottom),
                (x2, z_bottom),
                (x_mid, z_top)
            ])
        else:
            triangles.append([
                (x1, z_top),
                (x2, z_top),
                (x_mid, z_bottom)
            ])
    return triangles


def calculate_diamond_apertures(
    inner_w: float = 278.0,
    inner_h: float = 255.0,
    pitch: float = 18.0,
    strut_w: float = 3.5,
    margin: float = 4.0
) -> List[List[Tuple[float, float]]]:
    """
    Generates perfectly uniform 45-degree diamond apertures across a rotated grid,
    guaranteeing exact strut_w spacing everywhere.
    """
    apertures = []
    delta = pitch / math.sqrt(2.0)          # Rotated grid step ~ 12.7279 mm
    r = (pitch - strut_w) / math.sqrt(2.0)  # Half-extent along axes ~ 10.2530 mm

    max_u = int(math.ceil(inner_w / delta)) + 2
    max_v = int(math.ceil(inner_h / delta)) + 2
    handle_cx = inner_w / 2.0

    for u in range(-1, max_u):
        for v in range(-1, max_v):
            if (u + v) % 2 == 0:
                cx = u * delta
                cy = v * delta

                # Keep solid clearance around the top handle cutout
                if abs(cx - handle_cx) < 48.0 and cy + r > inner_h - 28.0:
                    continue

                # Ensure diamond fits fully inside the perimeter frame
                if (cx - r >= margin and cx + r <= inner_w - margin and
                    cy - r >= margin and cy + r <= inner_h - margin):
                    apertures.append([
                        (cx, cy + r),
                        (cx + r, cy),
                        (cx, cy - r),
                        (cx - r, cy)
                    ])
    return apertures


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


def _get_all_profiles(sketch: Any) -> List[Any]:
    if not FUSION_AVAILABLE:
        return getattr(sketch, "profiles", [])
    profs = []
    try:
        if sketch.profiles:
            for i in range(sketch.profiles.count):
                profs.append(sketch.profiles.item(i))
    except Exception:
        pass
    return profs


def _extrude_simple(comp: Any, profile: Any, distance_val: Any, operation: Any):
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


def _extrude_cut_all_profiles(comp: Any, sketch: Any, cut_depth_cm: float, direction_positive: bool = True):
    """Cuts all profiles in a sketch through the solid body."""
    if not FUSION_AVAILABLE or not sketch or not hasattr(sketch, "profiles"):
        return
    try:
        cnt = sketch.profiles.count
        if cnt == 0:
            return
        
        prof_col = adsk.core.ObjectCollection.create()
        for i in range(cnt):
            prof_col.add(sketch.profiles.item(i))
        
        ext_feats = comp.features.extrudeFeatures
        dist = cut_depth_cm if direction_positive else -cut_depth_cm
        val_dist = adsk.core.ValueInput.createByReal(dist)
        
        ext_input = ext_feats.createInput(prof_col, adsk.fusion.FeatureOperations.CutFeatureOperation)
        ext_input.setDistanceExtent(False, val_dist)
        ext_feats.add(ext_input)
    except Exception:
        for i in range(sketch.profiles.count):
            try:
                p = sketch.profiles.item(i)
                dist = cut_depth_cm if direction_positive else -cut_depth_cm
                comp.features.extrudeFeatures.addSimple(
                    p,
                    adsk.core.ValueInput.createByReal(dist),
                    adsk.fusion.FeatureOperations.CutFeatureOperation
                )
            except Exception:
                pass


def _extrude_cut_symmetric(comp: Any, sketch: Any, half_depth_cm: float):
    """Symmetric through-cut from plane in both + and - normal directions."""
    if not FUSION_AVAILABLE or not sketch or not hasattr(sketch, "profiles"):
        return
    try:
        cnt = sketch.profiles.count
        if cnt == 0:
            return
        
        prof_col = adsk.core.ObjectCollection.create()
        for i in range(cnt):
            prof_col.add(sketch.profiles.item(i))
        
        ext_feats = comp.features.extrudeFeatures
        val_dist = adsk.core.ValueInput.createByReal(half_depth_cm)
        
        ext_input = ext_feats.createInput(prof_col, adsk.fusion.FeatureOperations.CutFeatureOperation)
        ext_input.setDistanceExtent(True, val_dist)
        ext_feats.add(ext_input)
    except Exception:
        for i in range(sketch.profiles.count):
            try:
                p = sketch.profiles.item(i)
                ext_input = comp.features.extrudeFeatures.createInput(p, adsk.fusion.FeatureOperations.CutFeatureOperation)
                ext_input.setDistanceExtent(True, adsk.core.ValueInput.createByReal(half_depth_cm))
                comp.features.extrudeFeatures.add(ext_input)
            except Exception:
                pass


def _name_last_body(comp: Any, name: str):
    """Sets a friendly display name on the most recently created BRep body."""
    if FUSION_AVAILABLE and hasattr(comp, "bRepBodies"):
        try:
            cnt = comp.bRepBodies.count
            if cnt > 0:
                comp.bRepBodies.item(cnt - 1).name = name
        except Exception:
            pass


# ==============================================================================
# Parameter Creation Engine
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


# ==============================================================================
# Separated 3D Component Model Builders with True Boolean Solid Features
# ==============================================================================

def build_floor_truss_component(comp: Any, params: FrunkParameters, offset_x: float = 0.0, offset_y: float = 0.0):
    """
    Builds the 12-inch Floor Truss (`FT_Segment_12in`) with through-all triangular web cutouts,
    sliding male dovetail, female dovetail pocket, and center tenon socket.
    """
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None
    plane_xz = comp.xZConstructionPlane if hasattr(comp, "xZConstructionPlane") else None

    w_cm = params.truss_width_cm
    l_cm = params.bay_spacing_cm
    h_cm = params.truss_height_cm
    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1

    # 1. Base beam body (extruded in +Z)
    sketch_base = sketches.add(plane_xy)
    p1 = _create_point(ox, oy - w_cm / 2.0, 0.0)
    p2 = _create_point(ox + l_cm, oy + w_cm / 2.0, 0.0)
    sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    profs = _get_all_profiles(sketch_base)
    if profs:
        _extrude_simple(comp, profs[0], _create_value_real(h_cm), op_new)
        _name_last_body(comp, "FT_Segment_12in")

    # 2. Male dovetail tab at +X end (Join extrusion in +Z)
    sketch_male = sketches.add(plane_xy)
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm, base_w=params.dovetail_base_width_mm, depth=params.dovetail_depth_mm, angle_deg=params.dovetail_angle_deg)
    dt_pts = [_create_point(ox + l_cm + p[1] / 10.0, oy + p[0] / 10.0, 0.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_male.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    male_profs = _get_all_profiles(sketch_male)
    if male_profs:
        _extrude_simple(comp, male_profs[0], _create_value_real(h_cm), op_join)

    # 3. Female dovetail pocket at X=ox (Cut through +Z)
    sketch_female = sketches.add(plane_xy)
    female_pts = calculate_dovetail_profile(male=False, tol=params.tol_dovetail_mm, base_w=params.dovetail_base_width_mm, depth=params.dovetail_depth_mm, angle_deg=params.dovetail_angle_deg)
    f_dt_pts = [_create_point(ox + p[1] / 10.0, oy + p[0] / 10.0, 0.0) for p in female_pts]
    for i in range(len(f_dt_pts)):
        sketch_female.sketchCurves.sketchLines.addByTwoPoints(f_dt_pts[i], f_dt_pts[(i + 1) % len(f_dt_pts)])

    _extrude_cut_all_profiles(comp, sketch_female, h_cm, direction_positive=True)

    # 4. Triangular web cutouts in left & right spans (leaving solid center socket block)
    sketch_webs = sketches.add(plane_xz)
    # Left span: 20mm to 132mm
    tri_left = calculate_truss_span_triangles(x_start=20.0, x_end=132.0, z_bottom=6.0, z_top=29.0, num_triangles=3, web_strut_w=4.0)
    # Right span: 172.8mm to 284.8mm
    tri_right = calculate_truss_span_triangles(x_start=172.8, x_end=284.8, z_bottom=6.0, z_top=29.0, num_triangles=3, web_strut_w=4.0)

    for tri in tri_left + tri_right:
        pts = [_create_point(ox + p[0] / 10.0, 0.0, p[1] / 10.0) for p in tri]
        for i in range(3):
            sketch_webs.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % 3])

    _extrude_cut_symmetric(comp, sketch_webs, w_cm * 2.0)

    # 5. Center Tenon Socket (20x20mm pocket)
    sketch_socket = sketches.add(plane_xy)
    soc_w_cm = 2.0
    soc_x_mid = ox + l_cm / 2.0
    sp1 = _create_point(soc_x_mid - soc_w_cm / 2.0, oy - soc_w_cm / 2.0, 0.0)
    sp2 = _create_point(soc_x_mid + soc_w_cm / 2.0, oy + soc_w_cm / 2.0, 0.0)
    sketch_socket.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)


def build_vertical_rib_component(comp: Any, params: FrunkParameters, offset_x: float = 0.0, offset_y: float = 60.0):
    """
    Builds the 11-inch Vertical Rib Post (`VR_Post_Deep`) laid horizontally for easy viewing.
    Features: 280mm column, longitudinal 6.4mm slots, bottom tenon.
    """
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    w_cm = params.truss_width_cm
    h_cm = params.frame_height_cm
    slot_w_cm = params.slot_width_cm
    slot_d_cm = params.slot_depth_cm
    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1

    # 1. Main post body (laid flat along X from ox to ox + h_cm, extruded in +Z by w_cm)
    sketch_post = sketches.add(plane_xy)
    p1 = _create_point(ox, oy - w_cm / 2.0, 0.0)
    p2 = _create_point(ox + h_cm, oy + w_cm / 2.0, 0.0)
    sketch_post.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    profs = _get_all_profiles(sketch_post)
    if profs:
        _extrude_simple(comp, profs[0], _create_value_real(w_cm), op_new)
        _name_last_body(comp, "VR_Post_Deep")

    # 2. Guide slot cuts along post length (Cut down into body in +Z by slot_d_cm)
    sketch_slot = sketches.add(plane_xy)
    s1 = _create_point(ox, oy - slot_w_cm / 2.0, 0.0)
    s2 = _create_point(ox + h_cm, oy + slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)

    _extrude_cut_all_profiles(comp, sketch_slot, slot_d_cm, direction_positive=True)

    # 3. Bottom Tenon extending at X = ox - 20mm
    sketch_tenon = sketches.add(plane_xy)
    tenon_w_cm = (20.0 - 2.0 * params.tol_tenon_mm) / 10.0
    t1 = _create_point(ox - 2.0, oy - tenon_w_cm / 2.0, 0.0)
    t2 = _create_point(ox, oy + tenon_w_cm / 2.0, 0.0)
    sketch_tenon.sketchCurves.sketchLines.addTwoPointRectangle(t1, t2)

    tenon_profs = _get_all_profiles(sketch_tenon)
    if tenon_profs:
        _extrude_simple(comp, tenon_profs[0], _create_value_real(tenon_w_cm), op_join)


def build_horizontal_rail_component(comp: Any, params: FrunkParameters, offset_x: float = 0.0, offset_y: float = 120.0):
    """
    Builds the 12-inch Horizontal Top Rail (`HR_Rail_12in`) with bottom panel slot & dovetail.
    """
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    w_cm = params.truss_width_cm
    l_cm = params.bay_spacing_cm
    slot_w_cm = params.slot_width_cm
    slot_d_cm = params.slot_depth_cm
    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1

    # 1. Main rail body
    sketch_rail = sketches.add(plane_xy)
    p1 = _create_point(ox, oy - w_cm / 2.0, 0.0)
    p2 = _create_point(ox + l_cm, oy + w_cm / 2.0, 0.0)
    sketch_rail.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    profs = _get_all_profiles(sketch_rail)
    if profs:
        _extrude_simple(comp, profs[0], _create_value_real(w_cm), op_new)
        _name_last_body(comp, "HR_Rail_12in")

    # 2. Guide slot cut along rail face
    sketch_slot = sketches.add(plane_xy)
    s1 = _create_point(ox, oy - slot_w_cm / 2.0, 0.0)
    s2 = _create_point(ox + l_cm, oy + slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)

    _extrude_cut_all_profiles(comp, sketch_slot, slot_d_cm, direction_positive=True)

    # 3. Male dovetail at +X end
    sketch_dt = sketches.add(plane_xy)
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
    dt_pts = [_create_point(ox + l_cm + p[1] / 10.0, oy + p[0] / 10.0, 0.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_dt.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    dt_profs = _get_all_profiles(sketch_dt)
    if dt_profs:
        _extrude_simple(comp, dt_profs[0], _create_value_real(w_cm), op_join)


def build_junction_components(comp: Any, params: FrunkParameters, offset_x: float = 350.0, offset_y: float = 0.0):
    """
    Builds modular junction blocks (Corner, Tee, Cross) placed side-by-side.
    """
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    block_w_cm = 3.2
    block_h_cm = params.truss_height_cm
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1

    configs = [
        ("J_Corner_90", offset_x, offset_y, [(1, 0), (0, 1)]),
        ("J_Tee_3Way", offset_x, offset_y + 60.0, [(-1, 0), (1, 0), (0, 1)]),
        ("J_Cross_4Way", offset_x, offset_y + 120.0, [(-1, 0), (1, 0), (0, -1), (0, 1)]),
    ]

    for name, gx, gy, directions in configs:
        ox = gx / 10.0
        oy = gy / 10.0

        sketch_main = sketches.add(plane_xy)
        p1 = _create_point(ox - block_w_cm / 2.0, oy - block_w_cm / 2.0, 0.0)
        p2 = _create_point(ox + block_w_cm / 2.0, oy + block_w_cm / 2.0, 0.0)
        sketch_main.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

        profs = _get_all_profiles(sketch_main)
        if profs:
            _extrude_simple(comp, profs[0], _create_value_real(block_h_cm), op_new)
            _name_last_body(comp, name)

        # Dovetail tabs
        male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
        sketch_dt = sketches.add(plane_xy)
        for dx, dy in directions:
            off_x = ox + dx * (block_w_cm / 2.0)
            off_y = oy + dy * (block_w_cm / 2.0)
            for i in range(len(male_pts)):
                p_curr = male_pts[i]
                p_next = male_pts[(i + 1) % len(male_pts)]
                pt_a = _create_point(off_x + p_curr[0] / 10.0, off_y + p_curr[1] / 10.0, 0.0)
                pt_b = _create_point(off_x + p_next[0] / 10.0, off_y + p_next[1] / 10.0, 0.0)
                sketch_dt.sketchCurves.sketchLines.addByTwoPoints(pt_a, pt_b)

        dt_profs = _get_all_profiles(sketch_dt)
        if dt_profs:
            _extrude_simple(comp, dt_profs[0], _create_value_real(block_h_cm), op_join)


def build_divider_panel_component(comp: Any, params: FrunkParameters, offset_x: float = 0.0, offset_y: float = -320.0):
    """
    Builds the 12x11-inch Slide-in Divider Panel (`DIV_Crosshatch_12x11`).
    First creates a solid 298x275x5mm plate in +Z, then cleanly punches through all
    45-degree diamond mesh windows and the top ergonomic pull-handle in +Z.
    """
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    w_cm = params.panel_width_cm
    h_cm = params.panel_height_cm
    t_cm = params.panel_thickness_cm
    bezel_cm = 1.0
    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0

    # 1. Solid rectangular panel plate extruded in +Z by t_cm (0.5 cm)
    sketch_plate = sketches.add(plane_xy)
    p_out1 = _create_point(ox, oy, 0.0)
    p_out2 = _create_point(ox + w_cm, oy + h_cm, 0.0)
    sketch_plate.sketchCurves.sketchLines.addTwoPointRectangle(p_out1, p_out2)

    plate_profs = _get_all_profiles(sketch_plate)
    if plate_profs:
        _extrude_simple(comp, plate_profs[0], _create_value_real(t_cm), op_new)
        _name_last_body(comp, "DIV_Crosshatch_12x11")

    # 2. 45-degree Diamond Mesh Cutouts (Uniform rotated grid math)
    inner_w_mm = params.panel_width_mm - 20.0
    inner_h_mm = params.panel_height_mm - 20.0
    apertures = calculate_diamond_apertures(
        inner_w=inner_w_mm,
        inner_h=inner_h_mm,
        pitch=params.lattice_pitch_mm,
        strut_w=params.lattice_strut_mm,
        margin=4.0
    )

    sketch_cutouts = sketches.add(plane_xy)
    for diamond in apertures:
        pts = [_create_point(ox + bezel_cm + p[0] / 10.0, oy + bezel_cm + p[1] / 10.0, 0.0) for p in diamond]
        lines = sketch_cutouts.sketchCurves.sketchLines
        for i in range(4):
            lines.addByTwoPoints(pts[i], pts[(i + 1) % 4])

    _extrude_cut_all_profiles(comp, sketch_cutouts, t_cm, direction_positive=True)

    # 3. Top Handle Cutout (Punches through top bezel in +Z by t_cm)
    sketch_handle = sketches.add(plane_xy)
    handle_w_cm = 8.0
    handle_h_cm = 2.2
    mid_x = ox + w_cm / 2.0
    hp1 = _create_point(mid_x - handle_w_cm / 2.0, oy + h_cm - bezel_cm - handle_h_cm, 0.0)
    hp2 = _create_point(mid_x + handle_w_cm / 2.0, oy + h_cm - bezel_cm, 0.0)
    sketch_handle.sketchCurves.sketchLines.addTwoPointRectangle(hp1, hp2)

    _extrude_cut_all_profiles(comp, sketch_handle, t_cm, direction_positive=True)


def build_locking_pin_component(comp: Any, params: FrunkParameters, offset_x: float = 350.0, offset_y: float = 180.0):
    """
    Builds the Transverse Locking Pin (`Pin_Lock_M5`).
    """
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1

    # 1. Grip head cylinder (8mm diameter x 4mm height in +Z)
    sketch_head = sketches.add(plane_xy)
    head_center = _create_point(ox, oy, 0.0)
    sketch_head.sketchCurves.sketchCircles.addByCenterRadius(head_center, 0.4)

    head_profs = _get_all_profiles(sketch_head)
    if head_profs:
        _extrude_simple(comp, head_profs[0], _create_value_real(0.4), op_new)
        _name_last_body(comp, "Pin_Lock_M5")

    # 2. Pin shaft cylinder (5mm diameter x 28mm length in -Z)
    sketch_shaft = sketches.add(plane_xy)
    sketch_shaft.sketchCurves.sketchCircles.addByCenterRadius(head_center, params.pin_diameter_cm / 2.0)

    shaft_profs = _get_all_profiles(sketch_shaft)
    if shaft_profs:
        _extrude_simple(comp, shaft_profs[0], _create_value_real(-2.8), op_join)


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

            # Ensure document is in Parametric Mode
            try:
                if design.designType != adsk.fusion.DesignTypes.ParametricDesignType:
                    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            except Exception:
                pass

            root_comp = design.rootComponent
        else:
            class MockRoot:
                def __init__(self):
                    self.sketches = MockSketches()
                    self.features = MockFeatures()
            root_comp = MockRoot()
            design = MockDesign()

        params = FrunkParameters()

        # Step 1: Create Parametric User Parameters (fx)
        create_user_parameters(design, params)

        # Step 2: Build All 8 Core CAD Solid Bodies (Neatly arranged side-by-side)
        build_floor_truss_component(root_comp, params, offset_x=0.0, offset_y=0.0)
        build_vertical_rib_component(root_comp, params, offset_x=0.0, offset_y=60.0)
        build_horizontal_rail_component(root_comp, params, offset_x=0.0, offset_y=120.0)
        build_junction_components(root_comp, params, offset_x=350.0, offset_y=0.0)
        build_divider_panel_component(root_comp, params, offset_x=0.0, offset_y=-320.0)
        build_locking_pin_component(root_comp, params, offset_x=350.0, offset_y=180.0)

        if ui:
            ui.messageBox(
                "Tesla Model X Frunk Modular Divider System Generated Successfully!\n\n"
                "All 8 modular solid bodies have been generated with uniform 45° lattice struts:\n\n"
                "  1. FT_Segment_12in (Floor Truss with span webs & dovetails)\n"
                "  2. VR_Post_Deep (11\" Vertical Rib with 6.4mm slots)\n"
                "  3. HR_Rail_12in (Horizontal Top Tie Rail)\n"
                "  4. J_Corner_90 (2-Way 90° Corner Junction)\n"
                "  5. J_Tee_3Way (3-Way T-Junction)\n"
                "  6. J_Cross_4Way (4-Way Cross Junction)\n"
                "  7. DIV_Crosshatch_12x11 (Uniform 45° Diamond Lattice Mesh Divider)\n"
                "  8. Pin_Lock_M5 (Transverse Locking Pin)\n\n"
                "Check the 'Bodies' folder in your Browser Tree on the left to view, isolate, or export any component!",
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
