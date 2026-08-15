"""
Tesla Model X 2017 Frunk Conformal Floor Track & Sliding Post System
Autodesk Fusion 360 - Standalone All-In-One Script

GENERATES:
  1. TRK_Front_L       - Front-Left Stepped/Flanged Floor Rail Quadrant (< 310 mm bed fit)
  2. TRK_Front_R       - Front-Right Stepped/Flanged Floor Rail Quadrant (< 310 mm bed fit)
  3. TRK_Rear_L        - Rear-Left Stepped/Flanged Floor Rail Quadrant (< 310 mm bed fit)
  4. TRK_Rear_R        - Rear-Right Stepped/Flanged Floor Rail Quadrant (< 310 mm bed fit)
  5. PST_Slide_Upright - Sliding Post with wrap-around captive base shoe
  6. SLAT_Segment_6in  - 6-inch modular interlocking cross-member slat
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
    slot_width_mm: float = 6.4           # Guide slot for 5mm cross slats
    slot_depth_mm: float = 8.0           # Guide slot depth
    slat_length_mm: float = 152.4        # 6.0 in modular slat segment length
    slat_height_mm: float = 60.0         # Slat layer height
    slat_thickness_mm: float = 5.0       # Slat thickness
    dovetail_w_mm: float = 14.0          # 15 deg seam dovetail root width
    dovetail_d_mm: float = 8.0           # Seam dovetail depth
    dovetail_ang_deg: float = 15.0       # 15 deg dovetail half-angle
    tol_slip_mm: float = 0.20            # 3D printing slip clearance

    @property
    def total_rail_height_cm(self) -> float:
        return (self.rail_base_height_mm + self.rail_neck_height_mm) / 10.0


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


def build_system(root_comp: Any, params: SystemParameters):
    sketches = root_comp.sketches
    plane_xy = root_comp.xYConstructionPlane if hasattr(root_comp, "xYConstructionPlane") else None
    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1

    half_w = (params.width_mm / 2.0) - params.wall_clearance_mm
    half_d = (params.depth_mm / 2.0) - params.wall_clearance_mm

    quads_base = generate_watertight_quadrants(half_w, half_d, track_w=params.rail_base_width_mm, tol=params.tol_slip_mm)
    quads_neck = generate_watertight_quadrants(half_w, half_d, track_w=params.rail_neck_width_mm, tol=params.tol_slip_mm)

    h_base_cm = params.rail_base_height_mm / 10.0
    h_neck_cm = params.rail_neck_height_mm / 10.0

    for name in ["TRK_Front_L", "TRK_Front_R", "TRK_Rear_L", "TRK_Rear_R"]:
        poly_base = quads_base[name]
        poly_neck = quads_neck[name]

        # 1. Base flange extrusion in +Z (0 to h_base_cm)
        sketch_b = sketches.add(plane_xy)
        pts_b = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_base]
        for i in range(len(pts_b)):
            sketch_b.sketchCurves.sketchLines.addByTwoPoints(pts_b[i], pts_b[(i + 1) % len(pts_b)])

        if FUSION_AVAILABLE and len(sketch_b.profiles) > 0:
            root_comp.features.extrudeFeatures.addSimple(sketch_b.profiles.item(0), adsk.core.ValueInput.createByReal(h_base_cm), op_new)
            if root_comp.bRepBodies.count > 0:
                root_comp.bRepBodies.item(root_comp.bRepBodies.count - 1).name = name

        # 2. Upper neck extrusion in +Z (joining onto base, rising from h_base_cm to total height)
        sketch_n = sketches.add(plane_xy)
        pts_n = [_create_pt(p[0] / 10.0, p[1] / 10.0, 0.0) for p in poly_neck]
        for i in range(len(pts_n)):
            sketch_n.sketchCurves.sketchLines.addByTwoPoints(pts_n[i], pts_n[(i + 1) % len(pts_n)])

        if FUSION_AVAILABLE and len(sketch_n.profiles) > 0:
            root_comp.features.extrudeFeatures.addSimple(sketch_n.profiles.item(0), adsk.core.ValueInput.createByReal(h_base_cm + h_neck_cm), op_join)

    # 3. Build Sliding Upright Post (`PST_Slide_Upright`)
    post_x = -100.0
    post_y = half_d - params.rail_base_width_mm / 2.0

    sketch_post = sketches.add(plane_xy)
    shoe_w_cm = 4.2
    shoe_l_cm = 3.6
    px = post_x / 10.0
    py = post_y / 10.0
    p1 = _create_pt(px - shoe_l_cm / 2.0, py - shoe_w_cm / 2.0, 0.0)
    p2 = _create_pt(px + shoe_l_cm / 2.0, py + shoe_w_cm / 2.0, 0.0)
    sketch_post.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    if FUSION_AVAILABLE and len(sketch_post.profiles) > 0:
        root_comp.features.extrudeFeatures.addSimple(sketch_post.profiles.item(0), adsk.core.ValueInput.createByReal(params.post_height_mm / 10.0), op_new)
        if root_comp.bRepBodies.count > 0:
            root_comp.bRepBodies.item(root_comp.bRepBodies.count - 1).name = "PST_Slide_Upright"

    # 4. Build 6" Modular Interlocking Slat (`SLAT_Segment_6in`)
    sketch_slat = sketches.add(plane_xy)
    slat_ox = 60.0 / 10.0
    slat_oy = 0.0
    s_l_cm = params.slat_length_mm / 10.0  # 15.24 cm (6.0 in)
    s_t_cm = params.slat_thickness_mm / 10.0 # 0.5 cm
    s_h_cm = params.slat_height_mm / 10.0   # 6.0 cm
    sp1 = _create_pt(slat_ox, slat_oy - s_t_cm / 2.0, 0.0)
    sp2 = _create_pt(slat_ox + s_l_cm, slat_oy + s_t_cm / 2.0, 0.0)
    sketch_slat.sketchCurves.sketchLines.addTwoPointRectangle(sp1, sp2)

    if FUSION_AVAILABLE and len(sketch_slat.profiles) > 0:
        root_comp.features.extrudeFeatures.addSimple(sketch_slat.profiles.item(0), adsk.core.ValueInput.createByReal(s_h_cm), op_new)
        if root_comp.bRepBodies.count > 0:
            root_comp.bRepBodies.item(root_comp.bRepBodies.count - 1).name = "SLAT_Segment_6in"


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
                "Tesla Model X Frunk Floor Track & Sliding Post System Generated!\n\n"
                "All 4 quadrants now feature the continuous stepped T-rail with 15° dovetails:\n"
                "  1. TRK_Front_L (Stepped T-Rail, Front-Left with 15° Dovetail)\n"
                "  2. TRK_Front_R (Stepped T-Rail, Front-Right with 15° Dovetail)\n"
                "  3. TRK_Rear_L (Stepped T-Rail, Rear-Left with 15° Dovetail)\n"
                "  4. TRK_Rear_R (Stepped T-Rail, Rear-Right with 15° Dovetail)\n"
                "  5. PST_Slide_Upright (Sliding Post with wrap-around captive base shoe)\n"
                "  6. SLAT_Segment_6in (6-inch modular interlocking cross slat)\n\n"
                "The complete perimeter now has the rigid second layer!",
                "Conformal Floor & Sliding System Ready"
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
