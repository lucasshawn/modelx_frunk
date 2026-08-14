# Tesla Model X 2017 Frunk Modular Divider System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a parametric, 3D printable modular divider system for the 2017 Tesla Model X 100D frunk, engineered for Autodesk Fusion 360 and optimized for printing on a Creality K2 Combo (350×350×350 mm).

**Architecture:** The project provides a parametric Python automation script for the Autodesk Fusion 360 API that generates a 3-tier modular assembly (Floor Trusses with triangular webs, 11" Vertical Ribs with 6.4mm slots, 12" Horizontal Top Rails, 45° Diamond Lattice slide-in Dividers, Junctions, and Dovetail Locking Pins), complete with automated geometry test suites and detailed slicing/manufacturing guides.

**Tech Stack:** Python 3 (Geometry engine & Fusion 360 API `adsk.core`/`adsk.fusion`), `pytest` for test verification, Markdown for CAD & 3D printing guides.

## Global Constraints

- Center-to-center bay spacing: `12.0 in` (304.8 mm)
- Frame overall height: `11.0 in` (280.0 mm)
- Guide slot width: `6.4 mm` (for `5.0 mm` divider panel with `0.7 mm` clearance per side)
- Guide slot depth: `8.0 mm`
- Interlocking joint: 15° wedge sliding dovetail with `0.25 mm` 3D-printing slip clearance
- Vertical socket tenon: 20 mm × 20 mm with `0.20 mm` slip clearance and transverse 5 mm locking pin
- Divider wall: 10 mm solid perimeter bezel with exposed 45° diagonal diamond crosshatch (3.5 mm strut width, 18 mm diamond pitch)
- Printer compatibility: All parts sized under 310 mm to fit Creality K2 (350×350×350 mm) without supports
- Structural infill: Sliced with 4 walls/perimeters and 30% Hexagonal or Gyroid infill

---

### Task 1: Parametric Geometry & Coordinate Engine

**Files:**
- Create: `fusion_scripts/geometry_calc.py`
- Test: `tests/test_geometry_calc.py`

**Interfaces:**
- Produces:
  - `class FrunkParameters`: Dataclass holding all system dimensions and tolerances with unit conversions.
  - `def calculate_dovetail_profile(male: bool, tol: float) -> list[tuple[float, float]]`: Generates 2D polygon vertices for 15° dovetail tabs/pockets.
  - `def calculate_truss_web_triangles(span_length: float, height: float, web_thickness: float) -> list[list[tuple[float, float]]]`: Generates triangular cutout coordinates for floor truss spans.
  - `def calculate_diamond_lattice_segments(width: float, height: float, pitch: float, strut_w: float) -> list[tuple[tuple[float, float], tuple[float, float]]]`: Computes 45° intersecting lattice line segments.

- [ ] **Step 1: Write the failing test for geometry calculations**

```python
# tests/test_geometry_calc.py
import pytest
import math
from fusion_scripts.geometry_calc import (
    FrunkParameters,
    calculate_dovetail_profile,
    calculate_truss_web_triangles,
    calculate_diamond_lattice_segments
)

def test_frunk_parameters_defaults():
    params = FrunkParameters()
    assert params.bay_spacing_mm == pytest.approx(304.8, abs=0.1)
    assert params.frame_height_mm == pytest.approx(280.0, abs=0.1)
    assert params.slot_width_mm == 6.4
    assert params.panel_thickness_mm == 5.0
    assert params.tol_dovetail_mm == 0.25
    assert params.tol_tenon_mm == 0.20

def test_dovetail_profile_clearance():
    params = FrunkParameters()
    male_pts = calculate_dovetail_profile(male=True, tol=params.tol_dovetail_mm)
    female_pts = calculate_dovetail_profile(male=False, tol=params.tol_dovetail_mm)
    
    # Male width at base should be narrower than female width by 2 * tolerance
    male_width = max(p[0] for p in male_pts) - min(p[0] for p in male_pts)
    female_width = max(p[0] for p in female_pts) - min(p[0] for p in female_pts)
    assert female_width - male_width == pytest.approx(2 * params.tol_dovetail_mm, abs=0.01)

def test_truss_web_triangles():
    triangles = calculate_truss_web_triangles(span_length=304.8, height=35.0, web_thickness=4.0)
    assert len(triangles) >= 4
    for tri in triangles:
        assert len(tri) == 3

def test_diamond_lattice_45_degree():
    segments = calculate_diamond_lattice_segments(width=278.0, height=255.0, pitch=18.0, strut_w=3.5)
    assert len(segments) > 10
    for (x1, y1), (x2, y2) in segments:
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        # 45-degree angle check: dx should equal dy (within boundary clipping tolerance)
        angle = math.degrees(math.atan2(dy, dx))
        assert angle == pytest.approx(45.0, abs=1.0) or math.isclose(dx, 0) or math.isclose(dy, 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_geometry_calc.py -v`  
Expected: FAIL with ModuleNotFoundError: No module named 'fusion_scripts'

