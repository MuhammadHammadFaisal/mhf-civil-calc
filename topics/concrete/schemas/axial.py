from dataclasses import dataclass

@dataclass
class AxialInputs:
    section_type: str
    width: float
    height: float
    cover: float
    bar_diameter: float
    num_bars: int
    fck: float
    fyk: float
    confinement: str

@dataclass
class AxialResults:
    N1: float
    N2: float
    transition: str
