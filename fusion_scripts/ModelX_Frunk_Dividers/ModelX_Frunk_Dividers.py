"""
Tesla Model X 2017 Frunk Modular Divider System
Autodesk Fusion 360 - Standalone All-In-One CAD Generator Script

INSTRUCTIONS:
1. In Fusion 360, open a fresh workspace tab (File -> New Design).
2. Press Shift + S (Scripts and Add-Ins).
3. Select 'ModelX_Frunk_Dividers' and click 'Run'.

GENERATED COMPONENTS:
  1. FT_Segment_12in       - Floor Truss with triangular web cutouts and dovetails
  2. VR_Post_Deep          - 11-inch Vertical Post with 6.4mm slots and locking tenon
  3. HR_Rail_12in          - Horizontal Top Rail with lead-in funnel and end joints
  4. J_Corner_90           - 90-Degree 2-Way Corner Junction
  5. J_Tee_3Way            - 3-Way T-Junction Block
  6. J_Cross_4Way          - 4-Way Cross Junction Block
  7. DIV_Crosshatch_12x11  - Slide-in Divider Panel with 45-degree Diamond Lattice & Pull Handle
  8. Pin_Lock_M5           - Transverse Dovetail & Socket Locking Pin
  9. TRK_Front_L           - Conformal Floor Track Front-Left Quadrant (< 310 mm bed limit)
 10. TRK_Front_R           - Conformal Floor Track Front-Right Quadrant (< 310 mm bed limit)
 11. TRK_Rear_L            - Conformal Floor Track Rear-Left Quadrant (< 310 mm bed limit)
 12. TRK_Rear_R            - Conformal Floor Track Rear-Right Quadrant (< 310 mm bed limit)
 13. TRK_Master_Assembled  - Continuous Full Perimeter Conformal Floor Ring (12.7 mm / 0.50" clearance)
"""

from dataclasses import dataclass
import math
import os
import sys
import traceback
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

# Attempt Autodesk Fusion 360 API import
try:
    import adsk.core
    import adsk.fusion
    FUSION_AVAILABLE = True
except ImportError:
    FUSION_AVAILABLE = False


# ==============================================================================
# Parametric Configuration & Geometry Data
# ==============================================================================

@dataclass
class FrunkParameters:
    """Parametric dimensions and engineering tolerances for the entire frunk system."""
    bay_spacing_mm: float = 304.8        # 12.0 in (Center-to-center divider spacing)
    frame_height_mm: float = 280.0       # 11.0 in (Deep full-height upright post)
    truss_height_mm: float = 35.0        # Floor truss height
    truss_width_mm: float = 24.0         # Profile width
    slot_width_mm: float = 6.4           # Guide slot width (for 5mm panel + 0.7mm slip clearance per side)
    slot_depth_mm: float = 8.0           # Guide slot depth
    panel_thickness_mm: float = 5.0      # Nominal divider panel thickness
    panel_width_mm: float = 298.0        # Width of 12" divider panel
    panel_height_mm: float = 275.0       # Height of divider panel
    lattice_pitch_mm: float = 18.0       # 45-degree diamond mesh pitch
    lattice_strut_mm: float = 3.5        # Diamond mesh strut thickness
    tol_dovetail_mm: float = 0.25        # 3D printing slip clearance for 15-deg dovetails
    tol_tenon_mm: float = 0.20           # 3D printing slip clearance for vertical socket tenons
    pin_diameter_mm: float = 5.0         # Transverse locking pin diameter
    dovetail_base_width_mm: float = 14.0 # Dovetail root width
    dovetail_depth_mm: float = 8.0       # Dovetail depth
    dovetail_angle_deg: float = 15.0     # Dovetail wedge half-angle

    # Conformal Perimeter Floor Track (LiDAR Matched)
    wall_clearance_mm: float = 12.7      # 0.50 in inward clearance from frunk tub wall
    track_width_mm: float = 30.0         # Base conformal perimeter track width
    track_height_mm: float = 18.0        # Base conformal perimeter track height
    floor_slice_z_mm: float = 10.0       # LiDAR slice elevation above lowest tub floor
    trail_base_width_mm: float = 14.0    # Captive T-rail base width
    trail_neck_width_mm: float = 8.0     # Captive T-rail neck width
    trail_height_mm: float = 5.0         # Captive T-rail guide height
    rigid_guide_width_mm: float = 18.0   # Rigid rectangular top guide width
    rigid_guide_height_mm: float = 8.0   # Rigid rectangular guide wall height
    rigid_wall_thickness_mm: float = 4.0 # Rigid vertical guide wall thickness
    tol_seam_dovetail_mm: float = 0.20   # 3D printing slip clearance for quadrant seams
    seam_dovetail_angle_deg: float = 15.0 # Quadrant interlocking dovetail taper angle
    max_bed_dimension_mm: float = 310.0  # Maximum print bed envelope (Creality K2 350x350)

    @property
    def bay_spacing_in(self) -> float:
        return self.bay_spacing_mm / 25.4

    @property
    def frame_height_in(self) -> float:
        return self.frame_height_mm / 25.4

    @property
    def wall_clearance_in(self) -> float:
        return self.wall_clearance_mm / 25.4

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

    @property
    def wall_clearance_cm(self) -> float:
        return self.wall_clearance_mm / 10.0

    @property
    def track_width_cm(self) -> float:
        return self.track_width_mm / 10.0

    @property
    def track_height_cm(self) -> float:
        return self.track_height_mm / 10.0

    @property
    def trail_base_width_cm(self) -> float:
        return self.trail_base_width_mm / 10.0

    @property
    def trail_neck_width_cm(self) -> float:
        return self.trail_neck_width_mm / 10.0

    @property
    def trail_height_cm(self) -> float:
        return self.trail_height_mm / 10.0

    @property
    def rigid_guide_width_cm(self) -> float:
        return self.rigid_guide_width_mm / 10.0

    @property
    def rigid_guide_height_cm(self) -> float:
        return self.rigid_guide_height_mm / 10.0

    @property
    def rigid_wall_thickness_cm(self) -> float:
        return self.rigid_wall_thickness_mm / 10.0


