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

__all__ = [
    "FrunkParameters",
    "calculate_dovetail_profile",
    "calculate_truss_web_triangles",
    "calculate_diamond_lattice_segments",
]
