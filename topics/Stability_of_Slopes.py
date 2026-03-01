import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from theme import write_text, glass_box, glass_table

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def calculate_infinite_slope_general(beta, phi, c, gamma_dry, gamma_sat, z, m):
    gamma_w = 9.81
    beta_r = math.radians(beta)
    phi_r = math.radians(phi)
    gamma_total = ((1 - m) * gamma_dry) + (m * gamma_sat)
    W = gamma_total * z
    sigma = W * (math.cos(beta_r) ** 2)
    u = m * z * gamma_w * (math.cos(beta_r) ** 2)
    tau = W * math.sin(beta_r) * math.cos(beta_r)
    sigma_eff = sigma - u
    shear_strength = c + sigma_eff * math.tan(phi_r)
    if abs(tau) < 1e-6:
        return 999, sigma, u, tau, sigma_eff
    FS = shear_strength / tau
    return FS, sigma, u, tau, sigma_eff


def fs_theme_class(FS):
    if FS >= 1.5:
        return "stable", "Stable"
    elif FS >= 1.0:
        return "marginal", "Marginally Stable"
    else:
        return "unstable", "Unstable"


# =========================================================
# MAIN APP
# =========================================================
def app():
    tab_trans, tab_rot, tab_comp = st.tabs([
        "1. Translational (Infinite)",
        "2. Rotational (Circular)",
        "3. Compound (Block)"
    ])

    # ---------------------------------------------------------
    # TAB 1: TRANSLATIONAL (INFINITE SLOPE)
    # ---------------------------------------------------------
    with tab_trans:
    # Wider diagram column for better readability
    c1, c2, c3 = st.columns([0.40, 0.40, 0.70], gap="large")

    # -----------------------------
    # Example scenarios (optional)
    # -----------------------------
    with st.expander("Example scenarios (optional)"):
        preset = st.selectbox(
            "Auto-fill typical values",
            ["Custom", "Dry Sand (c'=0, m=0)", "Dry Soil (c'>0, m=0)", "Saturated (m=1)"],
            index=0,
            help="This only changes input values. It does NOT change the calculation method.",
            key="inf_preset"
        )

    # Default values stored in session_state (so preset can update inputs)
    if "inf_init_done" not in st.session_state:
        st.session_state.inf_init_done = True
        st.session_state.inf_beta = 25.0
        st.session_state.inf_z = 5.0
        st.session_state.inf_c = 5.0
        st.session_state.inf_phi = 30.0
        st.session_state.inf_gdry = 18.0
        st.session_state.inf_gsat = 20.0
        st.session_state.inf_m = 0.0
        st.session_state.inf_last_preset = "Custom"

    # Apply preset values only when preset changes
    if preset != st.session_state.inf_last_preset:
        if preset == "Dry Sand (c'=0, m=0)":
            st.session_state.inf_c = 0.0
            st.session_state.inf_phi = 32.0
            st.session_state.inf_m = 0.0
            st.session_state.inf_gdry = 18.0
            st.session_state.inf_gsat = 20.0

        elif preset == "Dry Soil (c'>0, m=0)":
            st.session_state.inf_c = 8.0
            st.session_state.inf_phi = 28.0
            st.session_state.inf_m = 0.0
            st.session_state.inf_gdry = 18.0
            st.session_state.inf_gsat = 20.0

        elif preset == "Saturated (m=1)":
            st.session_state.inf_c = 5.0
            st.session_state.inf_phi = 30.0
            st.session_state.inf_m = 1.0
            st.session_state.inf_gdry = 18.0
            st.session_state.inf_gsat = 20.0

        st.session_state.inf_last_preset = preset

    with c1:
        write_text("subheader", "1. Geometry")

        beta = st.number_input(
            "Slope Angle (β) [deg]",
            min_value=0.0, max_value=60.0,
            value=float(st.session_state.inf_beta),
            help="Angle of the ground surface measured from horizontal.",
            key="inf_beta"
        )

        z = st.number_input(
            "Depth Normal to Slope (z) [m]",
            min_value=0.5, max_value=20.0,
            value=float(st.session_state.inf_z),
            help="Thickness above the assumed failure plane measured perpendicular to the slope surface.",
            key="inf_z"
        )

        write_text("caption", "Assumption: failure plane is parallel to the ground surface (infinite slope).")

        with st.expander("Assumptions used in this model"):
            st.markdown(
                "- Failure plane is **parallel** to slope surface (infinite slope).\n"
                "- Combined unit weight:  $\\gamma_{total} = (1-m)\\gamma_{dry} + m\\gamma_{sat}$.\n"
                "- Pore pressure model:  $u = \\gamma_w (m z)\\cos^2\\beta$.\n"
                "- Stresses shown in **kPa** (since kN/m² = kPa)."
            )

    with c2:
        write_text("subheader", "2. Soil Properties")

        c_prime = st.number_input(
            "Cohesion (c') [kPa]",
            min_value=0.0, max_value=100.0,
            value=float(st.session_state.inf_c),
            help="Effective cohesion in Mohr–Coulomb shear strength.",
            key="inf_c"
        )

        phi_prime = st.number_input(
            "Friction Angle (ϕ') [deg]",
            min_value=0.0, max_value=45.0,
            value=float(st.session_state.inf_phi),
            help="Effective friction angle used in shear strength.",
            key="inf_phi"
        )

        gamma_dry = st.number_input(
            "Dry Unit Weight (γ_dry) [kN/m³]",
            min_value=15.0, max_value=25.0,
            value=float(st.session_state.inf_gdry),
            help="Typical: ~16–20 kN/m³ for many soils.",
            key="inf_gdry"
        )

        gamma_sat = st.number_input(
            "Saturated Unit Weight (γ_sat) [kN/m³]",
            min_value=15.0, max_value=25.0,
            value=float(st.session_state.inf_gsat),
            help="Typical: ~19–22 kN/m³ depending on soil.",
            key="inf_gsat"
        )

        m_ratio = st.slider(
            "Water Table Ratio (m = z_w / z)",
            min_value=0.0, max_value=1.0,
            value=float(st.session_state.inf_m),
            help="m=0 → dry. m=1 → fully saturated thickness.",
            key="inf_m"
        )

        calc_t = st.button("Calculate Factor of Safety", type="primary", key="inf_calc_btn")
        write_text("caption", "Press Calculate to freeze results while you explore inputs.")

    with c3:
        write_text("subheader", "Slope Diagram")

        fig_t, ax_t = plt.subplots(figsize=(7.2, 5.2))

        x = np.linspace(0, 10, 200)
        beta_r_diag = math.radians(beta)

        # Ground surface line
        y_surf = x * math.tan(beta_r_diag)

        # Unit normal pointing into the slope
        nx = math.sin(beta_r_diag)
        ny = -math.cos(beta_r_diag)

        # Failure plane at depth z (normal)
        x_fail = x + nx * z
        y_fail = y_surf + ny * z

        ax_t.plot(x, y_surf, 'k-', linewidth=2.5, label="Ground Surface")
        ax_t.plot(x_fail, y_fail, 'r--', linewidth=2.5, label="Failure Plane")
        ax_t.fill_between(x, y_surf, y_fail, where=(y_surf >= y_fail), alpha=0.22)

        # Water table line at z_w = m*z (parallel to slope)
        z_w = m_ratio * z
        if z_w > 0:
            x_wt = x + nx * z_w
            y_wt = y_surf + ny * z_w
            ax_t.plot(x_wt, y_wt, 'b--', linewidth=2.5, label="Water Table (z_w = m·z)")

        ax_t.set_aspect('equal')
        ax_t.axis('off')
        ax_t.legend(loc="upper left", fontsize=9)
        st.pyplot(fig_t)
        plt.close(fig_t)

    # -----------------------------
    # Persistent Results + Full Log
    # -----------------------------
    if "inf_last_result" not in st.session_state:
        st.session_state.inf_last_result = None

    if calc_t:
        FS, sigma, u, tau, sigma_eff = calculate_infinite_slope_general(
            beta, phi_prime, c_prime, gamma_dry, gamma_sat, z, m_ratio
        )

        phi_r = math.radians(phi_prime)
        tau_f = c_prime + sigma_eff * math.tan(phi_r)

        level_class, status_text = fs_theme_class(FS)

        st.session_state.inf_last_result = {
            "FS": FS,
            "sigma": sigma,
            "u": u,
            "tau": tau,
            "sigma_eff": sigma_eff,
            "tau_f": tau_f,
            "level_class": level_class,
            "status_text": status_text,
        }

    if st.session_state.inf_last_result is not None:
        r = st.session_state.inf_last_result

        st.markdown("---")

        # FS badge (blue theme aligned)
        st.markdown(
            f"""
            <div class="fs-card">
                <div class="fs-row">
                    <div class="fs-title">Factor of Safety</div>
                    <div class="fs-badge fs-{r['level_class']}">
                        <span class="fs-dot fs-dot-{r['level_class']}"></span>
                        <span>FS = {r['FS']:.3f}</span>
                        <span>—</span>
                        <span>{r['status_text']}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Results table
        stress_df = pd.DataFrame({
            "Parameter": [
                "Total Normal Stress (σ)",
                "Pore Water Pressure (u)",
                "Effective Normal Stress (σ')",
                "Shear Stress (τ)",
                "Shear Strength (τ_f)"
            ],
            "Value (kPa)": [
                f"{r['sigma']:.2f}",
                f"{r['u']:.2f}",
                f"{r['sigma_eff']:.2f}",
                f"{r['tau']:.2f}",
                f"{r['tau_f']:.2f}"
            ],
        })
        glass_table(stress_df)

        if c_prime == 0 and m_ratio == 0:
            st.info("ℹ️ Special Case: Dry Cohesionless Slope — FS = tan(ϕ') / tan(β)")
        if r["sigma_eff"] < 0:
            st.warning("⚠️ Effective stress is negative — tension condition may exist at failure plane.")

        # Detailed Calculation Log (Step 1 → Step 6)
        write_text("subheader", "Detailed Calculation Log")

        beta_r = math.radians(beta)
        phi_r = math.radians(phi_prime)
        z_w = m_ratio * z
        tan_phi = math.tan(phi_r)

        step1 = (
            f"### Step 1 — Total Normal Stress\n\n"
            f"**Given:** β = {beta}°, z = {z} m, γ_dry = {gamma_dry} kN/m³, γ_sat = {gamma_sat} kN/m³, m = {m_ratio}\n\n"
            f"Saturated depth = m · z = {m_ratio} × {z} = **{z_w:.2f} m**\n\n"
            r"$$\sigma = \left[\gamma_{dry}(1-m) + \gamma_{sat} \cdot m\right] \cdot z \cdot \cos^2\beta$$"
            "\n\n**Substitution:**\n\n"
            rf"$$\sigma = \left[{gamma_dry} \times {(1-m_ratio):.2f} + {gamma_sat} \times {m_ratio:.2f}\right] \times {z} \times \cos^2({beta}°) = {r['sigma']:.2f} \ kPa$$"
        )

        step2 = (
            f"### Step 2 — Pore Water Pressure\n\n"
            r"$$u = \gamma_w \cdot m \cdot z \cdot \cos^2\beta$$"
            "\n\n**Substitution:**\n\n"
            rf"$$u = 9.81 \times {m_ratio} \times {z} \times \cos^2({beta}°) = {r['u']:.2f} \ kPa$$"
        )

        step3 = (
            f"### Step 3 — Effective Normal Stress\n\n"
            r"$$\sigma' = \sigma - u$$"
            "\n\n**Substitution:**\n\n"
            rf"$$\sigma' = {r['sigma']:.2f} - {r['u']:.2f} = {r['sigma_eff']:.2f} \ kPa$$"
            + ("\n\n⚠️ **Tension condition — effective stress is negative.**" if r["sigma_eff"] < 0 else "")
        )

        step4 = (
            f"### Step 4 — Shear Stress on Failure Plane\n\n"
            r"$$\tau = \left[\gamma_{dry}(1-m) + \gamma_{sat} \cdot m\right] \cdot z \cdot \sin\beta \cdot \cos\beta$$"
            "\n\n**Substitution:**\n\n"
            rf"$$\tau = \left[{gamma_dry} \times {(1-m_ratio):.2f} + {gamma_sat} \times {m_ratio:.2f}\right] \times {z} \times \sin({beta}°) \times \cos({beta}°) = {r['tau']:.2f} \ kPa$$"
        )

        step5 = (
            f"### Step 5 — Shear Strength (Mohr-Coulomb)\n\n"
            r"$$\tau_f = c' + \sigma' \cdot \tan(\phi')$$"
            "\n\n**Substitution:**\n\n"
            rf"$$\tau_f = {c_prime} + {r['sigma_eff']:.2f} \times \tan({phi_prime}°) = {c_prime} + {r['sigma_eff']:.2f} \times {tan_phi:.4f} = {r['tau_f']:.2f} \ kPa$$"
        )

        step6 = (
            f"### Step 6 — Factor of Safety\n\n"
            r"$$FS = \frac{\tau_f}{\tau}$$"
            "\n\n**Substitution:**\n\n"
            rf"$$FS = \frac{{{r['tau_f']:.2f}}}{{{r['tau']:.2f}}} = {r['FS']:.3f}$$"
            "\n\n"
            f"<div class='fs-badge fs-{r['level_class']}'>"
            f"<span class='fs-dot fs-dot-{r['level_class']}'></span>"
            f"<span>FS = {r['FS']:.3f}</span><span>—</span><span>{r['status_text']}</span>"
            f"</div>"
        )

        for step in [step1, step2, step3, step4, step5, step6]:
            glass_box(step)

    # ---------------------------------------------------------
    # TAB 2: ROTATIONAL (CIRCULAR)
    # ---------------------------------------------------------
    with tab_rot:
        method = st.radio("**Calculation Method:**",
                          ["A. Mass Procedure (Undrained / ϕ=0)", "B. Method of Slices"],
                          horizontal=True, key="rot_method_select")
        st.markdown("---")

        # ── A. MASS PROCEDURE ─────────────────────────────────────
        if "Mass Procedure" in method:
            col_r1, col_r2 = st.columns([0.4, 0.6], gap="medium")

            with col_r1:
                write_text("subheader", "1. Geometry & Loads")
                H_slope = st.number_input("Slope Height (H) [m]", 1.0, 50.0, 8.5, key="mass_H")
                beta_slope = st.number_input("Slope Angle [deg]", 0.0, 90.0, 45.0, key="mass_beta")
                st.markdown("**Failure Circle**")
                R = st.number_input("Radius (R) [m]", 5.0, 50.0, 12.1, key="mass_R")
                o_x = st.number_input("Center X-coord (o_x) [m]", -20.0, 20.0, -2.0, key="mass_ox")
                dist_d = st.number_input("Moment Arm (d) [m]", 0.0, 20.0, 4.5,
                                         help="Horizontal distance from Center O to Centroid", key="mass_d")
                st.caption("⚠️ **Note:** This calculation currently assumes a toe failure. The circle geometry is forced to intersect the slope toe at coordinates (0,0).")
                write_text("subheader", "2. Soil Properties")
                gamma_clay = st.number_input("Unit Weight (γ) [kN/m³]", 10.0, 25.0, 19.0, key="mass_gamma")
                Cu = st.number_input("Undrained Shear Strength (Cu) [kPa]", 0.0, 200.0, 65.0, key="mass_cu")
                calc_rot = st.button("Calculate Factor of Safety", type="primary", key="btn_calc_rot_mass")
                st.caption("Weight Calculation:")
                area_approx = st.number_input("Area of Sliding Mass [m²]", 1.0, 500.0, 70.0, key="mass_area")
                W_calc = area_approx * gamma_clay
                st.write(f"Weight (W) = {W_calc:.1f} kN/m")

                z_c = 0.0
                water_crack = False
                if Cu > 0:
                    st.markdown("**Tension Crack**")
                    if gamma_clay > 0:
                        z_c = (2 * Cu) / gamma_clay
                    z_c = min(z_c, H_slope)
                    st.info(f"Tension Crack Depth ($z_c$) = **{z_c:.2f} m**")
                    if z_c > 0:
                        water_crack = st.checkbox("Crack filled with water (Adds driving force)", value=False)

            with col_r2:
                write_text("subheader", "Failure Diagram")
                fig_c, ax_c = plt.subplots(figsize=(8, 6))
                X_crest = H_slope / math.tan(math.radians(beta_slope)) if beta_slope > 0 else 10
                Y_crest = H_slope
                ground_x = [-10, 0, X_crest, X_crest + 10]
                ground_y = [0, 0, Y_crest, Y_crest]
                ax_c.plot(ground_x, ground_y, 'k-', linewidth=2.5, label="Ground Surface")
                y_crack_bottom = Y_crest - z_c
                L_calc = 0

                if R**2 >= o_x**2:
                    o_y = math.sqrt(R**2 - o_x**2)
                    term = R**2 - (y_crack_bottom - o_y)**2
                    if term > 0:
                        x_intersect = o_x + math.sqrt(term)
                        theta_start = math.atan2(0 - o_y, 0 - o_x)
                        theta_end = math.atan2(y_crack_bottom - o_y, x_intersect - o_x)
                        thetas = np.linspace(theta_start, theta_end, 50)
                        arc_x = o_x + R * np.cos(thetas)
                        arc_y = o_y + R * np.sin(thetas)
                        poly_verts = list(zip(arc_x, arc_y))
                        if z_c > 0:
                            poly_verts.append((x_intersect, Y_crest))
                        poly_verts.append((X_crest, Y_crest))
                        poly_verts.append((0, 0))
                        soil_mass = patches.Polygon(poly_verts, closed=True, facecolor='none',
                                                    edgecolor='black', hatch='//', alpha=0.5)
                        ax_c.add_patch(soil_mass)
                        ax_c.plot(arc_x, arc_y, 'k-', linewidth=1.5)
                        if z_c > 0:
                            ax_c.plot([x_intersect, x_intersect], [y_crack_bottom, Y_crest],
                                      'r-', linewidth=2, label="Tension Crack")
                            if water_crack:
                                ax_c.fill_between([x_intersect - 0.5, x_intersect],
                                                  [y_crack_bottom, Y_crest], color='blue', alpha=0.3,
                                                  label="Water Pressure")
                                y_force = Y_crest - (2 * z_c / 3)
                                ax_c.arrow(x_intersect - 1.5, y_force, 1.5, 0,
                                           head_width=0.3, color='blue', width=0.05)
                                ax_c.text(x_intersect - 2.0, y_force, "Pw", color='blue', fontweight='bold')
                        L_calc = R * abs(theta_end - theta_start)
                    else:
                        st.error("Geometry Error: Circle does not intersect the tension crack/crest elevation.")

                    ax_c.plot(o_x, o_y, 'bo', label="O")
                    ax_c.plot([o_x, 0], [o_y, 0], 'b--', linewidth=1)
                    X_w = o_x + dist_d
                    Y_w = Y_crest / 2
                    ax_c.plot([o_x, o_x], [o_y, o_y + 2], 'k-', linewidth=0.5)
                    ax_c.plot([X_w, X_w], [Y_w, o_y + 2], 'k-', linewidth=0.5)
                    ax_c.arrow(X_w, Y_w, 0, -3, head_width=0.5, color='black', width=0.1)
                    ax_c.text(X_w + 0.5, Y_w - 3, "W", fontweight='bold')
                    ax_c.set_aspect('equal')
                    ax_c.set_xlim(-5, X_crest + 10)
                    ax_c.set_ylim(-2, o_y + 5)
                    ax_c.legend(loc="upper right", fontsize=8)
                    ax_c.axis('off')
                    st.pyplot(fig_c)
                    plt.close(fig_c)

                    # ── RESULTS ───────────────────────────────────
                    if calc_rot and L_calc > 0:
                        M_res = Cu * L_calc * R
                        M_drv_weight = W_calc * dist_d
                        P_w = 0.0
                        M_drv_water = 0.0
                        arm_water = 0.0
                        if water_crack and z_c > 0:
                            gamma_w = 9.81
                            P_w = 0.5 * gamma_w * (z_c ** 2)
                            y_force = Y_crest - (2 * z_c / 3)
                            arm_water = abs(y_force - o_y)
                            M_drv_water = P_w * arm_water
                        M_drv_total = M_drv_weight + M_drv_water

                        st.markdown("---")

                        if M_drv_total > 0:
                            FS_rot = M_res / M_drv_total
                            col_tok, fs_status = fs_colour(FS_rot)

                            with st.container(border=True):
                                st.markdown(f"## Factor of Safety: :{col_tok}[{FS_rot:.3f}] — :{col_tok}[{fs_status}]")

                                moment_df = pd.DataFrame({
                                    "Component": [
                                        "Arc Length (L)",
                                        "Resisting Moment (M_res = Cu·L·R)",
                                        "Driving Moment — Soil Weight",
                                        "Driving Moment — Water in Crack",
                                        "Total Driving Moment",
                                    ],
                                    "Value": [
                                        f"{L_calc:.2f} m",
                                        f"{M_res:.2f} kNm/m",
                                        f"{M_drv_weight:.2f} kNm/m",
                                        f"{M_drv_water:.2f} kNm/m",
                                        f"{M_drv_total:.2f} kNm/m",
                                    ],
                                })
                                glass_table(moment_df)

                                if Cu == 0:
                                    st.warning("⚠️ Cohesion Cu = 0 — resisting moment is zero. Slope is unconditionally unstable.")

                                write_text("subheader", "Detailed Calculation Log")

                                step_arc = (
                                    "### Step 1 — Arc Length\n\n"
                                    r"$$L = R \cdot \theta$$"
                                    "\n\n**Substitution:**\n\n"
                                    rf"$$L = {R:.2f} \times {abs(theta_end - theta_start):.4f} \ rad = {L_calc:.2f} \ m$$"
                                )
                                step_mres = (
                                    "### Step 2 — Resisting Moment\n\n"
                                    r"$$M_{res} = C_u \cdot L \cdot R$$"
                                    "\n\n**Substitution:**\n\n"
                                    rf"$$M_{{res}} = {Cu} \times {L_calc:.2f} \times {R:.2f} = {M_res:.2f} \ kNm/m$$"
                                )
                                step_mdrv = (
                                    "### Step 3 — Driving Moment (Soil Weight)\n\n"
                                    r"$$M_{drv,W} = W \cdot d$$"
                                    "\n\n**Substitution:**\n\n"
                                    rf"$$M_{{drv,W}} = {W_calc:.1f} \times {dist_d:.2f} = {M_drv_weight:.2f} \ kNm/m$$"
                                )
                                steps = [step_arc, step_mres, step_mdrv]

                                if water_crack and z_c > 0:
                                    step_water = (
                                        "### Step 4 — Driving Moment (Water in Tension Crack)\n\n"
                                        r"$$P_w = \frac{1}{2} \gamma_w z_c^2$$"
                                        "\n\n**Substitution:**\n\n"
                                        rf"$$P_w = 0.5 \times 9.81 \times {z_c:.2f}^2 = {P_w:.2f} \ kN/m$$"
                                        "\n\n"
                                        rf"$$M_{{drv,w}} = P_w \times arm = {P_w:.2f} \times {arm_water:.2f} = {M_drv_water:.2f} \ kNm/m$$"
                                    )
                                    steps.append(step_water)

                                step_fs = (
                                    f"### Step {len(steps)+1} — Factor of Safety\n\n"
                                    r"$$FS = \frac{M_{res}}{M_{drv}}$$"
                                    "\n\n**Substitution:**\n\n"
                                    rf"$$FS = \frac{{{M_res:.2f}}}{{{M_drv_total:.2f}}} = {FS_rot:.3f} \quad \rightarrow \quad \textbf{{{fs_status}}}$$"
                                )
                                steps.append(step_fs)

                                for step in steps:
                                    glass_box(step)
                        else:
                            st.info("Total driving moment is zero or negative. Slope is theoretically stable against this failure surface.")
                else:
                    st.error("Geometry Error: Radius (R) is too small to calculate center.")

        # ── B. METHOD OF SLICES ───────────────────────────────────
        else:
            col_s1, col_s2 = st.columns([0.4, 0.6], gap="medium")
            with col_s1:
                write_text("subheader", "Global Parameters")
                c_sl = st.number_input("Cohesion (c') [kPa]", 0.0, 100.0, 5.0, key="slice_c")
                phi_sl = st.number_input("Friction Angle (ϕ') [deg]", 0.0, 45.0, 30.0, key="slice_phi")
                default_data = pd.DataFrame([
                    {"Slice": 1, "b (m)": 2.0, "h (m)": 1.0, "W (kN/m)": 38.0,  "α (deg)": -5.0, "u/γ_w (m)": 0.0},
                    {"Slice": 2, "b (m)": 4.0, "h (m)": 3.2, "W (kN/m)": 243.0, "α (deg)": 12.0, "u/γ_w (m)": 0.5},
                    {"Slice": 3, "b (m)": 4.8, "h (m)": 5.2, "W (kN/m)": 474.0, "α (deg)": 28.0, "u/γ_w (m)": 1.2},
                    {"Slice": 4, "b (m)": 4.0, "h (m)": 6.0, "W (kN/m)": 456.0, "α (deg)": 45.0, "u/γ_w (m)": 0.8},
                    {"Slice": 5, "b (m)": 4.0, "h (m)": 3.5, "W (kN/m)": 266.0, "α (deg)": 60.0, "u/γ_w (m)": 0.0},
                ])
                st.markdown("**Input Slice Data**")
                edited_df = st.data_editor(default_data, num_rows="dynamic", key="slice_editor")
                calc_slices = st.button("Calculate FS", type="primary", key="btn_calc_slices")

            with col_s2:
                write_text("subheader", "Slice Representation")
                fig_slice, ax_slice = plt.subplots(figsize=(8, 6))
                ground_x = [-4, 0, 10, 18]
                ground_y = [0, 0, 8, 8]
                ax_slice.plot(ground_x, ground_y, 'k-', linewidth=2)
                o_x_sl, o_y_sl = 3.0, 12.0
                R_sl = math.sqrt(o_x_sl**2 + o_y_sl**2)
                arc_x_full = np.linspace(0, 14.5, 100)
                arc_y_full = o_y_sl - np.sqrt(R_sl**2 - (arc_x_full - o_x_sl)**2)
                ax_slice.plot(arc_x_full, arc_y_full, 'k-', linewidth=2)
                ax_slice.plot(o_x_sl, o_y_sl, 'ko')
                ax_slice.text(o_x_sl - 0.5, o_y_sl + 0.5, "O", fontweight='bold', fontsize=12)
                rad_angle = math.radians(285)
                rad_x = o_x_sl + R_sl * math.cos(rad_angle)
                rad_y = o_y_sl + R_sl * math.sin(rad_angle)
                ax_slice.annotate("", xy=(rad_x, rad_y), xytext=(o_x_sl, o_y_sl),
                                  arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
                ax_slice.text(o_x_sl + 1.5, o_y_sl - 4, "R", fontsize=12, fontweight='bold', rotation=-65)
                ax_slice.text(14, 11, "— NOT TO SCALE —", ha='center', fontsize=10, fontweight='bold')
                num_slices = len(edited_df)
                if num_slices > 0:
                    slice_edges = np.linspace(0, 14.5, num_slices + 1)
                    for i in range(num_slices):
                        x_left = slice_edges[i]
                        x_right = slice_edges[i + 1]
                        y_b_left = o_y_sl - math.sqrt(R_sl**2 - (x_left - o_x_sl)**2)
                        y_b_right = o_y_sl - math.sqrt(R_sl**2 - (x_right - o_x_sl)**2)
                        y_t_left = np.interp(x_left, ground_x, ground_y)
                        y_t_right = np.interp(x_right, ground_x, ground_y)
                        if i > 0:
                            ax_slice.plot([x_left, x_left], [y_b_left, y_t_left], 'k--', linewidth=1)
                        if i == num_slices - 1:
                            ax_slice.plot([x_right, x_right], [y_b_right, y_t_right], 'k--', linewidth=1)
                        mid_x = (x_left + x_right) / 2
                        mid_y = (max(y_b_left, y_b_right) + min(y_t_left, y_t_right)) / 2
                        y_t_mid = np.interp(mid_x, ground_x, ground_y)
                        row = edited_df.iloc[i]
                        circ = patches.Circle((mid_x, y_t_mid - 1.2), 0.5,
                                              edgecolor='black', facecolor='white', zorder=3)
                        ax_slice.add_patch(circ)
                        ax_slice.text(mid_x, y_t_mid - 1.2, str(int(row['Slice'])),
                                      ha='center', va='center', fontweight='bold', zorder=4)
                        ax_slice.text(mid_x, mid_y - 0.5,
                                      f"W={row['W (kN/m)']}\nα={row['α (deg)']}°",
                                      ha='center', va='center', fontsize=8)
                ax_slice.set_aspect('equal')
                ax_slice.set_xlim(-4, 20)
                ax_slice.set_ylim(-4, 14)
                ax_slice.axis('off')
                st.pyplot(fig_slice)
                plt.close(fig_slice)

                if calc_slices:
                    gamma_w = 9.81
                    sum_l = sum_W_cos = sum_W_sin = sum_u_l = 0.0
                    results_list = []
                    for _, row in edited_df.iterrows():
                        b = row["b (m)"]; W_s = row["W (kN/m)"]
                        alpha_rad = math.radians(row["α (deg)"])
                        u_head = row["u/γ_w (m)"]
                        l = b / math.cos(alpha_rad) if math.cos(alpha_rad) != 0 else 0.0
                        W_cos = W_s * math.cos(alpha_rad)
                        W_sin = W_s * math.sin(alpha_rad)
                        u_l = u_head * gamma_w * l
                        sum_l += l; sum_W_cos += W_cos; sum_W_sin += W_sin; sum_u_l += u_l
                        results_list.append({
                            "Slice No": int(row["Slice"]), "b (m)": b, "h (m)": row["h (m)"],
                            "W (kN/m)": W_s, "α (°)": row["α (deg)"],
                            "W·cos(α)": round(W_cos, 2), "W·sin(α)": round(W_sin, 2),
                            "u/γ_w (m)": u_head, "l (m)": round(l, 2), "u·l": round(u_l, 2)
                        })

                    sum_N_prime = sum_W_cos - sum_u_l
                    phi_rad = math.radians(phi_sl)
                    resisting = (c_sl * sum_l) + (math.tan(phi_rad) * sum_N_prime)
                    driving = sum_W_sin

                    st.markdown("---")

                    if driving != 0:
                        FS_sl = resisting / driving
                        col_tok, fs_status = fs_colour(FS_sl)

                        with st.container(border=True):
                            st.markdown(f"## Factor of Safety: :{col_tok}[{FS_sl:.3f}] — :{col_tok}[{fs_status}]")

                            res_df = pd.DataFrame(results_list)
                            glass_table(res_df)

                            sums_df = pd.DataFrame({
                                "Summation": [
                                    "Σl (m)", "Σ W·cos(α) (kN/m)", "Σ u·l (kN/m)",
                                    "Σ(W·cos α − u·l) = ΣN' (kN/m)",
                                    "Σ W·sin(α) — Driving (kN/m)",
                                    "Total Resisting Forces (kN/m)",
                                ],
                                "Value": [
                                    f"{sum_l:.2f}", f"{sum_W_cos:.2f}", f"{sum_u_l:.2f}",
                                    f"{sum_N_prime:.2f}", f"{sum_W_sin:.2f}", f"{resisting:.2f}",
                                ],
                            })
                            glass_table(sums_df)

                            write_text("subheader", "Detailed Calculation Log")

                            step_formula = (
                                "### Step 1 — Ordinary Method of Slices Formula\n\n"
                                r"$$F_s = \frac{c' \cdot \sum l + \tan\phi' \cdot \sum(W\cos\alpha - u \cdot l)}{\sum W\sin\alpha}$$"
                            )
                            step_resist = (
                                "### Step 2 — Resisting Forces\n\n"
                                rf"**Cohesion term:** $c' \cdot \Sigma l = {c_sl} \times {sum_l:.2f} = {c_sl * sum_l:.2f} \ kN/m$\n\n"
                                rf"**Friction term:** $\tan(\phi') \cdot \Sigma N' = \tan({phi_sl}°) \times {sum_N_prime:.2f} = {math.tan(phi_rad) * sum_N_prime:.2f} \ kN/m$\n\n"
                                rf"$$\text{{Total Resisting}} = {resisting:.2f} \ kN/m$$"
                            )
                            step_drive = (
                                "### Step 3 — Driving Forces\n\n"
                                rf"$$\sum W \sin\alpha = {driving:.2f} \ kN/m$$"
                            )
                            step_fs = (
                                "### Step 4 — Factor of Safety\n\n"
                                r"$$FS = \frac{\text{Resisting}}{\text{Driving}}$$"
                                "\n\n**Substitution:**\n\n"
                                rf"$$FS = \frac{{{resisting:.2f}}}{{{driving:.2f}}} = {FS_sl:.3f} \quad \rightarrow \quad \textbf{{{fs_status}}}$$"
                            )
                            for step in [step_formula, step_resist, step_drive, step_fs]:
                                glass_box(step)
                    else:
                        st.error("Driving forces sum to zero. Check input angles and weights.")

    # ---------------------------------------------------------
    # TAB 3: COMPOUND (BLOCK & WEDGE)
    # ---------------------------------------------------------
    with tab_comp:
        col_c1, col_c2 = st.columns([0.4, 0.6], gap="medium")

        with col_c1:
            write_text("subheader", "Inputs")
            st.markdown("**Geometry**")
            H_left = st.number_input("Passive Depth at Toe (H_p) [m]", 1.0, 50.0, 3.0, key="blk_Hp")
            H_right = st.number_input("Active Depth at Crest (H_a) [m]", 1.0, 50.0, 18.0, key="blk_Ha")
            L_block = st.number_input("Block Length (L) [m]", 1.0, 100.0, 22.5, key="blk_L")
            st.markdown("**1. Top Soil Properties (Wedges & Block)**")
            gamma_top = st.number_input("Unit Weight (γ) [kN/m³]", 10.0, 30.0, 20.0, key="blk_gamma")
            c_top = st.number_input("Cohesion (c') [kPa]", 0.0, 100.0, 0.0, key="blk_c_top")
            phi_top = st.number_input("Friction Angle (ϕ') [deg]", 0.0, 50.0, 36.0, key="blk_phi_top")
            st.markdown("**2. Weak Layer Properties (Base)**")
            c_base = st.number_input("Undrained Shear Strength / Cohesion (Cu) [kPa]", 0.0, 200.0, 24.0, key="blk_c_base")
            phi_base = st.number_input("Base Friction (ϕ_base) [deg]", 0.0, 45.0, 0.0, key="blk_phi_base")
            calc_blk = st.button("Calculate FS", type="primary", key="btn_calc_block")

        with col_c2:
            write_text("subheader", "Block & Wedge Diagram")
            fig_b, ax_b = plt.subplots(figsize=(8, 4))
            wedge_L_width = H_left
            wedge_R_width = H_right
            block_x_start = wedge_L_width
            block_x_end = wedge_L_width + L_block
            ground_x = [0, block_x_start, block_x_end, block_x_end + wedge_R_width]
            ground_y = [H_left, H_left, H_right, H_right]
            ax_b.plot(ground_x, ground_y, 'k-', linewidth=2, label="Ground Surface")
            ax_b.plot([0, block_x_end + wedge_R_width], [0, 0], 'b-', linewidth=3, label="Weak Layer")
            ax_b.plot([block_x_start, block_x_start], [0, H_left], 'k--', linewidth=1)
            ax_b.plot([block_x_end, block_x_end], [0, H_right], 'k--', linewidth=1)
            ax_b.fill_between([0, block_x_start], 0, H_left, color='#A5D6A7', alpha=0.5)
            ax_b.fill_between([block_x_start, block_x_end], 0,
                              np.interp([block_x_start, block_x_end], ground_x, ground_y),
                              color='lightgrey', hatch='//', alpha=0.5)
            ax_b.fill_between([block_x_end, block_x_end + wedge_R_width], 0, H_right,
                              color='#FFCCBC', alpha=0.5)
            ax_b.text(block_x_start / 2, H_left / 2, "Passive\nZone", ha='center', fontsize=9)
            ax_b.text((block_x_start + block_x_end) / 2, (H_left + H_right) / 3,
                      "Central Block", ha='center', fontweight='bold')
            ax_b.text(block_x_end + wedge_R_width / 2, H_right / 2, "Active\nZone", ha='center', fontsize=9)
            ax_b.arrow(block_x_end + 1.5, H_right / 3, -1.5, 0, head_width=0.5, color='red', width=0.1)
            ax_b.text(block_x_end + 1.6, H_right / 3, "Pa", color='red', fontweight='bold', va='center')
            ax_b.arrow(block_x_start - 1.5, H_left / 3, 1.5, 0, head_width=0.5, color='green', width=0.1)
            ax_b.text(block_x_start - 2.5, H_left / 3, "Pp", color='green', fontweight='bold', va='center')
            ax_b.text((block_x_start + block_x_end) / 2, -1.5, r"$\tau_f$ (Shear Resistance)", ha='center')
            ax_b.arrow((block_x_start + block_x_end) / 2, -0.5, -3, 0, head_width=0.3, color='black')
            ax_b.annotate(f"L={L_block}m", xy=(block_x_start, -0.5), xytext=(block_x_end, -0.5),
                          arrowprops=dict(arrowstyle='<->'))
            ax_b.set_xlim(-2, block_x_end + wedge_R_width + 2)
            ax_b.set_ylim(-3, H_right + 3)
            ax_b.axis('off')
            st.pyplot(fig_b)
            plt.close(fig_b)

            if calc_blk:
                phi_top_rad = math.radians(phi_top)
                Ka = (1 - math.sin(phi_top_rad)) / (1 + math.sin(phi_top_rad))
                Kp = (1 + math.sin(phi_top_rad)) / (1 - math.sin(phi_top_rad))
                Pa_raw = (0.5 * gamma_top * H_right**2 * Ka) - (2 * c_top * H_right * math.sqrt(Ka))
                Pa = max(Pa_raw, 0.0)
                Pp = (0.5 * gamma_top * H_left**2 * Kp) + (2 * c_top * H_left * math.sqrt(Kp))
                W_block = ((H_left + H_right) / 2.0) * L_block * gamma_top
                tau_f = (c_base * L_block) + (W_block * math.tan(math.radians(phi_base)))
                total_resisting = Pp + tau_f

                st.markdown("---")

                if Pa > 0:
                    FS_blk = total_resisting / Pa
                    col_tok, fs_status = fs_colour(FS_blk)

                    with st.container(border=True):
                        st.markdown(f"## Factor of Safety: :{col_tok}[{FS_blk:.2f}] — :{col_tok}[{fs_status}]")

                        forces_df = pd.DataFrame({
                            "Force Component": [
                                "Earth Pressure Coeff. Ka",
                                "Active Thrust Pa (Driving)",
                                "Earth Pressure Coeff. Kp",
                                "Passive Resistance Pp",
                                "Block Weight W",
                                "Base Shear Resistance τf",
                                "Total Resisting (Pp + τf)",
                            ],
                            "Value": [
                                f"{Ka:.3f}",
                                f"{Pa:.1f} kN/m",
                                f"{Kp:.3f}",
                                f"{Pp:.1f} kN/m",
                                f"{W_block:.1f} kN/m",
                                f"{tau_f:.1f} kN/m",
                                f"{total_resisting:.1f} kN/m",
                            ],
                        })
                        glass_table(forces_df)

                        write_text("subheader", "Detailed Calculation Log")

                        step_ka = (
                            "### Step 1 — Rankine Earth Pressure Coefficients\n\n"
                            r"$$K_A = \frac{1-\sin\phi'}{1+\sin\phi'} \qquad K_P = \frac{1+\sin\phi'}{1-\sin\phi'}$$"
                            "\n\n**Substitution:**\n\n"
                            rf"$$K_A = \frac{{1-\sin({phi_top}°)}}{{1+\sin({phi_top}°)}} = {Ka:.3f}$$"
                            "\n\n"
                            rf"$$K_P = \frac{{1+\sin({phi_top}°)}}{{1-\sin({phi_top}°)}} = {Kp:.3f}$$"
                        )
                        step_pa = (
                            "### Step 2 — Active Thrust (Driving Force)\n\n"
                            r"$$P_A = \frac{1}{2}\gamma H_a^2 K_A - 2c' H_a \sqrt{K_A}$$"
                            "\n\n**Substitution:**\n\n"
                            rf"$$P_A = 0.5 \times {gamma_top} \times {H_right}^2 \times {Ka:.3f} - 2 \times {c_top} \times {H_right} \times \sqrt{{{Ka:.3f}}}$$"
                            "\n\n"
                            rf"$$P_A = {Pa_raw:.1f} \rightarrow P_A = {Pa:.1f} \ kN/m \ (\text{{min 0}})$$"
                        )
                        step_pp = (
                            "### Step 3 — Passive Resistance\n\n"
                            r"$$P_P = \frac{1}{2}\gamma H_p^2 K_P + 2c' H_p \sqrt{K_P}$$"
                            "\n\n**Substitution:**\n\n"
                            rf"$$P_P = 0.5 \times {gamma_top} \times {H_left}^2 \times {Kp:.3f} + 2 \times {c_top} \times {H_left} \times \sqrt{{{Kp:.3f}}}$$"
                            "\n\n"
                            rf"$$P_P = {Pp:.1f} \ kN/m$$"
                        )
                        step_tau = (
                            "### Step 4 — Base Shear Resistance\n\n"
                            r"$$\tau_f = C_u \cdot L + W \cdot \tan(\phi_{base})$$"
                            "\n\n**Block weight:**\n\n"
                            rf"$$W = \frac{{H_p + H_a}}{{2}} \times L \times \gamma = \frac{{{H_left}+{H_right}}}{{2}} \times {L_block} \times {gamma_top} = {W_block:.1f} \ kN/m$$"
                            "\n\n**Substitution:**\n\n"
                            rf"$$\tau_f = {c_base} \times {L_block} + {W_block:.1f} \times \tan({phi_base}°) = {tau_f:.1f} \ kN/m$$"
                        )
                        step_fs = (
                            "### Step 5 — Factor of Safety\n\n"
                            r"$$FS = \frac{P_P + \tau_f}{P_A}$$"
                            "\n\n**Substitution:**\n\n"
                            rf"$$FS = \frac{{{Pp:.1f} + {tau_f:.1f}}}{{{Pa:.1f}}} = \frac{{{total_resisting:.1f}}}{{{Pa:.1f}}} = {FS_blk:.2f} \quad \rightarrow \quad \textbf{{{fs_status}}}$$"
                        )
                        for step in [step_ka, step_pa, step_pp, step_tau, step_fs]:
                            glass_box(step)
                else:
                    st.error("Active Thrust ($P_a$) is zero or negative. No driving force to calculate FS.")


if __name__ == "__main__":
    app()
