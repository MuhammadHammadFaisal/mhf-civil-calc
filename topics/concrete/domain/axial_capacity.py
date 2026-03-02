def unconfined_capacity(fcd, fyd, Ag, Ast):
    Force_conc = 0.85 * fcd * (Ag - Ast)
    Force_steel = Ast * fyd
    Nor1 = Force_conc + Force_steel
    return Nor1
