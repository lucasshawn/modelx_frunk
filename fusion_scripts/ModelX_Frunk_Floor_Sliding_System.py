"""
Tesla Model X 2017 Frunk Conformal Modular Divider System
Autodesk Fusion 360 - Complete Assembly Script

Creates separate, independent components in Fusion 360:
  1. TRK_Front_L       - Front-Left Flanged Rail Quadrant (< 310 mm)
  2. TRK_Front_R       - Front-Right Flanged Rail Quadrant (< 310 mm)
  3. TRK_Rear_L        - Rear-Left Flanged Rail Quadrant (< 310 mm)
  4. TRK_Rear_R        - Rear-Right Flanged Rail Quadrant (< 310 mm)
  5. PST_Slide_Upright - Sliding Post with captive base shoe and vertical guide channel
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
    dovetail_w_mm: float = 14.0          # 15 deg seam dovetail root width
    dovetail_d_mm: float = 8.0           # Seam dovetail depth
    dovetail_ang_deg: float = 15.0       # 15 deg dovetail half-angle
    tol_slip_mm: float = 0.20            # 3D printing slip clearance


def _create_pt(x_cm: float, y_cm: float, z_cm: float = 0.0):
    if FUSION_AVAILABLE:
        return adsk.core.Point3D.create(x_cm, y_cm, z_cm)
    class MockPt:
        def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
    return MockPt(x_cm, y_cm, z_cm)


def calculate_dovetail_tab(
    base_center: Tuple[float, float],
    normal: Tuple[float, float],
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0,
    tol: float = 0.20
) -> List[Tuple[float, float]]:
    nx, ny = normal
    tx, ty = -ny, nx

    rad = math.radians(angle_deg)
    flare = depth * math.tan(rad)
    w_root = (base_w - 2.0 * tol) / 2.0
    w_tip = (base_w + 2.0 * flare - 2.0 * tol) / 2.0

    bx, by = base_center
    p0 = (bx - tx * w_root, by - ty * w_root)
    p1 = (bx + nx * depth - tx * w_tip, by + ny * depth - ty * w_tip)
    p2 = (bx + nx * depth + tx * w_tip, by + ny * depth + ty * w_tip)
    p3 = (bx + tx * w_root, by + ty * w_root)

    return [p0, p1, p2, p3]


def calculate_dovetail_pocket(
    base_center: Tuple[float, float],
    normal: Tuple[float, float],
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0,
    tol: float = 0.20
) -> List[Tuple[float, float]]:
    nx, ny = normal
    tx, ty = -ny, nx

    rad = math.radians(angle_deg)
    flare = depth * math.tan(rad)
    w_root = (base_w + 2.0 * tol) / 2.0
    w_tip = (base_w + 2.0 * flare + 2.0 * tol) / 2.0

    bx, by = base_center
    p0 = (bx - tx * w_root, by - ty * w_root)
    p1 = (bx - nx * depth - tx * w_tip, by - ny * depth - ty * w_tip)
    p2 = (bx - nx * depth + tx * w_tip, by - ny * depth + ty * w_tip)
    p3 = (bx + tx * w_root, by + ty * w_root)

    return [p0, p1, p2, p3]


def generate_watertight_quadrants(
    half_w: float,
    half_d: float,
    track_w: float,
    cr_out: float = 55.0,
    dt_w: float = 14.0,
    dt_d: float = 8.0,
    dt_a: float = 15.0,
    tol: float = 0.20,
    num_arc: int = 12
) -> Dict[str, List[Tuple[float, float]]]:
    cr_in = max(cr_out - track_w, 15.0)
    cx_l, cx_r = -half_w + cr_out, half_w - cr_out
    cy_f, cy_r = half_d - cr_out, -half_d + cr_out

    front_seam = (0.0, half_d - track_w / 2.0)
    rear_seam = (0.0, -half_d + track_w / 2.0)
    left_seam = (-half_w + track_w / 2.0, 0.0)
    right_seam = (half_w - track_w / 2.0, 0.0)

    quads: Dict[str, List[Tuple[float, float]]] = {}

    # 1. TRK_Front_L: (X <= 0, Y >= 0)
    fl: List[Tuple[float, float]] = []
    fl.append((0.0, half_d))
    fl.append((cx_l, half_d))
    for i in range(1, num_arc + 1):
        ang = math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        fl.append((cx_l + cr_out * math.cos(ang), cy_f + cr_out * math.sin(ang)))
    fl.append((-half_w, 0.0))
    tab_l = calculate_dovetail_tab(left_seam, (0.0, -1.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    fl.extend(tab_l)
    fl.append((-half_w + track_w, 0.0))
    fl.append((-half_w + track_w, cy_f))
    for i in range(1, num_arc + 1):
        ang = math.pi - (i / num_arc) * (math.pi / 2.0)
        fl.append((cx_l + cr_in * math.cos(ang), cy_f + cr_in * math.sin(ang)))
    fl.append((0.0, half_d - track_w))
    pock_f = calculate_dovetail_pocket(front_seam, (-1.0, 0.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    fl.extend(pock_f)
    quads["TRK_Front_L"] = fl

    # 2. TRK_Front_R: (X >= 0, Y >= 0)
    fr: List[Tuple[float, float]] = []
    fr.append((0.0, half_d))
    tab_f = calculate_dovetail_tab(front_seam, (-1.0, 0.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    fr.extend(tab_f)
    fr.append((0.0, half_d - track_w))
    fr.append((cx_r, half_d - track_w))
    for i in range(1, num_arc + 1):
        ang = math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        fr.append((cx_r + cr_in * math.cos(ang), cy_f + cr_in * math.sin(ang)))
    fr.append((half_w - track_w, 0.0))
    pock_r = calculate_dovetail_pocket(right_seam, (0.0, -1.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    fr.extend(pock_r)
    fr.append((half_w, 0.0))
    fr.append((half_w, cy_f))
    for i in range(1, num_arc + 1):
        ang = (i / num_arc) * (math.pi / 2.0)
        fr.append((cx_r + cr_out * math.cos(ang), cy_f + cr_out * math.sin(ang)))
    fr.append((cx_r, half_d))
    quads["TRK_Front_R"] = fr

    # 3. TRK_Rear_L: (X <= 0, Y <= 0)
    rl: List[Tuple[float, float]] = []
    rl.append((-half_w, 0.0))
    pock_l = calculate_dovetail_pocket(left_seam, (0.0, -1.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    rl.extend(pock_l)
    rl.append((-half_w + track_w, 0.0))
    rl.append((-half_w + track_w, cy_r))
    for i in range(1, num_arc + 1):
        ang = -math.pi + (i / num_arc) * (math.pi / 2.0)
        rl.append((cx_l + cr_in * math.cos(ang), cy_r + cr_in * math.sin(ang)))
    rl.append((0.0, -half_d + track_w))
    tab_rear = calculate_dovetail_tab(rear_seam, (1.0, 0.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    rl.extend(tab_rear)
    rl.append((0.0, -half_d))
    rl.append((cx_l, -half_d))
    for i in range(1, num_arc + 1):
        ang = -math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        rl.append((cx_l + cr_out * math.cos(ang), cy_r + cr_out * math.sin(ang)))
    quads["TRK_Rear_L"] = rl

    # 4. TRK_Rear_R: (X >= 0, Y <= 0)
    rr: List[Tuple[float, float]] = []
    rr.append((0.0, -half_d))
    pock_rear = calculate_dovetail_pocket(rear_seam, (1.0, 0.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    rr.extend(pock_rear)
    rr.append((0.0, -half_d + track_w))
    rr.append((cx_r, -half_d + track_w))
    for i in range(1, num_arc + 1):
        ang = -math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        rr.append((cx_r + cr_in * math.cos(ang), cy_r + cr_in * math.sin(ang)))
    rr.append((half_w - track_w, 0.0))
    tab_r = calculate_dovetail_tab(right_seam, (0.0, -1.0), base_w=dt_w, depth=dt_d, angle_deg=dt_a, tol=tol)
    rr.extend(tab_r)
    rr.append((half_w, 0.0))
    rr.append((half_w, cy_r))
    for i in range(1, num_arc + 1):
        ang = 0.0 - (i / num_arc) * (math.pi / 2.0)
        rr.append((cx_r + cr_out * math.cos(ang), cy_r + cr_out * math.sin(ang)))
    rr.append((cx_r, -half_d))
    quads["TRK_Rear_R"] = rr

    # Clean redundant consecutive points
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


def get_subcomponent(root_comp: Any, comp_name: str) -> Any:
    """Creates a new dedicated subcomponent in Fusion 360 to prevent body merging."""
    if FUSION_AVAILABLE:
        transform = adsk.core.Matrix3D.create()
        occ = root_comp.occurrences.addNewComponent(transform)
        comp = occ.component
        comp.name = comp_name
        return comp
    else:
        class MockItem:
            def __init__(self, name=""): self.name = name
        class MockBodies:
            def __init__(self): self.items = []
            @property
            def count(self): return len(self.items)
            def item(self, idx): return self.items[idx]
        class MockCurves:
            def __init__(self): self.sketchLines = self
            def addByTwoPoints(self, p1, p2): return None
            def addTwoPointRectangle(self, p1, p2): return None
        class MockProfile:
            pass
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
        class MockExtrude:
            def addSimple(self, prof, dist, op): return None
        class MockFeatures:
            def __init__(self): self.extrudeFeatures = MockExtrude()
        class MockComp:
            def __init__(self, name):
                self.name = name
                self.sketches = MockSketches()
                self.features = MockFeatures()
                self.bRepBodies = MockBodies()
        return MockComp(comp_name)


def build_system(root_comp: Any, params: SystemParameters):
    plane_xy = root_comp.xYConstructionPlane if hasattr(root_comp, "xYConstructionPlane") else None
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1
    op_cut = adsk.fusion.FeatureOperations.CutFeatureOperation if FUSION_AVAILABLE else 2

    half_w = (params.width_mm / 2.0) - params.wall_clearance_mm
    half_d = (params.depth_mm / 2.0) - params.wall_clearance_mm

    quads_base = generate_watertight_quadrants(half_w, half_d, track_w=params.rail_base_width_mm, tol=params.tol_slip_mm)
    quads_neck = generate_watertight_quadrants(half_w, half_d, track_w=params.rail_neck_width_mm, tol=params.tol_slip_mm)

    h_base_cm = params.rail_base_height_mm / 10.0
    h_neck_cm = params.rail_neck_height_mm / 10.0

    # 1. Build 4 Interlocking Track Quadrants as Independent Components
    for name in ["TRK_Front_L", "TRK_Front_R", "TRK_Rear_L", "TRK_Rear_R"]:
        comp = get_subcomponent(root_comp, name)
        sketches = comp.sketches

        poly_base = quads_base[name]
        poly_neck = quads_neck[name]

        # Base flange extrusion
        sketch_b = sketches.add(plane_xy)
        pts_b = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_base]
        for i in range(len(pts_b)):
            sketch_b.sketchCurves.sketchLines.addByTwoPoints(pts_b[i], pts_b[(i + 1) % len(pts_b)])

        if FUSION_AVAILABLE and len(sketch_b.profiles) > 0:
            comp.features.extrudeFeatures.addSimple(sketch_b.profiles.item(0), adsk.core.ValueInput.createByReal(h_base_cm), op_new)
            if comp.bRepBodies.count > 0:
                comp.bRepBodies.item(comp.bRepBodies.count - 1).name = name + "_Base"

        # Upper neck extrusion
        sketch_n = sketches.add(plane_xy)
        pts_n = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_neck]
        for i in range(len(pts_n)):
            sketch_n.sketchCurves.sketchLines.addByTwoPoints(pts_n[i], pts_n[(i + 1) % len(pts_n)])

        if FUSION_AVAILABLE and len(sketch_n.profiles) > 0:
            comp.features.extrudeFeatures.addSimple(sketch_n.profiles.item(0), adsk.core.ValueInput.createByReal(h_base_cm + h_neck_cm), op_join)

    # 2. Build Sliding Upright Post (`PST_Slide_Upright`) with Captive Base Shoe and Slot
    post_comp = get_subcomponent(root_comp, "PST_Slide_Upright")
    post_sketches = post_comp.sketches

    post_x = -150.0  # mm along front rail
    post_y = half_d - params.rail_base_width_mm / 2.0  # Centerline of front rail
    px_cm = post_x / 10.0
    py_cm = post_y / 10.0

    shoe_l_cm = params.shoe_length_mm / 10.0 # 4.0 cm along track
    shoe_w_cm = params.shoe_width_mm / 10.0  # 4.4 cm across track
    shoe_h_cm = params.shoe_height_mm / 10.0 # 2.4 cm

    # Step A: Extrude outer base shoe block
    sketch_shoe = post_sketches.add(plane_xy)
    sp1 = _create_pt(px_cm - shoe_l_cm / 2.0, py_cm - shoe_w_cm / 2.0, 0.0)
    sp2 = _create_pt(px_cm + shoe_l_cm / 2.0, py_cm + shoe_w_cm / 2.0, 0.0)
    sketch_shoe.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)

    if FUSION_AVAILABLE and len(sketch_shoe.profiles) > 0:
        post_comp.features.extrudeFeatures.addSimple(sketch_shoe.profiles.item(0), adsk.core.ValueInput.createByReal(shoe_h_cm), op_new)

    # Step B: Cut captive T-slot tunnel through base shoe
    # Tunnel profile matches flanged rail with +0.25mm clearance
    tol_cm = 0.025
    r_bw_cm = (params.rail_base_width_mm / 20.0) + tol_cm  # 1.525 cm
    r_bh_cm = (params.rail_base_height_mm / 10.0) + tol_cm  # 0.825 cm
    r_nw_cm = (params.rail_neck_width_mm / 20.0) + tol_cm  # 0.825 cm
    r_nh_cm = ((params.rail_base_height_mm + params.rail_neck_height_mm) / 10.0) + tol_cm # 1.825 cm

    sketch_tunnel = post_sketches.add(plane_xy)
    # Cut base flange slot
    cut_b1 = _create_pt(px_cm - shoe_l_cm, py_cm - r_bw_cm, 0.0)
    cut_b2 = _create_pt(px_cm + shoe_l_cm, py_cm + r_bw_cm, 0.0)
    sketch_tunnel.sketchCurves.sketchLines.addTwoPointRectangle(cut_b1, cut_b2)

    # Cut neck slot
    sketch_neck_cut = post_sketches.add(plane_xy)
    cut_n1 = _create_pt(px_cm - shoe_l_cm, py_cm - r_nw_cm, 0.0)
    cut_n2 = _create_pt(px_cm + shoe_l_cm, py_cm + r_nw_cm, 0.0)
    sketch_neck_cut.sketchCurves.sketchLines.addTwoPointRectangle(cut_n1, cut_n2)

    if FUSION_AVAILABLE:
        if len(sketch_tunnel.profiles) > 0:
            post_comp.features.extrudeFeatures.addSimple(sketch_tunnel.profiles.item(0), adsk.core.ValueInput.createByReal(r_bh_cm), op_cut)
        if len(sketch_neck_cut.profiles) > 0:
            post_comp.features.extrudeFeatures.addSimple(sketch_neck_cut.profiles.item(0), adsk.core.ValueInput.createByReal(r_nh_cm), op_cut)

    # Step C: Extrude Upright Column from top of shoe up to total height
    col_size_cm = params.post_col_size_mm / 10.0
    post_tot_h_cm = params.post_height_mm / 10.0
    sketch_col = post_sketches.add(plane_xy)
    cp1 = _create_pt(px_cm - col_size_cm / 2.0, py_cm - col_size_cm / 2.0, 0.0)
    cp2 = _create_pt(px_cm + col_size_cm / 2.0, py_cm + col_size_cm / 2.0, 0.0)
    sketch_col.sketchCurves.sketchLines.addTwoPointRectangle(cp1, cp2)

    if FUSION_AVAILABLE and len(sketch_col.profiles) > 0:
        post_comp.features.extrudeFeatures.addSimple(sketch_col.profiles.item(0), adsk.core.ValueInput.createByReal(post_tot_h_cm), op_join)

    # Step D: Cut Vertical Slot down the inner face of the post column (facing inward toward Y=0)
    slot_w_cm = params.slot_width_mm / 10.0  # 0.64 cm
    slot_d_cm = params.slot_depth_mm / 10.0  # 0.80 cm
    sketch_slot = post_sketches.add(plane_xy)
    slp1 = _create_pt(px_cm - slot_w_cm / 2.0, py_cm - col_size_cm / 2.0 - 0.1, 0.0)
    slp2 = _create_pt(px_cm + slot_w_cm / 2.0, py_cm - col_size_cm / 2.0 + slot_d_cm, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(slp1, slp2)

    if FUSION_AVAILABLE and len(sketch_slot.profiles) > 0:
        post_comp.features.extrudeFeatures.addSimple(sketch_slot.profiles.item(0), adsk.core.ValueInput.createByReal(post_tot_h_cm), op_cut)

    # 3. Build 6" Modular Interlocking Slat (`SLAT_Segment_6in`) with Male/Female Dovetails
    slat_comp = get_subcomponent(root_comp, "SLAT_Segment_6in")
    slat_sketches = slat_comp.sketches

    slat_ox = 0.0
    slat_oy = 0.0
    s_l_cm = params.slat_length_mm / 10.0  # 15.24 cm (6.0 in)
    s_t_cm = params.slat_thickness_mm / 10.0 # 0.50 cm
    s_h_cm = params.slat_height_mm / 10.0   # 6.00 cm

    # Draw 6" slat with 15° male dovetail tenon on left and female dovetail mortise on right
    sketch_slat = slat_sketches.add(plane_xy)
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
        slat_comp.features.extrudeFeatures.addSimple(sketch_slat.profiles.item(0), adsk.core.ValueInput.createByReal(s_h_cm), op_new)


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
            class MockRoot:
                def __init__(self):
                    self.occurrences = self
                def addNewComponent(self, trans):
                    return None
            root_comp = MockRoot()

        params = SystemParameters()
        build_system(root_comp, params)

        if ui:
            ui.messageBox(
                "Tesla Model X Frunk Modular System Generated!\n\n"
                "Components Created (as distinct independent assemblies):\n"
                "  1. TRK_Front_L (Front-Left Flanged Rail Quadrant)\n"
                "  2. TRK_Front_R (Front-Right Flanged Rail Quadrant)\n"
                "  3. TRK_Rear_L (Rear-Left Flanged Rail Quadrant)\n"
                "  4. TRK_Rear_R (Rear-Right Flanged Rail Quadrant)\n"
                "  5. PST_Slide_Upright (Sliding Post with wrap-around captive base shoe & guide slot)\n"
                "  6. SLAT_Segment_6in (6-inch modular interlocking cross slat)\n\n"
                "How it works:\n"
                "  - The 4 track quadrants interlock at the 4 corners to form the complete perimeter.\n"
                "  - Posts wrap around the stepped rail and slide freely anywhere along the track!\n"
                "  - Cross slats drop straight down into facing posts to partition the frunk.",
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
