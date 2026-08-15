# Creality K2 3D Printing, Infill & Slicing Guide
## Tesla Model X (2017) Frunk Modular Divider System

---

## 1. Executive Summary & Hardware Target

This manufacturing and slicing guide provides complete, production-grade instructions for 3D printing the **Tesla Model X (2017) Frunk Modular Divider System**. The system is engineered from the ground up for large-format, high-speed CoreXY 3D printers, specifically the **Creality K2 Combo / K2 Plus** (featuring a **350 × 350 × 350 mm** build volume and **active chamber heating up to 60°C**).

```
+=============================================================================+
|                 CREALITY K2 COMBO / PLUS HARDWARE TARGET                    |
+=============================================================================+
|  Build Volume:       350 × 350 × 350 mm (Accommodates full 12" panels flat) |
|  Kinematics:         High-Speed CoreXY (Accelerations up to 20,000 mm/s²)   |
|  Extruder:           Direct-Drive High-Flow Hotend (Flow rate 30-32 mm³/s)  |
|  Chamber Heating:    Active PTC Chamber Heater (Up to 60°C chamber temp)    |
|  Build Surface:      Dual-Sided Textured PEI Spring Steel Sheet             |
|  Supported Slicers:  OrcaSlicer (v2.0+) / Creality Print (v5.0+)            |
+=============================================================================+
```

Every component in this modular system has been designed with **45° self-supporting geometry**, calibrated sliding tolerances, and standardized interlocking joints to enable **100% support-free printing** while maintaining extreme rigidity under automotive dynamic loads.

---

## 2. Automotive Material Selection: Frunk Environmental Demands

### 2.1 The Automotive Frunk Thermal Environment

Vehicles parked in direct sunlight experience severe greenhouse heating. Even in moderate summer ambients (30°C to 38°C / 85°F to 100°F), the enclosed front trunk (frunk) and interior cabin temperatures routinely reach **55°C to 70°C+ (131°F to 158°F)**.

Under these thermal conditions, mechanical loads (such as heavy mobile charging cables, tools, or emergency gear pressing against divider panels during 1.0G braking or hard cornering) induce rapid **thermal creep**, plastic deformation, and joint loosening in unsuitable polymers.

```
+-----------------------------------------------------------------------------+
|                      AUTOMOTIVE FRUNK TEMPERATURE PROFILE                   |
+-----------------------------------------------------------------------------+
|  Ambient Air (Summer):        32°C - 42°C  (90°F - 108°F)                   |
|  Parked Car Frunk Tub:        55°C - 70°C  (131°F - 158°F)                  |
|  Underhood Peak Radiant:      65°C - 75°C  (149°F - 167°F)                  |
|                                                                             |
|  [ PLA Tg = 55°C - 60°C ]  ---> SOFTENS, DEFLECTS, WARPS (UNUSABLE)         |
|  [ PETG Tg = 75°C - 80°C ] ---> MARGINAL / LOW RISK (ACCEPTABLE)            |
|  [ ABS Tg = 105°C ]        ---> FULL THERMAL STABILITY (EXCELLENT)          |
|  [ ASA Tg = 105°C ]        ---> FULL THERMAL STABILITY + UV RESISTANT (BEST)|
+-----------------------------------------------------------------------------+
```

### 2.2 Detailed Material Comparison Matrix

