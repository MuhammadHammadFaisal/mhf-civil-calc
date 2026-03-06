import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# ==========================================================
# RECTANGULAR BAR DISTRIBUTION
# ==========================================================
def distribute_bars_rectangular(b, h, cover, num_bars):
    """
    Distribute bars along the perimeter of a rectangular section.

    Parameters
    ----------
    b, h : float
        Section width and depth (mm).
    cover : float
        Effective inset from the concrete face to bar centerline (mm).
        (This is NOT necessarily 'clear cover'; it's the bar placement inset.)
    num_bars : int
        Total number of longitudinal bars.

    Returns
    -------
    list[(x, y)]
        Bar center positions in mm.
    """
    eff_cover = cover

    xL, xR = eff_cover, b - eff_cover
    yB, yT = eff_cover, h - eff_cover

    # Start with 4 corners
    positions = [(xL, yB), (xR, yB), (xR, yT), (xL, yT)]

    remaining = num_bars - 4
    if remaining <= 0:
        return positions[:num_bars]

    # Prefer longer faces first
    if h >= b:
        faces = [
            ("left", xL, yB, yT),
            ("right", xR, yB, yT),
            ("bottom", yB, xL, xR),
            ("top", yT, xL, xR),
        ]
    else:
        faces = [
            ("bottom", yB, xL, xR),
            ("top", yT, xL, xR),
            ("left", xL, yB, yT),
            ("right", xR, yB, yT),
        ]

    # Distribute remaining bars around faces cyclically
    face_counts = [0] * 4
    for i in range(remaining):
        face_counts[i % 4] += 1

    for i, count in enumerate(face_counts):
        if count == 0:
            continue

        face_name, fixed, start, end = faces[i]
        spacing = (end - start) / (count + 1)

        internal_points = [start + spacing * (j + 1) for j in range(count)]

        for p in internal_points:
            if face_name in ["left", "right"]:
                positions.append((fixed, p))
            else:
                positions.append((p, fixed))

    return positions


# ==========================================================
# MAIN DRAW FUNCTION
# ==========================================================
def draw_cross_section(
    shape,
    dims,
    num_bars,
    bar_dia,
    reinf_style,
    show_ties,
    cover,
    core_diameter=0.0,  # SAFE DEFAULT
):
    """
    Draw a reinforced concrete cross-section with longitudinal bars and (optionally) ties/spiral.

    Notes
    -----
    - If you do NOT want to ask the user for cover, you can pass cover=0 from UI.
      This function will then use a safe visualization default cover internally.
    - For spiral, `core_diameter` (Dk) takes priority when > 0.
    - Units assumed: mm.
    """

    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)

    # Safety check (avoid crashes / weird math)
    if num_bars <= 0 or bar_dia <= 0:
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        ax.set_aspect("equal")
        ax.axis("off")
        return fig

    bar_r = bar_dia / 2

    # Transparent background (matches your theme)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # If user doesn't provide cover, use a safe visualization cover
    VIS_COVER_DEFAULT = 25.0  # mm (visual-only default)
    cover_eff = cover if (cover is not None and cover > 0) else VIS_COVER_DEFAULT

    # ======================================================
    # DRAW CONCRETE SHAPE
    # ======================================================
    if shape in ["Rectangular", "Square"]:
        b, h = dims
        cx, cy = b / 2, h / 2

        ax.add_patch(
            patches.Rectangle(
                (0, 0),
                b,
                h,
                fill=True,
                facecolor="#e0e0e0",
                edgecolor="black",
                linewidth=2,
            )
        )

        ax.set_xlim(-50, b + 50)
        ax.set_ylim(-50, h + 50)

    else:  # Circular
        D = dims[0]
        cx, cy = D / 2, D / 2

        ax.add_patch(
            patches.Circle(
                (cx, cy),
                D / 2,
                fill=True,
                facecolor="#e0e0e0",
                edgecolor="black",
                linewidth=2,
            )
        )

        ax.set_xlim(-50, D + 50)
        ax.set_ylim(-50, D + 50)

    # ======================================================
    # TIE LOGIC
    # ======================================================
    draw_ties_logic = (
        show_ties and
        ("Standard" in reinf_style or "Spiral" in reinf_style)
    )

    if "None" in reinf_style:
        ax.set_aspect("equal")
        ax.axis("off")
        return fig

    positions = []

    # ======================================================
    # SPIRAL ARRANGEMENT
    # ======================================================
    if "Spiral" in reinf_style:

        # Use manual core diameter if provided
        if core_diameter and core_diameter > 0:
            cage_D = float(core_diameter)
        else:
            # Fallback based on effective cover
            if shape == "Circular":
                cage_D = dims[0] - 2 * cover_eff
            else:
                cage_D = min(dims[0], dims[1]) - 2 * cover_eff

        # Prevent invalid geometry (tiny section / big bars / cover=0)
        cage_D = max(cage_D, 2 * bar_r + 10)

        r_bars = cage_D / 2 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0, 2 * np.pi, int(num_bars), endpoint=False)

        positions = [
            (cx + r_bars * np.cos(a),
             cy + r_bars * np.sin(a))
            for a in angles
        ]

        if draw_ties_logic:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    cage_D / 2,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.5,
                    linestyle="-",
                )
            )

    # ======================================================
    # CIRCULAR (NON-SPIRAL)
    # ======================================================
    elif shape == "Circular":
        cage_D = dims[0] - 2 * cover_eff

        # Prevent invalid geometry
        cage_D = max(cage_D, 2 * bar_r + 10)

        r_bars = cage_D / 2 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0, 2 * np.pi, int(num_bars), endpoint=False)

        positions = [
            (cx + r_bars * np.cos(a),
             cy + r_bars * np.sin(a))
            for a in angles
        ]

        # For circular ties (optional): draw hoop line if requested
        if draw_ties_logic:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    cage_D / 2,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.5,
                    linestyle="--",
                )
            )

    # ======================================================
    # RECTANGULAR ARRANGEMENT
    # ======================================================
    else:
        # Place bar centers inset by (cover_eff + bar_r)
        positions = distribute_bars_rectangular(
            dims[0],
            dims[1],
            cover_eff + bar_r,
            int(num_bars),
        )

        if draw_ties_logic:
            tie_inset = cover_eff
            w_tie = dims[0] - 2 * tie_inset
            h_tie = dims[1] - 2 * tie_inset

            # Prevent invalid tie rectangle
            w_tie = max(w_tie, 10.0)
            h_tie = max(h_tie, 10.0)

            ax.add_patch(
                patches.Rectangle(
                    (tie_inset, tie_inset),
                    w_tie,
                    h_tie,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.5,
                    linestyle="--",
                )
            )

    # ======================================================
    # DRAW BARS
    # ======================================================
    for x, y in positions:
        ax.add_patch(
            patches.Circle(
                (x, y),
                bar_r,
                color="#d32f2f",
                zorder=10,
            )
        )

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.2)

    return fig