import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def _draw_dim_line(ax, p1, p2, text, offset=(0, 0), color="#222"):
    """Simple dimension line with arrows + centered text."""
    ax.annotate(
        "",
        xy=p2, xytext=p1,
        arrowprops=dict(arrowstyle="<->", color=color, linewidth=1.2),
    )
    mx = 0.5 * (p1[0] + p2[0]) + offset[0]
    my = 0.5 * (p1[1] + p2[1]) + offset[1]
    ax.text(mx, my, text, color=color, fontsize=10, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7))


def draw_cross_section(
    shape,
    dims,
    num_bars,
    bar_dia,
    reinf_style,
    show_ties,
    cover,
    core_diameter=0.0,
    *,
    show_dims=False,
    bars_unknown=False,
    placeholder_bars=8,
    placeholder_bar_dia=16.0,
):
    """
    Draw cross-section.

    New features:
    - bars_unknown=True: shows placeholder bars even if num_bars is 0/unknown,
      and adds a label "As unknown".
    - show_dims=True: draws dimension lines (b/h for rectangular or D for circular).
    """

    fig, ax = plt.subplots(figsize=(4, 4), dpi=110)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # If bars are unknown, draw placeholders
    if bars_unknown:
        if num_bars is None or num_bars <= 0:
            num_bars = placeholder_bars
        if bar_dia is None or bar_dia <= 0:
            bar_dia = placeholder_bar_dia

    bar_r = bar_dia / 2

    # If no reinforcement AND not requesting unknown placeholders => just draw concrete
    if (num_bars is None or num_bars <= 0 or bar_dia is None or bar_dia <= 0) and not bars_unknown:
        # still draw concrete shape below, then exit cleanly
        num_bars = 0

    # ======================================================
    # DRAW CONCRETE SHAPE
    # ======================================================
    if shape in ["Rectangular", "Square"]:
        b, h = dims
        cx, cy = b / 2, h / 2

        ax.add_patch(
            patches.Rectangle((0, 0), b, h, fill=True, facecolor="#e0e0e0",
                              edgecolor="black", linewidth=2)
        )
        ax.set_xlim(-80, b + 80)
        ax.set_ylim(-80, h + 80)

        if show_dims:
            # width b (below)
            _draw_dim_line(ax, (0, -40), (b, -40), f"b = {b:.0f} mm", offset=(0, -8))
            # height h (left)
            _draw_dim_line(ax, (-40, 0), (-40, h), f"h = {h:.0f} mm", offset=(-10, 0))

    else:  # Circular
        D = dims[0]
        cx, cy = D / 2, D / 2

        ax.add_patch(
            patches.Circle((cx, cy), D / 2, fill=True, facecolor="#e0e0e0",
                           edgecolor="black", linewidth=2)
        )
        ax.set_xlim(-80, D + 80)
        ax.set_ylim(-80, D + 80)

        if show_dims:
            # diameter line across center
            _draw_dim_line(ax, (0, cy), (D, cy), f"D = {D:.0f} mm", offset=(0, 18))

    # ======================================================
    # Handle plain concrete
    # ======================================================
    if "None" in reinf_style and not bars_unknown:
        ax.set_aspect("equal")
        ax.axis("off")
        return fig

    # ======================================================
    # TIE LOGIC
    # ======================================================
    draw_ties_logic = show_ties and ("Standard" in reinf_style or "Spiral" in reinf_style)

    # ======================================================
    # BAR POSITIONS
    # ======================================================
    positions = []

    if num_bars <= 0:
        ax.set_aspect("equal")
        ax.axis("off")
        return fig

    # -------- Spiral arrangement (circular) --------
    if "Spiral" in reinf_style:
        if core_diameter > 0:
            cage_D = core_diameter
        else:
            cage_D = dims[0] - 2 * cover if shape == "Circular" else min(dims[0], dims[1]) - 2 * cover

        r_bars = cage_D / 2 - bar_r
        angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        if draw_ties_logic:
            ax.add_patch(patches.Circle((cx, cy), cage_D / 2, fill=False,
                                        edgecolor="#555", linewidth=1.5))

    # -------- Circular (non-spiral) --------
    elif shape == "Circular":
        cage_D = dims[0] - 2 * cover
        r_bars = cage_D / 2 - bar_r
        angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False)
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

    # -------- Rectangular --------
    else:
        positions = distribute_bars_rectangular(dims[0], dims[1], cover + bar_r, num_bars)

        if draw_ties_logic:
            tie_inset = cover
            w_tie = dims[0] - 2 * tie_inset
            h_tie = dims[1] - 2 * tie_inset
            ax.add_patch(
                patches.Rectangle((tie_inset, tie_inset), w_tie, h_tie,
                                  fill=False, edgecolor="#555", linewidth=1.5, linestyle="--")
            )

    # ======================================================
    # DRAW BARS
    # ======================================================
    for x, y in positions:
        ax.add_patch(patches.Circle((x, y), bar_r, color="#d32f2f", zorder=10))

    # Label for unknown bars
    if bars_unknown:
        ax.text(
            0.02, 0.98,
            "Reinforcement shown\nAs / #bars = unknown",
            transform=ax.transAxes,
            ha="left", va="top",
            fontsize=9, color="black",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.7),
        )

    ax.set_aspect("equal")
    ax.axis("off")
    return fig