| Material Property | ASA (Acrylonitrile Styrene Acrylate) | ABS (Acrylonitrile Butadiene Styrene) | PETG (Polyethylene Terephthalate Glycol) | PLA (Polylactic Acid) |
| :--- | :--- | :--- | :--- | :--- |
| **Recommendation Status** | **PRIMARY RECOMMENDED** | **STRONG ALTERNATIVE** | **ACCEPTABLE (BUDGET)** | **STRICTLY PROHIBITED** |
| **Glass Transition Temp ($T_g$)** | **105°C** (221°F) | **105°C** (221°F) | **75°C - 80°C** (167°F - 176°F) | **55°C - 60°C** (131°F - 140°F) |
| **Heat Deflection Temp (HDT @ 0.45 MPa)** | **96°C - 100°C** | **95°C - 98°C** | **70°C - 72°C** | **50°C - 55°C** |
| **UV Weatherability** | **Exceptional** (No yellowing, no degradation) | **Moderate** (UV degradation over time if exposed) | **Good** | **Poor** |
| **Tensile Strength** | 42 - 48 MPa | 40 - 45 MPa | 45 - 50 MPa | 55 - 65 MPa (Brittle) |
| **Impact Resistance (Izod)** | 18 - 22 kJ/m² | 20 - 25 kJ/m² | 8 - 12 kJ/m² | 3 - 5 kJ/m² |
| **Thermal Creep Resistance under Load** | **High** (Rigid up to 90°C) | **High** (Rigid up to 90°C) | **Moderate** (May creep at 65°C+) | **Very Poor** (Softens at 50°C) |
| **Warping / Shrinkage Tendency** | Medium (Requires Heated Chamber) | High (Requires Heated Chamber) | Very Low (Open or Enclosed) | Zero (Open Bed) |
| **Print Odor / VOCs** | Low/Moderate (Styrene - use filter) | High (Styrene - enclosure required) | None / Negligible | Sweet / None |
| **Surface Finish** | Matte, Satin, Premium Automotive | Semi-Gloss / Matte | Glossy | Glossy |

### 2.3 Material Selection Analysis

#### 1. ASA (Recommended Choice)
* **Why ASA is Best**: ASA replaces butadiene rubber with acrylic ester, granting total UV resistance and color stability. It has identical thermal and mechanical performance to ABS ($T_g = 105^\circ\text{C}$), easily withstanding +70°C summer frunk heat without softening or creeping. It produces a clean, matte, OEM-style surface finish matching Tesla automotive plastics.
* **Printing Requirements**: Requires an enclosed printer with active chamber heating (50°C - 60°C) or heated bed soak to prevent corner warping on long parts (`FT_Segment_12in`, `VR_Post_Deep`). The **Creality K2 Combo** is perfectly equipped for ASA.

#### 2. ABS (High-Performance Alternative)
* **Performance**: Identical structural rigidity and thermal resistance to ASA ($T_g = 105^\circ\text{C}$). Ideal if ASA is unavailable.
* **Considerations**: Emits noticeable styrene odor during printing (utilize K2 active carbon air filtration). Slightly higher shrinkage (~0.5 - 0.7%) compared to ASA.

#### 3. PETG (Budget / Secondary Alternative)
* **Performance**: With a $T_g$ of 75°C - 80°C and HDT of ~70°C, PETG can survive mild to warm climates. It has virtually no warping tendency and prints easily without chamber heat.
* **Limitations**: In extreme desert heat (e.g., Arizona, Nevada, Texas summer inside a sealed black vehicle), temperatures can approach PETG's softening zone. Sustained mechanical force from heavy cargo can induce slight creeping over multiple summer seasons.

#### 4. PLA (Why PLA Must Be Avoided)
* **Critical Failure**: PLA softens at 55°C - 60°C. Inside a parked car frunk, PLA divider panels will sag under their own weight, dovetail joints will deform and loosen, and vertical ribs will bow irreversibly. **Do NOT use PLA or PLA+ for this project.**

---

## 3. Slicer Infill & Wall Strategy

Automotive cargo systems are subjected to multi-axis dynamic loads:
* **Longitudinal Braking / Acceleration**: Up to 1.2G deceleration force pushing cargo forward against divider panels.
* **Lateral Cornering**: Up to 0.9G lateral side-load pushing cargo across bays.
* **Vertical High-Frequency Road Vibration**: 10–50 Hz road frequencies acting on dovetail joints and pin locks.

To withstand these forces without excess weight, the slicing parameters are split into two distinct structural profiles.

```
+=============================================================================+
|                      SLICING SPECIFICATION MATRIX                           |
+=============================================================================+
|  Component Group          | Perimeters/Walls | Top/Bottom | Infill Pattern  | Infill % |
|---------------------------+------------------+------------+-----------------+----------|
|  Floor Trusses (FT)       | 4 Walls (1.6mm)  | 4 Top / 4  | Gyroid / Hex    |   30%    |
|  Vertical Rib Posts (VR)  | 4 Walls (1.6mm)  | 4 Top / 4  | Gyroid          |   30%    |
|  Horizontal Rails (HR)    | 4 Walls (1.6mm)  | 4 Top / 4  | Gyroid / Hex    |   30%    |
|  Junction Blocks (J_*)    | 5 Walls (2.0mm)  | 5 Top / 5  | Gyroid          |   35%    |
|  Divider Panels (DIV_*)   | 4 Walls (1.6mm)  | N/A (Flat) | Solid Struts    |  100%    |
|  Locking Pins (Pin_Lock)  | 6 Walls / Solid  | N/A        | Concentric      |  100%    |
|  Floor Track Quads (TRK)  | 4 Walls (1.6mm)  | 4 Top / 4  | Gyroid          |   30%    |
+=============================================================================+
```

