import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def calculate_infinite_slope_general(beta, phi, c, gamma_dry, gamma_sat, z, m):

    gamma_w = 9.81
    
    beta_r = math.radians(beta)
    phi_r = math.radians(phi)
    
    # Total unit weight
    gamma_total = ((1 - m) * gamma_dry) + (m * gamma_sat)
    
    # Weight per unit area
    W = gamma_total * z
    
    # Normal stress
    sigma = W * (math.cos(beta_r) ** 2)
    
    # Pore pressure
    u = m * z * gamma_w * (math.cos(beta_r) ** 2)
    
    # Shear stress
    tau = W * math.sin(beta_r) * math.cos(beta_r)
    
    # Effective normal stress
    sigma_eff = sigma - u
    
    # Shear strength
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

        
        col_t1, col_t2 = st.columns([0.4, 0.6], gap="medium")
        
        with col_t1:
            st.subheader("Inputs")
            beta = st.number_input("Slope Angle (β) [deg]", 0.0, 60.0, 25.0)
            z = st.number_input("Depth Normal to Slope (z) [m]", 0.5, 20.0, 5.0)
            
            st.markdown("### Soil Properties")
            c_prime = st.number_input("Cohesion (c') [kPa]", 0.0, 100.0, 5.0)
            phi_prime = st.number_input("Friction Angle (ϕ') [deg]", 0.0, 45.0, 30.0)
            
            gamma_dry = st.number_input("Dry Unit Weight (γ_dry) [kN/m³]", 15.0, 25.0, 18.0)
            gamma_sat = st.number_input("Saturated Unit Weight (γ_sat) [kN/m³]", 15.0, 25.0, 20.0)
            
            m_ratio = st.slider("Water Table Ratio (m = z_w / z)", 0.0, 1.0, 0.0)
            calc_t = st.button("Calculate FS", type="primary", key="btn_calc_translational")

        with col_t2:
            st.subheader("Analysis")
            fig_t, ax_t = plt.subplots(figsize=(6, 4))
            x = np.linspace(0, 10, 100)
            beta_r = math.radians(beta)
            y_surf = x * math.tan(beta_r)
            # unit normal vector
            nx = -math.sin(beta_r)
            ny = math.cos(beta_r)
            
            x_fail = x + nx * z
            y_fail = y_surf + ny * z
            
            ax_t.plot(x, y_surf, 'k-', linewidth=2, label="Ground Surface")
            ax_t.plot(x, y_fail, 'r--', linewidth=2, label="Failure Plane")
            ax_t.fill_between(x, y_fail, y_surf, color='#E6D690', alpha=0.5)
            
            if soil_case == "Seepage Parallel to Slope":
                ax_t.plot(x, y_surf - 0.2, 'b--', linewidth=1, label="Flow Line")
            
            ax_t.text(5, 5*math.tan(beta_r) + 1, f"β={beta}°", ha='center')
            ax_t.arrow(5, 5*math.tan(beta_r), 0, -z, length_includes_head=True, head_width=0.2, color='black')
            ax_t.text(5.2, 5*math.tan(beta_r) - z/2, f"z={z}m", va='center')

            ax_t.set_aspect('equal')
            ax_t.legend()
            ax_t.axis('off')
            st.pyplot(fig_t)
            
            if calc_t:
                FS, sigma, u, tau, sigma_eff = calculate_infinite_slope_general(beta, phi_prime, c_prime, gamma_dry, gamma_sat, z, m_ratio)
                st.markdown("### Stress Components")

                st.write(f"Total Normal Stress σ = {sigma:.2f} kPa")
                st.write(f"Pore Pressure u = {u:.2f} kPa")
                st.write(f"Effective Stress σ' = {sigma_eff:.2f} kPa")
                st.write(f"Shear Stress τ = {tau:.2f} kPa")
                
                st.markdown("### Factor of Safety")
                
                if FS < 1:
                    st.error(f"FS = {FS:.3f} (Unstable)")
                elif FS < 1.5:
                    st.warning(f"FS = {FS:.3f} (Marginal)")
                else:
                    st.success(f"FS = {FS:.3f} (Stable)")
                if c_prime == 0 and m_ratio == 0:
                    st.info("Special Case: Dry Cohesionless Slope")
                
                if c_prime == 0 and m_ratio == 1:
                    st.info("Special Case: Fully Saturated Seepage Slope")

    # ---------------------------------------------------------
    # TAB 2: ROTATIONAL (CIRCULAR)
    # ---------------------------------------------------------
    with tab_rot:

        
        method = st.radio("**Calculation Method:**", 
                          ["A. Mass Procedure (Undrained / ϕ=0)", "B. Method of Slices"], 
                          horizontal=True, key="rot_method_select") 
        st.markdown("---")
        
        # --- A. MASS PROCEDURE ---
        if "Mass Procedure" in method:
            col_r1, col_r2 = st.columns([0.4, 0.6], gap="medium")
            
            with col_r1:
                st.subheader("1. Geometry & Loads")
                H_slope = st.number_input("Slope Height (H) [m]", 1.0, 50.0, 8.5, key="mass_H")
                beta_slope = st.number_input("Slope Angle [deg]", 0.0, 90.0, 45.0, key="mass_beta")
                
                st.markdown("**Failure Circle**")
                R = st.number_input("Radius (R) [m]", 5.0, 50.0, 12.1, key="mass_R")
                dist_d = st.number_input("Moment Arm (d) [m]", 0.0, 20.0, 4.5, help="Horizontal distance from Center O to Centroid", key="mass_d")
                
                st.subheader("2. Soil Properties")
                gamma_clay = st.number_input("Unit Weight (γ) [kN/m³]", 10.0, 25.0, 19.0, key="mass_gamma")
                Cu = st.number_input("Undrained Shear Strength (Cu) [kPa]", 10.0, 200.0, 65.0, key="mass_cu")
                
                st.caption("Weight Calculation:")
                area_approx = st.number_input("Area of Sliding Mass [m²]", 1.0, 500.0, 70.0, key="mass_area")
                W_calc = area_approx * gamma_clay
                st.write(f"Weight (W) = {W_calc:.1f} kN/m")
                
                calc_rot = st.button("Calculate FS (Mass Procedure)", type="primary", key="btn_calc_mass")

            with col_r2:
                st.subheader("Failure Diagram")
                fig_c, ax_c = plt.subplots(figsize=(8, 6))
                
                # 1. Slope Geometry
                # Use standard variable names X_crest and Y_crest
                X_crest = H_slope / math.tan(math.radians(beta_slope)) if beta_slope > 0 else 10
                Y_crest = H_slope
                
                ground_x = [-10, 0, X_crest, X_crest + 10]
                ground_y = [0, 0, Y_crest, Y_crest]
                
                ax_c.plot(ground_x, ground_y, 'k-', linewidth=2.5, label="Ground Surface")
                
                # 2. Failure Circle (Arc)
                o_x = -2.0 
                o_y = math.sqrt(R**2 - o_x**2) 
                
                # Calculate Intersection with Crest
                term = R**2 - (Y_crest - o_y)**2
                
                if term > 0:
                    x_intersect = o_x + math.sqrt(term)
                    
                    theta_start = math.atan2(0 - o_y, 0 - o_x)
                    theta_end = math.atan2(Y_crest - o_y, x_intersect - o_x)
                    
                    thetas = np.linspace(theta_start, theta_end, 50)
                    arc_x = o_x + R * np.cos(thetas)
                    arc_y = o_y + R * np.sin(thetas)
                    
                    # 3. Create the "Wedge" Polygon (Hatched)
                    poly_verts = list(zip(arc_x, arc_y))
                    poly_verts.append((X_crest, Y_crest)) 
                    poly_verts.append((0, 0)) 
                    
                    soil_mass = patches.Polygon(poly_verts, closed=True, facecolor='none', edgecolor='black', hatch='//', alpha=0.5)
                    ax_c.add_patch(soil_mass)
                    ax_c.plot(arc_x, arc_y, 'k-', linewidth=1.5)
                    
                    # Calculate Arc Length
                    theta_deg = math.degrees(theta_end - theta_start)
                    L_calc = (theta_deg/360) * 2 * math.pi * R
                else:
                    L_calc = 0
                    st.error("Geometry Error: Circle does not intersect crest or R is too small.")

                # Annotations
                ax_c.plot(o_x, o_y, 'bo', label="O")
                ax_c.plot([o_x, 0], [o_y, 0], 'b--', linewidth=1)
                ax_c.text(o_x/2, o_y/2, f"R={R}m", color='blue', rotation=60)
                
                X_w = o_x + dist_d
                Y_w = Y_crest / 2 
                ax_c.plot([o_x, o_x], [o_y, o_y+2], 'k-', linewidth=0.5)
                ax_c.plot([X_w, X_w], [Y_w, o_y+2], 'k-', linewidth=0.5)
                ax_c.annotate(f"d={dist_d}m", xy=(o_x, o_y+1.5), xytext=(X_w, o_y+1.5), arrowprops=dict(arrowstyle='<->'))
                
                ax_c.arrow(X_w, Y_w, 0, -3, head_width=0.5, color='black', width=0.1)
                ax_c.text(X_w + 0.5, Y_w - 3, "W", fontweight='bold')

                ax_c.set_aspect('equal')
                ax_c.set_xlim(-5, X_crest + 10)
                ax_c.set_ylim(-2, o_y + 5)
                ax_c.axis('off')
                st.pyplot(fig_c)
                
                if calc_rot:
                    M_res = Cu * L_calc * R
                    M_drv = W_calc * dist_d
                    
                    if M_drv > 0:
                        FS = M_res / M_drv
                        st.markdown("### Results")
                        st.latex(r"FS = \frac{C_u \cdot L_{arc} \cdot R}{W \cdot d}")
                        st.write(f"**L_arc:** {L_calc:.2f} m")
                        st.write(f"**Resisting Moment:** {M_res:.1f} kNm")
                        st.write(f"**Driving Moment:** {M_drv:.1f} kNm")
                        if FS < 1.0: st.error(f"**FS = {FS:.2f} (Unstable)**")
                        else: st.success(f"**FS = {FS:.2f} (Stable)**")

        # --- B. METHOD OF SLICES ---
        else:
            col_s1, col_s2 = st.columns([0.4, 0.6], gap="medium")
            with col_s1:
                st.subheader("Global Parameters")
                c_sl = st.number_input("Cohesion (c') [kPa]", 0.0, 100.0, 5.0, key="slice_c")
                phi_sl = st.number_input("Friction Angle (ϕ') [deg]", 0.0, 45.0, 30.0, key="slice_phi")
                
                default_data = pd.DataFrame([
                    {"Slice": 1, "Weight (kN)": 150, "Base Angle α (deg)": -10, "Base Length l (m)": 2.5, "u (kPa)": 0},
                    {"Slice": 2, "Weight (kN)": 250, "Base Angle α (deg)": 10, "Base Length l (m)": 2.5, "u (kPa)": 15},
                    {"Slice": 3, "Weight (kN)": 200, "Base Angle α (deg)": 35, "Base Length l (m)": 2.8, "u (kPa)": 10},
                ])
                edited_df = st.data_editor(default_data, num_rows="dynamic", key="slice_editor")
                calc_slices = st.button("Calculate FS (Ordinary Method)", type="primary", key="btn_calc_slices")

            with col_s2:
                if calc_slices:
                    sum_resisting = 0.0
                    sum_driving = 0.0
                    phi_rad = math.radians(phi_sl)
                    details = []
                    
                    for index, row in edited_df.iterrows():
                        W = row["Weight (kN)"]
                        alpha = math.radians(row["Base Angle α (deg)"])
                        l = row["Base Length l (m)"]
                        u = row["u (kPa)"]
                        
                        N_prime = (W * math.cos(alpha)) - (u * l)
                        T_f = (c_sl * l) + (N_prime * math.tan(phi_rad))
                        T_d = W * math.sin(alpha)
                        
                        sum_resisting += T_f
                        sum_driving += T_d
                        details.append({"Slice": row["Slice"], "Driving": round(T_d, 1), "Resisting": round(T_f, 1)})
                    
                    if sum_driving != 0:
                        FS_slices = sum_resisting / sum_driving
                        st.metric("Factor of Safety", f"{FS_slices:.3f}")
                        st.dataframe(pd.DataFrame(details))

    # ---------------------------------------------------------
    # TAB 3: COMPOUND (BLOCK & WEDGE)
    # ---------------------------------------------------------
    with tab_comp:

        col_c1, col_c2 = st.columns([0.4, 0.6], gap="medium")
        
        with col_c1:
            st.subheader("Inputs")
            
            st.markdown("**Geometry**")
            H_left = st.number_input("Passive Wedge Height (H_p) [m]", 1.0, 10.0, 3.0, key="blk_Hp")
            H_right = st.number_input("Active Wedge Height (H_a) [m]", 1.0, 20.0, 8.0, key="blk_Ha")
            L_block = st.number_input("Block Length (L) [m]", 1.0, 50.0, 12.0, key="blk_L")
            
            st.markdown("**Forces**")
            Pa = st.number_input("Active Thrust (Driving) Pa [kN]", 0.0, 5000.0, 500.0, key="block_Pa")
            Pp = st.number_input("Passive Resistance (Resisting) Pp [kN]", 0.0, 5000.0, 200.0, key="block_Pp")
            W_block = st.number_input("Weight of Central Block [kN]", 0.0, 10000.0, 2000.0, key="block_W")
            
            st.markdown("**Weak Layer**")
            c_base = st.number_input("Base Cohesion (c') [kPa]", 0.0, 100.0, 5.0, key="block_c")
            phi_base = st.number_input("Base Friction (ϕ') [deg]", 0.0, 45.0, 20.0, key="block_phi")
            
            calc_blk = st.button("Calculate FS", type="primary", key="btn_calc_block")

        with col_c2:
            st.subheader("Block & Wedge Diagram")
            fig_b, ax_b = plt.subplots(figsize=(8, 4))
            
            # Draw Geometry matching User Image
            wedge_L_width = H_left 
            wedge_R_width = H_right
            
            # 1. Passive Wedge (Left)
            passive_poly = [[0, 0], [wedge_L_width, H_left], [wedge_L_width, 0]]
            ax_b.add_patch(patches.Polygon(passive_poly, facecolor='#A5D6A7', edgecolor='black', alpha=0.5))
            ax_b.text(wedge_L_width/2, H_left/3, "Passive\nWedge", ha='center', fontsize=8)
            ax_b.text(wedge_L_width/2, 0.2, "45-ϕ/2", fontsize=7)
            
            # 2. Central Block
            block_x_start = wedge_L_width
            block_x_end = wedge_L_width + L_block
            block_poly = [
                [block_x_start, 0], [block_x_start, H_left], 
                [block_x_end, H_right], [block_x_end, 0]
            ]
            ax_b.add_patch(patches.Polygon(block_poly, facecolor='lightgrey', edgecolor='black', hatch='//', alpha=0.5))
            ax_b.text((block_x_start+block_x_end)/2, (H_left+H_right)/4, "BLOCK", ha='center', fontweight='bold')
            
            # 3. Active Wedge (Right)
            active_poly = [[block_x_end, 0], [block_x_end, H_right], [block_x_end + wedge_R_width, H_right]]
            ax_b.add_patch(patches.Polygon(active_poly, facecolor='#FFCCBC', edgecolor='black', alpha=0.5))
            ax_b.text(block_x_end + wedge_R_width/3, H_right*0.8, "Active\nWedge", ha='center', fontsize=8)
            ax_b.text(block_x_end + wedge_R_width/2, 0.2, "45+ϕ/2", fontsize=7)
            
            # 4. Forces
            ax_b.arrow(block_x_end + 1.5, H_right/3, -1.5, 0, head_width=0.3, color='red', width=0.05)
            ax_b.text(block_x_end + 1.6, H_right/3, "Pa", color='red', fontweight='bold', va='center')
            
            ax_b.arrow(block_x_start - 1.5, H_left/3, 1.5, 0, head_width=0.3, color='green', width=0.05)
            ax_b.text(block_x_start - 2.0, H_left/3, "Pp", color='green', fontweight='bold', va='center')
            
            ax_b.text((block_x_start+block_x_end)/2, -0.5, r"$\tau_f$ (Weak Layer)", ha='center')
            ax_b.arrow((block_x_start+block_x_end)/2, 0, -2, 0, head_width=0.2, color='black') # Resisting shear
            
            ax_b.annotate(f"L={L_block}m", xy=(block_x_start, -1), xytext=(block_x_end, -1), arrowprops=dict(arrowstyle='<->'))

            ax_b.set_xlim(-2, block_x_end + wedge_R_width + 2)
            ax_b.set_ylim(-2, H_right + 2)
            ax_b.axis('off')
            st.pyplot(fig_b)
            
            if calc_blk:
                resisting_base = (c_base * L_block) + (W_block * math.tan(math.radians(phi_base)))
                total_resisting = Pp + resisting_base
                total_driving = Pa
                
                if total_driving > 0:
                    FS_block = total_resisting / total_driving
                    st.markdown("### Results")
                    st.latex(r"FS = \frac{P_p + (c'L + W_{block}\tan\phi')}{P_a}")
                    st.write(f"**Base Resistance:** {resisting_base:.1f} kN")
                    st.write(f"**Total Resisting:** {total_resisting:.1f} kN")
                    
                    if FS_block < 1: st.error(f"**FS = {FS_block:.2f} (Unstable)**")
                    else: st.success(f"**FS = {FS_block:.2f} (Stable)**")
                else:
                    st.error("Active Thrust (Pa) must be > 0")

if __name__ == "__main__":
    app()
