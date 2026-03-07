import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# ==========================================================
# HELPERS
# ==========================================================
def _is_spiral(reinf_style: str) -> bool:
    s = (reinf_style or "").lower()
    return "spiral" in s


def _is_tied(reinf_style: str) -> bool:
    s = (reinf_style or "").lower()
    # treat any "tie"/"tied"/"standard" as tied confinement (non-spiral)
    return ("tie" in s) or ("tied" in s) or ("standard" in s)


def _is_plain(reinf_style: str) -> bool:
    s = (reinf_style or "").lower()
    return ("none" in s) or ("plain" in s)


def _safe_int(x, default=0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _auto_inset(bar_dia: float) -> float:
    """
    No clear cover input.
    Use a visual inset so bars/ties don't sit on the concrete edge.
    Feel free to tune the constants.
    """
    bar_dia = float(bar_dia or 0.0)
    # bar radius + a small buffer looks good visually
    return max(20.0, 0.5 * bar_dia + 20.0)


# ==========================================================
# RECTANGULAR BAR DISTRIBUTION
# ==========================================================
def distribute_bars_rectangular(b, h, inset_to_bar_center, num_bars):
    """
    Distribute bars along the perimeter of a rectangular section.

    inset_to_bar_center is the offset from the concrete face to bar centerline (mm).
    """
    b = float(b)
    h = float(h)
    n = _safe_int(num_bars, 0)
    if n <= 0:
        return []

    xL, xR = inset_to_bar_center, b - inset_to_bar_center
    yB, yT = inset_to_bar_center, h - inset_to_bar_center

    # If the inset is too large, clamp it so coordinates remain valid
    if xR <= xL:
        mid = b / 2.0
        xL, xR = mid, mid
    if yT <= yB:
        mid = h / 2.0
        yB, yT = mid, mid

    # Corner-first
    corners = [(xL, yB), (xR, yB), (xR, yT), (xL, yT)]

    if n <= 4:
        return corners[:n]

    positions = corners[:]
    remaining = n - 4

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

    face_counts = [0, 0, 0, 0]
    for i in range(remaining):
        face_counts[i % 4] += 1

    for i, count in enumerate(face_counts):
        if count <= 0:
            continue
        face_name, fixed, start, end = faces[i]
        spacing = (end - start) / (count + 1)
        pts = [start + spacing * (j + 1) for j in range(count)]
        for p in pts:
            if face_name in ["left", "right"]:
                positions.append((fixed, p))
            else:
                positions.append((p, fixed))

    return positions


# ==========================================================
# INTERNAL: DRAW CONCRETE AND RETURN CENTER + OUTER SIZE
# ==========================================================
def _draw_concrete(ax, shape, dims):
    """
    Draw the concrete section and return:
    (cx, cy, outer_w, outer_h)
    """
    if str(shape).lower() in ["rectangular", "square"]:
        b, h = float(dims[0]), float(dims[1])
        cx, cy = b / 2.0, h / 2.0

        ax.add_patch(
            patches.Rectangle(
                (0, 0),
                b,
                h,
                fill=True,
                facecolor="#e0e0e0",
                edgecolor="black",
                linewidth=2.0,
                zorder=1,
            )
        )

        pad = max(0.1 * min(b, h), 50.0)
        ax.set_xlim(-pad, b + pad)
        ax.set_ylim(-pad, h + pad)
        return cx, cy, b, h, pad

    else:
        D = float(dims[0])
        cx, cy = D / 2.0, D / 2.0

        ax.add_patch(
            patches.Circle(
                (cx, cy),
                D / 2.0,
                fill=True,
                facecolor="#e0e0e0",
                edgecolor="black",
                linewidth=2.0,
                zorder=1,
            )
        )

        pad = max(0.1 * D, 50.0)
        ax.set_xlim(-pad, D + pad)
        ax.set_ylim(-pad, D + pad)
        return cx, cy, D, D, pad

def _mm_to_cm_str(x_mm: float) -> str:
    # 500 mm -> "50 cm"
    return f"{x_mm/10:.0f} cm"


def _add_dim_line(ax, x1, y1, x2, y2, text, text_offset=(0, 0), lw=1.2):
    """
    Draw a dimension line with double arrow and centered label.
    """
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="<->", linewidth=lw, color="#777"),
        zorder=20,
    )
    tx = (x1 + x2) / 2.0 + text_offset[0]
    ty = (y1 + y2) / 2.0 + text_offset[1]
    ax.text(tx, ty, text, ha="center", va="center", color="#777", fontsize=11, zorder=21)