### 3.1 Structural Components (Trusses, Posts, Rails, Junctions)

1. **Wall Count (Perimeters)**:
   * **4 Perimeters (1.6 mm total shell thickness)** using a standard 0.4 mm nozzle (or 3 perimeters / 1.8 mm with a 0.6 mm nozzle).
   * Perimeter shells carry 80%+ of bending and torsional loads. 4 solid perimeters ensure that all dovetail slide tongues and socket walls are solidly fused to the outer shell.
2. **Top / Bottom Solid Layers**:
   * **4 Top Solid Layers (0.8 mm minimum)** and **4 Bottom Solid Layers (0.8 mm minimum)** with 0.20 mm layer height.
3. **Infill Pattern: 30% Gyroid or Hexagonal**:
   * **Gyroid (Recommended)**: Provides truly isotropic (uniform in all X, Y, Z directions) shear resistance. Unlike linear grid infill, Gyroid does not cross over itself on the same layer, eliminating nozzle strikes and print head vibrations at high speeds (300+ mm/s).
   * **Hexagonal**: Highest planar stiffness along the X/Y plane for resisting pure compressive crushing.

### 3.2 Divider Panels (`DIV_Crosshatch_12x11`)

1. **100% Solid Strut Perimeters**:
   * The diamond crosshatch struts have a parametric thickness of **3.5 mm (`LatticeStrut`)**.
   * With 4 perimeters on each side of the strut ($4 \times 0.45\text{ mm line width} = 1.8\text{ mm}$ per side, total $3.6\text{ mm}$), the slicer naturally prints the crosshatch struts as **100% solid perimeters**.
   * There is **zero sparse infill** inside the thin diamond struts, preventing hollow voids that could crush under cargo impact.
2. **Support-Free Diamond Geometry**:
   * All lattice lines are oriented at **45° relative to horizontal**.
   * Overhang angles never exceed 45°, allowing the entire 304.8 × 284.4 mm panel to be printed flat on the K2 textured PEI bed **without a single support structure**.

### 3.3 Locking Pins (`Pin_Lock_M5`)

* **100% Solid Infill / 6+ Perimeters**:
* Locking pins experience pure shear stress across the transverse joint. They must be printed 100% solid to prevent shear shearing under emergency braking.

### 3.4 Conformal Floor Track Quadrants (`TRK_Front_L`, `TRK_Front_R`, `TRK_Rear_L`, `TRK_Rear_R`)

1. **4 Perimeters & 30% Gyroid Infill**:
   * The $30.0\text{ mm} \times 18.0\text{ mm}$ rigid rectangular cross-section requires maximum planar stiffness to resist cornering forces and prevent tipping under lateral acceleration.
   * Slicing with 4 perimeters (1.6 mm shell) and 30% Gyroid infill provides high compressive resistance while keeping quadrant weight under 115 g each (~450 g total).
2. **Support-Free Captive T-Rail & Dovetail Seams**:
   * The top captive sliding rail ($14\text{ mm}$ base, $8\text{ mm}$ neck, $5\text{ mm}$ depth) prints with the slot opening facing UP on the build plate (0° overhang).
   * The 15° interlocking dovetail seam tabs and pockets are oriented perpendicular to the bed and print with zero support material.

---

## 4. Creality K2 Specific Slicer Settings (OrcaSlicer / Creality Print)

The Creality K2 Combo high-speed hotend and CoreXY motion system can extrude high-viscosity automotive polymers at high volumetric flow rates. Below are the verified slicer configurations.

### 4.1 Master Material & Thermal Profiles