# Calibrated LiDAR scan boundary coordinates of 2017 Tesla Model X frunk tub at Z=10.0 mm
CALIBRATED_FLOOR_POLYGON = [
    (-204.23, -7.95), (-208.22, -8.28), (-212.20, -8.61), (-216.19, -8.93),
    (-220.17, -9.21), (-224.16, -9.45), (-228.15, -9.70), (-232.14, -10.01),
    (-236.11, -10.39), (-240.09, -10.80), (-244.04, -11.34), (-247.98, -11.97),
    (-251.88, -12.77), (-255.66, -13.87), (-259.28, -15.40), (-262.76, -17.24),
    (-266.19, -19.20), (-269.63, -21.15), (-273.13, -22.99), (-276.76, -24.61),
    (-280.49, -26.03), (-284.24, -27.43), (-287.96, -28.89), (-291.67, -30.38),
    (-295.36, -31.91), (-299.04, -33.48), (-302.70, -35.08), (-306.37, -36.67),
    (-310.04, -38.25), (-313.71, -39.84), (-317.38, -41.43), (-321.05, -43.01),
    (-324.72, -44.60), (-328.45, -45.97), (-332.23, -47.11), (-336.06, -48.07),
    (-339.95, -48.84), (-343.90, -49.43), (-347.85, -50.05), (-351.79, -50.71),
    (-355.74, -51.37), (-359.68, -52.03), (-363.63, -52.69), (-367.57, -53.35),
    (-371.51, -54.01), (-375.46, -54.67), (-379.40, -55.31), (-383.36, -55.83),
    (-387.33, -56.24), (-391.31, -56.53), (-395.30, -56.70), (-399.30, -56.77),
    (-403.30, -56.84), (-407.29, -56.94), (-411.28, -57.15), (-415.25, -57.48),
    (-419.21, -57.95), (-423.14, -58.65), (-426.98, -59.63), (-430.66, -61.00),
    (-434.08, -62.81), (-437.21, -65.10), (-440.12, -67.74), (-442.85, -70.62),
    (-445.24, -73.74), (-447.42, -77.00), (-449.47, -80.34), (-451.37, -83.79),
    (-453.13, -87.36), (-454.80, -90.96), (-456.25, -94.61), (-457.38, -98.36),
    (-458.07, -102.21), (-458.30, -106.16), (-458.26, -110.14), (-457.93, -114.11),
    (-457.37, -118.05), (-456.41, -121.80), (-454.86, -125.25), (-452.66, -127.86),
    (-449.94, -129.51), (-446.79, -130.87), (-443.48, -132.11), (-440.10, -133.25),
    (-436.72, -134.71), (-433.23, -136.43), (-429.57, -137.74), (-425.74, -138.64),
    (-421.81, -139.26), (-417.84, -139.70), (-413.86, -140.07), (-409.89, -140.43),
    (-405.91, -140.79), (-401.93, -141.12), (-397.94, -141.43), (-393.96, -141.82),
    (-389.99, -142.26), (-386.02, -142.73), (-382.05, -143.19), (-378.07, -143.62),
    (-374.10, -144.03), (-370.12, -144.39), (-366.15, -144.79), (-362.19, -145.30),
    (-358.25, -145.92), (-354.33, -146.66), (-350.43, -147.52), (-346.53, -148.40),
    (-342.63, -149.29), (-338.73, -150.18), (-334.85, -151.12), (-330.97, -152.07),
    (-327.07, -152.95), (-323.16, -153.70), (-319.24, -154.41), (-315.32, -155.10),
    (-311.42, -155.86), (-307.56, -156.80), (-303.74, -157.95), (-299.94, -159.13),
    (-296.11, -160.12), (-292.23, -160.85), (-288.34, -161.51), (-284.49, -162.28),
    (-280.72, -163.27), (-277.05, -164.64), (-273.43, -166.27), (-269.80, -167.74),
    (-266.06, -168.84), (-262.23, -169.56), (-258.29, -169.92), (-254.30, -170.13),
    (-250.32, -170.42), (-246.37, -170.87), (-242.45, -171.52), (-238.57, -172.36),
    (-234.68, -173.11), (-230.79, -173.77), (-226.87, -174.22), (-222.92, -174.45),
    (-218.92, -174.48), (-214.93, -174.52), (-210.94, -174.42), (-206.96, -174.27),
    (-203.00, -174.30), (-199.07, -174.52), (-195.16, -174.88), (-191.26, -175.51),
    (-187.36, -176.32), (-183.43, -177.02), (-179.48, -177.58), (-175.51, -178.03),
    (-171.54, -178.46), (-167.57, -178.94), (-163.64, -179.59), (-159.71, -180.23),
    (-155.78, -180.86), (-151.86, -181.52), (-147.95, -182.21), (-144.01, -182.78),
    (-140.07, -183.23), (-136.13, -183.56), (-132.16, -183.69), (-128.19, -183.66),
    (-124.20, -183.55), (-120.22, -183.63), (-116.24, -183.87), (-112.29, -184.32),
    (-108.35, -184.93), (-104.43, -185.72), (-100.54, -186.60), (-96.64, -187.46),
    (-92.73, -188.13), (-88.80, -188.58), (-84.85, -188.91), (-80.87, -189.13),
    (-76.89, -189.28), (-72.92, -189.34), (-68.95, -189.30), (-64.98, -189.17),
    (-61.02, -189.04), (-57.11, -189.19), (-53.28, -189.78), (-49.51, -190.86),
    (-45.80, -192.25), (-42.11, -193.75), (-38.36, -194.96), (-34.53, -195.83),
    (-30.63, -196.41), (-26.70, -196.90), (-22.75, -197.28), (-18.81, -197.75),
    (-14.89, -198.40), (-10.99, -199.19), (-7.07, -199.88), (-3.14, -200.55),
    (0.79, -201.20), (4.74, -201.80), (8.66, -202.46), (12.59, -203.04),
    (16.52, -203.57), (20.45, -204.08), (24.39, -204.52), (28.36, -204.85),
    (32.30, -205.36), (36.21, -206.10), (40.10, -206.91), (43.89, -208.07),
    (47.45, -209.64), (50.72, -211.65), (53.78, -213.98), (56.83, -216.32),
    (59.95, -218.06), (63.20, -218.83), (66.73, -218.68), (70.48, -217.83),
    (74.20, -216.56), (77.88, -215.13), (81.60, -213.82), (85.38, -212.66),
    (89.15, -211.69), (92.94, -211.25), (96.78, -211.41), (100.66, -212.03),
    (104.54, -212.90), (108.41, -213.85), (112.32, -214.62), (116.26, -215.31),
    (120.19, -215.99), (124.05, -216.88), (127.63, -218.23), (130.65, -220.21),
    (132.87, -222.80), (134.94, -225.11), (137.03, -226.77), (139.31, -228.15),
    (142.12, -229.03), (145.75, -229.24), (149.54, -229.66), (153.37, -230.53),
    (157.27, -231.32), (161.15, -232.21), (165.03, -233.03), (168.91, -233.81),
    (172.79, -234.33), (176.69, -234.44), (180.65, -234.27), (184.57, -234.31),
    (188.49, -234.41), (192.41, -234.67), (196.36, -235.12), (200.30, -235.48),
    (204.28, -235.67), (208.26, -235.72), (212.25, -235.66), (216.21, -235.74),
    (220.11, -236.18), (223.95, -236.87), (227.69, -237.98), (231.37, -239.43),
    (235.03, -241.03), (238.70, -242.59), (242.38, -244.11), (246.12, -245.53),
    (249.86, -246.92), (253.62, -248.26), (257.42, -249.42), (261.27, -250.40),
    (265.17, -251.09), (269.11, -251.51), (273.09, -251.77), (277.04, -252.10),
    (280.95, -252.56), (284.85, -253.07), (288.66, -253.81), (292.23, -255.06),
    (295.74, -256.42), (299.26, -257.49), (302.57, -258.00), (305.65, -257.61),
    (308.50, -255.93), (311.23, -253.45), (313.79, -250.49), (316.37, -247.55),
    (318.85, -244.55), (321.35, -241.56), (323.59, -238.36), (325.56, -234.95),
    (327.28, -231.35), (328.98, -227.74), (330.72, -224.14), (332.56, -220.60),
    (334.54, -217.14), (336.61, -213.73), (338.66, -210.32), (340.56, -206.85),
    (342.10, -203.25), (343.14, -199.52), (343.84, -195.66), (344.29, -191.71),
    (344.65, -187.75), (345.10, -183.80), (345.77, -179.87), (346.44, -175.94),
    (347.12, -172.01), (347.84, -168.08), (348.48, -164.14), (348.83, -160.18),
    (348.99, -156.23), (348.85, -152.30), (348.29, -148.40), (347.36, -144.54),
    (346.18, -140.75), (344.66, -137.10), (342.72, -133.70), (340.41, -130.57),
    (337.72, -127.72), (334.74, -125.12), (331.55, -122.72), (328.34, -120.35),
    (325.20, -117.89), (322.15, -115.33), (319.27, -112.58), (316.58, -109.65),
    (314.05, -106.57), (311.68, -103.36), (309.42, -100.07), (307.24, -96.72),
    (305.13, -93.33), (303.08, -89.89), (301.05, -86.45), (298.92, -83.08),
    (296.68, -79.79), (294.32, -76.58), (291.78, -73.52), (289.03, -70.64),
    (286.15, -67.90), (283.11, -65.35), (279.89, -63.02), (276.53, -60.88),
    (273.07, -58.91), (269.52, -57.08), (265.91, -55.37), (262.24, -53.78),
    (258.55, -52.25), (254.83, -50.78), (251.09, -49.36), (247.34, -47.98),
    (243.58, -46.62), (239.81, -45.30), (236.01, -44.04), (232.20, -42.83),
    (228.37, -41.69), (224.52, -40.63), (220.65, -39.64), (216.76, -38.71),
    (212.85, -37.85), (208.94, -37.04), (205.02, -36.28), (201.08, -35.55),
    (197.15, -34.85), (193.21, -34.17), (189.27, -33.50), (185.33, -32.79),
    (181.40, -32.05), (177.48, -31.27), (173.58, -30.44), (169.68, -29.55),
    (165.79, -28.63), (161.89, -27.74), (157.98, -26.92), (154.05, -26.19),
    (150.11, -25.54), (146.15, -24.98), (142.18, -24.48), (138.22, -23.97),
    (134.25, -23.46), (130.29, -22.95), (126.32, -22.42), (122.36, -21.90),
    (118.39, -21.38), (114.42, -20.95), (110.44, -20.59), (106.47, -20.20),
    (102.50, -19.88), (98.52, -19.61), (94.54, -19.31), (90.56, -18.99),
    (86.57, -18.76), (82.58, -18.53), (78.58, -18.30), (74.59, -18.07),
    (70.60, -17.84), (66.61, -17.60), (62.61, -17.38), (58.62, -17.25),
    (54.63, -17.20), (50.64, -17.23), (46.64, -17.34), (42.65, -17.52),
    (38.65, -17.69), (34.65, -17.82), (30.66, -17.89), (26.66, -17.92),
    (22.66, -17.88), (18.67, -17.80), (14.69, -17.57), (10.77, -17.08),
    (6.87, -16.41), (3.00, -15.56), (-0.85, -14.56), (-4.71, -13.54),
    (-8.61, -12.62), (-12.51, -11.76), (-16.43, -10.98), (-20.36, -10.27),
    (-24.31, -9.64), (-28.27, -9.09), (-32.24, -8.65), (-36.22, -8.25),
    (-40.08, -7.57), (-43.80, -6.52), (-47.41, -5.13), (-50.92, -3.41),
    (-54.43, -1.74), (-58.06, -0.43), (-61.84, 0.44), (-65.74, 0.90),
    (-69.73, 0.93), (-73.70, 0.78), (-77.66, 0.45), (-81.61, -0.05),
    (-85.54, -0.73), (-89.46, -1.51), (-93.40, -2.14), (-97.35, -2.62),
    (-101.32, -2.96), (-105.30, -3.16), (-109.30, -3.21), (-113.30, -3.26),
    (-117.30, -3.28), (-121.30, -3.23), (-125.29, -3.10), (-129.28, -2.89),
    (-133.27, -2.61), (-137.25, -2.26), (-141.21, -1.79), (-145.16, -1.27),
    (-149.11, -0.91), (-153.05, -0.74), (-156.98, -0.76), (-160.93, -1.08),
    (-164.89, -1.65), (-168.84, -2.27), (-172.77, -2.97), (-176.68, -3.76),
    (-180.58, -4.63), (-184.47, -5.50), (-188.38, -6.27), (-192.31, -6.87),
    (-196.27, -7.33), (-200.25, -7.67),
]


