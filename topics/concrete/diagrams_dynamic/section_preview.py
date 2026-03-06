import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# ==========================================================
# RECTANGULAR BAR DISTRIBUTION (TIED RECTANGULAR)
# ==========================================================
def distribute_bars_rectangular(b, h, inset, num_bars):
    """
    Distribute bars around a rectangular perimeter with a given inset.
    inset = distance from concrete face to bar centerline.
    """
    xL, xR = inset, b - inset
    yB, yT = inset, h - inset

    positions = [(xL, yB), (xR, yB), (xR, yT), (xL, yT)]

    remaining = num_bars - 4
    if remaining <= 0:
        return positions[: max(0, num_bars)]

    # Prioritize longer faces first
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
# HELPERS (DIMENSIONS + LABEL BOX)
# ==========================================================
def _fmt_mm(x):
    try:
        return f"{float(x):.0f} mm"
    except Exception:
        return "—"


def _dim_arrow(ax, xy1, xy2, text, text_offset=(0, 0), lw=1.2):
    ax.annotate(
        "",
        xy=xy2,
        xytext=xy1,
        arrowprops=dict(arrowstyle="<->", linewidth=lw, color="#111"),
    )
    tx = (xy1[0] + xy2[0]) / 2 + text_offset[0]
    ty = (xy1[1] + xy2[1]) / 2 + text_offset[1]
    ax.text(tx, ty, text, ha="center", va="center", fontsize=10, color="#111")


def _info_box(ax, lines, x, y):
    text = "\n".join(lines)
    ax.text(
        x,
        y,
        text,
        ha="left",
        va="top",
        fontsize=10,
        color="#111",
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor="white",
            edgecolor="#777",
            alpha=0.95,
        ),
        zorder=100,
    )