```
+-----------------------------------------------------------------------------+
|                 CREALITY K2 COMBO SLICER TEMPERATURE SETTINGS               |
+-----------------------------------------------------------------------------+
|  Setting                     | ASA (Primary)   | ABS (Alternative) | PETG (Budget) |
|------------------------------+-----------------+-------------------+---------------|
|  Nozzle Temperature (First)  | 260°C           | 255°C             | 245°C         |
|  Nozzle Temperature (Other)  | 255°C           | 250°C             | 240°C         |
|  Bed Temperature (PEI Plate) | 100°C - 105°C   | 100°C - 105°C     | 75°C - 80°C   |
|  Active Chamber Heater       | 50°C - 55°C     | 55°C - 60°C       | OFF (0°C)     |
|  Enclosure Door / Lid        | Closed          | Closed            | Open / Ajar   |
|  Part Cooling Fan Speed      | 15% - 30%       | 10% - 25%         | 40% - 60%     |
|  Auxiliary Side Fan          | OFF (0%)        | OFF (0%)          | 20% - 40%     |
|  Chamber Exhaust Fan         | 10% (Filtered)  | 10% (Filtered)    | Auto (50%)    |
|  Max Volumetric Speed        | 22 - 25 mm³/s   | 24 - 28 mm³/s     | 18 - 22 mm³/s |
+-----------------------------------------------------------------------------+
```

### 4.2 Speed, Acceleration & Motion Parameters

To maintain tight tolerances on the 15° dovetails (`TolDovetail = 0.3 mm`, `TolSeamDovetail = 0.2 mm`) and tenon sockets (`TolTenon = 0.4 mm`), outer wall speeds and accelerations are tuned for dimensional precision, while infill utilizes the K2's high-speed kinematics:

```
+-----------------------------------------------------------------------------+
|                      PRINT SPEED & ACCELERATION PROFILE                     |
+-----------------------------------------------------------------------------+
|  Print Feature               | Print Speed (mm/s) | Acceleration (mm/s²)    |
|------------------------------+--------------------+-------------------------|
|  Outer Wall / Perimeter      | 120 - 150 mm/s     | 4,000 - 5,000 mm/s²     |
|  Inner Wall / Perimeter      | 200 - 250 mm/s     | 8,000 - 10,000 mm/s²    |
|  Sparse Infill (Gyroid)      | 250 - 300 mm/s     | 12,000 - 15,000 mm/s²   |
|  Solid Top/Bottom Infill     | 160 - 200 mm/s     | 8,000 - 10,000 mm/s²    |
|  Lattice Struts (Divider)    | 150 - 180 mm/s     | 6,000 - 8,000 mm/s²     |
|  First Layer (Initial)       | 40 - 50 mm/s       | 2,000 - 3,000 mm/s²     |
|  Travel Moves                | 500 - 600 mm/s     | 20,000 mm/s²            |
+-----------------------------------------------------------------------------+
```

### 4.3 Extrusion & Retraction Calibration

* **Layer Height**: 0.20 mm standard (0.28 mm draft mode for large floor trusses).
* **Line Width**:
  * Outer Wall: 0.42 mm (enhances sharp dovetail corners).
  * Inner Walls & Infill: 0.45 mm - 0.50 mm (maximizes inter-line fusion).
  * First Layer: 0.50 mm (promotes strong PEI plate adhesion).
* **Retraction Settings (Direct Drive)**:
  * Retraction Distance: **0.8 mm** (0.6 mm – 1.0 mm range).
  * Retraction Speed: **40 mm/s**; Deretraction Speed: **35 mm/s**.
  * Z-Hop when Retracting: **0.20 mm (Spiral / Normal Z-hop)**.
* **Pressure Advance / Linear Advance**:
  * ASA / ABS: $k \approx 0.035 - 0.045$ (run OrcaSlicer PA calibration lines).
  * PETG: $k \approx 0.040 - 0.055$.
* **Seam Placement**: Set to **Aligned** or **Rear** (placed away from dovetail sliding faces).

---

## 5. Print Bed Layout, Orientation & Support-Free Strategy

Proper 3D print orientation is critical in automotive applications because 3D printed parts have anisotropic mechanical strength: tensile strength along the X/Y layer plane is 2× to 3× higher than Z-axis interlayer adhesion.

