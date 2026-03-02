def design_strengths(fc, fy):
    gamma_c = 1.5
    gamma_s = 1.15
    fcd = fc / gamma_c
    fyd = fy / gamma_s
    return fcd, fyd