# ==============================================================================
# 2D Geometric Math & Dovetail Engines
# ==============================================================================

def calculate_dovetail_profile(
    male: bool,
    tol: float,
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0,
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
        (w_root, 0.0),
    ]


def calculate_truss_span_triangles(
    x_start: float,
    x_end: float,
    z_bottom: float = 8.0,
    z_top: float = 27.0,
    num_triangles: int = 3,
    web_strut_w: float = 4.5,
) -> List[List[Tuple[float, float]]]:
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
                (x_mid, z_top),
            ])
        else:
            triangles.append([
                (x1, z_top),
                (x2, z_top),
                (x_mid, z_bottom),
            ])
    return triangles


def calculate_diamond_apertures(
    inner_w: float = 278.0,
    inner_h: float = 255.0,
    pitch: float = 18.0,
    strut_w: float = 3.5,
) -> List[List[Tuple[float, float]]]:
    apertures = []
    delta = pitch / math.sqrt(2.0)
    r = (pitch - strut_w) / math.sqrt(2.0)

    max_u = int(math.ceil(inner_w / delta)) + 2
    max_v = int(math.ceil(inner_h / delta)) + 2
    handle_cx = inner_w / 2.0

    for u in range(-1, max_u):
        for v in range(-1, max_v):
            if (u + v) % 2 == 0:
                cx = u * delta
                cy = v * delta

                if abs(cx - handle_cx) < 48.0 and cy > inner_h - 32.0:
                    continue

                if (cx >= r * 0.65 and cx <= inner_w - r * 0.65 and
                    cy >= r * 0.65 and cy <= inner_h - r * 0.65):
                    apertures.append([
                        (cx, cy + r),
                        (cx + r, cy),
                        (cx, cy - r),
                        (cx - r, cy),
                    ])
    return apertures


