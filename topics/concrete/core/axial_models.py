import math
from topics.concrete.schemas.axial import AxialResults

def compute_axial_capacity(inputs):

    Ag = inputs.width * inputs.height
    As = inputs.num_bars * (math.pi * inputs.bar_diameter**2 / 4)

    fcd = inputs.fck / 1.5
    fyd = inputs.fyk / 1.15

    N1 = fcd * (Ag - As) + fyd * As

    if inputs.confinement == "Spiral":
        N2 = 1.15 * N1
        transition = "Ductile (Spiral)"
    else:
        N2 = 1.05 * N1
        transition = "Brittle (Tied)"

    return AxialResults(N1=N1/1000, N2=N2/1000, transition=transition)
