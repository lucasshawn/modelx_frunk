"""
Tesla Model X 2017 Frunk Conformal Modular Divider System
Autodesk Fusion 360 - Standalone Universal Part & Assembly Script

Works seamlessly in Part Design mode, Assembly mode, and fresh documents.

GENERATES:
  1. TRK_Front_L       - Front-Left Flanged Two-Tier Rail Quadrant (< 310 mm bed fit)
  2. TRK_Front_R       - Front-Right Flanged Two-Tier Rail Quadrant (< 310 mm bed fit)
  3. TRK_Rear_L        - Rear-Left Flanged Two-Tier Rail Quadrant (< 310 mm bed fit)
  4. TRK_Rear_R        - Rear-Right Flanged Two-Tier Rail Quadrant (< 310 mm bed fit)
  5. PST_Slide_Upright - Sliding Post with wrap-around captive base shoe & guide slot
  6. SLAT_Segment_6in  - 6-inch modular interlocking cross-member divider slat
"""

import math
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    import adsk.core
    import adsk.fusion
    FUSION_AVAILABLE = True
except ImportError:
    FUSION_AVAILABLE = False


@dataclass
class SystemParameters:
    width_mm: float = 808.0              # Floor tub width
    depth_mm: float = 208.0              # Floor tub depth
    wall_clearance_mm: float = 12.7      # 0.50 in clearance from tub wall
    rail_base_width_mm: float = 30.0     # Wide flanged base
    rail_base_height_mm: float = 8.0     # Base height
    rail_neck_width_mm: float = 16.0     # Upper neck width
    rail_neck_height_mm: float = 10.0    # Upper neck height (Total rail height = 18.0 mm)
    post_height_mm: float = 250.0        # Upright post column height
    post_col_size_mm: float = 22.0       # Upright column cross-section
    shoe_width_mm: float = 44.0          # Base shoe width
    shoe_length_mm: float = 40.0         # Base shoe length along track
    shoe_height_mm: float = 24.0         # Base shoe height
    slot_width_mm: float = 6.4           # Guide slot for 5mm cross slats
    slot_depth_mm: float = 8.0           # Guide slot depth
    slat_length_mm: float = 152.4        # 6.0 in modular slat segment length
    slat_height_mm: float = 60.0         # Slat layer height
    slat_thickness_mm: float = 5.0       # Slat thickness
    tol_slip_mm: float = 0.20            # 3D printing slip clearance


def _create_pt(x_cm: float, y_cm: float, z_cm: float = 0.0):
    if FUSION_AVAILABLE:
        return adsk.core.Point3D.create(x_cm, y_cm, z_cm)
    class MockPt:
        def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
    return MockPt(x_cm, y_cm, z_cm)


def make_tab_points(
    p_start: Tuple[float, float],
    p_end: Tuple[float, float],
    ext_vec: Tuple[float, float],
    tab_w: float = 12.0,
    tab_d: float = 7.0,
    flare_ang: float = 14.0,
    tol: float = 0.20
) -> List[Tuple[float, float]]:
    ex, ey = ext_vec
    dx = p_end[0] - p_start[0]
    dy = p_end[1] - p_start[1]
    edge_len = math.hypot(dx, dy)
    tx, ty = dx / edge_len, dy / edge_len

    mid_x = (p_start[0] + p_end[0]) / 2.0
    mid_y = (p_start[1] + p_end[1]) / 2.0

    flare = tab_d * math.tan(math.radians(flare_ang))
    w_root = (tab_w - 2.0 * tol) / 2.0
    w_tip = (tab_w + 2.0 * flare - 2.0 * tol) / 2.0

    p0 = (mid_x - tx * w_root, mid_y - ty * w_root)
    p1 = (mid_x - tx * w_tip + ex * tab_d, mid_y - ty * w_tip + ey * tab_d)
    p2 = (mid_x + tx * w_tip + ex * tab_d, mid_y + ty * w_tip + ey * tab_d)
    p3 = (mid_x + tx * w_root, mid_y + ty * w_root)

    return [p_start, p0, p1, p2, p3, p_end]