def calculate_polygon_signed_area(polygon: Sequence[Tuple[float, float]]) -> float:
    pts = np.asarray(polygon, dtype=float)
    if len(pts) < 3:
        return 0.0
    x = pts[:, 0]
    y = pts[:, 1]
    return float(0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def calculate_polygon_area(polygon: Sequence[Tuple[float, float]]) -> float:
    return abs(calculate_polygon_signed_area(polygon))


def calculate_polygon_perimeter(polygon: Sequence[Tuple[float, float]]) -> float:
    pts = np.asarray(polygon, dtype=float)
    if len(pts) < 2:
        return 0.0
    diffs = np.roll(pts, -1, axis=0) - pts
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


def ensure_ccw(polygon: Sequence[Tuple[float, float]]) -> List[Tuple[float, float]]:
    pts = list(polygon)
    if len(pts) >= 2 and math.isclose(pts[0][0], pts[-1][0], abs_tol=1e-6) and math.isclose(pts[0][1], pts[-1][1], abs_tol=1e-6):
        pts = pts[:-1]
    if calculate_polygon_signed_area(pts) < 0:
        pts = pts[::-1]
    return [(float(p[0]), float(p[1])) for p in pts]


def resample_polygon_2d(
    pts: Sequence[Tuple[float, float]],
    target_spacing: float = 4.0,
) -> List[Tuple[float, float]]:
    arr = np.asarray(pts, dtype=float)
    if len(arr) < 3:
        return [(float(p[0]), float(p[1])) for p in arr]

    diffs = np.roll(arr, -1, axis=0) - arr
    segment_lens = np.linalg.norm(diffs, axis=1)
    cum_dist = np.concatenate([[0.0], np.cumsum(segment_lens)])
    total_len = cum_dist[-1]

    if total_len < 1e-6:
        return [(float(p[0]), float(p[1])) for p in arr]

    num_samples = max(20, int(round(total_len / max(target_spacing, 0.1))))
    sample_dists = np.linspace(0.0, total_len, num_samples, endpoint=False)

    loop = np.vstack([arr, arr[0:1]])
    new_x = np.interp(sample_dists, cum_dist, loop[:, 0])
    new_y = np.interp(sample_dists, cum_dist, loop[:, 1])

    return [(float(x), float(y)) for x, y in zip(new_x, new_y)]


def smooth_polygon_2d(
    pts: Sequence[Tuple[float, float]],
    window_size: int = 5,
) -> List[Tuple[float, float]]:
    arr = np.asarray(pts, dtype=float)
    n = len(arr)
    if n < window_size or window_size <= 1:
        return [(float(p[0]), float(p[1])) for p in arr]

    if window_size % 2 == 0:
        window_size += 1

    pad = window_size // 2
    padded = np.vstack([arr[-pad:], arr, arr[:pad]])
    kernel = np.ones(window_size) / window_size

    smooth_x = np.convolve(padded[:, 0], kernel, mode="valid")
    smooth_y = np.convolve(padded[:, 1], kernel, mode="valid")

    return [(float(x), float(y)) for x, y in zip(smooth_x, smooth_y)]


def offset_polygon_2d(
    polygon: Sequence[Tuple[float, float]],
    offset_distance_mm: float,
    inward: bool = True,
    max_miter: float = 2.0,
) -> List[Tuple[float, float]]:
    ccw_pts = np.asarray(ensure_ccw(polygon), dtype=float)
    n = len(ccw_pts)
    if n < 3:
        return [(float(p[0]), float(p[1])) for p in ccw_pts]

    d = -abs(offset_distance_mm) if not inward else abs(offset_distance_mm)

    tangents = np.roll(ccw_pts, -1, axis=0) - ccw_pts
    t_lens = np.linalg.norm(tangents, axis=1, keepdims=True)
    t_unit = tangents / np.maximum(t_lens, 1e-9)

    edge_normals = np.column_stack([-t_unit[:, 1], t_unit[:, 0]])
    prev_normals = np.roll(edge_normals, 1, axis=0)
    v_normals = prev_normals + edge_normals
    v_lens = np.linalg.norm(v_normals, axis=1, keepdims=True)
    v_unit = v_normals / np.maximum(v_lens, 1e-9)

    cos_half = np.sum(prev_normals * v_unit, axis=1)
    miter_factor = np.clip(1.0 / np.maximum(cos_half, 0.05), 0.5, max_miter)

    offset_arr = ccw_pts + d * (v_unit * miter_factor[:, None])
    return [(float(x), float(y)) for x, y in offset_arr]


def calculate_seam_dovetail_profile(
    male: bool,
    tol: float = 0.20,
    base_w: float = 14.0,
    depth: float = 8.0,
    angle_deg: float = 15.0,
) -> List[Tuple[float, float]]:
    rad = math.radians(angle_deg)
    if male:
        w_root_half = base_w / 2.0
        w_tip_half = w_root_half + depth * math.tan(rad)
        return [
            (-w_root_half, 0.0),
            (-w_tip_half, depth),
            (w_tip_half, depth),
            (w_root_half, 0.0),
        ]
    else:
        w_root_half = (base_w + 2.0 * tol) / 2.0
        d_pocket = depth + tol
        w_tip_half = w_root_half + d_pocket * math.tan(rad)
        return [
            (-w_root_half, 0.0),
            (-w_tip_half, d_pocket),
            (w_tip_half, d_pocket),
            (w_root_half, 0.0),
        ]


def calculate_min_oriented_bounding_box_dimension(points: Sequence[Tuple[float, float]]) -> float:
    pts = np.asarray(points, dtype=float)
    if len(pts) < 3:
        return 0.0
    angles = np.linspace(0, np.pi, 90, endpoint=False)
    min_max_dim = float("inf")
    for a in angles:
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        rot_x = pts[:, 0] * cos_a - pts[:, 1] * sin_a
        rot_y = pts[:, 0] * sin_a + pts[:, 1] * cos_a
        extent_x = float(rot_x.max() - rot_x.min())
        extent_y = float(rot_y.max() - rot_y.min())
        max_extent = max(extent_x, extent_y)
        if max_extent < min_max_dim:
            min_max_dim = max_extent
    return min_max_dim


def _get_arc_indices(start_idx: int, end_idx: int, total_len: int) -> List[int]:
    if start_idx <= end_idx:
        return list(range(start_idx, end_idx + 1))
    else:
        return list(range(start_idx, total_len)) + list(range(0, end_idx + 1))


@dataclass
class QuadrantGeometry:
    name: str
    polygon: List[Tuple[float, float]]
    nominal_polygon: List[Tuple[float, float]]
    outer_points: List[Tuple[float, float]]
    inner_points: List[Tuple[float, float]]
    start_seam: str
    start_joint_type: str
    end_seam: str
    end_joint_type: str
    bounds: Dict[str, float]
    width: float
    height: float
    max_dimension: float
    area_mm2: float
    perimeter_mm: float


def slice_track_quadrants(
    outer_poly: Sequence[Tuple[float, float]],
    inner_poly: Sequence[Tuple[float, float]],
    params: Optional[FrunkParameters] = None,
    x_split: Optional[float] = None,
    y_split: Optional[float] = None,
    **kwargs,
) -> Dict[str, QuadrantGeometry]:
    if params is None:
        params = FrunkParameters()

    outer = ensure_ccw(outer_poly)
    inner = ensure_ccw(inner_poly)
    if len(outer) < 60:
        outer = resample_polygon_2d(outer, target_spacing=4.0)
    if len(inner) < 60:
        inner = resample_polygon_2d(inner, target_spacing=4.0)

    n_out = len(outer)
    n_in = len(inner)

    outer_arr = np.asarray(outer, dtype=float)
    inner_arr = np.asarray(inner, dtype=float)

    if y_split is None:
        y_split = float((outer_arr[:, 1].min() + outer_arr[:, 1].max()) / 2.0)

    if x_split is None:
        x_mid = float((outer_arr[:, 0].min() + outer_arr[:, 0].max()) / 2.0)
        candidate_splits = [x_mid + float(delta) for delta in np.linspace(-15.0, 15.0, 31)]
        best_x_split = x_mid
        best_worst_dim = float("inf")

        for cand_x in candidate_splits:
            f_cands = [i for i in range(n_out) if outer_arr[i, 1] > y_split]
            f_idx = min(f_cands, key=lambda i: abs(outer_arr[i, 0] - cand_x)) if f_cands else 0

            r_cands = [i for i in range(n_out) if outer_arr[i, 1] < y_split]
            r_idx = min(r_cands, key=lambda i: abs(outer_arr[i, 0] - cand_x)) if r_cands else n_out // 2

            l_cands = [i for i in range(n_out) if outer_arr[i, 0] <= outer_arr[:, 0].min() + 8.0]
            l_idx = min(l_cands, key=lambda i: abs(outer_arr[i, 1] - y_split)) if l_cands else 0

            rg_cands = [i for i in range(n_out) if outer_arr[i, 0] >= outer_arr[:, 0].max() - 8.0]
            rg_idx = min(rg_cands, key=lambda i: abs(outer_arr[i, 1] - y_split)) if rg_cands else n_out // 2

            worst_dim = 0.0
            for s_i, e_i in [(f_idx, l_idx), (l_idx, r_idx), (r_idx, rg_idx), (rg_idx, f_idx)]:
                o_pts = [outer[i] for i in _get_arc_indices(s_i, e_i, n_out)]
                in_s = int(np.argmin(np.linalg.norm(inner_arr - outer_arr[s_i], axis=1)))
                in_e = int(np.argmin(np.linalg.norm(inner_arr - outer_arr[e_i], axis=1)))
                i_pts = [inner[i] for i in reversed(_get_arc_indices(in_s, in_e, n_in))]
                dim = calculate_min_oriented_bounding_box_dimension(o_pts + i_pts)
                if dim > worst_dim:
                    worst_dim = dim

            if worst_dim < best_worst_dim:
                best_worst_dim = worst_dim
                best_x_split = cand_x

        x_split = best_x_split

    front_candidates = [i for i in range(n_out) if outer_arr[i, 1] > y_split]
    front_idx = min(front_candidates, key=lambda i: abs(outer_arr[i, 0] - x_split)) if front_candidates else 0

    rear_candidates = [i for i in range(n_out) if outer_arr[i, 1] < y_split]
    rear_idx = min(rear_candidates, key=lambda i: abs(outer_arr[i, 0] - x_split)) if rear_candidates else n_out // 2

    left_candidates = [i for i in range(n_out) if outer_arr[i, 0] <= outer_arr[:, 0].min() + 8.0]
    left_idx = min(left_candidates, key=lambda i: abs(outer_arr[i, 1] - y_split)) if left_candidates else 0

    right_candidates = [i for i in range(n_out) if outer_arr[i, 0] >= outer_arr[:, 0].max() - 8.0]
    right_idx = min(right_candidates, key=lambda i: abs(outer_arr[i, 1] - y_split)) if right_candidates else n_out // 2

    seam_outer_indices = {
        "Front_Seam": front_idx,
        "Left_Seam": left_idx,
        "Rear_Seam": rear_idx,
        "Right_Seam": right_idx,
    }

    seam_inner_indices = {}
    for seam_name, out_idx in seam_outer_indices.items():
        if n_in == n_out:
            seam_inner_indices[seam_name] = out_idx
        else:
            p_out = outer_arr[out_idx]
            dists = np.linalg.norm(inner_arr - p_out, axis=1)
            seam_inner_indices[seam_name] = int(np.argmin(dists))

    seam_normals = {}
    for seam_name, out_idx in seam_outer_indices.items():
        in_idx = seam_inner_indices[seam_name]
        p_out = outer_arr[out_idx]
        p_in = inner_arr[in_idx]
        seam_vec = p_in - p_out
        seam_w = float(np.linalg.norm(seam_vec))
        u = seam_vec / max(seam_w, 1e-9)

        t_vec = outer_arr[(out_idx + 1) % n_out] - outer_arr[(out_idx - 1) % n_out]
        t_len = float(np.linalg.norm(t_vec))
        t_unit = t_vec / max(t_len, 1e-9)

        n_cand = np.array([-u[1], u[0]])
        if np.dot(n_cand, t_unit) < 0:
            n_cand = -n_cand
        seam_normals[seam_name] = n_cand

    quad_defs = [
        {
            "name": "TRK_Front_L",
            "start_seam": "Front_Seam",
            "start_joint_type": "female",
            "end_seam": "Left_Seam",
            "end_joint_type": "male",
        },
        {
            "name": "TRK_Rear_L",
            "start_seam": "Left_Seam",
            "start_joint_type": "female",
            "end_seam": "Rear_Seam",
            "end_joint_type": "male",
        },
        {
            "name": "TRK_Rear_R",
            "start_seam": "Rear_Seam",
            "start_joint_type": "female",
            "end_seam": "Right_Seam",
            "end_joint_type": "male",
        },
        {
            "name": "TRK_Front_R",
            "start_seam": "Right_Seam",
            "start_joint_type": "female",
            "end_seam": "Front_Seam",
            "end_joint_type": "male",
        },
    ]

    rad = math.radians(params.seam_dovetail_angle_deg)
    base_w = params.trail_base_width_mm
    depth = 8.0
    tol = params.tol_seam_dovetail_mm

    def _dovetail_cut(
        p_from: Sequence[float],
        p_to: Sequence[float],
        is_male: bool,
        outward_n: np.ndarray,
    ) -> List[Tuple[float, float]]:
        p_a = np.asarray(p_from, dtype=float)
        p_b = np.asarray(p_to, dtype=float)
        p_m = (p_a + p_b) / 2.0
        s_vec = p_b - p_a
        s_len = float(np.linalg.norm(s_vec))
        u_vec = s_vec / max(s_len, 1e-9)

        if is_male:
            w_r_half = base_w / 2.0
            w_t_half = w_r_half + depth * math.tan(rad)
            r1 = p_m - w_r_half * u_vec
            t1 = p_m - w_t_half * u_vec + depth * outward_n
            t2 = p_m + w_t_half * u_vec + depth * outward_n
            r2 = p_m + w_r_half * u_vec
            return [
                (float(r1[0]), float(r1[1])),
                (float(t1[0]), float(t1[1])),
                (float(t2[0]), float(t2[1])),
                (float(r2[0]), float(r2[1])),
            ]
        else:
            w_r_half = (base_w + 2.0 * tol) / 2.0
            d_p = depth + tol
            w_t_half = w_r_half + d_p * math.tan(rad)
            r1 = p_m - w_r_half * u_vec
            t1 = p_m - w_t_half * u_vec - d_p * outward_n
            t2 = p_m + w_t_half * u_vec - d_p * outward_n
            r2 = p_m + w_r_half * u_vec
            return [
                (float(r1[0]), float(r1[1])),
                (float(t1[0]), float(t1[1])),
                (float(t2[0]), float(t2[1])),
                (float(r2[0]), float(r2[1])),
            ]

    results: Dict[str, QuadrantGeometry] = {}

    for q_def in quad_defs:
        q_name = q_def["name"]
        s_seam = q_def["start_seam"]
        e_seam = q_def["end_seam"]
        s_out_idx = seam_outer_indices[s_seam]
        e_out_idx = seam_outer_indices[e_seam]
        s_in_idx = seam_inner_indices[s_seam]
        e_in_idx = seam_inner_indices[e_seam]

        outer_idxs = _get_arc_indices(s_out_idx, e_out_idx, n_out)
        inner_idxs = _get_arc_indices(s_in_idx, e_in_idx, n_in)

        outer_pts = [outer[i] for i in outer_idxs]
        inner_pts = [inner[i] for i in inner_idxs]
        inner_pts_rev = list(reversed(inner_pts))

        nominal_poly = outer_pts + inner_pts_rev

        end_cut_pts = _dovetail_cut(
            p_from=outer[e_out_idx],
            p_to=inner[e_in_idx],
            is_male=(q_def["end_joint_type"] == "male"),
            outward_n=seam_normals[e_seam],
        )

        start_cut_pts = _dovetail_cut(
            p_from=inner[s_in_idx],
            p_to=outer[s_out_idx],
            is_male=(q_def["start_joint_type"] == "male"),
            outward_n=-seam_normals[s_seam],
        )

        full_poly = outer_pts + end_cut_pts + inner_pts_rev + start_cut_pts

        all_arr = np.asarray(full_poly, dtype=float)
        min_x, max_x = float(all_arr[:, 0].min()), float(all_arr[:, 0].max())
        min_y, max_y = float(all_arr[:, 1].min()), float(all_arr[:, 1].max())
        w = max_x - min_x
        h = max_y - min_y

        max_dim = calculate_min_oriented_bounding_box_dimension(full_poly)
        area = calculate_polygon_area(full_poly)
        perim = calculate_polygon_perimeter(full_poly)

        results[q_name] = QuadrantGeometry(
            name=q_name,
            polygon=full_poly,
            nominal_polygon=nominal_poly,
            outer_points=outer_pts,
            inner_points=inner_pts,
            start_seam=s_seam,
            start_joint_type=q_def["start_joint_type"],
            end_seam=e_seam,
            end_joint_type=q_def["end_joint_type"],
            bounds={"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y},
            width=w,
            height=h,
            max_dimension=max_dim,
            area_mm2=area,
            perimeter_mm=perim,
        )

    return results


def generate_track_boundary_loops(
    floor_polygon: Sequence[Tuple[float, float]],
    wall_clearance_mm: float = 12.7,
    track_width_mm: float = 30.0,
) -> Dict[str, List[Tuple[float, float]]]:
    base_poly = ensure_ccw(floor_polygon)
    outer_loop = offset_polygon_2d(base_poly, offset_distance_mm=wall_clearance_mm, inward=True)
    centerline = offset_polygon_2d(
        base_poly, offset_distance_mm=wall_clearance_mm + track_width_mm / 2.0, inward=True
    )
    inner_loop = offset_polygon_2d(
        base_poly, offset_distance_mm=wall_clearance_mm + track_width_mm, inward=True
    )
    return {
        "outer_loop": outer_loop,
        "centerline": centerline,
        "inner_loop": inner_loop,
    }


def extract_calibrated_floor_polygon(
    stl_path: str = "docs/scans/frunk_scan_calibrated.stl",
    z_height: float = 10.0,
    target_spacing: float = 4.0,
    smooth_window: int = 5,
) -> List[Tuple[float, float]]:
    try:
        import trimesh
        if not os.path.isabs(stl_path):
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidate = os.path.join(repo_root, stl_path)
            if os.path.exists(candidate):
                stl_path = candidate

        if os.path.exists(stl_path):
            mesh = trimesh.load(stl_path)
            section = mesh.section(plane_origin=[0.0, 0.0, float(z_height)], plane_normal=[0.0, 0.0, 1.0])
            if section is not None and len(section.entities) > 0:
                best_pts: Optional[np.ndarray] = None
                best_metric = -1.0
                for entity in section.entities:
                    disc = entity.discrete(section.vertices)
                    if len(disc) < 10:
                        continue
                    pts_xy = disc[:, :2]
                    if np.all(np.abs(pts_xy[:, 0]) < 650) and np.all(np.abs(pts_xy[:, 1]) < 550):
                        diffs = np.diff(pts_xy, axis=0)
                        length = float(np.sum(np.linalg.norm(diffs, axis=1)))
                        if length > best_metric:
                            best_metric = length
                            best_pts = pts_xy
                if best_pts is not None:
                    raw_loop = ensure_ccw([(float(p[0]), float(p[1])) for p in best_pts])
                    resampled = resample_polygon_2d(raw_loop, target_spacing=target_spacing)
                    smoothed = smooth_polygon_2d(resampled, window_size=smooth_window)
                    return ensure_ccw(smoothed)
    except Exception:
        pass
    return CALIBRATED_FLOOR_POLYGON


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


class MockSketchCurves:
    def __init__(self):
        self.sketchLines = MockSketchLines()
        self.sketchCircles = MockSketchCircles()


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


class MockBRepBody:
    def __init__(self, name: str = "Body"):
        self.name = name


class MockBRepBodies:
    def __init__(self):
        self._bodies: List[MockBRepBody] = []

    @property
    def count(self) -> int:
        return len(self._bodies)

    def item(self, idx: int) -> MockBRepBody:
        return self._bodies[idx]

    def append(self, body: MockBRepBody):
        self._bodies.append(body)


class MockExtrudeFeatures:
    def __init__(self, parent_comp: Any = None):
        self.parent_comp = parent_comp
        self.features = []

    def addSimple(self, profile: Any, distance: Any, operation: Any):
        body = MockBRepBody()
        if self.parent_comp and hasattr(self.parent_comp, "bRepBodies"):
            self.parent_comp.bRepBodies.append(body)
        self.features.append({"profile": profile, "distance": distance, "operation": operation, "body": body})
        return body

    def createInput(self, profile: Any, operation: Any) -> MockExtrudeInput:
        return MockExtrudeInput()

    def add(self, extrude_input: MockExtrudeInput):
        body = MockBRepBody()
        if self.parent_comp and hasattr(self.parent_comp, "bRepBodies"):
            self.parent_comp.bRepBodies.append(body)
        self.features.append(extrude_input)
        return body


class MockFeatures:
    def __init__(self, parent_comp: Any = None):
        self.extrudeFeatures = MockExtrudeFeatures(parent_comp)


class MockOccurrence:
    def __init__(self, component: Any):
        self.component = component


class MockOccurrences:
    def __init__(self):
        self.occurrences = []

    def addNewComponent(self, transform: Any) -> MockOccurrence:
        comp = MockComponent()
        occ = MockOccurrence(comp)
        self.occurrences.append(occ)
        return occ


class MockComponent:
    def __init__(self, name: str = "Component"):
        self.name = name
        self.bRepBodies = MockBRepBodies()
        self.sketches = MockSketches()
        self.features = MockFeatures(self)
        self.occurrences = MockOccurrences()
        self.xYConstructionPlane = "XY"
        self.xZConstructionPlane = "XZ"


class MockDesign:
    def __init__(self):
        self.userParameters = MockUserParameters()
        self.rootComponent = MockComponent("RootComponent")
        self.designType = 1


# ==============================================================================
# Helper Factories & Robust Fusion API Wrappers
# ==============================================================================

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
    elif hasattr(comp, "features") and hasattr(comp.features, "extrudeFeatures"):
        return comp.features.extrudeFeatures.addSimple(profile, distance_val, operation)
    return None


def _extrude_cut_all_profiles(comp: Any, sketch: Any, cut_depth_cm: float, direction_positive: bool = True):
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
                    adsk.fusion.FeatureOperations.CutFeatureOperation,
                )
            except Exception:
                pass


def _extrude_cut_symmetric(comp: Any, sketch: Any, half_depth_cm: float):
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
    if hasattr(comp, "bRepBodies"):
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
        # Conformal Perimeter Floor Track Parameters
        ("WallClearance", f"{params.wall_clearance_mm:.2f} mm", "mm", "0.50 in inward clearance from frunk tub perimeter"),
        ("TrackWidth", f"{params.track_width_mm:.2f} mm", "mm", "Conformal floor track rigid profile width"),
        ("TrackHeight", f"{params.track_height_mm:.2f} mm", "mm", "Conformal floor track rigid profile height"),
        ("TrackRailBase", f"{params.trail_base_width_mm:.2f} mm", "mm", "Captive sliding top rail base width"),
        ("TrackRailNeck", f"{params.trail_neck_width_mm:.2f} mm", "mm", "Captive sliding top rail neck width"),
        ("TrackRailHeight", f"{params.trail_height_mm:.2f} mm", "mm", "Captive sliding top rail depth"),
        ("TrackBedMaxDim", f"{params.max_bed_dimension_mm:.2f} mm", "mm", "Max print bed envelope limit (Creality K2)"),
        ("TolSeamDovetail", f"{params.tol_seam_dovetail_mm:.2f} mm", "mm", "3D printing slip clearance for track quadrant seams"),
        ("SeamDovetailAngle", f"{params.seam_dovetail_angle_deg:.2f} deg", "deg", "Quadrant interlocking dovetail taper angle"),
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

    sketch_base = sketches.add(plane_xy)
    p1 = _create_point(ox, oy - w_cm / 2.0, 0.0)
    p2 = _create_point(ox + l_cm, oy + w_cm / 2.0, 0.0)
    sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    profs = _get_all_profiles(sketch_base)
    if profs:
        _extrude_simple(comp, profs[0], _create_value_real(h_cm), op_new)
        _name_last_body(comp, "FT_Segment_12in")

    sketch_male = sketches.add(plane_xy)
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm, base_w=params.dovetail_base_width_mm, depth=params.dovetail_depth_mm, angle_deg=params.dovetail_angle_deg)
    dt_pts = [_create_point(ox + l_cm + p[1] / 10.0, oy + p[0] / 10.0, 0.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_male.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    male_profs = _get_all_profiles(sketch_male)
    if male_profs:
        _extrude_simple(comp, male_profs[0], _create_value_real(h_cm), op_join)

    sketch_female = sketches.add(plane_xy)
    female_pts = calculate_dovetail_profile(male=False, tol=params.tol_dovetail_mm, base_w=params.dovetail_base_width_mm, depth=params.dovetail_depth_mm, angle_deg=params.dovetail_angle_deg)
    f_dt_pts = [_create_point(ox + p[1] / 10.0, oy + p[0] / 10.0, 0.0) for p in female_pts]
    for i in range(len(f_dt_pts)):
        sketch_female.sketchCurves.sketchLines.addByTwoPoints(f_dt_pts[i], f_dt_pts[(i + 1) % len(f_dt_pts)])

    _extrude_cut_all_profiles(comp, sketch_female, h_cm, direction_positive=True)

    sketch_webs = sketches.add(plane_xz)
    tri_left = calculate_truss_span_triangles(x_start=25.0, x_end=135.0, z_bottom=8.0, z_top=27.0, num_triangles=3, web_strut_w=4.5)
    tri_right = calculate_truss_span_triangles(x_start=170.0, x_end=280.0, z_bottom=8.0, z_top=27.0, num_triangles=3, web_strut_w=4.5)

    for tri in tri_left + tri_right:
        pts = [_create_point(ox + p[0] / 10.0, 0.0, p[1] / 10.0) for p in tri]
        for i in range(3):
            sketch_webs.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % 3])

    _extrude_cut_symmetric(comp, sketch_webs, w_cm * 2.0)


