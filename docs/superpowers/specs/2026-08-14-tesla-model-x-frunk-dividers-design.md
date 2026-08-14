# Design Specification: Tesla Model X 2017 Frunk Modular Divider System

**Date**: 2026-08-14  
**Target Vehicle**: 2017 Tesla Model X 100D (AWD Frunk Tub)  
**Target 3D Printer**: Creality K2 Combo (350 × 350 × 350 mm build volume)  
**CAD Platform**: Autodesk Fusion 360 (Parametric Model & Python Automation Script)  

---

## 1. Overview & Objectives
The goal of this system is to provide a robust, modular, expandable 3D printable cargo management framework for the 2017 Tesla Model X frunk. The architecture uses a three-tier interlocking design:
1. **Floor Trusses**: Rest on the frunk floor to distribute loads and provide solid anchor points.
2. **Vertical Ribs**: Structural vertical posts (10–12" / 250–280 mm tall) that snap/lock into the floor trusses.
3. **Horizontal Rails**: Tie across the top of the vertical ribs to form rigid bays, featuring vertical guide channels spaced every 12 inches (304.8 mm).
4. **Interlocking System**: Precision sliding dovetails with locking pins for tool-free, rigid assembly.
5. **Dividers**: Removable slide-in panels with solid perimeter bezels and an exposed 45° diagonal diamond crosshatch lattice.
6. **Infill Strategy**: Trusses, ribs, and rails are modeled solid (printed with 30% hexagonal/gyroid infill); divider mesh is printed solid along the lattice struts.

---

## 2. Dimensional Envelope & Parametric Architecture

### 2.1 User Parameters in Fusion 360
All major dimensions are defined in Fusion 360 User Parameters (`fx`):

| Parameter Name | Expression / Value | Purpose |
| :--- | :--- | :--- |
| `Bay_Spacing` | `12.0 in` (304.8 mm) | Center-to-center distance between divider slots |
| `Frame_Height` | `11.0 in` (280.0 mm) | Total height from floor to top of rail |
| `Truss_Base_Height` | `35.0 mm` | Height of the floor truss beam |
| `Truss_Base_Width` | `24.0 mm` | Width of floor truss contact surface |
| `Slot_Width` | `6.4 mm` | Divider guide slot opening width |
| `Slot_Depth` | `8.0 mm` | Divider guide slot channel depth |
| `Panel_Thickness` | `5.0 mm` | Nominal thickness of the divider panel |
| `Panel_Width` | `298.0 mm` | Width of 12" nominal divider panel |
| `Panel_Height` | `275.0 mm` | Height of divider panel |
| `Lattice_Pitch` | `18.0 mm` | Diamond mesh aperture spacing |
| `Lattice_Strut` | `3.5 mm` | Diamond lattice bar thickness |
| `Tol_Dovetail` | `0.25 mm` | Horizontal dovetail 3D-printing slip clearance |
| `Tol_Tenon` | `0.20 mm` | Vertical socket tenon fit clearance |
| `Pin_Diameter` | `5.0 mm` | Tapered locking pin nominal size |

---

## 3. Detailed Component Specifications

### 3.1 Floor Truss Segment (`FT_Segment_12in`)
* **Length**: 304.8 mm center-to-center (+ male dovetail tongue on one end, female dovetail pocket on opposite end).
* **Cross-Section**: 24 mm wide × 35 mm high with open triangular truss cutouts along the span.
* **Vertical Post Socket**: 20 mm × 20 mm × 25 mm deep female square pocket at center and end nodes, with horizontal 5 mm lock-pin bore.
* **Base Contact**: Flat bottom with 1.5 mm anti-slip ridges/recesses to grip carpet or rubber liners.

### 3.2 Vertical Rib Post (`VR_Post_Deep`)
* **Height**: 280 mm overall height (245 mm exposed height + 25 mm bottom tenon + 10 mm top rail locator).
* **Profile**: I-beam cross section (24 mm × 24 mm outer envelope) with generous 3 mm fillets.
* **Guide Channels**: Dual opposing 6.4 mm wide × 8.0 mm deep vertical slots with 45° lead-in chamfers at the top for smooth divider entry.
* **Bottom Tenon**: 20 mm × 20 mm × 24.8 mm tenon (with 0.20 mm tolerance offset) and transverse 5 mm locking pin hole.

### 3.3 Horizontal Top Rail (`HR_Rail_12in`)
* **Length**: 304.8 mm center-to-center.
* **Profile**: 24 mm wide × 20 mm high channel cap that ties across the top of adjacent vertical ribs.
* **Divider Slots**: Continuous top opening aligned with the rib channels, featuring flared funnel chamfers.
* **Interlocking Ends**: Sliding dovetails with vertical pin lock holes to extend rails across multiple bays.

### 3.4 Modular Junction Brackets
* **Corner 90° Junction (`J_Corner_90`)**: 2-way 90° corner connecting orthogonal trusses and rails.
* **T-Junction (`J_Tee_3Way`)**: 3-way connector for internal divider walls.
* **Cross-Junction (`J_Cross_4Way`)**: 4-way connector for expanding multi-compartment frunk grids.

### 3.5 Slide-In Crosshatch Divider Panel (`DIV_Crosshatch_12x11`)
* **Dimensions**: 298.0 mm (W) × 275.0 mm (H) × 5.0 mm (T).
* **Perimeter Frame**: 10.0 mm solid border rim providing rigid engagement in the 6.4 mm rib slots (0.7 mm clearance per side).
* **Top Handle**: Centered 80 mm × 25 mm integrated oval cutout handle.
* **Lattice Pattern**: 45° diagonal intersecting cross-struts (3.5 mm strut width, 18 mm diamond pitch). Sliced without supports when printed flat on the K2 build bed.

### 3.6 Tapered Dovetail Locking Pin (`Pin_Lock_M5`)
* Tapered 5 mm pin with ergonomic pull-tab cap to lock dovetail joints and post sockets against vehicle vibration.

---

## 4. Manufacturing & Slicing Guidelines (Creality K2 Plus)

* **Build Bed Sizing**: All components are under 310 mm, fitting comfortably inside the 350 × 350 mm bed.
* **Recommended Materials**:
  * **ASA or ABS** (Primary Recommendation): High heat deflection temperature (>95°C) to withstand automotive frunk temperatures in summer.
  * **PETG** (Secondary): Acceptable for moderate climates (heat deflection ~70°C).
  * *Avoid PLA*: Subject to heat sag/creep in enclosed vehicles.
* **Slicer Settings (Creality Print / OrcaSlicer)**:
  * **Walls / Perimeters**: 4 perimeters (1.6 mm total shell with 0.4mm nozzle).
  * **Top/Bottom Solid Layers**: 4 layers.
  * **Infill Type**: **Hexagonal** or **Gyroid**.
  * **Infill Density**: 30% for Trusses, Ribs, and Rails.
  * **Dividers**: 100% infill on the lattice struts, zero supports required.

---

## 5. Software & Delivery Architecture

1. **`generate_modelx_frunk_dividers.py`**:
   * A Python script using the Autodesk Fusion 360 API (`adsk.core`, `adsk.fusion`).
   * Automatically initializes User Parameters, builds sketches, extrudes structural bodies, applies crosshatch patterns, and organizes components into a complete `.f3d` assembly.
2. **CAD Reference Documentation**:
   * Complete step-by-step parameter guide, component assembly instructions, and slicing profiles.