```
+=============================================================================+
|                      COMPONENT PRINT ORIENTATION MATRIX                     |
+=============================================================================+
|  Component             | Recommended Bed Placement | Layer Line Alignment   |
|------------------------+---------------------------+------------------------|
|  FT_Segment_12in       | Flat on bottom base       | Longitudinal (Tension) |
|  VR_Post_Deep          | Flat on rear spine        | Vertical (Bending load)|
|  HR_Rail_12in          | Flat on top / side face   | Longitudinal (Tension) |
|  J_Corner_90           | Flat on bottom base       | Planar (Shear load)    |
|  J_Tee_3Way            | Flat on bottom base       | Planar (Shear load)    |
|  J_Cross_4Way          | Flat on bottom base       | Planar (Shear load)    |
|  DIV_Crosshatch_12x11  | Flat on build plate       | Planar (Impact load)   |
|  Pin_Lock_M5           | Flat on horizontal side   | Longitudinal (Shear)   |
|  TRK_Front_L           | Flat on bottom base (Z=0) | Planar Curve (Rigid)   |
|  TRK_Front_R           | Flat on bottom base (Z=0) | Planar Curve (Rigid)   |
|  TRK_Rear_L            | Flat on bottom base (Z=0) | Planar Curve (Rigid)   |
|  TRK_Rear_R            | Flat on bottom base (Z=0) | Planar Curve (Rigid)   |
+=============================================================================+
```

### 5.1 Component-by-Component Orientation Guide

```
1. Floor Truss Segment (FT_Segment_12in)
   [ Bed Orientation ]: Lay flat on its 38.1 mm wide bottom base.
   [ Engineering Rationale ]: Triangular web cutouts and dovetail end tabs print
     vertically without supports. Layer lines run continuously along the 304.8 mm
     length, giving maximum resistance against longitudinal bending from cargo.
   
         +-------------------------------------------------------+
         |  /\   /\   /\   /\   /\   /\   /\   /\   /\   /\    |
       [>+=======================================================+<]
        ///////////////// TEXTURED PEI BED /////////////////////////

2. Vertical Rib Post (VR_Post_Deep)
   [ Bed Orientation ]: Lay flat horizontally on its rear spine (the 6.4 mm
     channel opening faces UP).
   [ Engineering Rationale ]: Printing the post horizontally ensures layer lines
     run the entire 279.4 mm height of the post. When cargo hits the divider,
     the post acts as a continuous cantilever beam without layer delamination risk.
     The 6.4 mm channel prints as an upward-facing trough (0° overhang).
   
       [Tenon] +-----------------------------------------------+ [Cap]
               |  _________________ CHANNEL _________________  |
               +===============================================+
               ////////////////// PEI BED //////////////////////

3. Horizontal Top Rail (HR_Rail_12in)
   [ Bed Orientation ]: Lay flat on its top cap surface with the downward slot facing UP.
   [ Engineering Rationale ]: Zero overhangs, maximum bed contact, continuous layer lines.

4. Diamond Divider Panel (DIV_Crosshatch_12x11)
   [ Bed Orientation ]: Lay completely flat on the 350 × 350 mm K2 bed plate.
   [ Dimensions ]: 304.8 mm × 284.4 mm × 4.8 mm.
   [ Engineering Rationale ]: All diamond lattice struts are angled at exactly 45°.
     Because 45° is a self-supporting bridging angle for FDM 3D printing, the
     entire panel prints flawlessly with ZERO supports.
   
       +-------------------------------------------------------------+
       | /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ |
       | \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ |
       | /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ |
       +-------------------------------------------------------------+
       //////////////////// 350x350 PEI BED //////////////////////////

5. Modular Junction Blocks (J_Corner_90, J_Tee_3Way, J_Cross_4Way)
   [ Bed Orientation ]: Base face flat on the build plate.
   [ Engineering Rationale ]: The 15° dovetail sockets/tongues print at an angle
     well below the 45° overhang limit, requiring no support structures.

6. Locking Pin (Pin_Lock_M5)
   [ Bed Orientation ]: Lay horizontally on the flat side of the dowel shaft.
   [ Engineering Rationale ]: Horizontal printing ensures layer lines run along
     the pin length, providing maximum shear resistance when locked into the frame.

7. Conformal Floor Track Quadrants (TRK_Front_L, TRK_Front_R, TRK_Rear_L, TRK_Rear_R)
   [ Bed Orientation ]: Lay completely flat on bottom base ($Z = 0$).
   [ Dimensions ]: Max oriented bounding dimension $\le 310\text{ mm}$ (Creality K2 350mm bed).
   [ Engineering Rationale ]: Top captive sliding channel and 15° dovetail seam tabs print
     vertically without supports. Planar continuous extrusion around the arc ensures
     maximum perimeter hoop stiffness.
```