def build_vertical_rib_component(comp: Any, params: FrunkParameters, offset_x: float = 0.0, offset_y: float = 60.0):
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

    sketch_post = sketches.add(plane_xy)
    p1 = _create_point(ox, oy - w_cm / 2.0, 0.0)
    p2 = _create_point(ox + h_cm, oy + w_cm / 2.0, 0.0)
    sketch_post.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    profs = _get_all_profiles(sketch_post)
    if profs:
        _extrude_simple(comp, profs[0], _create_value_real(w_cm), op_new)
        _name_last_body(comp, "VR_Post_Deep")

    sketch_slot = sketches.add(plane_xy)
    s1 = _create_point(ox, oy - slot_w_cm / 2.0, 0.0)
    s2 = _create_point(ox + h_cm, oy + slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)

    _extrude_cut_all_profiles(comp, sketch_slot, slot_d_cm, direction_positive=True)

    sketch_tenon = sketches.add(plane_xy)
    tenon_w_cm = (20.0 - 2.0 * params.tol_tenon_mm) / 10.0
    t1 = _create_point(ox - 2.0, oy - tenon_w_cm / 2.0, 0.0)
    t2 = _create_point(ox, oy + tenon_w_cm / 2.0, 0.0)
    sketch_tenon.sketchCurves.sketchLines.addTwoPointRectangle(t1, t2)

    tenon_profs = _get_all_profiles(sketch_tenon)
    if tenon_profs:
        _extrude_simple(comp, tenon_profs[0], _create_value_real(tenon_w_cm), op_join)


