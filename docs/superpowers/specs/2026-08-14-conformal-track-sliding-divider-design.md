# Tesla Model X 2017 Frunk: Conformal Track & Sliding Modular Divider System
## Technical Design Specification

- **Vehicle**: 2017 Tesla Model X 100D (AWD Front Trunk Tub)
- **Reference Geometry**: High-resolution LiDAR 3D Scan (`docs/scans/frunk_scan_calibrated.stl`)
- **3D Printer**: Creality K2 Combo (`350 x 350 x 350 mm` build volume)
- **Target Clearance**: 0.50 in (12.7 mm) perimeter offset from scanned tub wall

---

## 1. System Overview & Architecture

This system replaces static pre-set grids with a **continuous conformal perimeter floor track** and **infinitely repositionable sliding upright posts** that support **drop-in 6" interlocking cross-member slats**.

```
       [ Cross Member Slat 6" ] ───► [ Cross Member Slat 6" ] ───► [ Slat End Shoe ]
                      │                                                   │
                      │ (Interlock together to span any width)            │ (Slides down)
                      ▼                                                   ▼
       ┌────────────────────────┐                             ┌───────────────────────┐
       │   Post A (Sliding)     │                             │   Post B (Sliding)    │
       │   [Vertical C-Channel] │◄───────────────────────────►│   [Vertical C-Channel]│
       └───────────┬────────────┘     Adjustable Bay Space    └───────────┬───────────┘
                   │                                                      │
                   ▼ (Friction-fit sliding carriage shoe)                 ▼
     ═══════════════════════════════════════════════════════════════════════════════════
       CONFORMAL FLOOR TRACK (0.5" offset from Model X 2017 LiDAR Tub Perimeter)
     ═══════════════════════════════════════════════════════════════════════════════════
```

---

## 2. Component Specifications

### 2.1 Conformal Perimeter Floor Track (`TRK_Conformal_Floor`)
* **Geometry**: Derived directly from the calibrated LiDAR scan cross-section at $Z = 10\text{ mm}$, offset inward by exactly **$12.7\text{ mm}$ ($0.50\text{ in}$)**.
* **Track Profile**: $30\text{ mm}$ wide $\times 18\text{ mm}$ tall with a captive top T-rail / dovetail track ($14\text{ mm}$ base, $8\text{ mm}$ neck).
* **Modular Bed Partitioning**: The perimeter is split into 4 modular interlocking arc segments (`TRK_Front_L`, `TRK_Front_R`, `TRK_Rear_L`, `TRK_Rear_R`) under $310\text{ mm}$ each, connecting via rigid alignment dovetails to assemble seamlessly on the frunk carpet.
* **Non-Slip Base**: Flat bottom surface ready for optional rubber TPU pads or grip tape.

### 2.2 Paired Sliding Upright Posts (`PST_Slide_Upright`)
* **Height**: $260\text{ mm}$ ($10.2\text{ in}$) tall.
* **Base Shoe**: Captive T-slot carriage shoe that wraps around the floor track rail with a calibrated **$0.20\text{ mm}$ friction-fit slip clearance**. Slides easily by hand with firm friction to stay in place without tools or screws.
* **Vertical Guide Slot**: $6.4\text{ mm}$ wide $\times 8.0\text{ mm}$ deep C-channel facing inward across the frunk, allowing cross-member slats to slide down smoothly.
* **Lead-in Top Chamfer**: $45^\circ$ flared entry on top of the post for effortless drop-in insertion.

### 2.3 Modular 6" Interlocking Cross Members (`SLAT_Segment_6in` & `SLAT_EndCap`)
* **Unit Length**: $152.4\text{ mm}$ ($6.00\text{ in}$) per segment.
* **Segment Height**: $60.0\text{ mm}$ ($2.36\text{ in}$) per slat layer.
* **Thickness**: $5.0\text{ mm}$ nominal strut rib.
* **Interlocking Joint**: $15^\circ$ tapered sliding wedge dovetail on segment ends ($0.20\text{ mm}$ slip clearance).
* **Span Scalability**: 
  * 1 Segment = $6.0\text{ in}$ ($152.4\text{ mm}$)
  * 2 Segments = $12.0\text{ in}$ ($304.8\text{ mm}$)
  * 3 Segments = $18.0\text{ in}$ ($457.2\text{ mm}$)
  * 4 Segments = $24.0\text{ in}$ ($609.6\text{ mm}$)
  * 5 Segments = $30.0\text{ in}$ ($762.0\text{ mm}$)
  * 6 Segments = $36.0\text{ in}$ ($914.4\text{ mm}$)
* **Vertical Stacking**: Cross-member slats feature a tongue-and-groove lip along their top/bottom edges, allowing 1, 2, 3, or 4 slats to stack vertically to create half-height or full-height divider walls.

---

## 3. Manufacturing & Slicing Matrix (Creality K2 Combo)

| Component | Dimensions (mm) | Print Orientation | Infill Profile | Walls | Print Time (K2) |
|---|---|---|---|---|---|
| `TRK_Front_L` | $295 \times 180 \times 18$ | Flat on bed | 30% Gyroid / ASA | 4 perims | ~1.8 hrs |
| `TRK_Front_R` | $295 \times 180 \times 18$ | Flat on bed | 30% Gyroid / ASA | 4 perims | ~1.8 hrs |
| `TRK_Rear_L` | $305 \times 190 \times 18$ | Flat on bed | 30% Gyroid / ASA | 4 perims | ~2.0 hrs |
| `TRK_Rear_R` | $305 \times 190 \times 18$ | Flat on bed | 30% Gyroid / ASA | 4 perims | ~2.0 hrs |
| `PST_Slide_Upright` | $260 \times 36 \times 32$ | Standing vertical | 40% Gyroid / ASA | 5 perims | ~1.5 hrs / pair |
| `SLAT_Segment_6in` | $152.4 \times 60 \times 5$ | Flat on bed | 30% Hex / ASA | 4 perims | ~45 min / slat |
| `SLAT_EndCap` | $35 \times 60 \times 5$ | Flat on bed | 30% Hex / ASA | 4 perims | ~20 min / pair |

---

## 4. Verification & Testing Criteria

1. **Scan Conformance**: Floor track centerline matches the LiDAR scan contour at $Z=10\text{ mm}$ with $12.7\text{ mm} \pm 1.0\text{ mm}$ offset.
2. **Bed Fit**: Every single piece measures under $310\text{ mm}$ in maximum dimension to print flat on the Creality K2 ($350\text{ mm}$ bed).
3. **Friction Sliding**: Post shoe slides along the continuous track under hand force ($10\text{–}25\text{ N}$) and resists horizontal shifting under road acceleration ($>1.2\text{G}$).
4. **Modularity**: 6" slats interlock solidly and drop smoothly into the post C-channels.
