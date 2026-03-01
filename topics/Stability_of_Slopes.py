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
        c1, c2, c3 = st.columns([1, 1, 1])

        with c1:
            write_text("subheader", "1. Geometry")
            beta = st.number_input("Slope Angle (β) [deg]", 0.0, 60.0, 25.0)
            z = st.number_input("Depth Normal to Slope (z) [m]", 0.5, 20.0, 5.0)

        with c2:
            write_text("subheader", "2. Soil Properties")
            c_prime = st.number_input("Cohesion (c') [kPa]", 0.0, 100.0, 5.0)
            phi_prime = st.number_input("Friction Angle (ϕ') [deg]", 0.0, 45.0, 30.0)
            gamma_dry = st.number_input("Dry Unit Weight (γ_dry) [kN/m³]", 15.0, 25.0, 18.0)
            gamma_sat = st.number_input("Saturated Unit Weight (γ_sat) [kN/m³]", 15.0, 25.0, 20.0)
            m_ratio = st.slider("Water Table Ratio (m = z_w / z)", 0.0, 1.0, 0.0)
            calc_t = st.button("Calculate Factor of Safety", type="primary")

        with c3:
            write_text("subheader", "Slope Diagram")
            fig_t, ax_t = plt.subplots(figsize=(6, 4))
            x = np.linspace(0, 10, 100)
            beta_r = math.radians(beta)
            y_surf = x * math.tan(beta_r)
            nx = math.sin(beta_r)
            ny = -math.cos(beta_r)
            x_fail = x + nx * z
            y_fail = y_surf + ny * z
            ax_t.plot(x, y_surf, 'k-', linewidth=2)
            ax_t.plot(x, y_fail, 'r--', linewidth=2)
            ax_t.fill_between(x, y_surf, y_fail, where=(y_surf >= y_fail), alpha=0.3)
            if m_ratio > 0:
                ax_t.plot(x, y_surf - 0.2, 'b--', linewidth=1)
            ax_t.set_aspect('equal')
            ax_t.axis('off')
            st.pyplot(fig_t)
            plt.close(fig_t)

        # =====================================================
        # RESULTS SECTION
        # =====================================================
        if calc_t:
            FS, sigma, u, tau, sigma_eff = calculate_infinite_slope_general(
                beta, phi_prime, c_prime,
                gamma_dry, gamma_sat,
                z, m_ratio
            )

            # Pre-compute
            beta_r = math.radians(beta)
            phi_r  = math.radians(phi_prime)
            z_w    = m_ratio * z
            tau_f  = c_prime + sigma_eff * math.tan(phi_r)

            # Stability colour
            if FS >= 1.5:
                fs_color  = "#2ecc71"
                fs_status = "Stable"
            elif FS >= 1.0:
                fs_color  = "#f39c12"
                fs_status = "Marginally Stable"
            else:
                fs_color  = "#e74c3c"
                fs_status = "Unstable"

            # Blue accent (replaces yellow #FDE047 from theme)
            BLUE = "#60A5FA"

            st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
            st.markdown("---")

            # ── Hero line ────────────────────────────────────────
            st.markdown(
                f"""
                <h2 style="font-size:2rem; font-weight:800; color:#E2E8F0; margin-bottom:16px;">
                    Factor of Safety:&nbsp;
                    <span style="color:{fs_color};">{FS:.3f}</span>
                    <span style="
                        font-size: 0.9rem; font-weight: 600;
                        color: {fs_color};
                        background: {fs_color}22;
                        border: 1px solid {fs_color};
                        border-radius: 20px;
                        padding: 3px 14px;
                        margin-left: 12px;
                        vertical-align: middle;
                    ">{fs_status}</span>
                </h2>
                """,
                unsafe_allow_html=True,
            )

            # ── Stress Summary Table ──────────────────────────────
            stress_df = pd.DataFrame({
                "Parameter": [
                    "Total Normal Stress (σ)",
                    "Pore Water Pressure (u)",
                    "Effective Normal Stress (σ')",
                    "Shear Stress (τ)",
                ],
                "Value (kPa)": [
                    f"{sigma:.2f}",
                    f"{u:.2f}",
                    f"{sigma_eff:.2f}",
                    f"{tau:.2f}",
                ],
            })
            glass_table(stress_df)

            # ── Special Case Banners ───────────────────────────────
            if c_prime == 0 and m_ratio == 0:
                st.info("ℹ️ Special Case: Dry Cohesionless Slope — FS = tan(ϕ') / tan(β)")
            if c_prime == 0 and m_ratio == 1:
                st.info("ℹ️ Special Case: Fully Saturated with Seepage — FS = (γ' / γ_sat) · tan(ϕ') / tan(β)")
            if sigma_eff < 0:
                st.warning("⚠️ Effective stress is negative — tension condition may exist at failure plane.")

            # ── Detailed Calculation Log header ───────────────────
            write_text("section_header", "Detailed Calculation Log")

            # Helper: one step block
            def step(num, title, body):
                return f"""
                <div style="margin-bottom:16px;">
                    <div style="
                        font-size:12px; font-weight:700; letter-spacing:0.08em;
                        color:{BLUE}; margin-bottom:5px; text-transform:uppercase;
                    ">Step {num} — {title}</div>
                    <div style="
                        font-size:15px; font-weight:500; color:#CBD5E1; line-height:1.9;
                        padding-left:14px; border-left:2px solid {BLUE}44;
                    ">{body}</div>
                </div>
                <hr style="border:none; border-top:1px solid rgba(255,255,255,0.07); margin:14px 0;">
                """

            log_content = f"""
            <h3 style="margin-top:0; font-size:1.15rem; font-weight:700; color:#E2E8F0; margin-bottom:6px;">
                Infinite Slope Analysis
            </h3>
            <p style="font-size:13px; color:#94A3B8; margin-bottom:20px;">
                <strong style="color:#E2E8F0;">Given:</strong>&nbsp;
                β = {beta}°,&nbsp; z = {z} m,&nbsp; c' = {c_prime} kPa,&nbsp;
                ϕ' = {phi_prime}°,&nbsp; γ<sub>dry</sub> = {gamma_dry} kN/m³,&nbsp;
                γ<sub>sat</sub> = {gamma_sat} kN/m³,&nbsp; m = {m_ratio}
            </p>

            {step(1, "Total Normal Stress",
                f"Saturated depth = m · z = {m_ratio} × {z} = "
                f"<strong style='color:{BLUE};'>{z_w:.2f} m</strong><br>"
                f"σ = [γ<sub>dry</sub>(1−m) + γ<sub>sat</sub>·m] · z · cos²β<br>"
                f"σ = [{gamma_dry}×{(1-m_ratio):.2f} + {gamma_sat}×{m_ratio:.2f}] "
                f"× {z} × cos²({beta}°)<br>"
                f"σ = <strong style='color:{BLUE};'>{sigma:.2f} kPa</strong>"
            )}

            {step(2, "Pore Water Pressure",
                f"u = γ<sub>w</sub> · m · z · cos²β<br>"
                f"u = 9.81 × {m_ratio} × {z} × cos²({beta}°)<br>"
                f"u = <strong style='color:{BLUE};'>{u:.2f} kPa</strong>"
            )}

            {step(3, "Effective Normal Stress",
                f"σ' = σ − u = {sigma:.2f} − {u:.2f}<br>"
                f"σ' = <strong style='color:{BLUE};'>{sigma_eff:.2f} kPa</strong>"
                + (" &nbsp;<span style='color:#f39c12;'>⚠ Tension condition</span>" if sigma_eff < 0 else "")
            )}

            {step(4, "Shear Stress on Failure Plane",
                f"τ = [γ<sub>dry</sub>(1−m) + γ<sub>sat</sub>·m] · z · sinβ · cosβ<br>"
                f"τ = <strong style='color:{BLUE};'>{tau:.2f} kPa</strong>"
            )}

            {step(5, "Shear Strength (Mohr-Coulomb)",
                f"τ<sub>f</sub> = c' + σ' · tan(ϕ')<br>"
                f"τ<sub>f</sub> = {c_prime} + {sigma_eff:.2f} × tan({phi_prime}°)<br>"
                f"τ<sub>f</sub> = {c_prime} + {sigma_eff:.2f} × {math.tan(phi_r):.4f}<br>"
                f"τ<sub>f</sub> = <strong style='color:{BLUE};'>{tau_f:.2f} kPa</strong>"
            )}

            <div style="margin-bottom:4px;">
                <div style="
                    font-size:12px; font-weight:700; letter-spacing:0.08em;
                    color:{BLUE}; margin-bottom:5px; text-transform:uppercase;
                ">Step 6 — Factor of Safety</div>
                <div style="
                    font-size:15px; font-weight:500; color:#CBD5E1; line-height:1.9;
                    padding-left:14px; border-left:2px solid {BLUE}44;
                ">
                    FS = τ<sub>f</sub> / τ = {tau_f:.2f} / {tau:.2f}<br>
                    FS = <span style="color:{fs_color}; font-weight:800; font-size:1.3em;">{FS:.3f}</span>
                    &nbsp;→&nbsp;
                    <span style="
                        color:{fs_color}; font-weight:600;
                        background:{fs_color}22;
                        border:1px solid {fs_color};
                        border-radius:12px;
                        padding:2px 10px;
                    ">{fs_status}</span>
                </div>
            </div>
            """

            glass_box(log_content)

    # ---------------------------------------------------------
    # TAB 2: ROTATIONAL (CIRCULAR)
    # ---------------------------------------------------------
    with tab_rot:

        method = st.radio("**Calculation Method:**", 
                          ["A. Mass Procedure (Undrained / ϕ=0)", "B. Method of Slices"], 
                          horizontal=True, key="rot_method_select") 
        st.markdown("---")
        
        if "Mass Procedure" in method:
            col_r1, col_r2 = st.columns([0.4, 0.6], gap="medium")
            
            with col_r1:
                st.subheader("1. Geometry & Loads")
                H_slope = st.number_input("Slope Height (H) [m]", 1.0, 50.0, 8.5, key="mass_H")
                beta_slope = st.number_input("Slope Angle [deg]", 0.0, 90.0, 45.0, key="mass_beta")
                
                st.markdown("**Failure Circle**")
                R = st.number_input("Radius (R) [m]", 5.0, 50.0, 12.1, key="mass_R")
                o_x = st.number_input("Center X-coord (o_x) [m]", -20.0, 20.0, -2.0, key="mass_ox")
                dist_d = st.number_input("Moment Arm (d) [m]", 0.0, 20.0, 4.5, help="Horizontal distance from Center O to Centroid", key="mass_d")
                st.caption("⚠️ **Note:** This calculation currently assumes a toe failure. The circle geometry is forced to intersect the slope toe at coordinates (0,0).")
                st.subheader("2. Soil Properties")
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
                st.subheader("Failure Diagram")
                fig_c, ax_c = plt.subplots(figsize=(8, 6))
                
                X_crest = H_slope / math.tan(math.radians(beta_slope)) if beta_slope > 0 else 10
                Y_crest = H_slope
                
                ground_x = [-10, 0, X_crest, X_crest + 10]
                ground_y = [0, 0, Y_crest, Y_crest]
                
                ax_c.plot(ground_x, ground_y, 'k-', linewidth=2.5, label="Ground Surface")
                
                y_crack_bottom = Y_crest - z_c
                
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
                        
                        soil_mass = patches.Polygon(poly_verts, closed=True, facecolor='none', edgecolor='black', hatch='//', alpha=0.5)
                        ax_c.add_patch(soil_mass)
                        ax_c.plot(arc_x, arc_y, 'k-', linewidth=1.5)
                        
                        if z_c > 0:
                            ax_c.plot([x_intersect, x_intersect], [y_crack_bottom, Y_crest], 'r-', linewidth=2, label="Tension Crack")
                            if water_crack:
                                ax_c.fill_between([x_intersect - 0.5, x_intersect], [y_crack_bottom, Y_crest], color='blue', alpha=0.3, label="Water Pressure")
                                y_force = Y_crest - (2 * z_c / 3)
                                ax_c.arrow(x_intersect - 1.5, y_force, 1.5, 0, head_width=0.3, color='blue', width=0.05)
                                ax_c.text(x_intersect - 2.0, y_force, "Pw", color='blue', fontweight='bold')
                        
                        theta = abs(theta_end - theta_start)
                        theta_deg = math.degrees(theta)
                        L_calc = R * theta
                    else:
                        L_calc = 0
                        st.error("Geometry Error: Circle does not intersect the tension crack/crest elevation.")

                    ax_c.plot(o_x, o_y, 'bo', label="O")
                    ax_c.plot([o_x, 0], [o_y, 0], 'b--', linewidth=1)
                    
                    X_w = o_x + dist_d
                    Y_w = Y_crest / 2 
                    ax_c.plot([o_x, o_x], [o_y, o_y+2], 'k-', linewidth=0.5)
                    ax_c.plot([X_w, X_w], [Y_w, o_y+2], 'k-', linewidth=0.5)
                    ax_c.arrow(X_w, Y_w, 0, -3, head_width=0.5, color='black', width=0.1)
                    ax_c.text(X_w + 0.5, Y_w - 3, "W", fontweight='bold')

                    ax_c.set_aspect('equal')
                    ax_c.set_xlim(-5, X_crest + 10)
                    ax_c.set_ylim(-2, o_y + 5)
                    ax_c.legend(loc="upper right", fontsize=8)
                    ax_c.axis('off')
                    st.pyplot(fig_c)
                    plt.close(fig_c)
                    
                    if calc_rot:
                        M_res = Cu * L_calc * R
                        M_drv_weight = W_calc * dist_d
                        
                        M_drv_water = 0.0
                        P_w = 0.0
                        if water_crack and z_c > 0:
                            gamma_w = 9.81
                            P_w = 0.5 * gamma_w * (z_c ** 2)
                            y_force = Y_crest - (2 * z_c / 3)
                            arm_water = abs(y_force - o_y)
                            M_drv_water = P_w * arm_water
                            
                        M_drv_total = M_drv_weight + M_drv_water
                    
                        st.markdown("## 🔎 Step-by-Step Calculation")
                        st.markdown("### 1️⃣ Resisting Moment")
                        st.write(f"Arc Length (L) = {L_calc:.2f} m")
                        st.latex(r"M_{res} = C_u \cdot L \cdot R")
                        st.write(f"M_res = {M_res:.2f} kNm")
                        if Cu == 0:
                            st.warning("Cohesion is 0, so resisting moment is 0. Slope is unconditionally unstable in this undrained analysis.")
                    
                        st.markdown("### 2️⃣ Driving Moments")
                        st.write(f"Moment from Soil Weight: {M_drv_weight:.2f} kNm")
                        if water_crack and z_c > 0:
                            st.write(f"Hydrostatic Force ($P_w$) = {P_w:.2f} kN")
                            st.write(f"Moment from Water Pressure: {M_drv_water:.2f} kNm")
                        st.write(f"**Total Driving Moment ($M_{{drv}}$) = {M_drv_total:.2f} kNm**")
                    
                        if M_drv_total > 0:
                            FS = M_res / M_drv_total
                            st.markdown("### 3️⃣ Factor of Safety")
                            st.latex(r"FS = \frac{M_{res}}{M_{drv}}")
                            st.metric("Factor of Safety", f"{FS:.3f}")
                            if FS < 1.0:
                                st.error("Slope is UNSTABLE")
                            elif FS < 1.5:
                                st.warning("Slope is Marginally Stable")
                            else:
                                st.success("Slope is Stable")
                        else:
                            st.info("Total driving moment is zero or negative. Slope is theoretically stable against this failure surface.")
                else:
                    st.error("Geometry Error: Radius (R) is too small to calculate center.")

        else:
            col_s1, col_s2 = st.columns([0.4, 0.6], gap="medium")
            with col_s1:
                st.subheader("Global Parameters")
                c_sl = st.number_input("Cohesion (c') [kPa]", 0.0, 100.0, 5.0, key="slice_c")
                phi_sl = st.number_input("Friction Angle (ϕ') [deg]", 0.0, 45.0, 30.0, key="slice_phi")
                
                default_data = pd.DataFrame([
                    {"Slice": 1, "b (m)": 2.0, "h (m)": 1.0, "W (kN/m)": 38.0, "α (deg)": -5.0, "u/γ_w (m)": 0.0},
                    {"Slice": 2, "b (m)": 4.0, "h (m)": 3.2, "W (kN/m)": 243.0, "α (deg)": 12.0, "u/γ_w (m)": 0.5},
                    {"Slice": 3, "b (m)": 4.8, "h (m)": 5.2, "W (kN/m)": 474.0, "α (deg)": 28.0, "u/γ_w (m)": 1.2},
                    {"Slice": 4, "b (m)": 4.0, "h (m)": 6.0, "W (kN/m)": 456.0, "α (deg)": 45.0, "u/γ_w (m)": 0.8},
                    {"Slice": 5, "b (m)": 4.0, "h (m)": 3.5, "W (kN/m)": 266.0, "α (deg)": 60.0, "u/γ_w (m)": 0.0},
                ])
                st.markdown("**Input Slice Data**")
                edited_df = st.data_editor(default_data, num_rows="dynamic", key="slice_editor")
                calc_slices = st.button("Calculate FS", type="primary", key="btn_calc_slices")

            with col_s2:
                st.subheader("Slice Representation")
                fig_slice, ax_slice = plt.subplots(figsize=(8, 6))
                
                ground_x = [-4, 0, 10, 18]
                ground_y = [0, 0, 8, 8]
                ax_slice.plot(ground_x, ground_y, 'k-', linewidth=2)
                
                o_x, o_y = 3.0, 12.0
                R = math.sqrt(o_x**2 + o_y**2) 
                
                arc_x_full = np.linspace(0, 14.5, 100)
                arc_y_full = o_y - np.sqrt(R**2 - (arc_x_full - o_x)**2)
                ax_slice.plot(arc_x_full, arc_y_full, 'k-', linewidth=2)
                
                ax_slice.plot(o_x, o_y, 'ko')
                ax_slice.text(o_x - 0.5, o_y + 0.5, "O", fontweight='bold', fontsize=12)
                
                rad_angle = math.radians(285)
                rad_x = o_x + R * math.cos(rad_angle)
                rad_y = o_y + R * math.sin(rad_angle)
                ax_slice.annotate("", xy=(rad_x, rad_y), xytext=(o_x, o_y), 
                                  arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
                ax_slice.text(o_x + 1.5, o_y - 4, "R", fontsize=12, fontweight='bold', rotation=-65)
                ax_slice.text(14, 11, "— NOT TO SCALE —", ha='center', fontsize=10, fontweight='bold')
                
                num_slices = len(edited_df)
                if num_slices > 0:
                    slice_edges = np.linspace(0, 14.5, num_slices + 1)
                    for i in range(num_slices):
                        x_left = slice_edges[i]
                        x_right = slice_edges[i+1]
                        y_b_left = o_y - math.sqrt(R**2 - (x_left - o_x)**2)
                        y_b_right = o_y - math.sqrt(R**2 - (x_right - o_x)**2)
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
                        slice_num = int(row['Slice'])
                        weight = row['W (kN/m)']
                        alpha = row['α (deg)']
                        circle = patches.Circle((mid_x, y_t_mid - 1.2), 0.5, 
                                                edgecolor='black', facecolor='white', zorder=3)
                        ax_slice.add_patch(circle)
                        ax_slice.text(mid_x, y_t_mid - 1.2, str(slice_num), 
                                      ha='center', va='center', fontweight='bold', zorder=4)
                        ax_slice.text(mid_x, mid_y - 0.5, f"W={weight}\nα={alpha}°", 
                                      ha='center', va='center', fontsize=8)

                ax_slice.set_aspect('equal')
                ax_slice.set_xlim(-4, 20)
                ax_slice.set_ylim(-4, 14)
                ax_slice.axis('off')
                st.pyplot(fig_slice)
                plt.close(fig_slice)
                
                if calc_slices:
                    gamma_w = 9.81
                    sum_l = 0.0
                    sum_W_cos = 0.0
                    sum_W_sin = 0.0
                    sum_u_l = 0.0
                    results_list = []
                    
                    for index, row in edited_df.iterrows():
                        slice_num = int(row["Slice"])
                        b = row["b (m)"]
                        h = row["h (m)"]
                        W = row["W (kN/m)"]
                        alpha_deg = row["α (deg)"]
                        alpha_rad = math.radians(alpha_deg)
                        u_head = row["u/γ_w (m)"]
                        l = b / math.cos(alpha_rad) if math.cos(alpha_rad) != 0 else 0.0
                        W_cos = W * math.cos(alpha_rad)
                        W_sin = W * math.sin(alpha_rad)
                        u_pressure = u_head * gamma_w
                        u_l = u_pressure * l
                        sum_l += l
                        sum_W_cos += W_cos
                        sum_W_sin += W_sin
                        sum_u_l += u_l
                        results_list.append({
                            "Slice No": slice_num,
                            "b (m)": b, "h (m)": h, "W (kN/m)": W,
                            "α (degrees)": alpha_deg,
                            "W × cos(α)": round(W_cos, 2),
                            "W × sin(α)": round(W_sin, 2),
                            "u/γ_w (m)": u_head,
                            "l (m)": round(l, 2),
                            "u × l": round(u_l, 2)
                        })
                    
                    st.markdown("---")
                    st.markdown("## 📊 Completed Calculation Table")
                    res_df = pd.DataFrame(results_list)
                    st.dataframe(res_df, use_container_width=True, hide_index=True)
                    
                    sum_N_prime = sum_W_cos - sum_u_l
                    phi_rad = math.radians(phi_sl)
                    resisting_forces = (c_sl * sum_l) + (math.tan(phi_rad) * sum_N_prime)
                    driving_forces = sum_W_sin
                    
                    st.markdown("## 📐 Final Factor of Safety")
                    st.latex(r"F_s = \frac{c' \times \sum l + \tan \phi' \times \sum(W \times \cos \alpha - u \times l)}{\sum W \times \sin \alpha}")
                    
                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.write(f"**$\sum l$** = {sum_l:.2f} m")
                        st.write(f"**$\sum (W \times \cos\alpha)$** = {sum_W_cos:.2f} kN/m")
                        st.write(f"**$\sum (u \times l)$** = {sum_u_l:.2f} kN/m")
                        st.write(f"**$\sum W \times \sin\alpha$ (Driving)** = {sum_W_sin:.2f} kN/m")
                    with col_res2:
                        st.write(f"**Effective Normal $\sum(W\cos\alpha - ul)$** = {sum_N_prime:.2f} kN/m")
                        st.write(f"**Total Resisting Forces** = {resisting_forces:.2f} kN/m")
                        if driving_forces != 0:
                            FS_slices = resisting_forces / driving_forces
                            st.metric("Factor of Safety (Fs)", f"{FS_slices:.3f}")
                            if FS_slices < 1.0:
                                st.error("Slope is UNSTABLE")
                            elif FS_slices < 1.5:
                                st.warning("Slope is Marginally Stable")
                            else:
                                st.success("Slope is Stable")
                        else:
                            st.error("Driving forces sum to zero. Check input angles and weights.")

    # ---------------------------------------------------------
    # TAB 3: COMPOUND (BLOCK & WEDGE)
    # ---------------------------------------------------------
    with tab_comp:
        col_c1, col_c2 = st.columns([0.4, 0.6], gap="medium")
        
        with col_c1:
            st.subheader("Inputs")
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
            st.subheader("Block & Wedge Diagram")
            fig_b, ax_b = plt.subplots(figsize=(8, 4))
            wedge_L_width = H_left 
            wedge_R_width = H_right
            block_x_start = wedge_L_width
            block_x_end = wedge_L_width + L_block
            ground_x = [0, block_x_start, block_x_end, block_x_end + wedge_R_width]
            ground_y = [H_left, H_left, H_right, H_right]
            base_x = [0, block_x_end + wedge_R_width]
            base_y = [0, 0]
            ax_b.plot(ground_x, ground_y, 'k-', linewidth=2, label="Ground Surface")
            ax_b.plot(base_x, base_y, 'b-', linewidth=3, label="Weak Layer")
            ax_b.plot([block_x_start, block_x_start], [0, H_left], 'k--', linewidth=1)
            ax_b.plot([block_x_end, block_x_end], [0, H_right], 'k--', linewidth=1)
            ax_b.fill_between([0, block_x_start], 0, H_left, color='#A5D6A7', alpha=0.5)
            ax_b.fill_between([block_x_start, block_x_end], 0, np.interp([block_x_start, block_x_end], ground_x, ground_y), color='lightgrey', hatch='//', alpha=0.5)
            ax_b.fill_between([block_x_end, block_x_end + wedge_R_width], 0, H_right, color='#FFCCBC', alpha=0.5)
            ax_b.text(block_x_start/2, H_left/2, "Passive\nZone", ha='center', fontsize=9)
            ax_b.text((block_x_start+block_x_end)/2, (H_left+H_right)/3, "Central Block", ha='center', fontweight='bold')
            ax_b.text(block_x_end + wedge_R_width/2, H_right/2, "Active\nZone", ha='center', fontsize=9)
            ax_b.arrow(block_x_end + 1.5, H_right/3, -1.5, 0, head_width=0.5, color='red', width=0.1)
            ax_b.text(block_x_end + 1.6, H_right/3, "Pa", color='red', fontweight='bold', va='center')
            ax_b.arrow(block_x_start - 1.5, H_left/3, 1.5, 0, head_width=0.5, color='green', width=0.1)
            ax_b.text(block_x_start - 2.5, H_left/3, "Pp", color='green', fontweight='bold', va='center')
            ax_b.text((block_x_start+block_x_end)/2, -1.5, r"$\tau_f$ (Shear Resistance)", ha='center')
            ax_b.arrow((block_x_start+block_x_end)/2, -0.5, -3, 0, head_width=0.3, color='black') 
            ax_b.annotate(f"L={L_block}m", xy=(block_x_start, -0.5), xytext=(block_x_end, -0.5), arrowprops=dict(arrowstyle='<->'))
            ax_b.set_xlim(-2, block_x_end + wedge_R_width + 2)
            ax_b.set_ylim(-3, H_right + 3)
            ax_b.axis('off')
            st.pyplot(fig_b)
            plt.close(fig_b)
            
            if calc_blk:
                phi_top_rad = math.radians(phi_top)
                Ka = (1 - math.sin(phi_top_rad)) / (1 + math.sin(phi_top_rad))
                Kp = (1 + math.sin(phi_top_rad)) / (1 - math.sin(phi_top_rad))
                Pa_calc = (0.5 * gamma_top * (H_right**2) * Ka) - (2 * c_top * H_right * math.sqrt(Ka))
                Pa = max(Pa_calc, 0.0)
                Pp = (0.5 * gamma_top * (H_left**2) * Kp) + (2 * c_top * H_left * math.sqrt(Kp))
                area_block = ((H_left + H_right) / 2.0) * L_block
                W_block = area_block * gamma_top
                phi_base_rad = math.radians(phi_base)
                tau_f = (c_base * L_block) + (W_block * math.tan(phi_base_rad))
                total_resisting = Pp + tau_f
                total_driving = Pa
                
                st.markdown("## 🔎 Step-by-Step Calculation")
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.markdown("### Active Thrust (Driving)")
                    st.write(f"$K_A$ = {Ka:.3f}")
                    st.write(f"$P_A$ = {Pa:.1f} kN/m")
                    st.markdown("### Passive Resistance")
                    st.write(f"$K_P$ = {Kp:.3f}")
                    st.write(f"$P_P$ = {Pp:.1f} kN/m")
                with col_res2:
                    st.markdown("### Base Shear Resistance")
                    st.write(f"Block Weight (W) = {W_block:.1f} kN/m")
                    st.latex(r"\tau_f = C_u \cdot L + W \cdot \tan(\phi_{base})")
                    st.write(rf"$\tau_f$ = {tau_f:.1f} kN/m")
                
                st.markdown("---")
                st.markdown("### 📐 Final Factor of Safety")
                if total_driving > 0:
                    FS_block = total_resisting / total_driving
                    st.latex(r"FS = \frac{P_P + \tau_f}{P_A}")
                    st.write(f"FS = ({Pp:.1f} + {tau_f:.1f}) / {Pa:.1f}")
                    st.metric("Factor of Safety (Fs)", f"{FS_block:.2f}")
                    if FS_block < 1: st.error("Slope is UNSTABLE")
                    elif FS_block < 1.5: st.warning("Slope is Marginally Stable")
                    else: st.success("Slope is Stable")
                else:
                    st.error("Active Thrust ($P_a$) is zero. No driving force to calculate FS.")


if __name__ == "__main__":
    app()
