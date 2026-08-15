"""
Tesla Model X 2017 Frunk Conformal Modular Divider System
Autodesk Fusion 360 - Super-Compact Modular Assembly Script

ALL track pieces are strictly UNDER 185 mm (~7.2 in) to fit easily on any 3D printer build plate!

GENERATES:
  1. TRK_Cap_L        - Left U-Bend End Cap (182.6 x 62.0 mm)
  2. TRK_Front_1      - Front Rail Segment 1 (175.2 x 30.0 mm)
  3. TRK_Front_2      - Front Rail Segment 2 (175.2 x 30.0 mm)
  4. TRK_Front_3      - Front Rail Segment 3 (182.2 x 30.0 mm)
  5. TRK_Front_4      - Front Rail Segment 4 (175.2 x 30.0 mm)
  6. TRK_Cap_R        - Right U-Bend End Cap (182.6 x 62.0 mm)
  7. TRK_Rear_4       - Rear Rail Segment 4 (182.2 x 30.0 mm)
  8. TRK_Rear_3       - Rear Rail Segment 3 (182.2 x 30.0 mm)
  9. TRK_Rear_2       - Rear Rail Segment 2 (182.2 x 30.0 mm)
  10. TRK_Rear_1      - Rear Rail Segment 1 (182.2 x 30.0 mm)
  11. PST_Slide_Upright - Sliding Post with wrap-around captive base shoe & guide slot
  12. SLAT_Segment_6in  - 6-inch modular interlocking cross-member divider slat
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
    shoe_width_mm: float = 40.0          # Base shoe width
    shoe_length_mm: float = 42.0         # Base shoe length along track
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


def generate_modular_segments_compact(
    half_w: float = 391.3,
    half_d: float = 91.3,
    track_w: float = 30.0,
    cr_out: float = 55.0,
    tol: float = 0.20,
    num_arc: int = 12
) -> Dict[str, List[Tuple[float, float]]]:
    cr_in = max(cr_out - track_w, 15.0)
    cx_l = -half_w + cr_out  # -336.3
    cx_r = half_w - cr_out   # +336.3
    cy_f = half_d - cr_out   # +36.3
    cy_r = -half_d + cr_out  # -36.3

    dt_w = 12.0 if track_w >= 25.0 else 6.5
    dt_d = 7.0 if track_w >= 25.0 else 4.5
    dt_a = 14.0

    x_f1, x_f2, x_f3, x_f4, x_f5 = cx_l, cx_l / 2.0, 0.0, cx_r / 2.0, cx_r

    segs: Dict[str, List[Tuple[float, float]]] = {}

    # 1. TRK_Cap_L (Left U-Bend)
    cap_l = []
    cap_l.append((cx_l, half_d))
    for i in range(num_arc + 1):
        a = math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        cap_l.append((cx_l + cr_out * math.cos(a), cy_f + cr_out * math.sin(a)))
    cap_l.append((-half_w, cy_r))
    for i in range(num_arc + 1):
        a = math.pi + (i / num_arc) * (math.pi / 2.0)
        cap_l.append((cx_l + cr_out * math.cos(a), cy_r + cr_out * math.sin(a)))
    cap_l.append((cx_l, -half_d))
    pock_b = make_pocket_points((cx_l, -half_d), (cx_l, -half_d + track_w), (-1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    cap_l.extend(pock_b[1:])
    for i in range(num_arc + 1):
        a = -math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        cap_l.append((cx_l + cr_in * math.cos(a), cy_r + cr_in * math.sin(a)))
    cap_l.append((-half_w + track_w, cy_f))
    for i in range(num_arc + 1):
        a = math.pi - (i / num_arc) * (math.pi / 2.0)
        cap_l.append((cx_l + cr_in * math.cos(a), cy_f + cr_in * math.sin(a)))
    cap_l.append((cx_l, half_d - track_w))
    tab_t = make_tab_points((cx_l, half_d - track_w), (cx_l, half_d), (1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    cap_l.extend(tab_t[1:])
    segs["TRK_Cap_L"] = cap_l

    # 2. TRK_Front_1 (cx_l to x_f2)
    f1 = []
    f1.append((x_f1, half_d))
    f1.append((x_f2, half_d))
    tab_f1 = make_tab_points((x_f2, half_d), (x_f2, half_d - track_w), (1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    f1.extend(tab_f1[1:])
    f1.append((x_f1, half_d - track_w))
    pock_f1 = make_pocket_points((x_f1, half_d - track_w), (x_f1, half_d), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    f1.extend(pock_f1[1:])
    segs["TRK_Front_1"] = f1

    # 3. TRK_Front_2 (x_f2 to 0)
    f2 = []
    f2.append((x_f2, half_d))
    f2.append((x_f3, half_d))
    tab_f2 = make_tab_points((x_f3, half_d), (x_f3, half_d - track_w), (1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    f2.extend(tab_f2[1:])
    f2.append((x_f2, half_d - track_w))
    pock_f2 = make_pocket_points((x_f2, half_d - track_w), (x_f2, half_d), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    f2.extend(pock_f2[1:])
    segs["TRK_Front_2"] = f2

    # 4. TRK_Front_3 (0 to x_f4)
    f3 = []
    f3.append((x_f3, half_d))
    f3.append((x_f4, half_d))
    tab_f3 = make_tab_points((x_f4, half_d), (x_f4, half_d - track_w), (1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    f3.extend(tab_f3[1:])
    f3.append((x_f3, half_d - track_w))
    pock_f3 = make_pocket_points((x_f3, half_d - track_w), (x_f3, half_d), (-1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    f3.extend(pock_f3[1:])
    segs["TRK_Front_3"] = f3

    # 5. TRK_Front_4 (x_f4 to cx_r)
    f4 = []
    f4.append((x_f4, half_d))
    f4.append((x_f5, half_d))
    tab_f4 = make_tab_points((x_f5, half_d), (x_f5, half_d - track_w), (1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    f4.extend(tab_f4[1:])
    f4.append((x_f4, half_d - track_w))
    pock_f4 = make_pocket_points((x_f4, half_d - track_w), (x_f4, half_d), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    f4.extend(pock_f4[1:])
    segs["TRK_Front_4"] = f4

    # 6. TRK_Cap_R (Right U-Bend)
    cap_r = []
    cap_r.append((cx_r, half_d))
    for i in range(num_arc + 1):
        a = math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        cap_r.append((cx_r + cr_out * math.cos(a), cy_f + cr_out * math.sin(a)))
    cap_r.append((half_w, cy_r))
    for i in range(num_arc + 1):
        a = 0.0 - (i / num_arc) * (math.pi / 2.0)
        cap_r.append((cx_r + cr_out * math.cos(a), cy_r + cr_out * math.sin(a)))
    cap_r.append((cx_r, -half_d))
    tab_rc = make_tab_points((cx_r, -half_d), (cx_r, -half_d + track_w), (-1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    cap_r.extend(tab_rc[1:])
    for i in range(num_arc + 1):
        a = -math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        cap_r.append((cx_r + cr_in * math.cos(a), cy_r + cr_in * math.sin(a)))
    cap_r.append((half_w - track_w, cy_f))
    for i in range(num_arc + 1):
        a = (i / num_arc) * (math.pi / 2.0)
        cap_r.append((cx_r + cr_in * math.cos(a), cy_f + cr_in * math.sin(a)))
    cap_r.append((cx_r, half_d - track_w))
    pock_rc = make_pocket_points((cx_r, half_d - track_w), (cx_r, half_d), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    cap_r.extend(pock_rc[1:])
    segs["TRK_Cap_R"] = cap_r

    # 7. TRK_Rear_4 (cx_r to x_f4)
    r4 = []
    r4.append((x_f5, -half_d))
    pock_r4 = make_pocket_points((x_f5, -half_d), (x_f5, -half_d + track_w), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    r4.extend(pock_r4[1:])
    r4.append((x_f4, -half_d + track_w))
    tab_r4 = make_tab_points((x_f4, -half_d + track_w), (x_f4, -half_d), (-1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    r4.extend(tab_r4[1:])
    r4.append((x_f5, -half_d))
    segs["TRK_Rear_4"] = r4

    # 8. TRK_Rear_3 (x_f4 to 0)
    r3 = []
    r3.append((x_f4, -half_d))
    pock_r3 = make_pocket_points((x_f4, -half_d), (x_f4, -half_d + track_w), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    r3.extend(pock_r3[1:])
    r3.append((x_f3, -half_d + track_w))
    tab_r3 = make_tab_points((x_f3, -half_d + track_w), (x_f3, -half_d), (-1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    r3.extend(tab_r3[1:])
    r3.append((x_f4, -half_d))
    segs["TRK_Rear_3"] = r3

    # 9. TRK_Rear_2 (0 to x_f2)
    r2 = []
    r2.append((x_f3, -half_d))
    pock_r2 = make_pocket_points((x_f3, -half_d), (x_f3, -half_d + track_w), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    r2.extend(pock_r2[1:])
    r2.append((x_f2, -half_d + track_w))
    tab_r2 = make_tab_points((x_f2, -half_d + track_w), (x_f2, -half_d), (-1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    r2.extend(tab_r2[1:])
    r2.append((x_f3, -half_d))
    segs["TRK_Rear_2"] = r2

    # 10. TRK_Rear_1 (x_f2 to cx_l)
    r1 = []
    r1.append((x_f2, -half_d))
    pock_r1 = make_pocket_points((x_f2, -half_d), (x_f2, -half_d + track_w), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    r1.extend(pock_r1[1:])
    r1.append((x_f1, -half_d + track_w))
    tab_r1 = make_tab_points((x_f1, -half_d + track_w), (x_f1, -half_d), (-1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    r1.extend(tab_r1[1:])
    r1.append((x_f2, -half_d))
    segs["TRK_Rear_1"] = r1

    cleaned_dict: Dict[str, List[Tuple[float, float]]] = {}
    for name, raw_pts in segs.items():
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

    segs_base = generate_modular_segments_compact(half_w, half_d, track_w=params.rail_base_width_mm, tol=params.tol_slip_mm)
    segs_neck = generate_modular_segments_compact(half_w, half_d, track_w=params.rail_neck_width_mm, tol=params.tol_slip_mm)

    h_base_cm = params.rail_base_height_mm / 10.0
    h_neck_cm = params.rail_neck_height_mm / 10.0
    h_tot_cm = h_base_cm + h_neck_cm

    # 1. Build 10 Super-Compact Track Segments (All < 185 mm)
    for name in [
        "TRK_Cap_L", "TRK_Front_1", "TRK_Front_2", "TRK_Front_3", "TRK_Front_4",
        "TRK_Cap_R", "TRK_Rear_4", "TRK_Rear_3", "TRK_Rear_2", "TRK_Rear_1"
    ]:
        poly_base = segs_base[name]
        poly_neck = segs_neck[name]

        # Step 1: Base flange extrusion
        sketch_b = sketches.add(plane_xy)
        pts_b = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_base]
        for i in range(len(pts_b)):
            sketch_b.sketchCurves.sketchLines.addByTwoPoints(pts_b[i], pts_b[(i + 1) % len(pts_b)])

        body_base = None
        if FUSION_AVAILABLE and len(sketch_b.profiles) > 0:
            ext_b = root_comp.features.extrudeFeatures.addSimple(sketch_b.profiles.item(0), adsk.core.ValueInput.createByReal(h_base_cm), op_new)
            body_base = ext_b.bodies.item(0) if ext_b.bodies.count > 0 else None

        # Step 2: Upper neck extrusion
        sketch_n = sketches.add(plane_xy)
        pts_n = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_neck]
        for i in range(len(pts_n)):
            sketch_n.sketchCurves.sketchLines.addByTwoPoints(pts_n[i], pts_n[(i + 1) % len(pts_n)])

        body_neck = None
        if FUSION_AVAILABLE and len(sketch_n.profiles) > 0:
            ext_n = root_comp.features.extrudeFeatures.addSimple(sketch_n.profiles.item(0), adsk.core.ValueInput.createByReal(h_tot_cm), op_new)
            body_neck = ext_n.bodies.item(0) if ext_n.bodies.count > 0 else None

        # Step 3: Combine base and neck for THIS segment
        if FUSION_AVAILABLE and body_base and body_neck:
            tools = adsk.core.ObjectCollection.create()
            tools.add(body_neck)
            combine_input = root_comp.features.combineFeatures.createInput(body_base, tools)
            combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            root_comp.features.combineFeatures.add(combine_input)
            body_base.name = name

    # 2. Build Sliding Upright Post (`PST_Slide_Upright`)
    post_x = -100.0  # mm along front rail
    px_cm = post_x / 10.0

    shoe_l_cm = params.shoe_length_mm / 10.0
    shoe_w_cm = params.shoe_width_mm / 10.0
    shoe_h_cm = params.shoe_height_mm / 10.0

    shoe_y_max_cm = (half_d + 4.0) / 10.0
    shoe_y_min_cm = (half_d + 4.0 - params.shoe_width_mm) / 10.0

    sketch_shoe = sketches.add(plane_xy)
    sp1 = _create_pt(px_cm - shoe_l_cm / 2.0, shoe_y_min_cm, 0.0)
    sp2 = _create_pt(px_cm + shoe_l_cm / 2.0, shoe_y_max_cm, 0.0)
    sketch_shoe.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)

    body_shoe = None
    if FUSION_AVAILABLE and len(sketch_shoe.profiles) > 0:
        ext_shoe = root_comp.features.extrudeFeatures.addSimple(sketch_shoe.profiles.item(0), adsk.core.ValueInput.createByReal(shoe_h_cm), op_new)
        body_shoe = ext_shoe.bodies.item(0) if ext_shoe.bodies.count > 0 else None

    col_size_cm = params.post_col_size_mm / 10.0
    post_tot_h_cm = params.post_height_mm / 10.0
    col_y_center_cm = (half_d - params.rail_neck_width_mm / 2.0) / 10.0

    sketch_col = sketches.add(plane_xy)
    cp1 = _create_pt(px_cm - col_size_cm / 2.0, col_y_center_cm - col_size_cm / 2.0, 0.0)
    cp2 = _create_pt(px_cm + col_size_cm / 2.0, col_y_center_cm + col_size_cm / 2.0, 0.0)
    sketch_col.sketchCurves.sketchLines.addTwoPointRectangle(cp1, cp2)

    body_col = None
    if FUSION_AVAILABLE and len(sketch_col.profiles) > 0:
        ext_col = root_comp.features.extrudeFeatures.addSimple(sketch_col.profiles.item(0), adsk.core.ValueInput.createByReal(post_tot_h_cm), op_new)
        body_col = ext_col.bodies.item(0) if ext_col.bodies.count > 0 else None

    post_body = None
    if FUSION_AVAILABLE and body_shoe and body_col:
        tools = adsk.core.ObjectCollection.create()
        tools.add(body_col)
        comb_post = root_comp.features.combineFeatures.createInput(body_shoe, tools)
        comb_post.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        root_comp.features.combineFeatures.add(comb_post)
        post_body = body_shoe
        post_body.name = "PST_Slide_Upright"

    # Inverted T-slot tunnel cut
    tol_cm = 0.025
    r_bw_cm = (params.rail_base_width_mm / 10.0) + tol_cm
    r_bh_cm = (params.rail_base_height_mm / 10.0) + tol_cm
    r_nw_cm = (params.rail_neck_width_mm / 10.0) + tol_cm
    r_nh_cm = ((params.rail_base_height_mm + params.rail_neck_height_mm) / 10.0) + tol_cm
    rail_outer_y_cm = (half_d + 0.25) / 10.0

    sketch_tunnel = sketches.add(plane_xy)
    cut_b1 = _create_pt(px_cm - shoe_l_cm, rail_outer_y_cm - r_bw_cm, 0.0)
    cut_b2 = _create_pt(px_cm + shoe_l_cm, rail_outer_y_cm, 0.0)
    sketch_tunnel.sketchCurves.sketchLines.addTwoPointRectangle(cut_b1, cut_b2)

    sketch_neck_cut = sketches.add(plane_xy)
    cut_n1 = _create_pt(px_cm - shoe_l_cm, rail_outer_y_cm - r_nw_cm, 0.0)
    cut_n2 = _create_pt(px_cm + shoe_l_cm, rail_outer_y_cm, 0.0)
    sketch_neck_cut.sketchCurves.sketchLines.addTwoPointRectangle(cut_n1, cut_n2)

    if FUSION_AVAILABLE and post_body:
        if len(sketch_tunnel.profiles) > 0:
            ext_cut1 = root_comp.features.extrudeFeatures.createInput(sketch_tunnel.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext_cut1.setDistanceExtent(False, adsk.core.ValueInput.createByReal(r_bh_cm))
            ext_cut1.participantBodies = [post_body]
            root_comp.features.extrudeFeatures.add(ext_cut1)

        if len(sketch_neck_cut.profiles) > 0:
            ext_cut2 = root_comp.features.extrudeFeatures.createInput(sketch_neck_cut.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext_cut2.setDistanceExtent(False, adsk.core.ValueInput.createByReal(r_nh_cm))
            ext_cut2.participantBodies = [post_body]
            root_comp.features.extrudeFeatures.add(ext_cut2)

    # Vertical Guide Slot
    slot_w_cm = params.slot_width_mm / 10.0
    slot_d_cm = params.slot_depth_mm / 10.0
    sketch_slot = sketches.add(plane_xy)
    slp1 = _create_pt(px_cm - slot_w_cm / 2.0, col_y_center_cm - col_size_cm / 2.0 - 0.1, 0.0)
    slp2 = _create_pt(px_cm + slot_w_cm / 2.0, col_y_center_cm - col_size_cm / 2.0 + slot_d_cm, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(slp1, slp2)

    if FUSION_AVAILABLE and post_body and len(sketch_slot.profiles) > 0:
        ext_cut3 = root_comp.features.extrudeFeatures.createInput(sketch_slot.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        ext_cut3.setDistanceExtent(False, adsk.core.ValueInput.createByReal(post_tot_h_cm))
        ext_cut3.participantBodies = [post_body]
        root_comp.features.extrudeFeatures.add(ext_cut3)

    # 3. Build 6" Modular Slat (`SLAT_Segment_6in`)
    s_l_cm = params.slat_length_mm / 10.0
    s_t_cm = params.slat_thickness_mm / 10.0
    s_h_cm = params.slat_height_mm / 10.0

    slat_cx_cm = px_cm
    slat_cy_cm = (col_y_center_cm - col_size_cm / 2.0) - (s_l_cm / 2.0)

    sketch_slat = sketches.add(plane_xy)
    slat_pts = [
        (slat_cx_cm - s_t_cm / 2.0, slat_cy_cm - s_l_cm / 2.0),
        (slat_cx_cm - s_t_cm / 4.0, slat_cy_cm - s_l_cm / 2.0 - 0.6),
        (slat_cx_cm + s_t_cm / 4.0, slat_cy_cm - s_l_cm / 2.0 - 0.6),
        (slat_cx_cm + s_t_cm / 2.0, slat_cy_cm - s_l_cm / 2.0),
        (slat_cx_cm + s_t_cm / 2.0, slat_cy_cm + s_l_cm / 2.0),
        (slat_cx_cm + s_t_cm / 4.0, slat_cy_cm + s_l_cm / 2.0 - 0.6),
        (slat_cx_cm - s_t_cm / 4.0, slat_cy_cm + s_l_cm / 2.0 - 0.6),
        (slat_cx_cm - s_t_cm / 2.0, slat_cy_cm + s_l_cm / 2.0)
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
                "All 10 track pieces are strictly UNDER 185 mm (~7.2 in) to fit any print bed:\n"
                "  • 2x Curved End Caps: TRK_Cap_L, TRK_Cap_R (182.6 mm)\n"
                "  • 4x Front Rails: TRK_Front_1, TRK_Front_2, TRK_Front_3, TRK_Front_4 (175–182 mm)\n"
                "  • 4x Rear Rails: TRK_Rear_1, TRK_Rear_2, TRK_Rear_3, TRK_Rear_4 (182 mm)\n"
                "  • 1x Sliding Post: PST_Slide_Upright\n"
                "  • 1x 6\" Modular Slat: SLAT_Segment_6in\n\n"
                "Check the 'Bodies' folder in your Browser Tree!",
                "Super-Compact Modular System Ready"
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
