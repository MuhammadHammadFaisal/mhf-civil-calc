import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# ==========================================================
# RECTANGULAR BAR DISTRIBUTION
# ==========================================================
def distribute_bars_rectangular(b, h, inset, num_bars):
    """
    Distribute bars around a rectangular perimeter with a given inset.
    inset is the distance from concrete face to bar centerline.
    """
    xL, xR = inset, b - inset
    yB, yT = inset, h - inset

    # corners first
    positions = [(xL, yB), (xR, yB), (xR, yT), (xL, yT)]

    remaining = num_bars - 4
    if remaining <= 0:
        return positions[: max(0, num_bars)]

    # prioritize long faces
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
# SMALL HELPERS FOR LABELS
# ==========================================================
def _fmt_mm(x):
    try:
        return f"{float(x):.0f} mm"
    except Exception:
        return "—"


def _dim_arrow(ax, xy1, xy2, text, text_offset=(0, 0), lw=1.2):
    """
    Draw a simple double arrow dimension line with centered label.
    """
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
    """
    Draw a small info text box at (x, y) in data coordinates.
    """
    text = "\n".join(lines)
    ax.text(
        x,
        y,
        text,
        ha="left",
        va="top",
        fontsize=10,
        color="#111",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#777", alpha=0.9),
        zorder=50,
    )


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
    core_diameter=0.0,
):
    """
    Dynamic section sketch:
    - Does NOT rely on user-provided cover for stability. If cover <= 0, uses a visual-only default.
    - Spiral uses core_diameter if provided; otherwise falls back to (outer - 2*cover_eff).
    - Adds dimension labels (b/h or D) and reinforcement label (n, φ).
    """

    fig, ax = plt.subplots(figsize=(4.6, 4.6), dpi=110)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # -------------------------
    # Defaults / safety
    # -------------------------
    VIS_COVER_DEFAULT = 25.0  # visual-only default if cover not provided
    cover_eff = cover if (cover is not None and cover > 0) else VIS_COVER_DEFAULT

    unknown_bars = (num_bars is None) or (num_bars <= 0)
    unknown_dia = (bar_dia is None) or (bar_dia <= 0)

    # If bar dia unknown, still draw shape and label n=?
    bar_r = (bar_dia / 2.0) if not unknown_dia else 0.0

    # Decide whether ties/spiral outline should be drawn
    draw_ties_logic = (
        show_ties and (("Standard" in str(reinf_style)) or ("Spiral" in str(reinf_style)))
    )

    # Plain concrete: draw only shape + dimensions + note
    if "None" in str(reinf_style):
        unknown_bars = True  # reinforce label: n=0 / none
        unknown_dia = True

    # -------------------------
    # Draw concrete shape
    # -------------------------
    if shape in ["Rectangular", "Square"]:
        b, h = dims
        cx, cy = b / 2.0, h / 2.0

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

        pad = max(60, 0.12 * max(b, h))
        ax.set_xlim(-pad, b + pad)
        ax.set_ylim(-pad, h + pad)

        # Dimension labels
        # b at bottom
        _dim_arrow(ax, (0, -0.55 * pad), (b, -0.55 * pad), f"b = {_fmt_mm(b)}", text_offset=(0, 0.18 * pad))
        # h at left
        _dim_arrow(ax, (-0.55 * pad, 0), (-0.55 * pad, h), f"h = {_fmt_mm(h)}", text_offset=(0.18 * pad, 0))

    else:
        D = dims[0]
        cx, cy = D / 2.0, D / 2.0

        ax.add_patch(
            patches.Circle(
                (cx, cy),
                D / 2.0,
                fill=True,
                facecolor="#e0e0e0",
                edgecolor="black",
                linewidth=2,
            )
        )

        pad = max(60, 0.18 * D)
        ax.set_xlim(-pad, D + pad)
        ax.set_ylim(-pad, D + pad)

        # Dimension label (diameter)
        _dim_arrow(
            ax,
            (0, -0.55 * pad),
            (D, -0.55 * pad),
            f"D = {_fmt_mm(D)}",
            text_offset=(0, 0.18 * pad),
        )

    # -------------------------
    # If no reinforcement info, show labels only
    # -------------------------
    if ("None" in str(reinf_style)) or unknown_bars or unknown_dia:
        lines = []
        if "None" in str(reinf_style):
            lines.append("Reinf: Plain Concrete")
        else:
            n_text = "?" if unknown_bars else str(num_bars)
            phi_text = "?" if unknown_dia else f"{bar_dia:.0f} mm"
            lines.append(f"Bars: n = {n_text}")
            lines.append(f"Bar dia: φ = {phi_text}")

        # Put box near top-left inside plotting window
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        _info_box(ax, lines, x0 + 0.05 * (x1 - x0), y1 - 0.05 * (y1 - y0))

        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        return fig

    # -------------------------
    # Compute bar positions
    # -------------------------
    positions = []

    # Spiral arrangement (uses core_diameter if provided)
    if "Spiral" in str(reinf_style):
        if core_diameter and core_diameter > 0:
            cage_D = float(core_diameter)
        else:
            # fallback to something safe
            if shape == "Circular":
                cage_D = dims[0] - 2.0 * cover_eff
            else:
                cage_D = min(dims[0], dims[1]) - 2.0 * cover_eff

        # Clamp cage diameter so it can't go negative/silly
        cage_D = max(cage_D, 2.0 * bar_r + 10.0)

        r_bars = cage_D / 2.0 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0, 2 * np.pi, int(num_bars), endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        if draw_ties_logic:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    cage_D / 2.0,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.6,
                    linestyle="-",
                )
            )

            # label Dk if given
            dk_label = cage_D
            _info_box(
                ax,
                [f"Spiral core: Dk = {_fmt_mm(dk_label)}"],
                ax.get_xlim()[0] + 0.05 * (ax.get_xlim()[1] - ax.get_xlim()[0]),
                ax.get_ylim()[1] - 0.22 * (ax.get_ylim()[1] - ax.get_ylim()[0]),
            )

    # Circular (non-spiral): tied circular hoop (visual)
    elif shape == "Circular":
        cage_D = dims[0] - 2.0 * cover_eff
        cage_D = max(cage_D, 2.0 * bar_r + 10.0)

        r_bars = cage_D / 2.0 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0, 2 * np.pi, int(num_bars), endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        if draw_ties_logic:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    cage_D / 2.0,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.6,
                    linestyle="--",
                )
            )

    # Rectangular arrangement (tied)
    else:
        b, h = dims
        inset_to_bar_center = cover_eff + bar_r
        inset_to_bar_center = max(inset_to_bar_center, bar_r + 2.0)

        positions = distribute_bars_rectangular(b, h, inset_to_bar_center, int(num_bars))

        if draw_ties_logic:
            tie_inset = cover_eff
            w_tie = b - 2.0 * tie_inset
            h_tie = h - 2.0 * tie_inset

            # Clamp so rectangle tie doesn't invert
            w_tie = max(w_tie, 10.0)
            h_tie = max(h_tie, 10.0)

            ax.add_patch(
                patches.Rectangle(
                    (tie_inset, tie_inset),
                    w_tie,
                    h_tie,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.6,
                    linestyle="--",
                )
            )

    # -------------------------
    # Draw bars
    # -------------------------
    for x, y in positions:
        ax.add_patch(
            patches.Circle(
                (x, y),
                bar_r,
                color="#d32f2f",
                zorder=10,
            )
        )

    # -------------------------
    # Reinforcement label box (like "normal diagram")
    # -------------------------
    info_lines = [
        f"Bars: n = {int(num_bars)}",
        f"Bar dia: φ = {_fmt_mm(bar_dia)}",
    ]
    if "Spiral" in str(reinf_style) and core_diameter and core_diameter > 0:
        info_lines.append(f"Core: Dk = {_fmt_mm(core_diameter)}")

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    _info_box(ax, info_lines, x0 + 0.05 * (x1 - x0), y1 - 0.05 * (y1 - y0))

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    return fig