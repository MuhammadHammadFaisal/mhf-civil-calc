import numpy as np

def fcd(fc, gamma_c):
    return fc / gamma_c

def fyd(fy, gamma_s):
    return fy / gamma_s

def area_gross_rect(b, h):
    return b * h

def area_gross_square(a):
    return a * a

def area_gross_circ(D):
    return np.pi * D**2 / 4

def area_steel(num_bars, bar_dia):
    return num_bars * np.pi * (bar_dia / 2) ** 2

def unconfined_components(alpha_cc, fcd_val, Ag, Ast, fyd_val):
    Fc = alpha_cc * fcd_val * (Ag - Ast)
    Fs = Ast * fyd_val
    Nor = Fc + Fs
    return Fc, Fs, Nor

def core_area(Dk):
    return np.pi * Dk**2 / 4

def spiral_area(phi_sp):
    return np.pi * phi_sp**2 / 4

def rho_s(Asp, D_center, s):
    return (4 * Asp) / (D_center * s)

def rho_min_req(fc, fy, Ag, Ack):
    rho_min_calc = 0.45 * (fc / fy) * ((Ag / Ack) - 1)
    rho_min_abs = 0.12 * (fc / fy)
    return max(rho_min_calc, rho_min_abs), rho_min_calc, rho_min_abs

def f_ccd(alpha_cc, fc, gamma_c, rho_s_val, fy):
    fcd_val = (alpha_cc * fc) / gamma_c
    confinement_stress = (2 * rho_s_val * fy) / gamma_c
    return fcd_val + confinement_stress

def confined_capacity(f_ccd_val, Ack, Ast, fyd_val):
    return (f_ccd_val * Ack) + (Ast * fyd_val)