def make_pocket_points(
    p_start: Tuple[float, float],
    p_end: Tuple[float, float],
    int_vec: Tuple[float, float],
    pocket_w: float = 12.0,
    pocket_d: float = 7.0,
    flare_ang: float = 14.0,
    tol: float = 0.20
) -> List[Tuple[float, float]]:
    ix, iy = int_vec
    dx = p_end[0] - p_start[0]
    dy = p_end[1] - p_start[1]
    edge_len = math.hypot(dx, dy)
    tx, ty = dx / edge_len, dy / edge_len

    mid_x = (p_start[0] + p_end[0]) / 2.0
    mid_y = (p_start[1] + p_end[1]) / 2.0

    flare = pocket_d * math.tan(math.radians(flare_ang))
    w_root = (pocket_w + 2.0 * tol) / 2.0
    w_tip = (pocket_w + 2.0 * flare + 2.0 * tol) / 2.0

    p0 = (mid_x - tx * w_root, mid_y - ty * w_root)
    p1 = (mid_x - tx * w_tip + ix * pocket_d, mid_y - ty * w_tip + iy * pocket_d)
    p2 = (mid_x + tx * w_tip + ix * pocket_d, mid_y + ty * w_tip + iy * pocket_d)
    p3 = (mid_x + tx * w_root, mid_y + ty * w_root)

    return [p_start, p0, p1, p2, p3, p_end]