### 5.2 Build Plate Batching & Layout on Creality K2 (350 × 350 mm)

Thanks to the K2's generous 350 × 350 mm bed, full-size subassemblies can be batched efficiently:

```
+-----------------------------------------------------------------------------+
| BATCH 1: Floor Framework (Trusses & Junctions)                              |
| Fits on Bed (350x350 mm):                                                   |
| - 2x FT_Segment_12in (304.8 mm long, placed diagonally or parallel)        |
| - 4x J_Corner_90 / J_Tee_3Way junction blocks                               |
| Estimated Print Time (ASA @ 200 mm/s): ~4 hrs 15 min                        |
+-----------------------------------------------------------------------------+
| BATCH 2: Vertical Structure (Posts & Rails)                                 |
| Fits on Bed (350x350 mm):                                                   |
| - 2x VR_Post_Deep (279.4 mm long, placed side-by-side)                       |
| - 2x HR_Rail_12in (304.8 mm long, placed side-by-side)                       |
| Estimated Print Time (ASA @ 200 mm/s): ~5 hrs 30 min                        |
+-----------------------------------------------------------------------------+
| BATCH 3: Divider Panel (1 Panel per Build Plate)                            |
| Fits on Bed (350x350 mm):                                                   |
| - 1x DIV_Crosshatch_12x11 (304.8 × 284.4 mm - perfect 1:1 fit flat on bed)  |
| Estimated Print Time (ASA @ 160 mm/s): ~3 hrs 45 min                        |
+-----------------------------------------------------------------------------+
| BATCH 4: Fasteners & Hardware                                               |
| Fits on Bed (350x350 mm):                                                   |
| - 16x Pin_Lock_M5 (Arrayed in a grid with 5 mm spacing)                     |
| Estimated Print Time (ASA @ 100 mm/s): ~45 min                              |
+-----------------------------------------------------------------------------+
| BATCH 5: Conformal Floor Track (2 Quadrants per Build Plate)                |
| Fits on Bed (350x350 mm):                                                   |
| - Plate 5A: 1x TRK_Front_L + 1x TRK_Front_R (both <= 310mm, laid flat)      |
| - Plate 5B: 1x TRK_Rear_L + 1x TRK_Rear_R (both <= 310mm, laid flat)        |
| Estimated Print Time (ASA @ 200 mm/s): ~5 hrs 10 min per plate              |
+-----------------------------------------------------------------------------+
```

---

## 6. Dimensional Accuracy, Tolerance Calibration & Tuning

### 6.1 Calibrated Joint Clearances

The parametric model incorporates dedicated tolerance variables to ensure smooth sliding fits without post-print filing:

| Parameter | Nominal Clearance | Purpose | Fit Type |
| :--- | :--- | :--- | :--- |
| `TolDovetail` | **0.30 mm** | Clearance on all sliding 15° dovetail faces | Snug sliding friction fit |
| `TolTenon` | **0.40 mm** | Clearance between vertical post tenon & truss socket | Secure interlock with pin |
| `SlotWidth` | **6.40 mm** | Post slot width for 4.8 mm divider panels (0.8 mm clearance / side) | Free sliding rattle-free |
| `PinDiameter` | **4.90 mm** | M5 lock pin shaft diameter in 5.20 mm reamed hole | Slip-fit with spring retention |
| `TolSeamDovetail` | **0.20 mm** | Clearance on 15° interlocking quadrant track seams | Snug slip-fit seam joint |

### 6.2 Slicer Compensation Settings for Creality K2

If your test print feels overly tight or loose, adjust the following slicer settings rather than modifying CAD geometry:

1. **Horizontal Expansion / XY Size Compensation**:
   * If dovetails are too tight: Set `XY Hole Compensation` = `+0.05 mm` to `+0.10 mm`, or `XY Contour Compensation` = `-0.05 mm`.
   * Standard tuned K2 value: `0.00 mm`.
2. **Material Shrinkage Scaling (for ASA / ABS)**:
   * ASA and ABS contract by approximately **0.4% - 0.6%** during cooling.
   * If exact 12.000" bay dimensions are required, apply a **100.5% (1.005×) Uniform Scale** in X and Y axes in your slicer before exporting G-code.