- [ ] **Step 3: Implement `fusion_scripts/geometry_calc.py`**

```python
# fusion_scripts/geometry_calc.py
from dataclasses import dataclass
import math
from typing import List, Tuple

@dataclass
class FrunkParameters:
    bay_spacing_mm: float = 304.8       # 12.0 inches
    frame_height_mm: float = 280.0      # 11.0 inches
    truss_height_mm: float = 35.0
    truss_width_mm: float = 24.0
    slot_width_mm: float = 6.4
    slot_depth_mm: float = 8.0
    panel_thickness_mm: float = 5.0
    panel_width_mm: float = 298.0
    panel_height_mm: float = 275.0
    lattice_pitch_mm: float = 18.0
    lattice_strut_mm: float = 3.5
    tol_dovetail_mm: float = 0.25
    tol_tenon_mm: float = 0.20
    pin_diameter_mm: float = 5.0
    dovetail_base_width_mm: float = 14.0
    dovetail_depth_mm: float = 8.0
    dovetail_angle_deg: float = 15.0

def calculate_dovetail_profile(male: bool, tol: float, base_w: float = 14.0, depth: float = 8.0, angle_deg: float = 15.0) -> List[Tuple[float, float]]:
    rad = math.radians(angle_deg)
    flare = depth * math.tan(rad)
    offset = -tol if male else tol
    
    w_root = (base_w + 2 * offset) / 2.0
    w_tip = (base_w + 2 * flare + 2 * offset) / 2.0
    
    if male:
        return [
            (-w_root, 0.0),
            (-w_tip, depth),
            (w_tip, depth),
            (w_root, 0.0)
        ]
    else:
        return [
            (-w_root, 0.0),
            (-w_tip, depth),
            (w_tip, depth),
            (w_root, 0.0)
        ]

def calculate_truss_web_triangles(span_length: float, height: float, web_thickness: float) -> List[List[Tuple[float, float]]]:
    num_bays = 6
    bay_w = span_length / num_bays
    margin_y = web_thickness
    h_inner = height - 2 * margin_y
    triangles = []
    
    for i in range(num_bays):
        x_left = i * bay_w + web_thickness / 2.0
        x_right = (i + 1) * bay_w - web_thickness / 2.0
        x_mid = (x_left + x_right) / 2.0
        
        if i % 2 == 0:
            # Upright triangle
            triangles.append([
                (x_left, margin_y),
                (x_right, margin_y),
                (x_mid, margin_y + h_inner)
            ])
        else:
            # Inverted triangle
            triangles.append([
                (x_left, margin_y + h_inner),
                (x_right, margin_y + h_inner),
                (x_mid, margin_y)
            ])
    return triangles

def calculate_diamond_lattice_segments(width: float, height: float, pitch: float, strut_w: float) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    segments = []
    # Generate +45 degree lines: y - x = c
    c_min = -width
    c_max = height
    c = c_min
    while c <= c_max:
        # Line: y = x + c
        # Intersect with [0, width] x [0, height]
        pts = []
        # x = 0 -> y = c
        if 0 <= c <= height:
            pts.append((0.0, c))
        # x = width -> y = width + c
        if 0 <= width + c <= height:
            pts.append((width, width + c))
        # y = 0 -> x = -c
        if 0 <= -c <= width and ( -c != 0 or c != 0 ):
            pts.append((-c, 0.0))
        # y = height -> x = height - c
        if 0 <= height - c <= width and ( height - c != width or width + c != height ):
            pts.append((height - c, height))
            
        unique_pts = list(set([(round(p[0], 4), round(p[1], 4)) for p in pts]))
        if len(unique_pts) == 2:
            segments.append((unique_pts[0], unique_pts[1]))
        c += pitch * math.sqrt(2)

    # Generate -45 degree lines: y + x = d
    d_min = 0.0
    d_max = width + height
    d = d_min
    while d <= d_max:
        # Line: y = -x + d
        pts = []
        if 0 <= d <= height:
            pts.append((0.0, d))
        if 0 <= d - width <= height:
            pts.append((width, d - width))
        if 0 <= d <= width:
            pts.append((d, 0.0))
        if 0 <= d - height <= width:
            pts.append((d - height, height))
            
        unique_pts = list(set([(round(p[0], 4), round(p[1], 4)) for p in pts]))
        if len(unique_pts) == 2:
            segments.append((unique_pts[0], unique_pts[1]))
        d += pitch * math.sqrt(2)

    return segments
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_geometry_calc.py -v`  
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add fusion_scripts/geometry_calc.py tests/test_geometry_calc.py
git commit -m "feat(cad): add parametric geometry and coordinate engine for Model X frunk dividers"
```

---

### Task 2: Fusion 360 Automation API Script

**Files:**
- Create: `fusion_scripts/generate_modelx_frunk_dividers.py`
- Modify: `fusion_scripts/__init__.py`
- Test: `tests/test_fusion_script_syntax.py`

**Interfaces:**
- Produces:
  - Fusion 360 script entry point `run(context)` executable within Autodesk Fusion 360.
  - Registers User Parameters in active design document.
  - Builds components:
    1. `FT_Segment_12in` (Floor truss with interlocking dovetails and rib socket)
    2. `VR_Post_Deep` (Vertical rib post with 6.4mm slots and bottom tenon)
    3. `HR_Rail_12in` (Horizontal top rail with dovetails and top lead-in funnel)
    4. `J_Corner_90`, `J_Tee_3Way`, `J_Cross_4Way` (Modular junction blocks)
    5. `DIV_Crosshatch_12x11` (Slide-in divider panel with 45° diamond mesh and pull handle)
    6. `Pin_Lock_M5` (Tapered locking pin)
  - Creates 2×2 Demo Assembly layout.

- [ ] **Step 1: Write the test for Fusion 360 script syntax and structure**

```python
# tests/test_fusion_script_syntax.py
import ast
import os
import pytest

