import math
from typing import Dict, List, Tuple

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