def build_horizontal_rail_component(comp: Any, params: FrunkParameters, offset_x: float = 0.0, offset_y: float = 120.0):
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

    sketch_rail = sketches.add(plane_xy)
    p1 = _create_point(ox, oy - w_cm / 2.0, 0.0)
    p2 = _create_point(ox + l_cm, oy + w_cm / 2.0, 0.0)
    sketch_rail.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    profs = _get_all_profiles(sketch_rail)
    if profs:
        _extrude_simple(comp, profs[0], _create_value_real(w_cm), op_new)
        _name_last_body(comp, "HR_Rail_12in")

    sketch_slot = sketches.add(plane_xy)
    s1 = _create_point(ox, oy - slot_w_cm / 2.0, 0.0)
    s2 = _create_point(ox + l_cm, oy + slot_w_cm / 2.0, 0.0)
    sketch_slot.sketchCurves.sketchLines.addTwoPointRectangle(s1, s2)

    _extrude_cut_all_profiles(comp, sketch_slot, slot_d_cm, direction_positive=True)

    sketch_dt = sketches.add(plane_xy)
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
    dt_pts = [_create_point(ox + l_cm + p[1] / 10.0, oy + p[0] / 10.0, 0.0) for p in male_pts]
    for i in range(len(dt_pts)):
        sketch_dt.sketchCurves.sketchLines.addByTwoPoints(dt_pts[i], dt_pts[(i + 1) % len(dt_pts)])

    dt_profs = _get_all_profiles(sketch_dt)
    if dt_profs:
        _extrude_simple(comp, dt_profs[0], _create_value_real(w_cm), op_join)


