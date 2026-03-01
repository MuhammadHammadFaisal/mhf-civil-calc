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
            nx = math.sin(beta_r)
            ny = -math.cos(beta_r)
            
            x_fail = x + nx * z
            y_fail = y_surf + ny * z
            
            ax_t.plot(x, y_surf, 'k-', linewidth=2, label="Ground Surface")
            ax_t.plot(x, y_fail, 'r--', linewidth=2, label="Failure Plane")
            ax_t.fill_between(x, y_surf, y_fail, where=(y_surf >= y_fail),
                  color='#E6D690', alpha=0.5)
            
            if m_ratio > 0:
                ax_t.plot(x, y_surf - 0.2, 'b--', linewidth=1, label="Water Table / Seepage Line")
            
            ax_t.text(5, 5*math.tan(beta_r) + 1, f"β={beta}°", ha='center')
            # Draw normal depth arrow
            x0 = 5
            y0 = 5 * math.tan(beta_r)
            
            ax_t.arrow(
                x0,
                y0,
                nx * z,
                ny * z,
                length_includes_head=True,
                head_width=0.2,
                color='black'
            )
            
            ax_t.text(
                x0 + nx * z / 2,
                y0 + ny * z / 2,
                f"z={z}m",
                va='center'
            )
            ax_t.text(5.2, 5*math.tan(beta_r) - z/2, f"z={z}m", va='center')

            ax_t.set_aspect('equal')
            ax_t.legend()
            ax_t.axis('off')
            st.pyplot(fig_t)
            plt.close(fig_t)
            
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
                if sigma_eff < 0:
                    st.warning("Effective stress is negative (possible tension condition).")

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
                o_x = st.number_input("Center X-coord (o_x) [m]", -20.0, 20.0, -2.0, key="mass_ox")
                dist_d = st.number_input("Moment Arm (d) [m]", 0.0, 20.0, 4.5, help="Horizontal distance from Center O to Centroid", key="mass_d")
                st.caption("⚠️ **Note:** This calculation currently assumes a toe failure. The circle geometry is forced to intersect the slope toe at coordinates (0,0).")
                st.subheader("2. Soil Properties")
                gamma_clay = st.number_input("Unit Weight (γ) [kN/m³]", 10.0, 25.0, 19.0, key="mass_gamma")
                # Minimum cohesion set to 0.0
                Cu = st.number_input("Undrained Shear Strength (Cu) [kPa]", 0.0, 200.0, 65.0, key="mass_cu")
                
                st.caption("Weight Calculation:")
                area_approx = st.number_input("Area of Sliding Mass [m²]", 1.0, 500.0, 70.0, key="mass_area")
                W_calc = area_approx * gamma_clay
                st.write(f"Weight (W) = {W_calc:.1f} kN/m")
                
                # --- TENSION CRACK & WATER ---
                z_c = 0.0
                water_crack = False
                
                # Only calculate and display if the soil actually has cohesion
                if Cu > 0:
                    st.markdown("**Tension Crack**")
                    if gamma_clay > 0:
                        z_c = (2 * Cu) / gamma_clay
                    z_c = min(z_c, H_slope) # Ensure crack isn't deeper than slope
                    
                    st.info(f"Tension Crack Depth ($z_c$) = **{z_c:.2f} m**")
                    
                    if z_c > 0:
                        water_crack = st.checkbox("Crack filled with water (Adds driving force)", value=False)
            with col_r2:
                st.subheader("Failure Diagram")
                fig_c, ax_c = plt.subplots(figsize=(8, 6))
                
                # 1. Slope Geometry
                X_crest = H_slope / math.tan(math.radians(beta_slope)) if beta_slope > 0 else 10
                Y_crest = H_slope
                
                ground_x = [-10, 0, X_crest, X_crest + 10]
                ground_y = [0, 0, Y_crest, Y_crest]
                
                ax_c.plot(ground_x, ground_y, 'k-', linewidth=2.5, label="Ground Surface")
                
                y_crack_bottom = Y_crest - z_c
                
                # 2. Failure Circle (Arc)
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
                        
                        # 3. Create the "Wedge" Polygon
                        poly_verts = list(zip(arc_x, arc_y))
                        if z_c > 0:
                            poly_verts.append((x_intersect, Y_crest)) 
                        poly_verts.append((X_crest, Y_crest)) 
                        poly_verts.append((0, 0)) 
                        
                        soil_mass = patches.Polygon(poly_verts, closed=True, facecolor='none', edgecolor='black', hatch='//', alpha=0.5)
                        ax_c.add_patch(soil_mass)
                        ax_c.plot(arc_x, arc_y, 'k-', linewidth=1.5)
                        
                        # Draw Tension Crack
                        if z_c > 0:
                            ax_c.plot([x_intersect, x_intersect], [y_crack_bottom, Y_crest], 'r-', linewidth=2, label="Tension Crack")
                            # Draw water force if checked
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

                    # Annotations
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
                st.subheader("Slice Representation")
                fig_slice, ax_slice = plt.subplots(figsize=(8, 6))
                
                # 1. Static "Not to Scale" Geometry
                # Ground surface (fixed dimensions for visual reference)
                ground_x = [-3, 0, 12, 22]
                ground_y = [0, 0, 10, 10]
                ax_slice.plot(ground_x, ground_y, 'k-', linewidth=2.5, label="Ground Surface")
                
                # Failure Arc (Fixed circular arc passing from toe to crest)
                o_x, o_y = 4.0, 15.0
                R = math.sqrt(o_x**2 + o_y**2) # Radius to pass through (0,0)
                
                # Generate points for the smooth slip circle
                arc_x_full = np.linspace(0, 18, 100)
                arc_y_full = o_y - np.sqrt(R**2 - (arc_x_full - o_x)**2)
                ax_slice.plot(arc_x_full, arc_y_full, 'r-', linewidth=2.5, label="Slip Surface")
                
                # Add "NOT TO SCALE" indicator exactly like the textbook
                ax_slice.text(15, 13, "— NOT TO SCALE —", ha='center', fontsize=10, fontweight='bold')
                
                # 2. Dynamic Slices based on User Table Rows
                num_slices = len(edited_df)
                if num_slices > 0:
                    # Evenly divide the arc based on the number of slices in the table
                    slice_edges = np.linspace(0, 18, num_slices + 1)
                    
                    for i in range(num_slices):
                        x_left = slice_edges[i]
                        x_right = slice_edges[i+1]
                        
                        # Calculate bottom bounds on the arc
                        y_b_left = o_y - math.sqrt(R**2 - (x_left - o_x)**2)
                        y_b_right = o_y - math.sqrt(R**2 - (x_right - o_x)**2)
                        
                        # Calculate top bounds on the ground surface
                        y_t_left = np.interp(x_left, ground_x, ground_y)
                        y_t_right = np.interp(x_right, ground_x, ground_y)
                        
                        # Draw the closed polygon for the slice
                        poly = [[x_left, y_b_left], [x_right, y_b_right], 
                                [x_right, y_t_right], [x_left, y_t_left]]
                        
                        slice_patch = patches.Polygon(poly, edgecolor='black', facecolor='lightgrey', alpha=0.5)
                        ax_slice.add_patch(slice_patch)
                        
                        # Center coordinates for text labels
                        mid_x = (x_left + x_right) / 2
                        mid_y = (max(y_b_left, y_b_right) + min(y_t_left, y_t_right)) / 2
                        
                        # Get user's actual data from the table to display
                        row = edited_df.iloc[i]
                        slice_num = int(row['Slice'])
                        weight = row['Weight (kN)']
                        
                        # Draw vertical dashed line down the center of the slice
                        y_b_mid = o_y - math.sqrt(R**2 - (mid_x - o_x)**2)
                        y_t_mid = np.interp(mid_x, ground_x, ground_y)
                        ax_slice.plot([mid_x, mid_x], [y_b_mid, y_t_mid], 'k--', linewidth=0.5)
                        
                        # Label the slice with its ID and Weight
                        ax_slice.text(mid_x, mid_y, f"S{slice_num}\n{weight}kN", 
                                      ha='center', va='center', fontsize=8, fontweight='bold')

                ax_slice.set_aspect('equal')
                ax_slice.set_xlim(-4, 24)
                ax_slice.set_ylim(-4, 16)
                ax_slice.axis('off')
                
                st.pyplot(fig_slice)
                plt.close(fig_slice)

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
            plt.close(fig_b)
            
            if calc_blk:
                resisting_base = (c_base * L_block) + (W_block * math.tan(math.radians(phi_base)))
                total_resisting = Pp + resisting_base
                total_driving = Pa
                
                if total_driving > 0:
                    FS_block = total_resisting / total_driving
                    st.markdown("### Results")
                    st.latex(r"FS = \frac{P_p + (c'L + W_{block}\\tan\\phi')}{P_a}")
                    st.write(f"**Base Resistance:** {resisting_base:.1f} kN")
                    st.write(f"**Total Resisting:** {total_resisting:.1f} kN")
                    
                    if FS_block < 1: st.error(f"**FS = {FS_block:.2f} (Unstable)**")
                    else: st.success(f"**FS = {FS_block:.2f} (Stable)**")
                else:
                    st.error("Active Thrust (Pa) must be > 0")

if __name__ == "__main__":
    app()
