import numpy as np
from types import SimpleNamespace


def compute_axial(fc, fy_long, fywk, Ag, Ast, reinf_style,
                  core_diameter_input, spiral_dia, spiral_spacing,
                  strength_basis):

    gamma_c = 1.5
    gamma_s = 1.15
    ALPHA_CC = 0.85

    if "Design" in strength_basis:
        fcd = fc / gamma_c
        fyd = fy_long / gamma_s
    else:
        fcd = fc
        fyd = fy_long

    Fc = ALPHA_CC * fcd * Ag 
    Fs = Ast * fyd
    Nor1 = Fc + Fs

    Nor2 = None
    rho_s_val = None
    rho_min_req = None
    spiral_ok = False

    if "Spiral" in reinf_style and spiral_spacing > 0:

        d_outer = core_diameter_input
        d_center = d_outer - spiral_dia

        Ack = np.pi * d_outer**2 / 4
        Asp = np.pi * spiral_dia**2 / 4

        rho_s_val = (4 * Asp) / (d_center * spiral_spacing)

        rho_min_calc = 0.45 * (fc / fywk) * ((Ag / Ack) - 1)
        rho_min_abs = 0.12 * (fc / fywk)
        rho_min_req = max(rho_min_calc, rho_min_abs)

        confinement_boost = (2 * rho_s_val * fywk) / 1.5
        fccd = fcd + confinement_boost

        Nor2 = fccd * Ack + Ast * fyd

        spiral_ok = rho_s_val >= rho_min_req

    return SimpleNamespace(
        gamma_c=gamma_c,
        gamma_s=gamma_s,
        fcd=fcd,
        fyd=fyd,
        Fc=Fc,
        Fs=Fs,
        Nor1=Nor1,
        Nor2=Nor2,
        rho_s=rho_s_val,
        rho_min_req=rho_min_req,
        spiral_ok=spiral_ok
    )