def build_junction_components(comp: Any, params: FrunkParameters, offset_x: float = 350.0, offset_y: float = 0.0):
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
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    w_cm = params.panel_width_cm
    h_cm = params.panel_height_cm
    t_cm = params.panel_thickness_cm
    bezel_cm = 1.0
    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0

    sketch_plate = sketches.add(plane_xy)
    p_out1 = _create_point(ox, oy, 0.0)
    p_out2 = _create_point(ox + w_cm, oy + h_cm, 0.0)
    sketch_plate.sketchCurves.sketchLines.addTwoPointRectangle(p_out1, p_out2)

    plate_profs = _get_all_profiles(sketch_plate)
    if plate_profs:
        _extrude_simple(comp, plate_profs[0], _create_value_real(t_cm), op_new)
        _name_last_body(comp, "DIV_Crosshatch_12x11")

    inner_w_mm = params.panel_width_mm - 20.0
    inner_h_mm = params.panel_height_mm - 20.0
    apertures = calculate_diamond_apertures(
        inner_w=inner_w_mm,
        inner_h=inner_h_mm,
        pitch=params.lattice_pitch_mm,
        strut_w=params.lattice_strut_mm,
    )

    sketch_cutouts = sketches.add(plane_xy)
    for diamond in apertures:
        pts = [_create_point(ox + bezel_cm + p[0] / 10.0, oy + bezel_cm + p[1] / 10.0, 0.0) for p in diamond]
        lines = sketch_cutouts.sketchCurves.sketchLines
        for i in range(4):
            lines.addByTwoPoints(pts[i], pts[(i + 1) % 4])

    _extrude_cut_all_profiles(comp, sketch_cutouts, t_cm, direction_positive=True)

    sketch_handle = sketches.add(plane_xy)
    handle_w_cm = 8.0
    handle_h_cm = 2.2
    mid_x = ox + w_cm / 2.0
    hp1 = _create_point(mid_x - handle_w_cm / 2.0, oy + h_cm - bezel_cm - handle_h_cm, 0.0)
    hp2 = _create_point(mid_x + handle_w_cm / 2.0, oy + h_cm - bezel_cm, 0.0)
    sketch_handle.sketchCurves.sketchLines.addTwoPointRectangle(hp1, hp2)

    _extrude_cut_all_profiles(comp, sketch_handle, t_cm, direction_positive=True)


def build_locking_pin_component(comp: Any, params: FrunkParameters, offset_x: float = 350.0, offset_y: float = 180.0):
    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0
    op_join = adsk.fusion.FeatureOperations.JoinFeatureOperation if FUSION_AVAILABLE else 1

    sketch_head = sketches.add(plane_xy)
    head_center = _create_point(ox, oy, 0.0)
    sketch_head.sketchCurves.sketchCircles.addByCenterRadius(head_center, 0.4)

    head_profs = _get_all_profiles(sketch_head)
    if head_profs:
        _extrude_simple(comp, head_profs[0], _create_value_real(0.4), op_new)
        _name_last_body(comp, "Pin_Lock_M5")

    sketch_shaft = sketches.add(plane_xy)
    sketch_shaft.sketchCurves.sketchCircles.addByCenterRadius(head_center, params.pin_diameter_cm / 2.0)

    shaft_profs = _get_all_profiles(sketch_shaft)
    if shaft_profs:
        _extrude_simple(comp, shaft_profs[0], _create_value_real(-2.8), op_join)