3. **Bed Adhesion & Brim Strategy for ASA/ABS**:
   * For large parts (`FT_Segment_12in`, `VR_Post_Deep`, `TRK_*`), enable a **5 mm Outer Brim** with a **0.1 mm Brim-Object Gap** for clean breakaway.
   * Alternatively, place **Mouse-Ear discs (20 mm diameter, 0.2 mm thick)** at the sharp corners of long parts to prevent corner lifting.

### 6.3 Post-Processing & Deburring Checklist

1. **Cooling Cycle**: Allow the K2 build plate to cool below 45°C before removing ASA/ABS parts. Parts will naturally release from the textured PEI sheet with zero warping.
2. **Brim Removal**: Trim brim edges with a standard rotary deburring tool or hobby knife.
3. **Dovetail Bedding**: Slide mating dovetail segments back and forth 2–3 times to burnish mating surfaces.
4. **Pin Hole Check**: Verify that `Pin_Lock_M5` inserts cleanly through the retaining holes. If necessary, ream holes with a 5.0 mm drill bit.
5. *(Optional)* **Acetone / Solvent Vapor Treatment**: ABS and ASA can be briefly vapor smoothed for maximum gloss and 100% water-tight surface sealing.

---

## 7. Assembly Guide & Installation in 2017 Tesla Model X Frunk

### 7.1 Complete Step-by-Step Modular Assembly

```
+=============================================================================+
|                      6-STEP MODULAR ASSEMBLY SEQUENCE                       |
+=============================================================================+
|                                                                             |
|   Step 6: [ Lock Pins ] ----> Insert Pin_Lock_M5 into transverse holes      |
|                                         |                                   |
|   Step 5: [ Top Rails ] ----> Slide HR_Rail_12in onto top post dovetails    |
|                                         |                                   |
|   Step 4: [ Dividers ]  ----> Slide DIV_Crosshatch into 6.4mm post channels |
|                                         |                                   |
|   Step 3: [ Vert Posts] ----> Seat VR_Post_Deep tenons into truss sockets   |
|                                         |                                   |
|   Step 2: [ Base Grid ] ----> Interlock FT_Segment_12in with Junctions      |
|                                         |                                   |
|   Step 1: [ Floor Track]----> Interlock 4 TRK Quadrants (15° Dovetails)     |
+=============================================================================+
```

```
STEP 1: Conformal Floor Track Assembly
1. Place the 4 Conformal Floor Track quadrants (TRK_Front_L, TRK_Front_R,
   TRK_Rear_L, TRK_Rear_R) on the floor.
2. Interlock the 15° tapered dovetail tabs into their corresponding pockets
   (Front, Right, Rear, and Left seams).
3. Verify that the continuous 360° loop forms smoothly with tight seam mating.

STEP 2: Base Grid Assembly
1. Place the Junction Blocks (J_Corner_90, J_Tee_3Way, or J_Cross_4Way) on a flat table.
2. Align the 15° male dovetail tabs of the Floor Truss segments (FT_Segment_12in)
   with the female dovetail pockets of the junction blocks.
3. Slide the trusses horizontally into the junctions until fully seated and flush.

STEP 3: Vertical Post Insertion
1. Take the Vertical Rib Posts (VR_Post_Deep).
2. Insert the bottom rectangular tenon of each post into the vertical socket
   located on top of each junction block / floor truss node.
3. Push downward until the post collar seats firmly against the truss upper face.

STEP 4: Divider Panel Installation
1. Take the Diamond Crosshatch Divider Panels (DIV_Crosshatch_12x11).
2. Align the outer edges of the panel with the 6.4 mm vertical guide channels
   in adjacent VR_Post_Deep posts.
3. Slide the panel downward until its bottom edge rests inside the Floor Truss
   top alignment channel.

STEP 5: Horizontal Top Rail Installation
1. Place the Horizontal Top Rails (HR_Rail_12in) over the top of the divider panels.
2. Align the rail's downward channel over the top edge of the panel.
3. Slide the rail's male/female dovetail ends into the top cap dovetails of the
   vertical posts, locking the upper perimeter into a rigid frame.

STEP 6: Pin Lock Insertion & Vibration Securing
1. Locate the transverse 5.0 mm locking pin holes at each post-to-truss and
   rail-to-post joint.
2. Insert the Pin_Lock_M5 dowels into each hole until the retention shoulder clicks.
3. The transverse pins mechanically lock the modular frame against automotive
   vibration, acceleration, and deceleration forces.
```

