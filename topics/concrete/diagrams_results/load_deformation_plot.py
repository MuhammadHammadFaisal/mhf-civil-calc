import numpy as np
import matplotlib.pyplot as plt

try:
    from scipy.interpolate import PchipInterpolator
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def plot_load_deformation(N1, N2, trans_type):
    """Create an illustrative axial load–deformation plot.

    Important:
    - The curve *shape* is illustrative (control points).
    - The x-axis is converted to axial shortening δ (mm) using assumed strains
      and an assumed column height (gauge length).

    Fix applied:
    - Annotations/arrow pointers are now placed in the correct x-units (mm),
      not the pre-conversion "r" coordinate.
    """

    # -----------------------------
    # Assumptions (make explicit)
    # -----------------------------
    L_assumed = 3000.0  # mm (assumed column height / gauge length)
    eps_peak_unconf = 0.002  # peak concrete strain (typical)
    eps_ult_tied = 0.004  # assumed ultimate strain for tied/unconfined behavior
    eps_ult_spiral_good = 0.015  # assumed ultimate strain for good spiral confinement
    eps_ult_spiral_weak = 0.006  # assumed ultimate strain for weak spiral confinement

    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    text_color = "white"
    ax.spines["bottom"].set_color(text_color)
    ax.spines["left"].set_color(text_color)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", colors=text_color)
    ax.tick_params(axis="y", colors=text_color)
    ax.yaxis.label.set_color(text_color)
    ax.xaxis.label.set_color(text_color)

    # -----------------------------
    # Build illustrative SHAPE points (r) and loads (y)
    # We'll later convert r -> strain -> shortening δ(mm)
    # -----------------------------
    if trans_type == "Spiral":
        if N2 > N1:
            # good spiral confinement: second peak and ductility
            r = np.array([0, 1.0, 2.0, 3.5, 5.5, 6.5])
            y = np.array([0, N1, 0.85 * N1, N2, N2, 0.9 * N2])
            color = "#00BFFF"
            eps_max = eps_ult_spiral_good
            spiral_case = "good"
        else:
            # weak spiral: first peak governs
            r = np.array([0, 1.0, 2.0, 3.5, 5.0])
            y = np.array([0, N1, 0.80 * N1, N2, 0.8 * N2])
            color = "#FF4B4B"
            eps_max = eps_ult_spiral_weak
            spiral_case = "weak"
    else:
        # tied / unconfined-like: post-peak softening
        r = np.array([0, 1.0, 2.5, 4.0])
        y = np.array([0, N1, 0.5 * N1, 0.3 * N1])
        color = "#FFA500"
        eps_max = eps_ult_tied
        spiral_case = None

    # -----------------------------
    # Convert r -> strain profile (scaled so r=1 corresponds to peak strain)
    # Then strain -> shortening δ(mm)
    # -----------------------------
    r_peak = 1.0
    r_max = r.max()

    eps = np.zeros_like(r, dtype=float)
    for i, ri in enumerate(r):
        if ri <= r_peak:
            eps[i] = (ri / r_peak) * eps_peak_unconf
        else:
            eps[i] = eps_peak_unconf + ((ri - r_peak) / (r_max - r_peak)) * (eps_max - eps_peak_unconf)

    x = eps * L_assumed  # δ in mm

    # Helper: convert an r-location to the correct x(mm) coordinate
    def x_at_r(r_target: float) -> float:
        return float(np.interp(r_target, r, x))

    # -----------------------------
    # Plot (smooth if possible)
    # -----------------------------
    if HAS_SCIPY:
        try:
            interpolator = PchipInterpolator(x, y)
            x_smooth = np.linspace(x.min(), x.max(), 300)
            y_smooth = interpolator(x_smooth)
            ax.plot(x_smooth, y_smooth, color=color, linewidth=3)
        except Exception:
            ax.plot(x, y, color=color, linewidth=3)
    else:
        ax.plot(x, y, color=color, linewidth=3)

    # -----------------------------
    # Annotations (FIXED: now use x(mm), not raw r)
    # Use offset-points so labels look consistent across scales
    # -----------------------------
    if trans_type == "Spiral":
        if spiral_case == "good":
            ax.annotate(
                "First Peak\n(Shell Spalls)",
                xy=(x_at_r(1.0), N1),
                xytext=(20, 25),
                textcoords="offset points",
                arrowprops=dict(color=text_color, arrowstyle="->"),
                ha="left",
                va="bottom",
                color=text_color,
            )
            ax.annotate(
                "Second Peak\n(Confined Core)",
                xy=(x_at_r(3.5), N2),
                xytext=(0, 28),
                textcoords="offset points",
                arrowprops=dict(color=text_color, arrowstyle="->"),
                ha="center",
                va="bottom",
                color=text_color,
            )
            ax.annotate(
                "Ductile Plateau",
                xy=(x_at_r(5.5), N2),
                xytext=(0, -30),
                textcoords="offset points",
                arrowprops=dict(color=text_color, arrowstyle="->"),
                ha="center",
                va="top",
                color=text_color,
            )
            ax.axhline(y=N1, color="gray", linestyle="--", alpha=0.5)
        else:
            ax.annotate(
                "First Peak\n(Governs)",
                xy=(x_at_r(1.0), N1),
                xytext=(25, 30),
                textcoords="offset points",
                arrowprops=dict(color=text_color, arrowstyle="->"),
                ha="left",
                va="bottom",
                color=text_color,
            )
            ax.annotate(
                "Spiral too weak",
                xy=(x_at_r(3.5), N2),
                xytext=(0, 28),
                textcoords="offset points",
                arrowprops=dict(color=text_color, arrowstyle="->"),
                ha="center",
                va="bottom",
                color=text_color,
            )
    else:
        ax.annotate(
            r"Failure ($N_{max}$)",
            xy=(x_at_r(1.0), N1),
            xytext=(25, 10),
            textcoords="offset points",
            arrowprops=dict(color=text_color, arrowstyle="->"),
            ha="left",
            va="bottom",
            color=text_color,
        )

    # -----------------------------
    # Labels & bounds
    # -----------------------------
    ax.set_xlabel(rf"Axial Shortening $\delta$ (mm) — assumed $L={int(L_assumed)}$ mm", fontsize=11)
    ax.set_ylabel("Axial Load (N)", fontsize=11)
    ax.set_ylim(bottom=0, top=max(N1, N2) * 1.3)
    ax.set_xlim(left=0)

    # Small note on assumptions
    ax.text(
        0.02,
        0.02,
        rf"Assumed: $\varepsilon_{{c0}}={eps_peak_unconf:.3f}$, $\varepsilon_{{max}}={eps_max:.3f}$",
        transform=ax.transAxes,
        color="white",
        fontsize=9,
    )

    return fig