def test_script_syntax_and_ast():
    script_path = os.path.join("fusion_scripts", "generate_modelx_frunk_dividers.py")
    assert os.path.exists(script_path)
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Must parse without syntax errors
    tree = ast.parse(code)
    
    # Verify required functions exist
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert "run" in func_names
    assert "create_user_parameters" in func_names
    assert "build_floor_truss_component" in func_names
    assert "build_vertical_rib_component" in func_names
    assert "build_horizontal_rail_component" in func_names
    assert "build_divider_panel_component" in func_names
    assert "build_locking_pin_component" in func_names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fusion_script_syntax.py -v`  
Expected: FAIL with file not found.

- [ ] **Step 3: Implement `fusion_scripts/generate_modelx_frunk_dividers.py`**

Write the complete Fusion 360 Python script implementing full geometry creation, sketches, sweeps/extrusions, user parameters, and component organization with robust error handling and fallback mock support.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fusion_script_syntax.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add fusion_scripts/generate_modelx_frunk_dividers.py tests/test_fusion_script_syntax.py
git commit -m "feat(fusion360): implement complete automated CAD generation script for Model X frunk system"
```

---

### Task 3: Comprehensive CAD Modeling Guide & Parameter Reference

**Files:**
- Create: `docs/cad_modeling_guide.md`
- Test: Validate markdown link structure and parameter accuracy

**Interfaces:**
- Produces documentation covering:
  - Step-by-step installation into Autodesk Fusion 360 (`Scripts and Add-Ins` folder location on Windows/Mac).
  - Executing the script and managing User Parameters (`fx`).
  - Assembling custom frunk configurations (1x1, 2x1, 2x2, 2x3 grids).
  - Exporting components as STEP and high-resolution STL/3MF files for Creality K2.

- [ ] **Step 1: Write `docs/cad_modeling_guide.md`**

Write detailed documentation with screenshots/code blocks, parameters table, troubleshooting, and STEP/3MF export checklist.

- [ ] **Step 2: Commit**

```bash
git add docs/cad_modeling_guide.md
git commit -m "docs(cad): add comprehensive Fusion 360 user and parametric reference guide"
```

---

### Task 4: Creality K2 3D Printing, Infill & Slicing Guide

**Files:**
- Create: `docs/3d_printing_and_slicing_guide.md`
- Test: Validate print parameters and thermal profiles

**Interfaces:**
- Produces guide covering:
  - Material selection for Tesla frunk (ASA vs ABS vs PETG thermal resistance data).
  - Creality K2 Combo print profile settings (nozzle temp, bed temp, chamber/cooling).
  - Slicer infill configuration: **30% Hexagonal or Gyroid** for structural frames (Trusses, Ribs, Rails) and **100% infill** on lattice struts.
  - Bed orientation and zero-support placement strategies.
  - Post-processing, tolerance fitting, and vehicle installation.

- [ ] **Step 1: Write `docs/3d_printing_and_slicing_guide.md`**

Write complete slicing profile specification for Creality Print and OrcaSlicer.

- [ ] **Step 2: Commit**

```bash
git add docs/3d_printing_and_slicing_guide.md
git commit -m "docs(3dprint): add Creality K2 slicing and ASA/ABS/PETG printing guide"
```

---

### Task 5: Repository README, Bill of Materials & Assembly Architecture

**Files:**
- Create: `README.md`
- Test: Verify links and repository completeness

**Interfaces:**
- Produces root documentation with:
  - Project Overview & Visual ASCII/Mermaid Architecture Diagrams.
  - Bill of Materials (BOM) for 2×2 and 2×3 standard Model X frunk layouts.
  - Quick Start guide.
  - License and contribution notes.

- [ ] **Step 1: Write `README.md`**

Write clear, comprehensive repository README.

- [ ] **Step 2: Run all test suites**

Run: `pytest tests/ -v`  
Expected: All tests pass.

- [ ] **Step 3: Commit and Push**

```bash
git add README.md
git commit -m "docs: add project README, Bill of Materials, and assembly architecture"
```
