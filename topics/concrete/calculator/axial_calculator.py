from dataclasses import dataclass
from ..config.constants import GAMMA_C_TS500, GAMMA_S_TS500, ALPHA_CC
from ..formulas.axial_formulas import (
    fcd, fyd, unconfined_components,
    core_area, spiral_area, rho_s, rho_min_req,
    f_ccd, confined_capacity
)

@dataclass
class AxialResults:
    gamma_c: float
    gamma_s: float
    fcd: float
    fyd: float
    Fc: float
    Fs: float
    Nor1: float
    # spiral
    Ack: float | None = None
    Asp: float | None = None
    rho_s: float | None = None
    rho_min_req: float | None = None
    rho_min_calc: float | None = None
    rho_min_abs: float | None = None
    f_ccd: float | None = None
    Nor2: float | None = None
    spiral_ok: bool | None = None

def compute_axial(fc, fy, fywk, Ag, Ast, reinf_style, core_diameter_input, spiral_dia, spiral_spacing, use_design_values=True):
    gamma_c, gamma_s = GAMMA_C_TS500, GAMMA_S_TS500
    fcd_val = fcd(fc, gamma_c)
    fyd_val = fyd(fy, gamma_s)

    Fc, Fs, Nor1 = unconfined_components(ALPHA_CC, fcd_val, Ag, Ast, fyd_val)

    res = AxialResults(
        gamma_c=gamma_c, gamma_s=gamma_s,
        fcd=fcd_val, fyd=fyd_val,
        Fc=Fc, Fs=Fs, Nor1=Nor1
    )

    if "Spiral" in reinf_style:
        d_outer = core_diameter_input
        d_center = d_outer - spiral_dia

        Ack = core_area(d_outer)
        Asp = spiral_area(spiral_dia)

        res.Ack = Ack
        res.Asp = Asp

        # Only stop if geometry is invalid
        if spiral_spacing <= 0 or d_center <= 0 or Ack <= 0:
            res.spiral_ok = False
            res.Nor2 = None
            return res

        # Compute confinement ratio + requirement
        rs = rho_s(Asp, d_center, spiral_spacing)
        req, calc_req, abs_req = rho_min_req(fc, fy, Ag, Ack)

        res.rho_s = rs
        res.rho_min_req = req
        res.rho_min_calc = calc_req
        res.rho_min_abs = abs_req

        # IMPORTANT: always compute Nor2 if spiral geometry is valid
        res.spiral_ok = (rs >= req)

        fccd = f_ccd(ALPHA_CC, fc, gamma_c, rs, fy)
        res.f_ccd = fccd
        res.Nor2 = confined_capacity(fccd, Ack, Ast, fyd_val)

    return res