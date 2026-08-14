# Autodesk Fusion 360 CAD Modeling Guide & Parameter Reference
## Tesla Model X (2017) Frunk Modular Divider System

---

## 1. System Overview & Architecture

The **Tesla Model X Frunk Modular Divider System** is a fully parametric, 3D-printable cargo management framework designed specifically for the front trunk (frunk) of the 2017 Tesla Model X (AWD tub layout). It provides rigid, rattle-free compartmentalization for charging cables, mobile connectors, tools, emergency kits, groceries, and travel gear.

```
+=============================================================================+
|                      MODULAR 3-TIER SYSTEM ARCHITECTURE                     |
+=============================================================================+
|                                                                             |
|   [ Tier 3: Horizontal Rails ]  ====== HR_Rail_12in ====== (Top Cap)        |
|                                         |           |                       |
|   [ Slide-In Divider Panels ]   [DIV_Crosshatch]    |  (45° Diamond Mesh)   |
|                                         |           |                       |
|   [ Tier 2: Vertical Posts ]    |-- VR_Post_Deep --|  (6.4mm Guide Slots)   |
|                                 |                   |                       |
|   [ Tier 1: Floor Trusses ]     +-- FT_Segment_12in +  (Triangular Webs)    |
|                                 |                   |                       |
|   [ Modular Junctions ]      J_Corner_90 / J_Tee_3Way / J_Cross_4Way        |
|                                                                             |
|   [ Vibration Pin Locks ]    Pin_Lock_M5 (Transverse Locking Dowels)        |
+=============================================================================+
```

### Key Engineering Features
* **Three-Tier Interlocking Topology**: Load-bearing Floor Trusses rest on the frunk carpet, Vertical Rib Posts lock into truss sockets, and Horizontal Rails tie the upper perimeter into a rigid frame.
* **15° Sliding Dovetails**: Tool-free assembly between trusses, rails, and corner/Tee/Cross junction blocks with calibrated slip tolerances.
* **Transverse Pin Locks (`Pin_Lock_M5`)**: Tapered dowel pins with pull tabs that mechanically lock joints against automotive road vibration and lateral acceleration.
* **45° Diamond Crosshatch Panels**: High strength-to-weight slide-in dividers printable without support structures on large-format 3D printers like the **Creality K2 Combo** (350 × 350 × 350 mm build volume).
* **Fully Parametric Engine (`fx`)**: Every dimension (bay spacing, frame height, slot width, dovetail clearances, mesh pitch) is dynamically linked to Fusion 360 User Parameters.

---

## 2. Installation & Script Execution in Autodesk Fusion 360

The automation script (`generate_modelx_frunk_dividers.py`) programmatically creates all user parameters, sketches, extrusions, sockets, dovetail joints, lattice meshes, and organized component structures in Autodesk Fusion 360.

### 2.1 Locating Fusion 360's Scripts Directory

Autodesk Fusion 360 looks for Python scripts in specific user directory paths depending on your operating system:

| Operating System | Default Fusion 360 Scripts Directory Path |
| :--- | :--- |
| **Windows 10 / 11** | `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`<br>`C:\Users\<YourUsername>\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\` |
| **macOS** | `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts/` |

### 2.2 Step-by-Step Installation

#### Method A: Directory Copy / Link (Recommended)
1. Open your terminal or file explorer.
2. Create a folder named `modelx_frunk_dividers` inside Fusion 360's `Scripts` directory:
   * **Windows (PowerShell)**:
     ```powershell
     $target = "$env:APPDATA\Autodesk\Autodesk Fusion 360\API\Scripts\modelx_frunk_dividers"
     New-Item -ItemType Directory -Force -Path $target
     Copy-Item -Path "C:\Users\lucas\source\repos\modelx_frunk\fusion_scripts\*" -Destination $target -Recurse
     ```
   * **macOS (Terminal)**:
     ```bash
     mkdir -p ~/Library/Application\ Support/Autodesk/Autodesk\ Fusion\ 360/API/Scripts/modelx_frunk_dividers
     cp -r /path/to/modelx_frunk/fusion_scripts/* ~/Library/Application\ Support/Autodesk/Autodesk\ Fusion\ 360/API/Scripts/modelx_frunk_dividers/
     ```

#### Method B: Direct Script Open in Fusion 360
1. Launch **Autodesk Fusion 360**.
2. Press `Shift + S` (<kbd>Shift</kbd> + <kbd>S</kbd>) (or navigate to **Utilities** > **Scripts and Add-Ins** in the toolbar, or **Automation** > **Scripts and Add-Ins** in newer UI layouts).
3. Under the **Scripts** tab, click the **+** (Create/Add) button next to **My Scripts**.
4. Browse to `C:\Users\lucas\source\repos\modelx_frunk\fusion_scripts\generate_modelx_frunk_dividers.py` and select it.

```
+-----------------------------------------------------------------------+
| Scripts and Add-Ins                                              [X]  |
+-----------------------------------------------------------------------+
|  Scripts  |  Add-Ins  |                                               |
|                                                                       |
|  My Scripts                                                           |
|    > modelx_frunk_dividers                                            |
|        generate_modelx_frunk_dividers.py   [Python]                   |
|                                                                       |
|  [ Run ]   [ Debug ]   [ Edit ]   [ Create ]   [ + (Add) ]   [ Close ]|
+-----------------------------------------------------------------------+
```

### 2.3 Running the Script

1. In Fusion 360, create a new empty design document (**File** > **New Design** or <kbd>Ctrl</kbd> + <kbd>N</kbd>).
2. Open **Scripts and Add-Ins** (<kbd>Shift</kbd> + <kbd>S</kbd>).
3. Select `generate_modelx_frunk_dividers` under **My Scripts**.
4. Click **Run**.
5. The script automatically executes the parametric pipeline:
   * Populates **User Parameters (`fx`)**.
   * Creates 6 root-level component classes (8 distinct functional parts).
   * Generates sketches, triangular web profiles, 15° dovetail tabs/pockets, guide channels, tenons, and diamond crosshatch lines.
   * Displays a confirmation dialog: `Tesla Model X Frunk Divider System generated successfully!`.

### 2.4 Standalone Dry-Run / Headless Verification

You can also run the script outside Fusion 360 in standard Python (3.9+) to verify geometry calculations, parameters, and component definitions:

```bash
cd C:\Users\lucas\source\repos\modelx_frunk
python fusion_scripts\generate_modelx_frunk_dividers.py
```

---

## 3. Parametric User Parameters (`fx`) Reference

All geometric relationships are controlled by global User Parameters in Fusion 360.

### 3.1 Accessing Parameters in Fusion 360

1. In the Fusion 360 toolbar, navigate to **Modify** > **Change Parameters** (or click the **$f_x$** icon in the ribbon).
2. The **Parameters** dialog opens, displaying **User Parameters** and **Model Parameters**.
3. Edit any expression in the **Expression** column. All downstream components, sketches, extrusions, and joints immediately update in real-time.

```
+------------------------------------------------------------------------------------------------------+
| Parameters (fx)                                                                                 [X]  |
+------------------------------------------------------------------------------------------------------+
| User Parameters                                                                                      |
|   Name             | Unit | Expression | Value     | Comments                                        |
|   -----------------+------+------------+-----------+------------------------------------------------ |
|   BaySpacing       | mm   | 304.80 mm  | 304.8 mm  | Center-to-center bay spacing (12.0 in nominal)  |
|   FrameHeight      | mm   | 280.00 mm  | 280.0 mm  | Frame overall height (11.0 in nominal)          |
|   TrussHeight      | mm   | 35.00 mm   | 35.0 mm   | Floor truss structure height                    |
|   TrussWidth       | mm   | 24.00 mm   | 24.0 mm   | Floor truss and rail profile width              |
|   SlotWidth        | mm   | 6.40 mm    | 6.4 mm    | Guide slot width (5mm panel + 0.7mm clearance)  |
|   SlotDepth        | mm   | 8.00 mm    | 8.0 mm    | Guide slot insertion depth                      |
|   PanelThickness   | mm   | 5.00 mm    | 5.0 mm    | Nominal divider panel thickness                 |
|   PanelWidth       | mm   | 298.00 mm  | 298.0 mm  | Divider panel overall width                     |
|   PanelHeight      | mm   | 275.00 mm  | 275.0 mm  | Divider panel overall height                    |
|   LatticePitch     | mm   | 18.00 mm   | 18.0 mm   | 45-degree diamond mesh pitch                    |
|   LatticeStrut     | mm   | 3.50 mm    | 3.5 mm    | Diamond mesh strut width                        |
|   TolDovetail      | mm   | 0.25 mm    | 0.25 mm   | 3D printing slip clearance for 15-deg dovetail  |
|   TolTenon         | mm   | 0.20 mm    | 0.20 mm   | 3D printing slip clearance for vertical socket  |
|   PinDiameter      | mm   | 5.00 mm    | 5.0 mm    | Transverse locking pin nominal diameter         |
|   DovetailBaseWidth| mm   | 14.00 mm   | 14.0 mm   | Dovetail root width                             |
|   DovetailDepth    | mm   | 8.00 mm    | 8.0 mm    | Dovetail tab depth                              |
|   DovetailAngle    | deg  | 15.00 deg  | 15.0 deg  | Dovetail wedge flare half-angle                 |
+------------------------------------------------------------------------------------------------------+
```

### 3.2 Detailed Parameter Dictionary

| Parameter Name | Default Value | Unit | Description & Engineering Purpose |
| :--- | :--- | :--- | :--- |
| `BaySpacing` | `304.80` | `mm` | Center-to-center grid spacing (12.0 inches). Sized to partition the ~650mm wide frunk tub into 2 equal modular columns. |
| `FrameHeight` | `280.00` | `mm` | Total vertical height from frunk floor to top rail (11.0 inches). Optimized for the deep forward well of the 2017 Model X. |
| `TrussHeight` | `35.00` | `mm` | Height of the base floor truss. Distributes weight and raises divider panels above carpet dirt and moisture. |
| `TrussWidth` | `24.00` | `mm` | Structural profile width for trusses and top rails. Provides stable floor contact and stiffness against bending. |
| `SlotWidth` | `6.40` | `mm` | Width of vertical and horizontal guide channels. Sized for a 5.0mm nominal panel with 0.70mm slip clearance on each side. |
| `SlotDepth` | `8.00` | `mm` | Depth of panel engagement slots. Prevents panels from popping out under lateral vehicle cornering loads ($>0.8\text{ g}$). |
| `PanelThickness` | `5.00` | `mm` | Nominal thickness of the removable divider panel. Balances structural stiffness and lightweight printing. |
| `PanelWidth` | `298.00` | `mm` | Overall divider panel width ($=\text{BaySpacing} - 2\times\text{TrussWidth}/2 + 2\times(\text{SlotDepth} - 1.0\text{mm})$). |
| `PanelHeight` | `275.00` | `mm` | Overall divider panel height ($=\text{FrameHeight} - \text{TrussHeight} + 30.0\text{mm}$ upper engagement). |
| `LatticePitch` | `18.00` | `mm` | Perpendicular center-to-center pitch between adjacent 45° diamond crosshatch struts. |
| `LatticeStrut` | `3.50` | `mm` | Solid width of each diamond lattice strut. Yields an open area of ~72% for maximum weight savings. |
| `TolDovetail` | `0.25` | `mm` | Radial clearance per side on 15° dovetail joints. Compensates for filament thermal shrinkage and nozzle expansion. |
| `TolTenon` | `0.20` | `mm` | Radial clearance per side on 20×20mm vertical tenon sockets. Ensures snug press-fit without wobble. |
| `PinDiameter` | `5.00` | `mm` | Nominal diameter of transverse locking pins (`Pin_Lock_M5`). |
| `DovetailBaseWidth` | `14.00` | `mm` | Root width of 15° dovetail wedge before angular flare. |
| `DovetailDepth` | `8.00` | `mm` | Total longitudinal extension of dovetail tab along connection axis. |
| `DovetailAngle` | `15.00` | `deg` | Dovetail flare half-angle. 15° provides optimal pull-out resistance while allowing smooth vertical/horizontal slide engagement. |

---

### 3.3 Tolerance & Printer Calibration Guide

Different 3D printers and filaments exhibit varying shrinkage, extrusion widths, and layer expansion. Use the following guide to fine-tune tolerances in the **Parameters** window:

```
                            TOLERANCE TUNING SPECTRUM
   [ Ultra-Tight Press-Fit ] <---------- [ Nominal ] ----------> [ Easy Slide / Loose ]
   TolDovetail: 0.15 mm                  TolDovetail: 0.25 mm    TolDovetail: 0.35 mm
   TolTenon:    0.12 mm                  TolTenon:    0.20 mm    TolTenon:    0.30 mm
```

1. **Filament Thermal Shrinkage**:
   * **ASA / ABS**: Shrinks ~0.4% to 0.7% upon cooling. Keep `TolDovetail = 0.25 mm` and `TolTenon = 0.20 mm`. If using an actively heated chamber (Creality K2), parts hold tight tolerances.
   * **PETG**: Shrinks ~0.2%. If joints feel tight, increase `TolDovetail` to `0.30 mm`.
2. **Printer Calibration Check**:
   * Print two test dovetail coupons or a `J_Corner_90` and `FT_Segment_12in`.
   * If the male tab requires excessive force or a mallet: Increase `TolDovetail` by `+0.05 mm`.
   * If the joint wobbles or exhibits play: Decrease `TolDovetail` by `-0.05 mm`.
3. **Custom Divider Materials (Wood / Acrylic Sheets)**:
   * If you plan to laser-cut 3.0mm acrylic or 6.0mm plywood divider panels instead of 3D printing:
     * Set `PanelThickness = 3.0 mm` (or `6.0 mm`).
     * Set `SlotWidth = PanelThickness + 1.2 mm` (`4.2 mm` or `7.2 mm`).

---

## 4. Component Library & Functional Specifications

The generator script produces 8 distinct CAD components organized in the Fusion 360 browser tree:

```
Browser
 ├── (o) Unsaved [Active Design]
 ├── (o) FT_Segment_12in:1       <-- 12" Floor Truss Beam
 ├── (o) VR_Post_Deep:1          <-- 11" Vertical Post with 6.4mm Slots
 ├── (o) HR_Rail_12in:1          <-- 12" Horizontal Top Rail
 ├── (o) J_Corner_90:1           <-- 2-Way 90° Corner Block
 ├── (o) J_Tee_3Way:1            <-- 3-Way T-Junction Block
 ├── (o) J_Cross_4Way:1          <-- 4-Way Cross Junction Block
 ├── (o) DIV_Crosshatch_12x11:1  <-- Slide-in Diamond Mesh Divider Panel
 └── (o) Pin_Lock_M5:1           <-- Transverse Locking Pin
```

### Component Details

```
+---------------------------------------------------------------------------------------------------+
| 1. FT_Segment_12in (Floor Truss Segment)                                                          |
|    - Envelope: 304.8 mm (L) × 24.0 mm (W) × 35.0 mm (H)                                          |
|    - Features: 6 alternating triangular weight-reduction cutouts, +X male dovetail tab,          |
|      -X female dovetail pocket, 20×20mm center post socket, 5.0mm cross pin bore.                 |
+---------------------------------------------------------------------------------------------------+
| 2. VR_Post_Deep (Vertical Rib Post)                                                               |
|    - Envelope: 24.0 mm (W) × 24.0 mm (D) × 280.0 mm (H)                                          |
|    - Features: Dual opposing 6.4mm wide × 8.0mm deep guide slots, bottom 20×20mm tenon            |
|      (with 0.20mm slip tolerance), 5.0mm transverse pin hole, top rail locator pin.              |
+---------------------------------------------------------------------------------------------------+
| 3. HR_Rail_12in (Horizontal Top Rail)                                                             |
|    - Envelope: 304.8 mm (L) × 24.0 mm (W) × 24.0 mm (H)                                          |
|    - Features: Bottom 6.4mm guide channel with 45° chamfer lead-in funnel for easy panel insertion|
|      and end dovetail connection interfaces.                                                      |
+---------------------------------------------------------------------------------------------------+
| 4. J_Corner_90, J_Tee_3Way, J_Cross_4Way (Modular Junction Blocks)                                |
|    - Envelope: 32.0 mm × 32.0 mm × 35.0 mm                                                        |
|    - Features: Multi-directional 15° male dovetail tabs (2-way, 3-way, 4-way), central 20×20mm   |
|      vertical post tenon socket, and transverse 5.0mm pin holes.                                  |
+---------------------------------------------------------------------------------------------------+
| 5. DIV_Crosshatch_12x11 (Slide-In Diamond Mesh Divider)                                           |
|    - Envelope: 298.0 mm (W) × 275.0 mm (H) × 5.0 mm (T)                                          |
|    - Features: 10.0mm solid perimeter rim for smooth slot engagement, 45° diagonal diamond       |
|      lattice mesh (18mm pitch, 3.5mm struts), ergonomic 80×22mm top finger pull handle.           |
+---------------------------------------------------------------------------------------------------+
| 6. Pin_Lock_M5 (Transverse Locking Pin)                                                           |
|    - Envelope: 8.0 mm cap diameter × 32.0 mm total length (28.0mm shaft)                          |
|    - Features: 5.0mm nominal pin shaft, 1° lead-in chamfered tip, flanged 8.0mm grip cap.        |
+---------------------------------------------------------------------------------------------------+
```

---

## 5. Multi-Bay Assembly & Expansion Guide

Using Fusion 360's native **Joint** tools, you can assemble any custom grid configuration for the Tesla Model X frunk tub.

### 5.1 Fusion 360 Joint Assembly Workflow

1. **Ground the Base Component**:
   * In the browser tree, right-click the first corner block (`J_Corner_90:1`) or floor truss and select **Ground**. This fixes its coordinate frame in 3D space.
2. **Create Rigid Joints for Dovetails**:
   * Press <kbd>J</kbd> (or select **Assemble** > **Joint**).
   * **Motion Type**: `Rigid`.
   * **Snap Point 1**: Select the center Joint Origin on the root face of the male dovetail tab.
   * **Snap Point 2**: Select the corresponding Joint Origin on the female dovetail pocket.
   * The components will snap together flush.
3. **Assemble Vertical Posts**:
   * Press <kbd>J</kbd> (`Rigid Joint`).
   * Select the bottom face center of the vertical post tenon (`VR_Post_Deep`).
   * Select the floor socket center on the truss or junction block.
4. **Insert Locking Pins**:
   * Align `Pin_Lock_M5` with the transverse 5.0mm holes on the sockets.
5. **Slide-In Divider Panels**:
   * For dynamic simulation: Create a **Slider Joint** along the vertical Z-axis between the panel side edge and the post guide slot. Set motion limits between $Z = 0\text{ mm}$ and $Z = 280\text{ mm}$.

---

### 5.2 Standard Layout Configurations & Bill of Materials (BOM)

```
+=============================================================================+
|                      STANDARD FRUNK GRID CONFIGURATIONS                     |
+=============================================================================+

   [ Layout A: 1x1 Single Bay ]           [ Layout B: 2x1 Dual Bay ]
   +--------------------------+           +--------------------------+--------------------------+
   | (J_C)=== HR_Rail ===(J_C)|           | (J_C)=== HR_Rail ===(J_T)=== HR_Rail ===(J_C)|
   |  ||                  ||  |           |  ||                  ||                  ||  |
   |  ||  DIV_Crosshatch  ||  |           |  ||     Bay 1        ||     Bay 2        ||  |
   |  ||                  ||  |           |  ||  DIV_Crosshatch  ||  DIV_Crosshatch  ||  |
   | (J_C)=== HR_Rail ===(J_C)|           | (J_C)=== HR_Rail ===(J_T)=== HR_Rail ===(J_C)|
   +--------------------------+           +--------------------------+--------------------------+
   Footprint: ~336 × 336 mm               Footprint: ~640 × 336 mm

   [ Layout C: 2x2 Four-Bay Grid (Recommended for Model X AWD Tub) ]
   +--------------------------+--------------------------+
   | (J_C)=== HR_Rail ===(J_T)=== HR_Rail ===(J_C)|
   |  ||                  ||                  ||  |
   |  ||     Bay (1,1)    ||     Bay (1,2)    ||  |
   | (J_T)=== HR_Rail ===(J_X)=== HR_Rail ===(J_T)|
   |  ||                  ||                  ||  |
   |  ||     Bay (2,1)    ||     Bay (2,2)    ||  |
   | (J_C)=== HR_Rail ===(J_T)=== HR_Rail ===(J_C)|
   +--------------------------+--------------------------+
   Footprint: ~640 × 640 mm (Fills lower frunk tub)

   [ Layout D: 2x3 Six-Bay High-Density Grid ]
   +--------------------------+--------------------------+--------------------------+
   | (J_C)=== HR_Rail ===(J_T)=== HR_Rail ===(J_T)=== HR_Rail ===(J_C)|
   |  ||      Bay 1       ||      Bay 2       ||      Bay 3       ||  |
   | (J_T)=== HR_Rail ===(J_X)=== HR_Rail ===(J_X)=== HR_Rail ===(J_T)|
   |  ||      Bay 4       ||      Bay 5       ||      Bay 6       ||  |
   | (J_C)=== HR_Rail ===(J_T)=== HR_Rail ===(J_T)=== HR_Rail ===(J_C)|
   +--------------------------+--------------------------+--------------------------+
   Footprint: ~640 × 945 mm
```

#### Bill of Materials (BOM) Summary Table

| Component Name | Description | 1×1 Single | 2×1 Dual | 2×2 Grid (Full Frunk) | 2×3 High-Density |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `FT_Segment_12in` | 12" Floor Truss Beam | 4 | 7 | 12 | 17 |
| `VR_Post_Deep` | 11" Vertical Post Column | 4 | 6 | 9 | 12 |
| `HR_Rail_12in` | 12" Horizontal Top Rail | 4 | 7 | 12 | 17 |
| `J_Corner_90` | 2-Way 90° Corner Block | 4 | 4 | 4 | 4 |
| `J_Tee_3Way` | 3-Way T-Junction Block | 0 | 2 | 4 | 6 |
| `J_Cross_4Way` | 4-Way Cross Junction Block | 0 | 0 | 1 | 2 |
| `DIV_Crosshatch_12x11` | Removable Divider Panel | 1 to 4 | 2 to 7 | 4 to 12 | 6 to 17 |
| `Pin_Lock_M5` | M5 Locking Pin | 8 | 14 | 22 | 30 |

---

## 6. Exporting for 3D Printing & Manufacturing

To transfer your parts to slicers (Creality Print, OrcaSlicer, PrusaSlicer, Bambu Studio), use either **Binary 3MF** or **STEP** export.

### 6.1 Exporting as 3MF (Recommended)

3MF preserves exact millimeter scaling, component names, color metadata, and high-density curved surfaces without file bloat.

1. In the Fusion 360 Browser tree, right-click the component you want to export (e.g. `FT_Segment_12in`).
2. Select **Save As Mesh**.
3. Configure the **Save As Mesh** dialog options:
   * **Format**: `3MF (3D Manufacturing Format)`
   * **Unit**: `Millimeter`
   * **Structure**: `One File Per Component`
   * **Refinement**: `High`
     * *Optional Custom Refinement*:
       * Surface Deviation: $\le 0.01\text{ mm}$
       * Normal Deviation: $\le 10.0^\circ$
       * Maximum Edge Length: $10.0\text{ mm}$
4. Click **OK** and save to your project directory.

```
+-----------------------------------------------------------------------+
| Save As Mesh                                                     [X]  |
+-----------------------------------------------------------------------+
|  Format:        [ 3MF (3D Manufacturing Format)           v ]         |
|  Unit Type:     [ Millimeter                              v ]         |
|  Structure:     [ One File Per Component                  v ]         |
|  Refinement:    [ High                                    v ]         |
|                                                                       |
|  Output:                                                              |
|  [X] Send to 3D Print Utility (Creality Print / OrcaSlicer)           |
|                                                                       |
|                                [ OK ]     [ Cancel ]                  |
+-----------------------------------------------------------------------+
```

### 6.2 Exporting as STEP (`.step` / `.stp`)

Modern slicers (OrcaSlicer, Creality Print, Bambu Studio) support direct STEP CAD geometry import, generating pristine toolpaths directly from mathematical surfaces rather than tessellated polygons:

1. Right-click the component > **Export**.
2. Set **Type** to `STEP Files (*.step, *.stp)`.
3. Select your destination directory and click **Export**.

---

### 6.3 Creality K2 Combo Build Orientation Guidelines

The **Creality K2 Combo** features a large **350 × 350 × 350 mm** build volume, allowing all components of this system to be printed flat on the bed with **zero support material**.

```
+=============================================================================+
|                 CREALITY K2 BUILD PLATE PLACEMENT STRATEGY                  |
+=============================================================================+

  [ 1. FT_Segment_12in (304.8mm) ]      [ 2. DIV_Crosshatch_12x11 (298x275mm) ]
  +-------------------------------+     +-------------------------------------+
  | [Triangles] [Socket] [DT]     |     | [========= Finger Pull ==========]  |
  +-------------------------------+     |  /\  /\  /\  /\  /\  /\  /\  /\  /\ |
  Bed Contact: Flat base on bed         |  \/  \/  \/  \/  \/  \/  \/  \/  \/ |
  Supports: ZERO required               |  45° Self-Supporting Diamond Mesh   |
                                        +-------------------------------------+
                                        Bed Contact: Flat face (5.0mm high)
                                        Supports: ZERO required

  [ 3. VR_Post_Deep (280mm) ]           [ 4. Junctions & Pins (Batch) ]
  +-------------------------------+     +---------+  +---------+  (o) (o)
  | Tenon | === Slots === | Pin   |     | J_Corner|  | J_Tee   |  (o) (o)
  +-------------------------------+     +---------+  +---------+  Pins
  Bed Contact: Lay flat on side         Bed Contact: Upright base
  Supports: ZERO required               Supports: ZERO required
```

* **Floor Trusses (`FT_Segment_12in`)**: Place flat on bottom surface. Triangular cutouts bridge at 45° angles without sagging.
* **Vertical Posts (`VR_Post_Deep`)**: Place flat horizontally on one face. The 6.4mm slots run parallel to the build plate and bridge cleanly.
* **Divider Panels (`DIV_Crosshatch_12x11`)**: Lay flat on build plate (Z-height = 5.0mm). 45° diamond struts print continuously as self-supporting infill.
* **Junction Blocks (`J_Corner_90`, `J_Tee_3Way`, `J_Cross_4Way`)**: Print standing upright on bottom base.
* **Locking Pins (`Pin_Lock_M5`)**: Print standing upright with a 3mm brim, or lying flat in batches of 10.

---

## 7. Troubleshooting & FAQ

### Q1: The Python script shows an error about missing `geometry_calc`.
* **Fix**: Ensure that `geometry_calc.py` is in the same directory as `generate_modelx_frunk_dividers.py`, or install the entire `fusion_scripts` folder into Fusion 360's `API/Scripts` directory as detailed in Section 2.

### Q2: Changing `BaySpacing` causes a downstream extrusion error.
* **Cause**: Changing `BaySpacing` to a very small value ($<150\text{ mm}$) may cause the 6 triangular truss cutouts to overlap.
* **Fix**: Keep `BaySpacing` between `200.0 mm` and `400.0 mm`. For smaller compartments, use 12" bays with multiple internal slot dividers.

### Q3: Dovetails fit too tightly or require excessive force.
* **Fix**: Open **Modify** > **Change Parameters** (`fx`). Increase `TolDovetail` from `0.25 mm` to `0.30 mm` or `0.35 mm`. Re-export the 3MF mesh and slice.

### Q4: Does this system fit the refreshed (2021+) Model X frunk?
* **Answer**: The 2021+ refreshed Model X frunk is slightly wider and shallower. By adjusting `FrameHeight` to `230.0 mm` and `BaySpacing` to `320.0 mm` in the parameters window, the system adapts directly to newer vehicle geometries.

---

*Document Revision: 1.0.0 — Automated Parametric Engine for Tesla Model X Frunk Storage.*
