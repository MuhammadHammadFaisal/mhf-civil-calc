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

        c1, c2, c3 = st.columns([0.40, 0.40, 0.70], gap="large")

        # -----------------------------
        # Example Scenarios (optional)
        # -----------------------------
        with st.expander("Example Scenarios (optional)"):
            preset = st.selectbox(
                "Auto-fill typical values",
                ["Custom", "Dry Sand (c'=0, m=0)", "Dry Soil (c'>0, m=0)", "Saturated (m=1)"],
                index=0,
                help="This only changes input values. It does NOT change the calculation method.",
                key="inf_preset"
            )

        # Initialize session defaults
        if "inf_initialized" not in st.session_state:
            st.session_state.inf_initialized = True
            st.session_state.inf_beta = 25.0
            st.session_state.inf_z = 5.0
            st.session_state.inf_c = 5.0
            st.session_state.inf_phi = 30.0
            st.session_state.inf_gdry = 18.0
            st.session_state.inf_gsat = 20.0
            st.session_state.inf_m = 0.0
            st.session_state.inf_last_preset = "Custom"

        # Apply preset only when changed
        if preset != st.session_state.inf_last_preset:
            if preset == "Dry Sand (c'=0, m=0)":
                st.session_state.inf_c = 0.0
                st.session_state.inf_phi = 32.0
                st.session_state.inf_m = 0.0
            elif preset == "Dry Soil (c'>0, m=0)":
                st.session_state.inf_c = 8.0
                st.session_state.inf_phi = 28.0
                st.session_state.inf_m = 0.0
            elif preset == "Saturated (m=1)":
                st.session_state.inf_c = 5.0
                st.session_state.inf_phi = 30.0
                st.session_state.inf_m = 1.0

            st.session_state.inf_last_preset = preset

        # -----------------------------
        # INPUTS
        # -----------------------------
        with c1:
            write_text("subheader", "1. Geometry")

            beta = st.number_input(
                "Slope Angle (β) [deg]",
                min_value=0.0,
                max_value=60.0,
                value=float(st.session_state.inf_beta),
                key="inf_beta"
            )

            z = st.number_input(
                "Depth Normal to Slope (z) [m]",
                min_value=0.5,
                max_value=20.0,
                value=float(st.session_state.inf_z),
                key="inf_z"
            )

            write_text("caption", "Failure plane is assumed parallel to slope surface.")

        with c2:
            write_text("subheader", "2. Soil Properties")

            c_prime = st.number_input(
                "Cohesion (c') [kPa]",
                0.0, 100.0,
                float(st.session_state.inf_c),
                key="inf_c"
            )

            phi_prime = st.number_input(
                "Friction Angle (ϕ') [deg]",
                0.0, 45.0,
                float(st.session_state.inf_phi),
                key="inf_phi"
            )

            gamma_dry = st.number_input(
                "Dry Unit Weight (γ_dry) [kN/m³]",
                15.0, 25.0,
                float(st.session_state.inf_gdry),
                key="inf_gdry"
            )

            gamma_sat = st.number_input(
                "Saturated Unit Weight (γ_sat) [kN/m³]",
                15.0, 25.0,
                float(st.session_state.inf_gsat),
                key="inf_gsat"
            )

            m_ratio = st.slider(
                "Water Table Ratio (m = z_w / z)",
                0.0, 1.0,
                float(st.session_state.inf_m),
                key="inf_m"
            )

            calc_t = st.button("Calculate Factor of Safety", type="primary")

        # -----------------------------
        # DIAGRAM (REPLACE THIS WHOLE BLOCK)
        # -----------------------------
        with c3:
            write_text("subheader", "Slope Diagram")
        
            fig_t, ax_t = plt.subplots(figsize=(7, 5))
        
            # Main slope line
            x = np.linspace(0, 10, 400)
            beta_r = math.radians(beta)
            y_surf = x * math.tan(beta_r)
        
            # Unit normal pointing into the slope (perpendicular to surface)
            nx = math.sin(beta_r)
            ny = -math.cos(beta_r)
        
            # Failure plane at depth z (normal to slope)
            x_fail = x + nx * z
            y_fail = y_surf + ny * z
        
            # Plot ground + failure plane
            ax_t.plot(x, y_surf, 'k-', linewidth=3.0, label="Ground Surface")
            ax_t.plot(x_fail, y_fail, 'r--', linewidth=3.0, label="Failure Plane")
        
            # Shade soil mass between surface and failure plane
            ax_t.fill_between(x, y_surf, y_fail, where=(y_surf >= y_fail), alpha=0.22)
        
            # Water table line at z_w = m*z (parallel to slope)
            z_w = m_ratio * z
            if z_w > 0:
                x_wt = x + nx * z_w
                y_wt = y_surf + ny * z_w
                ax_t.plot(x_wt, y_wt, 'b--', linewidth=2.5, label="Water Table")
        
            # -----------------------------
            # 1 m slice (visual)
            # -----------------------------
            slice_x1 = 3.0
            slice_x2 = 4.0  # 1 m width
        
            y_surf_x1 = np.interp(slice_x1, x, y_surf)
            y_fail_x1 = np.interp(slice_x1, x_fail, y_fail)
            y_surf_x2 = np.interp(slice_x2, x, y_surf)
            y_fail_x2 = np.interp(slice_x2, x_fail, y_fail)
        
            ax_t.plot([slice_x1, slice_x1], [y_fail_x1, y_surf_x1], 'k-', linewidth=1.8)
            ax_t.plot([slice_x2, slice_x2], [y_fail_x2, y_surf_x2], 'k-', linewidth=1.8)
        
            ax_t.text((slice_x1 + slice_x2) / 2, max(y_surf_x1, y_surf_x2) + 0.4, "1 m",
                      ha="center", fontweight="bold")
        
            # -----------------------------
            # Forces on slice (W, Wsinβ, Wcosβ)
            # -----------------------------
            mid_x = (slice_x1 + slice_x2) / 2
            mid_y = (y_surf_x1 + y_surf_x2) / 2 - 0.8
        
            # Weight W (vertical down)
            ax_t.arrow(mid_x, mid_y, 0, -1.4,
                       head_width=0.20, head_length=0.25,
                       color='black', width=0.04, length_includes_head=True)
            ax_t.text(mid_x + 0.25, mid_y - 1.5, "W", fontweight="bold")
        
            # Unit vectors along plane and normal to plane
            tx, ty = math.cos(beta_r), math.sin(beta_r)      # along slope
            nx_p, ny_p = -math.sin(beta_r), math.cos(beta_r) # outward normal (for display)
        
            # Component arrows (purely illustrative directions)
            comp_len = 1.2
        
            # W sinβ (downslope, along plane)
            ax_t.arrow(mid_x, mid_y - 0.5, tx * comp_len, ty * comp_len,
                       head_width=0.18, head_length=0.22,
                       color='red', width=0.035, length_includes_head=True)
            ax_t.text(mid_x + tx * (comp_len + 0.2), mid_y - 0.5 + ty * (comp_len + 0.2),
                      r"$W\sin\beta$", color="red", fontweight="bold")
        
            # W cosβ (normal to plane)
            ax_t.arrow(mid_x, mid_y - 0.5, nx_p * comp_len, ny_p * comp_len,
                       head_width=0.18, head_length=0.22,
                       color='blue', width=0.035, length_includes_head=True)
            ax_t.text(mid_x + nx_p * (comp_len + 0.2), mid_y - 0.5 + ny_p * (comp_len + 0.2),
                      r"$W\cos\beta$", color="blue", fontweight="bold")
        
            # -----------------------------
            # Stress labels on failure plane
            # -----------------------------
            # Place labels near left slice edge on the failure plane
            lab_x = slice_x1 + 0.2
            lab_y = np.interp(lab_x, x_fail, y_fail)
        
            ax_t.text(lab_x + 0.4, lab_y + 0.15, r"$\tau$", color="red", fontweight="bold")
            ax_t.text(lab_x - 0.2, lab_y + 0.50, r"$\sigma$", color="blue", fontweight="bold")
        
            # -----------------------------
            # Show beta angle at toe (visual only)
            # -----------------------------
            # Small arc hint
            ax_t.text(0.35, 0.15, r"$\beta$", fontsize=13, fontweight="bold")
        
            # Final formatting
            ax_t.set_aspect('equal')
            ax_t.axis('off')
            ax_t.legend(loc="upper left", fontsize=9)
        
            st.pyplot(fig_t)
            plt.close(fig_t)
        # -----------------------------
        # CALCULATION + RESULTS
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
                "status_text": status_text
            }

        if st.session_state.inf_last_result is not None:
            r = st.session_state.inf_last_result

            st.markdown("---")

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

            write_text("subheader", "Detailed Calculation Log")

            beta_r = math.radians(beta)
            phi_r = math.radians(phi_prime)
            z_w = m_ratio * z
            tan_phi = math.tan(phi_r)

            step1 = (
                f"### Step 1 — Total Normal Stress\n\n"
                rf"$$\sigma = [{gamma_dry}(1-{m_ratio}) + {gamma_sat}({m_ratio})] \cdot {z} \cdot \cos^2({beta}°) = {r['sigma']:.2f} \ kPa$$"
            )

            step2 = (
                f"### Step 2 — Pore Water Pressure\n\n"
                rf"$$u = 9.81 \cdot {m_ratio} \cdot {z} \cdot \cos^2({beta}°) = {r['u']:.2f} \ kPa$$"
            )

            step3 = (
                f"### Step 3 — Effective Stress\n\n"
                rf"$$\sigma' = {r['sigma']:.2f} - {r['u']:.2f} = {r['sigma_eff']:.2f} \ kPa$$"
            )

            step4 = (
                f"### Step 4 — Shear Stress\n\n"
                rf"$$\tau = [{gamma_dry}(1-{m_ratio}) + {gamma_sat}({m_ratio})] \cdot {z} \cdot \sin({beta}°)\cos({beta}°) = {r['tau']:.2f} \ kPa$$"
            )

            step5 = (
                f"### Step 5 — Shear Strength\n\n"
                rf"$$\tau_f = {c_prime} + {r['sigma_eff']:.2f} \cdot \tan({phi_prime}°) = {r['tau_f']:.2f} \ kPa$$"
            )

            step6 = (
                f"### Step 6 — Factor of Safety\n\n"
                rf"$$FS = \frac{{{r['tau_f']:.2f}}}{{{r['tau']:.2f}}} = {r['FS']:.3f}$$"
            )

            for step in [step1, step2, step3, step4, step5, step6]:
                glass_box(step)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # TAB 2: ROTATIONAL (CIRCULAR)
    # ---------------------------------------------------------
    with tab_rot:
        c1, c2, c3 = st.columns([0.40, 0.40, 0.70], gap="large")
    
        # -----------------------------
        # Method Selector (Top)
        # -----------------------------
        with st.expander("Calculation Method (choose one)", expanded=True):
            method = st.radio(
                "",
                ["A. Mass Procedure (Undrained / ϕ=0)", "B. Method of Slices"],
                horizontal=True,
                key="rot_method_select",
                label_visibility="collapsed",
            )
    
        # =========================================================
        # A) MASS PROCEDURE (UI like Tab 1)
        # =========================================================
        if "Mass Procedure" in method:
    
            # -----------------------------
            # Optional Preset (UI only)
            # -----------------------------
            with st.expander("Example Scenarios (optional)"):
                preset_mass = st.selectbox(
                    "Auto-fill typical values",
                    ["Custom", "Typical Clay Slope", "High Cu (Stiffer Clay)", "With Water Crack (demo)"],
                    index=0,
                    help="This only changes input values. It does NOT change the calculation method.",
                    key="mass_preset",
                )
    
            # Initialize session defaults
            if "mass_initialized" not in st.session_state:
                st.session_state.mass_initialized = True
                st.session_state.mass_H = 8.5
                st.session_state.mass_beta = 45.0
                st.session_state.mass_R = 12.1
                st.session_state.mass_ox = -2.0
                st.session_state.mass_d = 4.5
                st.session_state.mass_gamma = 19.0
                st.session_state.mass_cu = 65.0
                st.session_state.mass_area = 70.0
                st.session_state.mass_water = False
                st.session_state.mass_last_preset = "Custom"
    
            # Apply preset only when changed
            if preset_mass != st.session_state.mass_last_preset:
                if preset_mass == "Typical Clay Slope":
                    st.session_state.mass_gamma = 19.0
                    st.session_state.mass_cu = 60.0
                    st.session_state.mass_area = 70.0
                    st.session_state.mass_water = False
    
                elif preset_mass == "High Cu (Stiffer Clay)":
                    st.session_state.mass_gamma = 19.0
                    st.session_state.mass_cu = 90.0
                    st.session_state.mass_area = 70.0
                    st.session_state.mass_water = False
    
                elif preset_mass == "With Water Crack (demo)":
                    st.session_state.mass_gamma = 19.0
                    st.session_state.mass_cu = 55.0
                    st.session_state.mass_area = 70.0
                    st.session_state.mass_water = True
    
                st.session_state.mass_last_preset = preset_mass
    
            # -----------------------------
            # INPUTS (2 columns like Tab 1)
            # -----------------------------
            with c1:
                write_text("subheader", "1. Geometry")
    
                H_slope = st.number_input(
                    "Slope Height (H) [m]",
                    min_value=1.0, max_value=50.0,
                    value=float(st.session_state.mass_H),
                    key="mass_H",
                )
    
                beta_slope = st.number_input(
                    "Slope Angle [deg]",
                    min_value=0.0, max_value=90.0,
                    value=float(st.session_state.mass_beta),
                    key="mass_beta",
                )
    
                write_text("caption", "This Mass Procedure assumes toe failure and uses moment equilibrium.")
    
                with st.expander("Assumptions used in this model"):
                    st.markdown(
                        "- Circular slip surface intersects the **toe at (0,0)** (forced).\n"
                        "- Undrained analysis (ϕ = 0), resisting is **Cu** along arc.\n"
                        "- Driving is from **weight moment** (+ optional water in tension crack).\n"
                        "- Results are per **meter out of plane**."
                    )
    
            with c2:
                write_text("subheader", "2. Failure Circle & Soil")
    
                R = st.number_input(
                    "Radius (R) [m]",
                    min_value=5.0, max_value=50.0,
                    value=float(st.session_state.mass_R),
                    key="mass_R",
                )
    
                o_x = st.number_input(
                    "Center X-coord (o_x) [m]",
                    min_value=-20.0, max_value=20.0,
                    value=float(st.session_state.mass_ox),
                    key="mass_ox",
                )
    
                dist_d = st.number_input(
                    "Moment Arm (d) [m]",
                    min_value=0.0, max_value=20.0,
                    value=float(st.session_state.mass_d),
                    help="Horizontal distance from Center O to centroid (user input).",
                    key="mass_d",
                )
    
                gamma_clay = st.number_input(
                    "Unit Weight (γ) [kN/m³]",
                    min_value=10.0, max_value=25.0,
                    value=float(st.session_state.mass_gamma),
                    key="mass_gamma",
                )
    
                Cu = st.number_input(
                    "Undrained Shear Strength (Cu) [kPa]",
                    min_value=0.0, max_value=200.0,
                    value=float(st.session_state.mass_cu),
                    key="mass_cu",
                )
    
                st.markdown("**Weight (user approximation)**")
                area_approx = st.number_input(
                    "Area of Sliding Mass [m²]",
                    min_value=1.0, max_value=500.0,
                    value=float(st.session_state.mass_area),
                    key="mass_area",
                )
                W_calc = area_approx * gamma_clay
                st.write(f"Weight (W) = **{W_calc:.1f} kN/m**")
    
                # Tension crack option (UI exactly as your existing logic)
                z_c = 0.0
                if Cu > 0 and gamma_clay > 0:
                    z_c = (2 * Cu) / gamma_clay
                z_c = min(z_c, H_slope)
    
                if z_c > 0:
                    st.markdown("**Tension Crack**")
                    st.info(f"Tension Crack Depth ($z_c$) = **{z_c:.2f} m**")
                    water_crack = st.checkbox(
                        "Crack filled with water (Adds driving force)",
                        value=bool(st.session_state.mass_water),
                        key="mass_water",
                    )
                else:
                    water_crack = False
    
                calc_rot = st.button("Calculate Factor of Safety", type="primary", key="btn_calc_rot_mass")
                write_text("caption", "Press Calculate to freeze results while you explore inputs.")
    
            # -----------------------------
            # DIAGRAM (right column)
            # -----------------------------
            with c3:
                write_text("subheader", "Failure Diagram")
    
                fig_c, ax_c = plt.subplots(figsize=(8, 6))
    
                X_crest = H_slope / math.tan(math.radians(beta_slope)) if beta_slope > 0 else 10
                Y_crest = H_slope
    
                ground_x = [-10, 0, X_crest, X_crest + 10]
                ground_y = [0, 0, Y_crest, Y_crest]
                ax_c.plot(ground_x, ground_y, 'k-', linewidth=2.5, label="Ground Surface")
    
                y_crack_bottom = Y_crest - z_c
                L_calc = 0.0
                theta_start = None
                theta_end = None
                o_y = None
    
                if R**2 >= o_x**2:
                    o_y = math.sqrt(R**2 - o_x**2)
    
                    term = R**2 - (y_crack_bottom - o_y)**2
                    if term > 0:
                        x_intersect = o_x + math.sqrt(term)
    
                        theta_start = math.atan2(0 - o_y, 0 - o_x)
                        theta_end = math.atan2(y_crack_bottom - o_y, x_intersect - o_x)
    
                        thetas = np.linspace(theta_start, theta_end, 60)
                        arc_x = o_x + R * np.cos(thetas)
                        arc_y = o_y + R * np.sin(thetas)
    
                        poly_verts = list(zip(arc_x, arc_y))
                        if z_c > 0:
                            poly_verts.append((x_intersect, Y_crest))
                        poly_verts.append((X_crest, Y_crest))
                        poly_verts.append((0, 0))
    
                        soil_mass = patches.Polygon(
                            poly_verts, closed=True,
                            facecolor='none', edgecolor='black',
                            hatch='//', alpha=0.5
                        )
                        ax_c.add_patch(soil_mass)
                        ax_c.plot(arc_x, arc_y, 'k-', linewidth=1.6, label="Slip Surface")
    
                        if z_c > 0:
                            ax_c.plot([x_intersect, x_intersect], [y_crack_bottom, Y_crest],
                                      'r-', linewidth=2.0, label="Tension Crack")
    
                            if water_crack:
                                ax_c.fill_between(
                                    [x_intersect - 0.5, x_intersect],
                                    [y_crack_bottom, Y_crest],
                                    color='blue', alpha=0.25,
                                    label="Water Pressure"
                                )
                                y_force = Y_crest - (2 * z_c / 3)
                                ax_c.arrow(x_intersect - 1.5, y_force, 1.5, 0,
                                           head_width=0.3, color='blue', width=0.05)
                                ax_c.text(x_intersect - 2.0, y_force, "Pw",
                                          color='blue', fontweight='bold')
    
                        L_calc = R * abs(theta_end - theta_start)
    
                    else:
                        ax_c.text(0.5, 0.5, "Geometry error:\nCircle does not intersect crack/crest.",
                                  transform=ax_c.transAxes, ha="center", va="center", fontweight="bold")
    
                    ax_c.plot(o_x, o_y, 'bo', label="O")
                    ax_c.plot([o_x, 0], [o_y, 0], 'b--', linewidth=1.0)
    
                    # Weight arrow
                    X_w = o_x + dist_d
                    Y_w = Y_crest / 2
                    ax_c.arrow(X_w, Y_w, 0, -3,
                               head_width=0.5, color='black', width=0.1)
                    ax_c.text(X_w + 0.5, Y_w - 3, "W", fontweight='bold')
    
                    ax_c.set_aspect('equal')
                    ax_c.set_xlim(-5, X_crest + 10)
                    ax_c.set_ylim(-2, o_y + 5)
                    ax_c.legend(loc="upper right", fontsize=8)
                    ax_c.axis('off')
    
                else:
                    ax_c.text(0.5, 0.5, "Geometry error:\nR is too small for this o_x.",
                              transform=ax_c.transAxes, ha="center", va="center", fontweight="bold")
                    ax_c.axis('off')
    
                st.pyplot(fig_c)
                plt.close(fig_c)
    
            # -----------------------------
            # CALCULATION + PERSISTENT RESULTS
            # -----------------------------
            if "mass_last_result" not in st.session_state:
                st.session_state.mass_last_result = None
    
            if calc_rot and L_calc > 0 and o_y is not None:
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
    
                if M_drv_total > 0:
                    FS_rot = M_res / M_drv_total
                else:
                    FS_rot = 999.0
    
                level_class, status_text = fs_theme_class(FS_rot)
    
                st.session_state.mass_last_result = {
                    "FS": FS_rot,
                    "status_text": status_text,
                    "level_class": level_class,
                    "L": L_calc,
                    "M_res": M_res,
                    "M_drv_weight": M_drv_weight,
                    "M_drv_water": M_drv_water,
                    "M_drv_total": M_drv_total,
                    "P_w": P_w,
                    "arm_water": arm_water,
                    "z_c": z_c,
                }
    
            if st.session_state.mass_last_result is not None:
                r = st.session_state.mass_last_result
    
                st.markdown("---")
    
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
    
                moment_df = pd.DataFrame({
                    "Component": [
                        "Arc Length (L)",
                        "Resisting Moment (M_res = Cu·L·R)",
                        "Driving Moment — Soil Weight (W·d)",
                        "Driving Moment — Water in Crack",
                        "Total Driving Moment",
                    ],
                    "Value": [
                        f"{r['L']:.2f} m",
                        f"{r['M_res']:.2f} kNm/m",
                        f"{r['M_drv_weight']:.2f} kNm/m",
                        f"{r['M_drv_water']:.2f} kNm/m",
                        f"{r['M_drv_total']:.2f} kNm/m",
                    ],
                })
                glass_table(moment_df)
    
                if Cu == 0:
                    st.warning("⚠️ Cohesion Cu = 0 — resisting moment is zero. Slope is unconditionally unstable.")
    
                write_text("subheader", "Detailed Calculation Log")
    
                # Step 1: arc length
                step1 = (
                    "### Step 1 — Arc Length\n\n"
                    r"$$L = R \cdot \theta$$"
                    "\n\n**Substitution:**\n\n"
                    rf"$$L = {R:.2f} \times {abs(theta_end - theta_start):.4f} = {r['L']:.2f}\ \text{{m}}$$"
                )
    
                # Step 2: resisting moment
                step2 = (
                    "### Step 2 — Resisting Moment\n\n"
                    r"$$M_{res} = C_u \cdot L \cdot R$$"
                    "\n\n**Substitution:**\n\n"
                    rf"$$M_{{res}} = {Cu:.2f} \times {r['L']:.2f} \times {R:.2f} = {r['M_res']:.2f}\ \text{{kNm/m}}$$"
                )
    
                # Step 3: driving moment (weight)
                step3 = (
                    "### Step 3 — Driving Moment (Soil Weight)\n\n"
                    r"$$M_{drv,W} = W \cdot d$$"
                    "\n\n**Substitution:**\n\n"
                    rf"$$M_{{drv,W}} = {W_calc:.2f} \times {dist_d:.2f} = {r['M_drv_weight']:.2f}\ \text{{kNm/m}}$$"
                )
    
                steps = [step1, step2, step3]
    
                # Step 4: water crack (optional)
                if water_crack and r["z_c"] > 0:
                    step4 = (
                        "### Step 4 — Water in Tension Crack (Driving)\n\n"
                        r"$$P_w = \frac{1}{2}\gamma_w z_c^2$$"
                        "\n\n**Substitution:**\n\n"
                        rf"$$P_w = 0.5 \times 9.81 \times {r['z_c']:.2f}^2 = {r['P_w']:.2f}\ \text{{kN/m}}$$"
                        "\n\n"
                        rf"$$M_{{drv,w}} = P_w \times arm = {r['P_w']:.2f} \times {r['arm_water']:.2f} = {r['M_drv_water']:.2f}\ \text{{kNm/m}}$$"
                    )
                    steps.append(step4)
    
                # Final step: FS (always last)
                step_last = (
                    f"### Step {len(steps) + 1} — Factor of Safety\n\n"
                    r"$$FS = \frac{M_{res}}{M_{drv}}$$"
                    "\n\n**Substitution:**\n\n"
                    rf"$$FS = \frac{{{r['M_res']:.2f}}}{{{r['M_drv_total']:.2f}}} = {r['FS']:.3f}$$"
                )
                steps.append(step_last)
    
                for s in steps:
                    glass_box(s)
    
        # =========================================================
        # B) METHOD OF SLICES (UI like Tab 1)
        # =========================================================
        else:
            # Optional presets (UI only)
            with st.expander("Example Scenarios (optional)"):
                preset_slices = st.selectbox(
                    "Auto-fill typical values",
                    ["Custom", "Dry (u=0 everywhere)", "Moderate Pore Pressure", "Higher Friction (φ'=35°)"],
                    index=0,
                    help="This only changes input values / table defaults. It does NOT change the calculation method.",
                    key="slice_preset",
                )
    
            if "slice_initialized" not in st.session_state:
                st.session_state.slice_initialized = True
                st.session_state.slice_phi = 30.0
                st.session_state.slice_c = 5.0
                st.session_state.slice_last_result = None
                st.session_state.slice_last_preset = "Custom"
    
            # Apply preset only when changed (only updates phi/c; table can be edited by user anyway)
            if preset_slices != st.session_state.slice_last_preset:
                if preset_slices == "Dry (u=0 everywhere)":
                    st.session_state.slice_phi = 30.0
                    st.session_state.slice_c = 5.0
    
                elif preset_slices == "Moderate Pore Pressure":
                    st.session_state.slice_phi = 30.0
                    st.session_state.slice_c = 5.0
    
                elif preset_slices == "Higher Friction (φ'=35°)":
                    st.session_state.slice_phi = 35.0
                    st.session_state.slice_c = 5.0
    
                st.session_state.slice_last_preset = preset_slices
    
            # Inputs
            with c1:
                write_text("subheader", "1. Global Parameters")
    
                c_sl = st.number_input(
                    "Cohesion (c') [kPa]",
                    min_value=0.0, max_value=100.0,
                    value=float(st.session_state.slice_c),
                    key="slice_c",
                )
    
                phi_sl = st.number_input(
                    "Friction Angle (ϕ') [deg]",
                    min_value=0.0, max_value=45.0,
                    value=float(st.session_state.slice_phi),
                    key="slice_phi",
                )
    
                write_text("caption", "Ordinary Method of Slices (force equilibrium form).")
    
            # Table editor
            with c2:
                write_text("subheader", "2. Input Slice Data")
    
                default_data = pd.DataFrame([
                    {"Slice": 1, "b (m)": 2.0, "h (m)": 1.0, "W (kN/m)": 38.0,  "α (deg)": -5.0, "u/γ_w (m)": 0.0},
                    {"Slice": 2, "b (m)": 4.0, "h (m)": 3.2, "W (kN/m)": 243.0, "α (deg)": 12.0, "u/γ_w (m)": 0.5},
                    {"Slice": 3, "b (m)": 4.8, "h (m)": 5.2, "W (kN/m)": 474.0, "α (deg)": 28.0, "u/γ_w (m)": 1.2},
                    {"Slice": 4, "b (m)": 4.0, "h (m)": 6.0, "W (kN/m)": 456.0, "α (deg)": 45.0, "u/γ_w (m)": 0.8},
                    {"Slice": 5, "b (m)": 4.0, "h (m)": 3.5, "W (kN/m)": 266.0, "α (deg)": 60.0, "u/γ_w (m)": 0.0},
                ])
    
                # If preset says "dry", prefill u with 0 (still editable)
                if preset_slices == "Dry (u=0 everywhere)":
                    default_data["u/γ_w (m)"] = 0.0
    
                edited_df = st.data_editor(default_data, num_rows="dynamic", key="slice_editor")
    
                calc_slices = st.button("Calculate Factor of Safety", type="primary", key="btn_calc_slices")
                write_text("caption", "Press Calculate to freeze results while you explore inputs.")
    
            # Diagram
            with c3:
                write_text("subheader", "Slice Representation")
    
                fig_slice, ax_slice = plt.subplots(figsize=(8, 6))
    
                ground_x = [-4, 0, 10, 18]
                ground_y = [0, 0, 8, 8]
                ax_slice.plot(ground_x, ground_y, 'k-', linewidth=2.5)
    
                o_x_sl, o_y_sl = 3.0, 12.0
                R_sl = math.sqrt(o_x_sl**2 + o_y_sl**2)
    
                arc_x_full = np.linspace(0, 14.5, 160)
                arc_y_full = o_y_sl - np.sqrt(R_sl**2 - (arc_x_full - o_x_sl)**2)
                ax_slice.plot(arc_x_full, arc_y_full, 'k-', linewidth=2.5)
    
                ax_slice.plot(o_x_sl, o_y_sl, 'ko')
                ax_slice.text(o_x_sl - 0.5, o_y_sl + 0.5, "O", fontweight='bold', fontsize=12)
    
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
                        y_t_mid = np.interp(mid_x, ground_x, ground_y)
                        row = edited_df.iloc[i]
    
                        circ = patches.Circle((mid_x, y_t_mid - 1.2), 0.5,
                                              edgecolor='black', facecolor='white', zorder=3)
                        ax_slice.add_patch(circ)
                        ax_slice.text(mid_x, y_t_mid - 1.2, str(int(row["Slice"])),
                                      ha='center', va='center', fontweight='bold', zorder=4)
    
                        ax_slice.text(mid_x, (y_b_left + y_t_left) / 2,
                                      f"W={row['W (kN/m)']}\nα={row['α (deg)']}°",
                                      ha='center', va='center', fontsize=8)
    
                ax_slice.set_aspect('equal')
                ax_slice.set_xlim(-4, 20)
                ax_slice.set_ylim(-4, 14)
                ax_slice.axis('off')
    
                st.pyplot(fig_slice)
                plt.close(fig_slice)
    
            # Calculation + persistent results
            if calc_slices:
                gamma_w = 9.81
                sum_l = 0.0
                sum_W_cos = 0.0
                sum_W_sin = 0.0
                sum_u_l = 0.0
    
                results_list = []
    
                for _, row in edited_df.iterrows():
                    b = row["b (m)"]
                    W_s = row["W (kN/m)"]
                    alpha_rad = math.radians(row["α (deg)"])
                    u_head = row["u/γ_w (m)"]
    
                    l = b / math.cos(alpha_rad) if math.cos(alpha_rad) != 0 else 0.0
                    W_cos = W_s * math.cos(alpha_rad)
                    W_sin = W_s * math.sin(alpha_rad)
                    u_l = u_head * gamma_w * l
    
                    sum_l += l
                    sum_W_cos += W_cos
                    sum_W_sin += W_sin
                    sum_u_l += u_l
    
                    results_list.append({
                        "Slice No": int(row["Slice"]),
                        "b (m)": b,
                        "h (m)": row["h (m)"],
                        "W (kN/m)": W_s,
                        "α (°)": row["α (deg)"],
                        "W·cos(α)": round(W_cos, 2),
                        "W·sin(α)": round(W_sin, 2),
                        "u/γ_w (m)": u_head,
                        "l (m)": round(l, 2),
                        "u·l": round(u_l, 2),
                    })
    
                sum_N_prime = sum_W_cos - sum_u_l
                phi_rad = math.radians(phi_sl)
    
                resisting = (c_sl * sum_l) + (math.tan(phi_rad) * sum_N_prime)
                driving = sum_W_sin
    
                if driving != 0:
                    FS_sl = resisting / driving
                else:
                    FS_sl = 999.0
    
                level_class, status_text = fs_theme_class(FS_sl)
    
                st.session_state.slice_last_result = {
                    "FS": FS_sl,
                    "level_class": level_class,
                    "status_text": status_text,
                    "results_list": results_list,
                    "sum_l": sum_l,
                    "sum_W_cos": sum_W_cos,
                    "sum_u_l": sum_u_l,
                    "sum_N_prime": sum_N_prime,
                    "sum_W_sin": sum_W_sin,
                    "resisting": resisting,
                    "driving": driving,
                    "tan_phi": math.tan(phi_rad),
                }
    
            if st.session_state.get("slice_last_result") is not None:
                r = st.session_state.slice_last_result
    
                st.markdown("---")
    
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
    
                res_df = pd.DataFrame(r["results_list"])
                glass_table(res_df)
    
                sums_df = pd.DataFrame({
                    "Summation": [
                        "Σl (m)",
                        "Σ W·cos(α) (kN/m)",
                        "Σ u·l (kN/m)",
                        "Σ(W·cos α − u·l) = ΣN' (kN/m)",
                        "Σ W·sin(α) — Driving (kN/m)",
                        "Total Resisting Forces (kN/m)",
                    ],
                    "Value": [
                        f"{r['sum_l']:.2f}",
                        f"{r['sum_W_cos']:.2f}",
                        f"{r['sum_u_l']:.2f}",
                        f"{r['sum_N_prime']:.2f}",
                        f"{r['sum_W_sin']:.2f}",
                        f"{r['resisting']:.2f}",
                    ],
                })
                glass_table(sums_df)
    
                write_text("subheader", "Detailed Calculation Log")
    
                step1 = (
                    "### Step 1 — Ordinary Method of Slices Formula\n\n"
                    r"$$F_s = \frac{c' \cdot \sum l + \tan\phi' \cdot \sum(W\cos\alpha - u \cdot l)}{\sum W\sin\alpha}$$"
                )
    
                step2 = (
                    "### Step 2 — Resisting Forces\n\n"
                    rf"**Cohesion term:** $c' \cdot \Sigma l = {c_sl:.2f} \times {r['sum_l']:.2f} = {(c_sl * r['sum_l']):.2f}\ \text{{kN/m}}$\n\n"
                    rf"**Friction term:** $\tan(\phi') \cdot \Sigma N' = {r['tan_phi']:.4f} \times {r['sum_N_prime']:.2f} = {(r['tan_phi'] * r['sum_N_prime']):.2f}\ \text{{kN/m}}$\n\n"
                    rf"$$\text{{Total Resisting}} = {r['resisting']:.2f}\ \text{{kN/m}}$$"
                )
    
                step3 = (
                    "### Step 3 — Driving Forces\n\n"
                    rf"$$\sum W \sin\alpha = {r['driving']:.2f}\ \text{{kN/m}}$$"
                )
    
                step4 = (
                    "### Step 4 — Factor of Safety\n\n"
                    r"$$FS = \frac{\text{Resisting}}{\text{Driving}}$$"
                    "\n\n**Substitution:**\n\n"
                    rf"$$FS = \frac{{{r['resisting']:.2f}}}{{{r['driving']:.2f}}} = {r['FS']:.3f}$$"
                )
    
                for s in [step1, step2, step3, step4]:
                    glass_box(s)
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
