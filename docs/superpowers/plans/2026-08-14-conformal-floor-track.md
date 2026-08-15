# Conformal Floor Track (LiDAR Matched) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Design and automate the CAD generation of a continuous perimeter floor track that matches the bottom of the 2017 Tesla Model X frunk tub with 0.5" (12.7 mm) clearance, sliced into 4 printable interlocking segments with captive sliding top rails.

**Architecture:** A pure Python geometry engine extracts the calibrated LiDAR floor boundary, offsets it inward by 12.7 mm, constructs the 30mm x 18mm captive T-track profile, slices it into 4 quadrants under 310 mm, and integrates with Autodesk Fusion 360 API to generate printable solid bodies with 15° interlocking joints.

**Tech Stack:** Python 3.14, Trimesh, NumPy, Autodesk Fusion 360 Python API (`adsk.core`, `adsk.fusion`), Pytest.

## Global Constraints
- Target Vehicle: 2017 Tesla Model X 100D (AWD tub scan: `docs/scans/frunk_scan_calibrated.stl`)
- Perimeter Clearance: 0.50 in (12.7 mm) inward offset from tub boundary at $Z = 10\text{ mm}$
- Track Profile: 30 mm width x 18 mm height with top captive sliding rail ($14\text{ mm}$ base, $8\text{ mm}$ neck, $5\text{ mm}$ height)
- Bed Envelope: All sliced segments must measure under $310\text{ mm}$ in maximum dimension to print flat on Creality K2 ($350\text{ mm}$ bed)
- Interlocking Seams: $15^\circ$ tapered dovetail joints with $0.20\text{ mm}$ 3D printing slip clearance

---

### Task 1: LiDAR Floor Contour Extraction & Inset Math

**Files:**
- Create: `fusion_scripts/conformal_track_calc.py`
- Test: `tests/test_conformal_track_calc.py`

**Interfaces:**
- Produces:
  `extract_calibrated_floor_polygon(stl_path: str, z_height: float, offset_mm: float) -> List[Tuple[float, float]]`
  `generate_track_quadrant_polygons(perimeter_pts: List[Tuple[float, float]], track_width_mm: float) -> Dict[str, Dict[str, Any]]`

- [ ] **Step 1: Write failing unit test for floor polygon extraction and 0.5" inset**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement extraction and offset algorithms in `conformal_track_calc.py`**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit changes**

---

### Task 2: Quadrant Slicing & 15° Interlocking Seam Geometry Engine

**Files:**
- Modify: `fusion_scripts/conformal_track_calc.py`
- Test: `tests/test_conformal_track_calc.py`

**Interfaces:**
- Produces:
  `slice_track_quadrants(outer_poly, inner_poly) -> Dict[str, QuadrantGeometry]`
  `calculate_seam_dovetail_joint(seam_center, seam_normal, male: bool, tol: float = 0.20) -> List[Tuple[float, float]]`

- [ ] **Step 1: Write failing unit test for quadrant slicing and seam joints**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement slicing logic and male/female dovetail seam features**
- [ ] **Step 4: Run test to verify all 4 quadrants measure under 310 mm and joints mate with 0.20 mm tolerance**
- [ ] **Step 5: Commit changes**

---

### Task 3: Fusion 360 Automated Solid Generation & Script Deployment

**Files:**
- Modify: `fusion_scripts/ModelX_Frunk_Dividers_Standalone.py`
- Modify: `fusion_scripts/ModelX_Frunk_Dividers/ModelX_Frunk_Dividers.py`
- Test: `tests/test_conformal_floor_generation.py`

**Interfaces:**
- Produces:
  `build_conformal_floor_track(comp, params, scan_mesh_path)`
  4 distinct named bodies: `TRK_Front_L`, `TRK_Front_R`, `TRK_Rear_L`, `TRK_Rear_R` + `TRK_Master_Assembled`

- [ ] **Step 1: Write unit test validating headless generation of 4 quadrant bodies**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement 3D track extrusion, captive top rail, and interlocking seam features**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Deploy script to `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\ModelX_Frunk_Dividers\`**
- [ ] **Step 6: Commit changes**

---

### Task 4: Documentation, Assembly & Slicing Matrix

**Files:**
- Modify: `README.md`
- Modify: `docs/cad_modeling_guide.md`
- Modify: `docs/3d_printing_and_slicing_guide.md`

- [ ] **Step 1: Update README with conformal floor track architecture and assembly diagrams**
- [ ] **Step 2: Document Creality K2 slicing parameters for ASA/PETG track quadrants**
- [ ] **Step 3: Run full test suite (`pytest`) to ensure 100% repo integrity**
- [ ] **Step 4: Commit and push to GitHub**
