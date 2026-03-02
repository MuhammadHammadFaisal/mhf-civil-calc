import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def distribute_bars_rectangular(b, h, cover, num_bars):
    eff_cover = cover
    xL, xR = eff_cover, b - eff_cover
    yB, yT = eff_cover, h - eff_cover

    positions = [(xL, yB), (xR, yB), (xR, yT), (xL, yT)]
    remaining = num_bars - 4
    if remaining <= 0:
        return positions[:num_bars]

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


def draw_cross_section(shape, dims, num_bars, bar_dia, reinf_style, show_ties, cover):
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    bar_r = bar_dia / 2
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # Concrete shape
    if shape in ["Rectangular", "Square"]:
        b, h = dims
        ax.add_patch(
            patches.Rectangle((0, 0), b, h, fill=True, facecolor="#e0e0e0", edgecolor="black", linewidth=2)
        )
        ax.set_xlim(-50, b + 50)
        ax.set_ylim(-50, h + 50)
        cx, cy = b / 2, h / 2
        min_dim = min(b, h)
    else:
        D = dims[0]
        cx, cy = D / 2, D / 2
        ax.add_patch(
            patches.Circle((cx, cy), D / 2, fill=True, facecolor="#e0e0e0", edgecolor="black", linewidth=2)
        )
        ax.set_xlim(-50, D + 50)
        ax.set_ylim(-50, D + 50)
        min_dim = D

    # Draw ties logic
    draw_ties_logic = False
    if show_ties and ("Standard" in reinf_style or "Spiral" in reinf_style):
        draw_ties_logic = True

    if "None" in reinf_style:
        ax.set_aspect("equal")
        ax.axis("off")
        return fig

    positions = []

    # Spiral or circular arrangement
    if "Spiral" in reinf_style or shape == "Circular":
        if shape == "Circular":
            cage_D = dims[0] - 2 * cover
        else:
            cage_D = min_dim - 2 * cover

        r_bars = cage_D / 2 - bar_r
        angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False)
        if shape != "Circular":
            angles += np.pi / 4

        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        if draw_ties_logic:
            linestyle = "-" if "Spiral" in reinf_style else "--"
            r_tie = cage_D / 2
            ax.add_patch(patches.Circle((cx, cy), r_tie, fill=False, edgecolor="#555", linewidth=1.5, linestyle=linestyle))

    # Rectangular arrangement
    else:
        positions = distribute_bars_rectangular(dims[0], dims[1], cover + bar_r, num_bars)

        if draw_ties_logic:
            tie_inset = cover
            w_tie = dims[0] - 2 * tie_inset
            h_tie = dims[1] - 2 * tie_inset
            ax.add_patch(
                patches.Rectangle((tie_inset, tie_inset), w_tie, h_tie, fill=False, edgecolor="#555", linewidth=1.5, linestyle="--")
            )

    # Bars
    for x, y in positions:
        ax.add_patch(patches.Circle((x, y), bar_r, color="#d32f2f", zorder=10))

    ax.set_aspect("equal")
    ax.axis("off")
    return fig
