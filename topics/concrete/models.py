from dataclasses import dataclass

@dataclass
class ColumnInput:
    shape: str
    dims: tuple
    cover: float
    bar_dia: float
    num_bars: int
    spiral_dia: float
    spiral_spacing: float
    core_diameter: float
    fc: float
    fy: float
    confinement_type: str

@dataclass
class CapacityResult:
    Nor1: float
    Nor2: float
    rho_percent: float
    rho_s: float
    rho_min_req: float
    fcd: float
    fyd: float
    fccd: float
