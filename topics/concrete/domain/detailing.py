def reinforcement_ratio(Ast, Ag):
    return (Ast / Ag) * 100

def spiral_min_ratio(fc, fy, Ag, Ack):
    rho_min_calc = 0.45 * (fc/fy) * ((Ag/Ack)-1)
    rho_min_abs = 0.12 * (fc/fy)
    return max(rho_min_calc, rho_min_abs)
