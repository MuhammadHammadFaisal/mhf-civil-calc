from topics.concrete.models import ColumnInput, CapacityResult
from topics.concrete.domain.materials import design_strengths
from topics.concrete.domain.geometry import (
    gross_area,
    steel_area,
    core_area,
    spiral_area,
)
from topics.concrete.domain.detailing import (
    reinforcement_ratio,
    spiral_min_ratio,
)
from topics.concrete.domain.confinement import (
    spiral_ratio,
    confined_strength,
    confined_capacity,
)


def compute_column_capacity(inputs: ColumnInput) -> CapacityResult:

    # --- GEOMETRY ---
    Ag = gross_area(inputs.shape, inputs.dims)
    Ast = steel_area(inputs.num_bars, inputs.bar_dia)

    # --- MATERIALS ---
    fcd, fyd = design_strengths(inputs.fc, inputs.fy)

    # --- UNCONFINED CAPACITY ---
    Force_conc = 0.85 * fcd * (Ag - Ast)
    Force_steel = Ast * fyd
    Nor1 = Force_conc + Force_steel

    # --- DETAILING ---
    rho_percent = reinforcement_ratio(Ast, Ag)

    # Default confined values
    Nor2 = 0
    rho_s = 0
    rho_min_req = 0
    fccd = 0

    # --- CONFINEMENT CHECK ---
    if inputs.confinement_type == "Spiral" and inputs.spiral_spacing > 0:

        Ack = core_area(inputs.core_diameter)
        Asp = spiral_area(inputs.spiral_dia)

        rho_s = spiral_ratio(
            Asp,
            inputs.core_diameter - inputs.spiral_dia,
            inputs.spiral_spacing,
        )

        rho_min_req = spiral_min_ratio(inputs.fc, inputs.fy, Ag, Ack)

        if rho_s >= rho_min_req:
            fccd = confined_strength(fcd, rho_s, inputs.fy)
            Nor2 = confined_capacity(fccd, Ack, Ast, fyd)

    return CapacityResult(
        Nor1=Nor1,
        Nor2=Nor2,
        rho_percent=rho_percent,
        rho_s=rho_s,
        rho_min_req=rho_min_req,
        fcd=fcd,
        fyd=fyd,
        fccd=fccd,
    )