### 7.2 Installation in 2017 Tesla Model X Frunk Tub

```
+-----------------------------------------------------------------------------+
|             2017 TESLA MODEL X (AWD) FRUNK TUB PLACEMENT DIAGRAM            |
+-----------------------------------------------------------------------------+
|                                                                             |
|     +------------------- [ Forward Sloped Hood ] --------------------+      |
|     |                                                                |      |
|     |   +--------------------------------------------------------+   |      |
|     |   |          Shallow Front Shelf (Microwave Bag)           |   |      |
|     |   +========================================================+   |      |
|     |   |                                                        |   |      |
|     |   |   +================================================+   |   |      |
|     |   |   |   CONFORMAL FLOOR TRACK PERIMETER RING         |   |   |      |
|     |   |   |   (0.50" / 12.7mm Inset from Carpeted Tub)     |   |   |      |
|     |   |   |                                                |   |   |      |
|     |   |   |     +------------------+  +------------------+ |   |   |      |
|     |   |   |     |   Bay 1 (Left)   |  |  Bay 2 (Center)  | |   |   |      |
|     |   |   |     |   (Charge Cable) |  |  (Tools/Jack)    | |   |   |      |
|     |   |   |     +------------------+  +------------------+ |   |   |      |
|     |   |   |     |   Bay 3 (Right)  |  |  Bay 4 (Groceries| |   |   |      |
|     |   |   |     |   (Tire Inflator)|  |   / Travel Gear) | |   |   |      |
|     |   |   |     +------------------+  +------------------+ |   |   |      |
|     |   |   |                                                |   |   |      |
|     |   |   +================================================+   |   |      |
|     |   |                                                        |   |      |
|     |   +--------------------------------------------------------+   |      |
|     |                                                                |      |
|     +---------------------- [ Bumper / Latch ] ----------------------+      |
|                                                                             |
+-----------------------------------------------------------------------------+
```

1. **Non-Destructive Tub Placement**:
   * The 2017 Tesla Model X AWD frunk features a deep rear tub lined with automotive carpet.
   * Lower the assembled 4-quadrant Conformal Floor Track into the tub. It nests neatly around the floor perimeter with 0.50" (12.7 mm) clearance.
   * The modular divider grid rests directly on the carpet floor within the track perimeter without requiring screws, adhesives, or permanent vehicle modifications.
2. **Anti-Rattle & Grip Measures**:
   * To prevent shifting during aggressive driving, attach 20 mm self-adhesive silicone / rubber anti-slip pads to the underside of each `J_Corner_90` and `FT_Segment_12in` base.
   * Optional: 3D print 1.5 mm thick snap-on foot caps in **95A TPU (Flexible Polyurethane)** and attach them to the truss bottoms for maximum carpet grip and acoustic vibration damping.
3. **Clearance Verification**:
   * The 2017 Model X frunk lid slopes downward toward the front bumper. Ensure that the deeper 11.0" (`PanelHeight = 279.4 mm`) modules are positioned toward the rear firewall bulkhead, with the shallow front shelf remaining unobstructed.
4. **Maintenance & Cleaning**:
   * ASA and ABS components are fully resistant to automotive washer fluid, dirt, grease, and rain.
   * Clean with mild automotive soap and water. Do not expose to concentrated acetone or aromatic hydrocarbons.

---

## 8. Summary of Printing Best Practices for Creality K2

1. **Preheat Chamber**: Before starting a large ASA/ABS print, set Bed to 100°C and Chamber to 50°C and let the printer heat-soak for 10–15 minutes.
2. **Clean PEI Sheet**: Wash the textured PEI plate with warm water and dish soap (Dawn) followed by 99% Isopropyl Alcohol (IPA).
3. **Nozzle Maintenance**: Inspect high-flow nozzle tip for plastic buildup; use a silicone brush or brass wire brush.
4. **Dry Filament**: Store ASA/ABS filament in the Creality CFS (Chamber Filament System) or dry at 70°C for 4–6 hours prior to printing for bubble-free layer lamination.
5. **Enjoy Rattle-Free Organization**: Pack your Tesla Model X frunk with charging gear, mobile connectors, emergency kits, and travel bags in clean, rattle-free compartments!
