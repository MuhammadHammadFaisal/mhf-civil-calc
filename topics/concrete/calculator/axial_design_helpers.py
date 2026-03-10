import numpy as np
from types import SimpleNamespace

def required_Ast_for_load(Nu_N: float, Fc_N: float, fyd_MPa: float) -> float:
    """
    Solve: Nu = Fc + Ast*fyd  => Ast = (Nu - Fc)/fyd
    Units:
      Nu_N, Fc_N in N
      fyd_MPa in N/mm^2 (MPa)
      returns Ast in mm^2
    """
    if fyd_MPa <= 0:
        return 0.0
    return max(0.0, (Nu_N - Fc_N) / fyd_MPa)