def _add_section_dimensions(ax, shape, dims, pad):
    """
    Adds outer dimension labels (b/h for rectangle, D for circle).
    dims are in mm. pad is the plotting pad used in _draw_concrete().
    """
    if str(shape).lower() in ["rectangular", "square"]:
        b, h = float(dims[0]), float(dims[1])

        # Right-side vertical dimension (h)
        x_dim = b + pad * 0.45
        _add_dim_line(
            ax,
            x_dim,
            0,
            x_dim,
            h,
            _mm_to_cm_str(h),
            text_offset=(pad * 0.15, 0),
        )

        # Bottom horizontal dimension (b)
        y_dim = -pad * 0.45
        _add_dim_line(
            ax,
            0,
            y_dim,
            b,
            y_dim,
            _mm_to_cm_str(b),
            text_offset=(0, -pad * 0.15),
        )

    else:
        D = float(dims[0])

        # Right-side vertical dimension (D)
        x_dim = D + pad * 0.45
        _add_dim_line(
            ax,
            x_dim,
            0,
            x_dim,
            D,
            _mm_to_cm_str(D),
            text_offset=(pad * 0.15, 0),
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
    cover_unused=0.0,      # kept for backward compatibility, NOT USED
    core_diameter=0.0,     # for spiral: Ack/Dk to spiral centerline (works for rectangular too)
):
    """
    Draw RC cross-section with longitudinal bars and (optional) ties/spiral.

    IMPORTANT:
    - No clear cover input is required.
    - cover_unused is ignored (kept so your existing call signature doesn't break).
    - A visual inset is auto-computed from bar diameter.
    - For spiral: core_diameter (Ack/Dk) is used if provided (>0), even for rectangular sections.
    """

    # ---- sanitize ----
    n = _safe_int(num_bars, 0)
    bar_dia = float(bar_dia or 0.0)
    bar_r = bar_dia / 2.0

    fig, ax = plt.subplots(figsize=(4, 4), dpi=120)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # If no reinforcement info, just draw concrete
    if n <= 0 or bar_dia <= 0 or _is_plain(reinf_style):
        _draw_concrete(ax, shape, dims)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        fig.tight_layout(pad=0.2)
        return fig

    # ---- draw concrete + get center and outer size ----
    cx, cy, outer_w, outer_h, pad = _draw_concrete(ax, shape, dims)
    _add_section_dimensions(ax, shape, dims, pad)

    # Auto inset (no cover input)
    inset = _auto_inset(bar_dia)

    # Whether to draw tie/spiral line
    draw_confinement = bool(show_ties) and (_is_tied(reinf_style) or _is_spiral(reinf_style))

    positions = []

    # ======================================================
    # SPIRAL (use core_diameter if provided; clamp to section)
    # ======================================================
    if _is_spiral(reinf_style):
        # Dk/Ack to spiral centerline (preferred)
        if core_diameter and float(core_diameter) > 0:
            cage_D = float(core_diameter)
        else:
            # fallback: derive a reasonable cage diameter from outer size and inset
            cage_D = min(outer_w, outer_h) - 2.0 * inset

        # clamp so spiral stays inside concrete
        max_D = min(outer_w, outer_h) - 2.0 * inset
        if max_D > 0:
            cage_D = min(cage_D, max_D)

        # keep cage_D feasible vs bar size
        cage_D = max(cage_D, 2.0 * bar_r + 10.0)

        r_bars = cage_D / 2.0 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        if draw_confinement:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    cage_D / 2.0,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.6,
                    linestyle="-",
                    zorder=5,
                )
            )

    # ======================================================
    # CIRCULAR (TIES)
    # ======================================================
    elif str(shape).lower() == "circular":
        # tie hoop diameter (to centerline) based on inset
        cage_D = outer_w - 2.0 * inset  # outer_w == D for circular

        # keep cage_D feasible vs bar size
        cage_D = max(cage_D, 2.0 * bar_r + 10.0)

        r_bars = cage_D / 2.0 - bar_r
        r_bars = max(r_bars, 1.0)

        angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        if draw_confinement:
            ax.add_patch(
                patches.Circle(
                    (cx, cy),
                    cage_D / 2.0,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.6,
                    linestyle="--",
                    zorder=5,
                )
            )

    # ======================================================
    # RECTANGULAR (TIES)
    # ======================================================
    else:
        # bars inset to centerline is inset + bar radius
        bar_inset = inset + bar_r

        b, h = float(dims[0]), float(dims[1])
        positions = distribute_bars_rectangular(b, h, bar_inset, n)

        if draw_confinement:
            tie_inset = inset  # tie/hoop line at inset
            w_tie = max(b - 2.0 * tie_inset, 10.0)
            h_tie = max(h - 2.0 * tie_inset, 10.0)

            ax.add_patch(
                patches.Rectangle(
                    (tie_inset, tie_inset),
                    w_tie,
                    h_tie,
                    fill=False,
                    edgecolor="#555",
                    linewidth=1.6,
                    linestyle="--",
                    zorder=5,
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
                facecolor="#d32f2f",
                edgecolor="none",
                zorder=10,
            )
        )

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    # Example note labels (top-left)
    try:
        note1 = f"{int(num_bars)}Ø{bar_dia:.0f}"
    except Exception:
        note1 = ""

    note2 = ""
    if _is_spiral(reinf_style):
        if core_diameter and float(core_diameter) > 0:
            note2 = f"Spiral, Ack={core_diameter:.0f} mm"
        else:
            note2 = "Spiral"

    if note1:
        ax.text(0.02, 0.98, note1, transform=ax.transAxes, va="top", ha="left",
                fontsize=11, color="#444", zorder=30)
    if note2:
    ax.text(
        0.02, 0.92, note2,
        transform=ax.transAxes,
        va="top", ha="left",
        fontsize=10, color="#444",
        zorder=30
    )
    return fig