def generate_watertight_quadrants(
    half_w: float,
    half_d: float,
    track_w: float,
    cr_out: float = 55.0,
    tol: float = 0.20,
    num_arc: int = 12
) -> Dict[str, List[Tuple[float, float]]]:
    cr_in = max(cr_out - track_w, 15.0)
    cx_l, cx_r = -half_w + cr_out, half_w - cr_out
    cy_f, cy_r = half_d - cr_out, -half_d + cr_out

    dt_w = 12.0 if track_w >= 25.0 else 6.5
    dt_d = 7.0 if track_w >= 25.0 else 4.5
    dt_a = 14.0

    quads: Dict[str, List[Tuple[float, float]]] = {}

    # 1. TRK_Front_L: (X in [-half_w, 0], Y in [half_d - track_w, half_d])
    fl: List[Tuple[float, float]] = []
    fl.append((0.0, half_d))
    fl.append((cx_l, half_d))
    for i in range(1, num_arc + 1):
        a = math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        fl.append((cx_l + cr_out * math.cos(a), cy_f + cr_out * math.sin(a)))
    fl.append((-half_w, 0.0))
    tab_l = make_tab_points((-half_w, 0.0), (-half_w + track_w, 0.0), (0.0, -1.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    fl.extend(tab_l[1:])
    fl.append((-half_w + track_w, cy_f))
    for i in range(1, num_arc + 1):
        a = math.pi - (i / num_arc) * (math.pi / 2.0)
        fl.append((cx_l + cr_in * math.cos(a), cy_f + cr_in * math.sin(a)))
    fl.append((0.0, half_d - track_w))
    pock_f = make_pocket_points((0.0, half_d - track_w), (0.0, half_d), (-1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    fl.extend(pock_f[1:])
    quads["TRK_Front_L"] = fl

    # 2. TRK_Front_R: (X in [0, half_w], Y in [half_d - track_w, half_d])
    fr: List[Tuple[float, float]] = []
    fr.append((0.0, half_d))
    tab_f = make_tab_points((0.0, half_d), (0.0, half_d - track_w), (-1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    fr.extend(tab_f[1:])
    fr.append((cx_r, half_d - track_w))
    for i in range(1, num_arc + 1):
        a = math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        fr.append((cx_r + cr_in * math.cos(a), cy_f + cr_in * math.sin(a)))
    fr.append((half_w - track_w, 0.0))
    pock_r = make_pocket_points((half_w - track_w, 0.0), (half_w, 0.0), (0.0, 1.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    fr.extend(pock_r[1:])
    fr.append((half_w, cy_f))
    for i in range(1, num_arc + 1):
        a = (i / num_arc) * (math.pi / 2.0)
        fr.append((cx_r + cr_out * math.cos(a), cy_f + cr_out * math.sin(a)))
    fr.append((cx_r, half_d))
    fr.append((0.0, half_d))
    quads["TRK_Front_R"] = fr

    # 3. TRK_Rear_L: (X in [-half_w, 0], Y in [-half_d, -half_d + track_w])
    rl: List[Tuple[float, float]] = []
    rl.append((-half_w, 0.0))
    pock_l = make_pocket_points((-half_w, 0.0), (-half_w + track_w, 0.0), (0.0, -1.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    rl.extend(pock_l[1:])
    rl.append((-half_w + track_w, cy_r))
    for i in range(1, num_arc + 1):
        a = -math.pi + (i / num_arc) * (math.pi / 2.0)
        rl.append((cx_l + cr_in * math.cos(ang := a), cy_r + cr_in * math.sin(ang)))
    rl.append((0.0, -half_d + track_w))
    tab_rear = make_tab_points((0.0, -half_d + track_w), (0.0, -half_d), (1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    rl.extend(tab_rear[1:])
    rl.append((cx_l, -half_d))
    for i in range(1, num_arc + 1):
        a = -math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        rl.append((cx_l + cr_out * math.cos(a), cy_r + cr_out * math.sin(a)))
    rl.append((-half_w, 0.0))
    quads["TRK_Rear_L"] = rl

    # 4. TRK_Rear_R: (X in [0, half_w], Y in [-half_d, -half_d + track_w])
    rr: List[Tuple[float, float]] = []
    rr.append((0.0, -half_d))
    pock_rear = make_pocket_points((0.0, -half_d), (0.0, -half_d + track_w), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    rr.extend(pock_rear[1:])
    rr.append((cx_r, -half_d + track_w))
    for i in range(1, num_arc + 1):
        a = -math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        rr.append((cx_r + cr_in * math.cos(a), cy_r + cr_in * math.sin(a)))
    rr.append((half_w - track_w, 0.0))
    tab_r = make_tab_points((half_w - track_w, 0.0), (half_w, 0.0), (0.0, 1.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    rr.extend(tab_r[1:])
    rr.append((half_w, cy_r))
    for i in range(1, num_arc + 1):
        a = 0.0 - (i / num_arc) * (math.pi / 2.0)
        rr.append((cx_r + cr_out * math.cos(a), cy_r + cr_out * math.sin(a)))
    rr.append((cx_r, -half_d))
    rr.append((0.0, -half_d))
    quads["TRK_Rear_R"] = rr

    cleaned_dict: Dict[str, List[Tuple[float, float]]] = {}
    for name, raw_pts in quads.items():
        cleaned = []
        for p in raw_pts:
            if not cleaned or math.hypot(p[0]-cleaned[-1][0], p[1]-cleaned[-1][1]) > 1e-3:
                cleaned.append(p)
        if len(cleaned) > 1 and math.hypot(cleaned[0][0]-cleaned[-1][0], cleaned[0][1]-cleaned[-1][1]) < 1e-3:
            cleaned.pop()
        cleaned_dict[name] = cleaned

    return cleaned_dict


def build_system(root_comp: Any, params: SystemParameters):
    sketches = root_comp.sketches
    plane_xy = root_comp.xYConstructionPlane if hasattr(root_comp, "xYConstructionPlane") else None
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0

    half_w = (params.width_mm / 2.0) - params.wall_clearance_mm
    half_d = (params.depth_mm / 2.0) - params.wall_clearance_mm

    quads_base = generate_watertight_quadrants(half_w, half_d, track_w=params.rail_base_width_mm, tol=params.tol_slip_mm)
    quads_neck = generate_watertight_quadrants(half_w, half_d, track_w=params.rail_neck_width_mm, tol=params.tol_slip_mm)

    h_base_cm = params.rail_base_height_mm / 10.0
    h_neck_cm = params.rail_neck_height_mm / 10.0
    h_tot_cm = h_base_cm + h_neck_cm

    # 1. Build 4 Interlocking Two-Tier Track Quadrants as Distinct Solid BRep Bodies
    for name in ["TRK_Front_L", "TRK_Front_R", "TRK_Rear_L", "TRK_Rear_R"]:
        poly_base = quads_base[name]
        poly_neck = quads_neck[name]

        # Step 1: Base flange extrusion as New Body (0 to h_base_cm)
        sketch_b = sketches.add(plane_xy)
        pts_b = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_base]
        for i in range(len(pts_b)):
            sketch_b.sketchCurves.sketchLines.addByTwoPoints(pts_b[i], pts_b[(i + 1) % len(pts_b)])

        body_base = None
        if FUSION_AVAILABLE and len(sketch_b.profiles) > 0:
            ext_b = root_comp.features.extrudeFeatures.addSimple(sketch_b.profiles.item(0), adsk.core.ValueInput.createByReal(h_base_cm), op_new)
            body_base = ext_b.bodies.item(0) if ext_b.bodies.count > 0 else None

        # Step 2: Upper neck extrusion as New Body (0 to h_tot_cm)
        sketch_n = sketches.add(plane_xy)
        pts_n = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_neck]
        for i in range(len(pts_n)):
            sketch_n.sketchCurves.sketchLines.addByTwoPoints(pts_n[i], pts_n[(i + 1) % len(pts_n)])

        body_neck = None
        if FUSION_AVAILABLE and len(sketch_n.profiles) > 0:
            ext_n = root_comp.features.extrudeFeatures.addSimple(sketch_n.profiles.item(0), adsk.core.ValueInput.createByReal(h_tot_cm), op_new)
            body_neck = ext_n.bodies.item(0) if ext_n.bodies.count > 0 else None

        # Step 3: Combine base and neck for THIS quadrant into one solid body
        if FUSION_AVAILABLE and body_base and body_neck:
            tools = adsk.core.ObjectCollection.create()
            tools.add(body_neck)
            combine_input = root_comp.features.combineFeatures.createInput(body_base, tools)
            combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            root_comp.features.combineFeatures.add(combine_input)
            body_base.name = name

    # 2. Build Sliding Upright Post (`PST_Slide_Upright`) with Captive Base Shoe and Slot
    post_x = -150.0  # mm along front rail
    post_y = half_d - params.rail_base_width_mm / 2.0  # Centerline of front rail
    px_cm = post_x / 10.0
    py_cm = post_y / 10.0

    shoe_l_cm = params.shoe_length_mm / 10.0 # 4.0 cm along track
    shoe_w_cm = params.shoe_width_mm / 10.0  # 4.4 cm across track
    shoe_h_cm = params.shoe_height_mm / 10.0 # 2.4 cm

    # Step A: Outer base shoe block
    sketch_shoe = sketches.add(plane_xy)
    sp1 = _create_pt(px_cm - shoe_l_cm / 2.0, py_cm - shoe_w_cm / 2.0, 0.0)
    sp2 = _create_pt(px_cm + shoe_l_cm / 2.0, py_cm + shoe_w_cm / 2.0, 0.0)
    sketch_shoe.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)

    body_shoe = None
    if FUSION_AVAILABLE and len(sketch_shoe.profiles) > 0:
        ext_shoe = root_comp.features.extrudeFeatures.addSimple(sketch_shoe.profiles.item(0), adsk.core.ValueInput.createByReal(shoe_h_cm), op_new)
        body_shoe = ext_shoe.bodies.item(0) if ext_shoe.bodies.count > 0 else None

    # Step B: Upright column
    col_size_cm = params.post_col_size_mm / 10.0
    post_tot_h_cm = params.post_height_mm / 10.0
    sketch_col = sketches.add(plane_xy)
    cp1 = _create_pt(px_cm - col_size_cm / 2.0, py_cm - col_size_cm / 2.0, 0.0)
    cp2 = _create_pt(px_cm + col_size_cm / 2.0, py_cm + col_size_cm / 2.0, 0.0)
    sketch_col.sketchCurves.sketchLines.addTwoPointRectangle(cp1, cp2)

    body_col = None
    if FUSION_AVAILABLE and len(sketch_col.profiles) > 0:
        ext_col = root_comp.features.extrudeFeatures.addSimple(sketch_col.profiles.item(0), adsk.core.ValueInput.createByReal(post_tot_h_cm), op_new)
        body_col = ext_col.bodies.item(0) if ext_col.bodies.count > 0 else None

    # Combine shoe and column into one solid post body
    post_body = None
    if FUSION_AVAILABLE and body_shoe and body_col:
        tools = adsk.core.ObjectCollection.create()
        tools.add(body_col)
        comb_post = root_comp.features.combineFeatures.createInput(body_shoe, tools)
        comb_post.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        root_comp.features.combineFeatures.add(comb_post)
        post_body = body_shoe
        post_body.name = "PST_Slide_Upright"

    # Step C: Cut captive inverted T-slot tunnel through post shoe
    tol_cm = 0.025
    r_bw_cm = (params.rail_base_width_mm / 20.0) + tol_cm  # 1.525 cm
    r_bh_cm = (params.rail_base_height_mm / 10.0) + tol_cm  # 0.825 cm
    r_nw_cm = (params.rail_neck_width_mm / 20.0) + tol_cm  # 0.825 cm
    r_nh_cm = ((params.rail_base_height_mm + params.rail_neck_height_mm) / 10.0) + tol_cm # 1.825 cm

    sketch_tunnel = sketches.add(plane_xy)
    cut_b1 = _create_pt(px_cm - shoe_l_cm, py_cm - r_bw_cm, 0.0)
    cut_b2 = _create_pt(px_cm + shoe_l_cm, py_cm + r_bw_cm, 0.0)
    sketch_tunnel.sketchCurves.sketchLines.addTwoPointRectangle(cut_b1, cut_b2)

    sketch_neck_cut = sketches.add(plane_xy)
    cut_n1 = _create_pt(px_cm - shoe_l_cm, py_cm - r_nw_cm, 0.0)
    cut_n2 = _create_pt(px_cm + shoe_l_cm, py_cm + r_nw_cm, 0.0)
    sketch_neck_cut.sketchCurves.sketchLines.addTwoPointRectangle(cut_n1, cut_n2)

    if FUSION_AVAILABLE and post_body:
        # Cut flange pocket
        if len(sketch_tunnel.profiles) > 0:
            ext_cut1 = root_comp.features.extrudeFeatures.createInput(sketch_tunnel.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext_cut1.setDistanceExtent(False, adsk.core.ValueInput.createByReal(r_bh_cm))
            ext_cut1.participantBodies = [post_body]
            root_comp.features.extrudeFeatures.add(ext_cut1)

        # Cut neck channel
        if len(sketch_neck_cut.profiles) > 0:
            ext_cut2 = root_comp.features.extrudeFeatures.createInput(sketch_neck_cut.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext_cut2.setDistanceExtent(False, adsk.core.ValueInput.createByReal(r_nh_cm))
            ext_cut2.participantBodies = [post_body]
            root_comp.features.extrudeFeatures.add(ext_cut2)

    # Step D: Cut Vertical Guide Slot down the inner face of the post column
    slot_w_cm = params.slot_width_mm / 10.0  # 0.64 cm
    slot_d_cm = params.slot_depth_mm / 10.0  # 0.80 cm
    sketch_slot = sketches.add(plane_xy)
    slp1 = _create_pt(px_cm - slot_w_cm / 2.0, py_cm - col_size_cm / 2.0 - 0.1, 0.0)
    slp2 = _create_pt(px_cm + slot_w_cm / 2.0, py_cm - col_size_cm / 2.0 + slot_d_cm, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(slp1, slp2)

    if FUSION_AVAILABLE and post_body and len(sketch_slot.profiles) > 0:
        ext_cut3 = root_comp.features.extrudeFeatures.createInput(sketch_slot.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        ext_cut3.setDistanceExtent(False, adsk.core.ValueInput.createByReal(post_tot_h_cm))
        ext_cut3.participantBodies = [post_body]
        root_comp.features.extrudeFeatures.add(ext_cut3)

    # 3. Build 6" Modular Interlocking Slat (`SLAT_Segment_6in`) with Male/Female Dovetails
    s_l_cm = params.slat_length_mm / 10.0  # 15.24 cm (6.0 in)
    s_t_cm = params.slat_thickness_mm / 10.0 # 0.50 cm
    s_h_cm = params.slat_height_mm / 10.0   # 6.00 cm

    sketch_slat = sketches.add(plane_xy)
    slat_pts = [
        (-s_l_cm / 2.0, -s_t_cm / 2.0),
        (-s_l_cm / 2.0 - 0.6, -s_t_cm / 4.0),  # Male dovetail tab on left
        (-s_l_cm / 2.0 - 0.6, s_t_cm / 4.0),
        (-s_l_cm / 2.0, s_t_cm / 2.0),
        (s_l_cm / 2.0, s_t_cm / 2.0),
        (s_l_cm / 2.0 - 0.6, s_t_cm / 4.0),   # Female dovetail pocket on right
        (s_l_cm / 2.0 - 0.6, -s_t_cm / 4.0),
        (s_l_cm / 2.0, -s_t_cm / 2.0)
    ]
    s_pts = [_create_pt(p[0], p[1], 0.0) for p in slat_pts]
    for i in range(len(s_pts)):
        sketch_slat.sketchCurves.sketchLines.addByTwoPoints(s_pts[i], s_pts[(i + 1) % len(s_pts)])

    if FUSION_AVAILABLE and len(sketch_slat.profiles) > 0:
        ext_slat = root_comp.features.extrudeFeatures.addSimple(sketch_slat.profiles.item(0), adsk.core.ValueInput.createByReal(s_h_cm), op_new)
        if ext_slat.bodies.count > 0:
            ext_slat.bodies.item(0).name = "SLAT_Segment_6in"


def run(context=None):
    ui = None
    try:
        if FUSION_AVAILABLE:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)

            if not design:
                if ui:
                    ui.messageBox("Please open a document in Fusion 360 (File -> New Design) before running.", "Tesla Model X Frunk")
                return

            try:
                if design.designType != adsk.fusion.DesignTypes.ParametricDesignType:
                    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            except Exception:
                pass

            root_comp = design.rootComponent
        else:
            class MockBodies:
                def __init__(self): self.items = []
                @property
                def count(self): return len(self.items)
                def item(self, idx): return self.items[idx]
            class MockCurves:
                def __init__(self): self.sketchLines = self
                def addByTwoPoints(self, p1, p2): return None
                def addTwoPointRectangle(self, p1, p2): return None
            class MockProfile: pass
            class MockProfiles:
                @property
                def count(self): return 1
                def item(self, idx): return MockProfile()
                def __len__(self): return 1
            class MockSketch:
                def __init__(self):
                    self.sketchCurves = MockCurves()
                    self.profiles = MockProfiles()
            class MockSketches:
                def add(self, plane): return MockSketch()
            class MockExtrudeRes:
                def __init__(self): self.bodies = MockBodies()
            class MockExtrude:
                def addSimple(self, prof, dist, op): return MockExtrudeRes()
                def createInput(self, prof, op): return None
                def add(self, inp): return MockExtrudeRes()
            class MockCombine:
                def createInput(self, target, tools): return None
                def add(self, inp): return None
            class MockFeatures:
                def __init__(self):
                    self.extrudeFeatures = MockExtrude()
                    self.combineFeatures = MockCombine()
            class MockRoot:
                def __init__(self):
                    self.sketches = MockSketches()
                    self.features = MockFeatures()
                    self.bRepBodies = MockBodies()
            root_comp = MockRoot()

        params = SystemParameters()
        build_system(root_comp, params)

        if ui:
            ui.messageBox(
                "Tesla Model X Frunk Modular System Generated Successfully!\n\n"
                "All 4 quadrants now feature the complete Two-Tier Stepped T-Rail:\n"
                "  1. TRK_Front_L (Two-Tier T-Rail with 15° Dovetails)\n"
                "  2. TRK_Front_R (Two-Tier T-Rail with 15° Dovetails)\n"
                "  3. TRK_Rear_L (Two-Tier T-Rail with 15° Dovetails)\n"
                "  4. TRK_Rear_R (Two-Tier T-Rail with 15° Dovetails)\n"
                "  5. PST_Slide_Upright (Sliding Post with wrap-around captive base shoe & guide slot)\n"
                "  6. SLAT_Segment_6in (6-inch modular interlocking cross slat)\n\n"
                "Check the 'Bodies' folder in your Browser Tree!",
                "Modular System Ready"
            )
        else:
            print("Headless Execution Complete!")

    except Exception:
        err_msg = f"Error generating system:\n{traceback.format_exc()}"
        if ui:
            ui.messageBox(err_msg, "Script Error")
        else:
            print(err_msg, file=sys.stderr)


if __name__ == "__main__":
    run(None)
