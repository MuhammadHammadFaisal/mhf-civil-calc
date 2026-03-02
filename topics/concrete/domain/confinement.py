def spiral_ratio(Asp, core_diameter_center, spacing):
    if spacing == 0:
        return 0
    return (4 * Asp) / (core_diameter_center * spacing)

def confined_strength(fcd, rho_s, fy):
    confinement_boost = (2 * rho_s * fy) / 1.5
    return fcd + confinement_boost

def confined_capacity(fccd, Ack, Ast, fyd):
    return (fccd * Ack) + (Ast * fyd)
