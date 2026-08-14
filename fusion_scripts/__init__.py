"""
Tesla Model X 2017 Frunk Modular Divider System
Parametric CAD automation scripts for Autodesk Fusion 360.
"""

from .geometry_calc import (
    FrunkParameters,
    calculate_dovetail_profile,
    calculate_truss_web_triangles,
    calculate_diamond_lattice_segments,
)
from .generate_modelx_frunk_dividers import (
    run,
    create_user_parameters,
    build_floor_truss_component,
    build_vertical_rib_component,
    build_horizontal_rail_component,
    build_junction_components,
    build_divider_panel_component,
    build_locking_pin_component,
)

__all__ = [
    "FrunkParameters",
    "calculate_dovetail_profile",
    "calculate_truss_web_triangles",
    "calculate_diamond_lattice_segments",
    "run",
    "create_user_parameters",
    "build_floor_truss_component",
    "build_vertical_rib_component",
    "build_horizontal_rail_component",
    "build_junction_components",
    "build_divider_panel_component",
    "build_locking_pin_component",
]