# ==========================================================
# MAIN DRAW
# ==========================================================
def draw_cross_section(
    shape,
    dims,
    num_bars,
    bar_dia,
    reinf_style,
    show_ties,
    cover,
    core_diameter=0.0,
    # optional extras (if you want to pass them later)
    fc_label=None,              # e.g. "C20"
    fywk=None,                  # e.g. 220
    spiral_dia=None,            # e.g. 10
    spiral_spacing=None,        # e.g. 50
):
    """
    Sketch-style cross section:
    - Rectangular/circular concrete boundary
    - Bars
    - Spiral cage circle for spiral case (even inside rectangular like your sketch)
    - Dimension arrows: b/h or D and Dk (if spiral)
    - Labels: nØdia, As, Concrete, Spiral info
    """

    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=110)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # ---------- sanitize ----------
    reinf_style = str(reinf_style or "")
    shape = str(shape or "")

    # If user doesn't provide cover, use a visual default (so diagram never collapses)
    VIS_COVER_DEFAULT = 25.0
    cover_eff = cover if (cover is not None and cover > 0) else VIS_COVER_DEFAULT

    # Make sure bars are valid ints
    try:
        n_bars = int(num_bars)
    except Exception:
        n_bars = 0

    try:
        bar_d = float(bar_dia)
    except Exception:
        bar_d = 0.0

    unknown_bars = (n_bars <= 0)
    unknown_dia = (bar_d <= 0)

    bar_r = bar_d / 2.0 if not unknown_dia else 0.0

    draw_ties_logic = show_ties and (("Standard" in reinf_style) or ("Spiral" in reinf_style))

    # ---------- draw concrete ----------
    if shape in ["Rectangular", "Square"]:
        b, h = dims
        cx, cy = b / 2.0, h / 2.0

        ax.add_patch(
            patches.Rectangle(
                (0, 0), b, h,
                facecolor="#e0e0e0",
                edgecolor="black",
                linewidth=2,
            )
        )

        pad = max(70, 0.14 * max(b, h))
        ax.set_xlim(-pad, b + pad)
        ax.set_ylim(-pad, h + pad)

        # Dimension arrows like your sketch
        _dim_arrow(ax, (0, -0.55 * pad), (b, -0.55 * pad), f"b = {_fmt_mm(b)}", text_offset=(0, 0.18 * pad))
        _dim_arrow(ax, (-0.55 * pad, 0), (-0.55 * pad, h), f"h = {_fmt_mm(h)}", text_offset=(0.18 * pad, 0))

    else:
        D = dims[0]
        cx, cy = D / 2.0, D / 2.0

        ax.add_patch(
            patches.Circle(
                (cx, cy),
                D / 2.0,
                facecolor="#e0e0e0",
                edgecolor="black",
                linewidth=2,
            )
        )

        pad = max(70, 0.20 * D)
        ax.set_xlim(-pad, D + pad)
        ax.set_ylim(-pad, D + pad)

        _dim_arrow(ax, (0, -0.55 * pad), (D, -0.55 * pad), f"D = {_fmt_mm(D)}", text_offset=(0, 0.18 * pad))

    # Plain concrete: show only dims + label
    if "None" in reinf_style:
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        _info_box(ax, ["Plain Concrete"], x0 + 0.05 * (x1 - x0), y1 - 0.05 * (y1 - y0))
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        return fig

    # If bars unknown, show label only
    if unknown_bars or unknown_dia:
        n_txt = "?" if unknown_bars else str(n_bars)
        phi_txt = "?" if unknown_dia else f"{bar_d:.0f} mm"
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        _info_box(ax, [f"Bars: n = {n_txt}", f"Bar dia: φ = {phi_txt}"], x0 + 0.05 * (x1 - x0), y1 - 0.05 * (y1 - y0))
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        return fig

    # ---------- compute and draw reinforcement ----------
    positions = []

    # ======================================================
    # SPIRAL CASE (matches your sketch: circle cage inside square)
    # ======================================================
    if "Spiral" in reinf_style:
        # Determine cage diameter (Dk)
        # If provided, use it. Otherwise fallback from section size and cover_eff.
        try:
            Dk = float(core_diameter) if core_diameter is not None else 0.0
        except Exception:
            Dk = 0.0

        if Dk <= 0:
            if shape == "Circular":
                Dk = dims[0] - 2.0 * cover_eff
            else:
                # spiral cage circle inside rectangle
                Dk = min(dims[0], dims[1]) - 2.0 * cover_eff

        # Clamp so it can't be silly small
        Dk = max(Dk, 2.0 * bar_r + 20.0)

        # Draw cage circle
        if draw_ties_logic:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    Dk / 2.0,
                    fill=False,
                    edgecolor="#5b3cc4",   # purple-ish like your sketch
                    linewidth=2.0,
                )
            )

        # Bars on the cage circle (bar centers)
        r_bars = Dk / 2.0 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0, 2 * np.pi, n_bars, endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        # Add Dk dimension label (vertical on right like your sketch)
        # Only if rectangular (since circular already has D)
        if shape in ["Rectangular", "Square"]:
            x_right = ax.get_xlim()[1]
            # place Dk arrow near right side inside pad area
            x_dim = (dims[0] + 0.25 * (x_right - dims[0])) if len(dims) >= 2 else (cx + 0.55 * Dk)
            y1 = cy - Dk / 2.0
            y2 = cy + Dk / 2.0
            _dim_arrow(ax, (x_dim, y1), (x_dim, y2), f"Dk = {_fmt_mm(Dk)}", text_offset=(0.12 * (x_right - dims[0]), 0))

    # ======================================================
    # TIED CIRCULAR (non-spiral)
    # ======================================================
    elif shape == "Circular":
        cage_D = dims[0] - 2.0 * cover_eff
        cage_D = max(cage_D, 2.0 * bar_r + 20.0)

        if draw_ties_logic:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    cage_D / 2.0,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.8,
                    linestyle="--",
                )
            )

        r_bars = cage_D / 2.0 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0, 2 * np.pi, n_bars, endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

    # ======================================================
    # TIED RECTANGULAR
    # ======================================================
    else:
        b, h = dims
        inset_to_bar_center = cover_eff + bar_r
        inset_to_bar_center = max(inset_to_bar_center, bar_r + 4.0)

        positions = distribute_bars_rectangular(b, h, inset_to_bar_center, n_bars)

        if draw_ties_logic:
            tie_inset = cover_eff
            w_tie = max(b - 2.0 * tie_inset, 10.0)
            h_tie = max(h - 2.0 * tie_inset, 10.0)

            ax.add_patch(
                patches.Rectangle(
                    (tie_inset, tie_inset),
                    w_tie,
                    h_tie,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.8,
                    linestyle="--",
                )
            )

    # ---------- draw bars ----------
    for x, y in positions:
        ax.add_patch(
            patches.Circle(
                (x, y),
                bar_r,
                color="#d32f2f",
                zorder=20,
            )
        )

    # ---------- labels like your sketch ----------
    # As label
    As = n_bars * np.pi * (bar_d / 2.0) ** 2
    as_line = f"{n_bars}Ø{bar_d:.0f}, As={As:.0f} mm²"

    # Concrete label
    conc_line = f"Concrete: {fc_label}" if fc_label else ""

    # Spiral label
    spiral_line = ""
    if "Spiral" in reinf_style:
        parts = []
        if fywk is not None:
            parts.append(f"fywk={float(fywk):.0f} MPa")
        if spiral_dia is not None:
            parts.append(f"Ø{float(spiral_dia):.0f}")
        if spiral_spacing is not None:
            parts.append(f"@{float(spiral_spacing):.0f} mm")
        if parts:
            spiral_line = "Spiral: " + ", ".join(parts)

    # Put labels in two boxes (top left and bottom)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()

    top_lines = [f"Bars: n = {n_bars}", f"Bar dia: φ = {bar_d:.0f} mm", as_line]
    _info_box(ax, top_lines, x0 + 0.05 * (x1 - x0), y1 - 0.05 * (y1 - y0))

    bottom_lines = []
    if conc_line:
        bottom_lines.append(conc_line)
    if spiral_line:
        bottom_lines.append(spiral_line)

    if bottom_lines:
        _info_box(ax, bottom_lines, x0 + 0.05 * (x1 - x0), y0 + 0.20 * (y1 - y0))

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    return fig