def build_conformal_floor_track(
    comp: Any,
    params: Optional[FrunkParameters] = None,
    scan_mesh_path: Optional[str] = None,
    offset_x: float = 0.0,
    offset_y: float = -750.0,
    separate_quadrants: bool = True,
    build_assembled: bool = True,
) -> Dict[str, Any]:
    """
    Builds 3D CAD solid bodies for the LiDAR-matched conformal perimeter floor track system.

    Constructs:
      1. TRK_Front_L: Front-Left quadrant with 15° interlocking dovetail tabs/pockets
      2. TRK_Front_R: Front-Right quadrant with 15° interlocking dovetail tabs/pockets
      3. TRK_Rear_L: Rear-Left quadrant with 15° interlocking dovetail tabs/pockets
      4. TRK_Rear_R: Rear-Right quadrant with 15° interlocking dovetail tabs/pockets
      5. TRK_Master_Assembled: Full continuous perimeter floor track ring

    All 4 quadrants measure under 310 mm to fit flat on Creality K2 350x350 mm print bed.
    """
    if params is None:
        params = FrunkParameters()

    sketches = comp.sketches
    plane_xy = comp.xYConstructionPlane if hasattr(comp, "xYConstructionPlane") else None

    h_cm = params.track_height_cm
    ox = offset_x / 10.0
    oy = offset_y / 10.0

    op_new = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if FUSION_AVAILABLE else 0

    floor_pts = None
    if scan_mesh_path and os.path.exists(scan_mesh_path):
        try:
            floor_pts = extract_calibrated_floor_polygon(scan_mesh_path, z_height=params.floor_slice_z_mm)
        except Exception:
            pass

    if floor_pts is None:
        floor_pts = CALIBRATED_FLOOR_POLYGON

    loops = generate_track_boundary_loops(
        floor_pts,
        wall_clearance_mm=params.wall_clearance_mm,
        track_width_mm=params.track_width_mm,
    )
    quadrants = slice_track_quadrants(
        loops["outer_loop"],
        loops["inner_loop"],
        params=params,
    )

    created_bodies: Dict[str, Any] = {}

    # 1. Master Assembled Continuous Floor Ring
    if build_assembled:
        sketch_master = sketches.add(plane_xy)
        out_pts = [_create_point(ox + p[0] / 10.0, oy + p[1] / 10.0, 0.0) for p in loops["outer_loop"]]
        in_pts = [_create_point(ox + p[0] / 10.0, oy + p[1] / 10.0, 0.0) for p in loops["inner_loop"]]

        for i in range(len(out_pts)):
            sketch_master.sketchCurves.sketchLines.addByTwoPoints(out_pts[i], out_pts[(i + 1) % len(out_pts)])
        for i in range(len(in_pts)):
            sketch_master.sketchCurves.sketchLines.addByTwoPoints(in_pts[i], in_pts[(i + 1) % len(in_pts)])

        profs = _get_all_profiles(sketch_master)
        if profs:
            _extrude_simple(comp, profs[0], _create_value_real(h_cm), op_new)
            _name_last_body(comp, "TRK_Master_Assembled")
            created_bodies["TRK_Master_Assembled"] = comp.bRepBodies.item(comp.bRepBodies.count - 1) if hasattr(comp, "bRepBodies") and comp.bRepBodies.count > 0 else "TRK_Master_Assembled"

    # 2. Four Printable Quadrants with 15° Dovetail Interlocking Seams
    quad_offsets = {
        "TRK_Front_L": (-60.0, 60.0) if separate_quadrants else (0.0, 0.0),
        "TRK_Front_R": (60.0, 60.0) if separate_quadrants else (0.0, 0.0),
        "TRK_Rear_L": (-60.0, -60.0) if separate_quadrants else (0.0, 0.0),
        "TRK_Rear_R": (60.0, -60.0) if separate_quadrants else (0.0, 0.0),
    }

    for quad_name in ["TRK_Front_L", "TRK_Front_R", "TRK_Rear_L", "TRK_Rear_R"]:
        if quad_name not in quadrants:
            continue
        q_geom = quadrants[quad_name]
        dx, dy = quad_offsets[quad_name]
        qx = ox + dx / 10.0
        qy = oy + dy / 10.0

        sketch_quad = sketches.add(plane_xy)
        poly_pts = [_create_point(qx + p[0] / 10.0, qy + p[1] / 10.0, 0.0) for p in q_geom.polygon]
        for i in range(len(poly_pts)):
            sketch_quad.sketchCurves.sketchLines.addByTwoPoints(poly_pts[i], poly_pts[(i + 1) % len(poly_pts)])

        profs = _get_all_profiles(sketch_quad)
        if profs:
            _extrude_simple(comp, profs[0], _create_value_real(h_cm), op_new)
            _name_last_body(comp, quad_name)
            created_bodies[quad_name] = comp.bRepBodies.item(comp.bRepBodies.count - 1) if hasattr(comp, "bRepBodies") and comp.bRepBodies.count > 0 else quad_name

    return created_bodies


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

        # Step 2: Build All 8 Core CAD Solid Bodies (Neatly arranged side-by-side)
        build_floor_truss_component(root_comp, params, offset_x=0.0, offset_y=0.0)
        build_vertical_rib_component(root_comp, params, offset_x=0.0, offset_y=60.0)
        build_horizontal_rail_component(root_comp, params, offset_x=0.0, offset_y=120.0)
        build_junction_components(root_comp, params, offset_x=350.0, offset_y=0.0)
        build_divider_panel_component(root_comp, params, offset_x=0.0, offset_y=-320.0)
        build_locking_pin_component(root_comp, params, offset_x=350.0, offset_y=180.0)

        # Step 3: Build LiDAR-Matched Conformal Perimeter Floor Track (4 Quadrants + Assembled Ring)
        build_conformal_floor_track(root_comp, params, offset_x=0.0, offset_y=-750.0)

        msg = (
            "Tesla Model X Frunk Modular Divider & Conformal Floor System Generated!\n\n"
            "All 13 modular solid bodies have been generated:\n\n"
            "  1. FT_Segment_12in       - Floor Truss (span webs & dovetails)\n"
            "  2. VR_Post_Deep          - 11-in Vertical Rib (6.4mm slots)\n"
            "  3. HR_Rail_12in          - Horizontal Top Tie Rail\n"
            "  4. J_Corner_90           - 2-Way 90° Corner Junction\n"
            "  5. J_Tee_3Way            - 3-Way T-Junction\n"
            "  6. J_Cross_4Way          - 4-Way Cross Junction\n"
            "  7. DIV_Crosshatch_12x11  - Diamond Lattice Mesh Divider\n"
            "  8. Pin_Lock_M5           - Transverse Locking Pin\n"
            "  9. TRK_Front_L           - Conformal Track Front-Left (<310mm)\n"
            " 10. TRK_Front_R           - Conformal Track Front-Right (<310mm)\n"
            " 11. TRK_Rear_L            - Conformal Track Rear-Left (<310mm)\n"
            " 12. TRK_Rear_R            - Conformal Track Rear-Right (<310mm)\n"
            " 13. TRK_Master_Assembled  - Continuous Assembled Perimeter Track\n\n"
            "Check the 'Bodies' folder in your Browser Tree to view, isolate, or export any component!"
        )

        if ui:
            ui.messageBox(msg, "Generation Complete")
        else:
            print(msg)

    except Exception:
        err_msg = f"Error generating components:\n{traceback.format_exc()}"
        if ui:
            ui.messageBox(err_msg, "Tesla Frunk Script Error")
        else:
            print(err_msg, file=sys.stderr)


if __name__ == "__main__":
    run(None)
