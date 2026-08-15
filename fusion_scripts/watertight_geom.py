import math
from typing import Dict, List, Tuple

def make_tab_points(
    p_start: Tuple[float, float],
    p_end: Tuple[float, float],
    ext_vec: Tuple[float, float],
    tab_w: float = 12.0,
    tab_d: float = 7.0,
    flare_ang: float = 14.0,
    tol: float = 0.20
) -> List[Tuple[float, float]]:
    """
    Creates counter-clockwise male dovetail tab points along a seam edge from p_start to p_end.
    ext_vec is unit vector in direction of tab extension (outward into neighboring part).
    """
    ex, ey = ext_vec
    # Tangent vector along seam edge (from p_start towards p_end)
    dx = p_end[0] - p_start[0]
    dy = p_end[1] - p_start[1]
    edge_len = math.hypot(dx, dy)
    tx, ty = dx / edge_len, dy / edge_len

    mid_x = (p_start[0] + p_end[0]) / 2.0
    mid_y = (p_start[1] + p_end[1]) / 2.0

    flare = tab_d * math.tan(math.radians(flare_ang))
    w_root = (tab_w - 2.0 * tol) / 2.0
    w_tip = (tab_w + 2.0 * flare - 2.0 * tol) / 2.0

    # Along the seam edge: p0 (root start) -> p1 (tip start) -> p2 (tip end) -> p3 (root end)
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
    """
    Creates counter-clockwise female dovetail pocket points along a seam edge from p_start to p_end.
    int_vec is unit vector in direction of pocket indentation (inward into this part).
    """
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

    # Indents into part in direction int_vec:
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

    # Scale dovetail appropriately for base flange vs neck
    dt_w = 12.0 if track_w >= 25.0 else 6.5
    dt_d = 7.0 if track_w >= 25.0 else 4.5
    dt_a = 14.0

    quads: Dict[str, List[Tuple[float, float]]] = {}

    # 1. TRK_Front_L: (X in [-half_w, 0], Y in [half_d - track_w, half_d])
    # CCW: Outer top (0, half_d) -> Front-Left arc -> Left outer (-half_w, 0)
    #      -> Left Seam: Male Tab (extending in -Y) to (-half_w + track_w, 0)
    #      -> Inner arc to (0, half_d - track_w)
    #      -> Front Seam: Female Pocket (indenting in -X) to (0, half_d)
    fl: List[Tuple[float, float]] = []
    fl.append((0.0, half_d))
    fl.append((cx_l, half_d))
    for i in range(1, num_arc + 1):
        a = math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        fl.append((cx_l + cr_out * math.cos(a), cy_f + cr_out * math.sin(a)))
    fl.append((-half_w, 0.0))
    # Left seam: goes from (-half_w, 0) to (-half_w + track_w, 0), tab extends in -Y
    tab_l = make_tab_points((-half_w, 0.0), (-half_w + track_w, 0.0), (0.0, -1.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    fl.extend(tab_l[1:])
    fl.append((-half_w + track_w, cy_f))
    for i in range(1, num_arc + 1):
        a = math.pi - (i / num_arc) * (math.pi / 2.0)
        fl.append((cx_l + cr_in * math.cos(a), cy_f + cr_in * math.sin(a)))
    fl.append((0.0, half_d - track_w))
    # Front seam: goes from (0, half_d - track_w) to (0, half_d), pocket indents in -X
    pock_f = make_pocket_points((0.0, half_d - track_w), (0.0, half_d), (-1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    fl.extend(pock_f[1:])
    quads["TRK_Front_L"] = fl

    # 2. TRK_Front_R: (X in [0, half_w], Y in [half_d - track_w, half_d])
    # CCW: Front Seam: Male Tab (extending in -X) from (0, half_d) to (0, half_d - track_w)
    #      -> Inner arc to (half_w - track_w, 0)
    #      -> Right Seam: Female Pocket (indenting in +Y) to (half_w, 0)
    #      -> Outer arc to (cx_r, half_d) -> (0, half_d)
    fr: List[Tuple[float, float]] = []
    fr.append((0.0, half_d))
    tab_f = make_tab_points((0.0, half_d), (0.0, half_d - track_w), (-1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    fr.extend(tab_f[1:])
    fr.append((cx_r, half_d - track_w))
    for i in range(1, num_arc + 1):
        a = math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        fr.append((cx_r + cr_in * math.cos(a), cy_f + cr_in * math.sin(a)))
    fr.append((half_w - track_w, 0.0))
    # Right seam: goes from (half_w - track_w, 0) to (half_w, 0), pocket indents in +Y
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
    # CCW: Left Seam: Female Pocket (indenting in -Y) from (-half_w, 0) to (-half_w + track_w, 0)
    #      -> Inner arc to (0, -half_d + track_w)
    #      -> Rear Seam: Male Tab (extending in +X) to (0, -half_d)
    #      -> Outer arc to (-half_w, cy_r) -> (-half_w, 0)
    rl: List[Tuple[float, float]] = []
    rl.append((-half_w, 0.0))
    pock_l = make_pocket_points((-half_w, 0.0), (-half_w + track_w, 0.0), (0.0, -1.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    rl.extend(pock_l[1:])
    rl.append((-half_w + track_w, cy_r))
    for i in range(1, num_arc + 1):
        a = -math.pi + (i / num_arc) * (math.pi / 2.0)
        rl.append((cx_l + cr_in * math.cos(a), cy_r + cr_in * math.sin(a)))
    rl.append((0.0, -half_d + track_w))
    # Rear seam: goes from (0, -half_d + track_w) to (0, -half_d), tab extends in +X
    tab_rear = make_tab_points((0.0, -half_d + track_w), (0.0, -half_d), (1.0, 0.0), tab_w=dt_w, tab_d=dt_d, flare_ang=dt_a, tol=tol)
    rl.extend(tab_rear[1:])
    rl.append((cx_l, -half_d))
    for i in range(1, num_arc + 1):
        a = -math.pi / 2.0 - (i / num_arc) * (math.pi / 2.0)
        rl.append((cx_l + cr_out * math.cos(a), cy_r + cr_out * math.sin(a)))
    rl.append((-half_w, 0.0))
    quads["TRK_Rear_L"] = rl

    # 4. TRK_Rear_R: (X in [0, half_w], Y in [-half_d, -half_d + track_w])
    # CCW: Rear Seam: Female Pocket (indenting in +X) from (0, -half_d) to (0, -half_d + track_w)
    #      -> Inner arc to (half_w - track_w, 0)
    #      -> Right Seam: Male Tab (extending in +Y) to (half_w, 0)
    #      -> Outer arc to (0, -half_d)
    rr: List[Tuple[float, float]] = []
    rr.append((0.0, -half_d))
    pock_rear = make_pocket_points((0.0, -half_d), (0.0, -half_d + track_w), (1.0, 0.0), pocket_w=dt_w, pocket_d=dt_d, flare_ang=dt_a, tol=tol)
    rr.extend(pock_rear[1:])
    rr.append((cx_r, -half_d + track_w))
    for i in range(1, num_arc + 1):
        a = -math.pi / 2.0 + (i / num_arc) * (math.pi / 2.0)
        rr.append((cx_r + cr_in * math.cos(a), cy_r + cr_in * math.sin(a)))
    rr.append((half_w - track_w, 0.0))
    # Right seam: goes from (half_w - track_w, 0) to (half_w, 0), tab extends in +Y
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
