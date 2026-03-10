from __future__ import annotations
from typing import List, Tuple


def _section_limit(shape: str, dims: Tuple[float, ...]) -> float:
    if shape == "Circular":
        return dims[0]
    return min(dims[0], dims[1])


def validate_axial_capacity_inputs(
    *,
    shape: str,
    dims: Tuple[float, ...],
    reinf_style: str,
    fc: float,
    fy_long: float,
    fywk: float,
    Ag: float,
    Ast: float,
    bar_dia: float,
    num_bars: int,
    spiral_dia: float,
    spiral_spacing: float,
    core_diameter_input: float,
):
    errors: List[str] = []
    warnings: List[str] = []

    # -------------------------------------------------
    # Basic geometry
    # -------------------------------------------------
    if shape == "Rectangular":
        b, h = dims
        if b <= 0:
            errors.append("Width b must be greater than 0 mm.")
        if h <= 0:
            errors.append("Depth h must be greater than 0 mm.")
    elif shape == "Circular":
        D = dims[0]
        if D <= 0:
            errors.append("Column diameter D must be greater than 0 mm.")

    if Ag <= 0:
        errors.append("Gross section area Ag must be greater than 0.")

    # -------------------------------------------------
    # Materials
    # -------------------------------------------------
    if fc <= 0:
        errors.append("Concrete strength fck must be greater than 0 MPa.")

    if "Plain Concrete" not in reinf_style:
        if fy_long <= 0:
            errors.append("Longitudinal steel strength fyk must be greater than 0 MPa.")
        if bar_dia <= 0:
            errors.append("Longitudinal bar diameter must be greater than 0 mm.")
        if num_bars < 4:
            errors.append("Number of longitudinal bars must be at least 4.")

    # -------------------------------------------------
    # Longitudinal steel
    # -------------------------------------------------
    if Ast < 0:
        errors.append("Longitudinal steel area Ast cannot be negative.")

    if Ast >= Ag:
        errors.append("Longitudinal steel area Ast cannot be equal to or exceed gross section area Ag.")

    if Ag > 0:
        rho_long = Ast / Ag
        if "Plain Concrete" not in reinf_style:
            if rho_long < 0.005:
                warnings.append("Longitudinal steel ratio looks very low.")
            if rho_long > 0.08:
                warnings.append("Longitudinal steel ratio looks very high.")

    # -------------------------------------------------
    # Spiral checks
    # -------------------------------------------------
    if "Spiral" in reinf_style:
        if fywk <= 0:
            errors.append("Spiral steel strength fywk must be greater than 0 MPa.")

        if spiral_dia <= 0:
            errors.append("Spiral bar diameter must be greater than 0 mm.")

        if spiral_spacing <= 0:
            errors.append("Spiral spacing s must be greater than 0 mm.")
        elif spiral_spacing < 20:
            warnings.append("Spiral spacing is very small and may be impractical.")
        elif spiral_spacing > 150:
            warnings.append("Spiral spacing is quite large; check confinement detailing.")

        if core_diameter_input <= 0:
            errors.append("Core diameter Dk must be greater than 0 mm.")

        max_core = _section_limit(shape, dims)
        if core_diameter_input > max_core:
            errors.append(
                f"Core diameter Dk ({core_diameter_input:.1f} mm) cannot exceed section limit ({max_core:.1f} mm)."
            )

        if spiral_dia > 0 and core_diameter_input <= spiral_dia:
            errors.append(
                "Core diameter Dk must be greater than spiral bar diameter so spiral centerline diameter stays positive."
            )

    return errors, warnings
