import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ============================================================
# MAINTENANCE BANNER
# ============================================================
def show_maintenance_banner():
    st.markdown("""
    <div style="background: linear-gradient(90deg, #ff6b6b 0%, #ffa500 100%); 
                padding: 15px; 
                border-radius: 10px; 
                border: 3px solid #cc0000;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0; text-align: center;">
             UNDER MAINTENANCE 
        </h2>
        <p style="color: white; margin: 10px 0 0 0; text-align: center; font-size: 16px;">
            Flow net calculations are currently being calibrated and improved.<br>
            Results may not be accurate. Please use with caution.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_scientific(val):
    if val == 0:
        return "0"
    exponent = int(np.floor(np.log10(abs(val))))
    mantissa = val / (10**exponent)
    if -3 < exponent < 4:
        return f"{val:.4f}"
    return f"{mantissa:.2f} \\times 10^{{{exponent}}}"

def get_complex_potential_sheet_pile(x, y, pile_depth, pile_x, h_up, h_down, soil_depth):
    """
    CORRECTED Sheet Pile Flow Net based on soil mechanics principles.
    
    Key observations from hand sketch:
    1. Flow lines (blue) start horizontal upstream, curve DOWN around pile, exit horizontal downstream
    2. Equipotentials (red dashed) are nearly vertical far away, curve around pile tip
    3. Flow concentrates at PILE TIP (bottom of pile)
    4. Pattern is symmetric-ish but biased by head difference
    """
    
    # Pile tip location (critical point)
    pile_tip_x = pile_x
    pile_tip_y = -pile_depth
    
    # Create complex coordinates
    z = x + 1j * y
    z_tip = pile_tip_x + 1j * pile_tip_y
    
    # Distance from pile tip
    z_from_tip = z - z_tip
    
    # Avoid singularity
    epsilon = 0.01
    z_from_tip = np.where(np.abs(z_from_tip) < epsilon, epsilon * (1 + 1j), z_from_tip)
    
    with np.errstate(all="ignore"):
        # COMPONENT 1: Uniform horizontal flow (baseline seepage)
        # This creates the horizontal flow from left to right
        flow_velocity = (h_up - h_down) / 24.0  # Normalized velocity
        W_uniform = flow_velocity * z
        
        # COMPONENT 2: Source at pile tip (creates flow diverging from tip)
        # Water flows OUT from underneath the pile
        source_strength = pile_depth * flow_velocity * 8.0
        W_source = source_strength * np.log(z_from_tip + 0j)
        
        # COMPONENT 3: Dipole to create asymmetry and proper flow pattern
        # This makes flow go AROUND the pile (up and down)
        dipole_strength = pile_depth**1.5 * flow_velocity * 6.0
        W_dipole = dipole_strength / z_from_tip
        
        # COMPONENT 4: Image system for impervious base
        # Reflection from bottom boundary
        z_from_base = z - (pile_tip_x + 1j * (-soil_depth))
        z_from_base = np.where(np.abs(z_from_base) < epsilon, epsilon * (1 + 1j), z_from_base)
        W_base = -source_strength * 0.3 * np.log(z_from_base + 0j)
        
        # Combine all components
        W = W_uniform + W_source + W_dipole + W_base
        
        return W

def get_complex_potential_dam(x, y, dam_width, h_up, h_down):
    """
    Flow under concrete dam - uses conformal mapping.
    """
    b = max(dam_width / 2, 0.1)
    z = x + 1j * y
    
    with np.errstate(all="ignore"):
        # Normalize
        zeta = z / b
        
        # Conformal transformation for flow under rectangular dam
        # Schwarz-Christoffel approximation
        w = b * (zeta + np.sqrt(zeta**2 - 1 + 0j))
        
        # Scale by head difference
        flow_scale = (h_up - h_down) / 20.0
        W = flow_scale * w
        
        return W

def get_complex_potential(x, y, mode, pile_depth, pile_x, dam_width, h_up, h_down, soil_depth):
    """
    Main function to get complex potential based on mode.
    Returns W = Phi + i*Psi
    """
    
    if mode == "Sheet Pile Only":
        return get_complex_potential_sheet_pile(x, y, pile_depth, pile_x, h_up, h_down, soil_depth)
    
    elif mode == "Concrete Dam Only":
        return get_complex_potential_dam(x, y, dam_width, h_up, h_down)
    
    elif mode == "Combined (Dam + Pile)":
        # Superpose both effects
        W_pile = get_complex_potential_sheet_pile(x, y, pile_depth, pile_x, h_up, h_down, soil_depth)
        W_dam = get_complex_potential_dam(x, y, dam_width, h_up, h_down)
        return 0.6 * W_pile + 0.4 * W_dam
    
    return 0 + 0j

def calculate_pore_pressure(px, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d):
    """
    Calculate pore pressure at point (px, py) based on flow net.
    """
    
    if py > 0:
        return None  # Above ground surface
    
    gamma_w = 10  # kN/m³
    
    # Get complex potential at point
    w_pt = get_complex_potential(px, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d)
    phi_pt = np.real(w_pt)
    
    # Get boundary values
    w_up = get_complex_potential(-15.0, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d)
    w_down = get_complex_potential(15.0, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d)
    
    phi_up = np.real(w_up)
    phi_down = np.real(w_down)
    
    # Handle numerical issues
    if not np.isfinite(phi_pt) or not np.isfinite(phi_up) or not np.isfinite(phi_down):
        return None
    
    # Interpolate total head
    if abs(phi_up - phi_down) < 1e-6:
        h_total = (h_up + h_down) / 2
    else:
        ratio = (phi_pt - phi_down) / (phi_up - phi_down)
        ratio = np.clip(ratio, 0, 1)
        h_total = h_down + ratio * (h_up - h_down)
    
    # Calculate pore pressure
    pressure_head = h_total - py
    u = pressure_head * gamma_w
    
    return {"u": u, "h_total": h_total, "pressure_head": pressure_head}

# ============================================================
# MAIN APP
# ============================================================

def app():

    
    tab1, tab2 = st.tabs(["1D Seepage", "Permeability"])
    
# =================================================================
    # TAB 1: 1D SEEPAGE (Effective Stress)
    # =================================================================
    with tab1:
        st.caption("Determine Effective Stress at Point A. (Datum is at the Bottom of Soil)")
        
        col_setup, col_plot = st.columns([1, 1.2])
        
        with col_setup:
            st.markdown("### 1. Problem Setup")
            val_z = st.number_input("Soil Specimen Height (z) [m]", 0.1, step=0.5, value=4.0)
            val_y = st.number_input("Water Height above Soil (y) [m]", 0.0, step=0.5, value=2.0)
            val_x = st.number_input("Piezometer Head at Bottom (x) [m]", 0.0, step=0.5, value=7.5)
            gamma_sat = st.number_input("Saturated Unit Weight (γ_sat) [kN/m³]", 18.0, step=0.1)
            gamma_w = 10
            val_A = st.slider("Height of Point 'A' from Datum [m]", 0.0, val_z, val_z/2)

            st.markdown("---")
            
            # --- THIS WAS MISSING ---
                        if st.button("Calculate Effective Stress", type="primary"):
                # --- PRELIMINARY CALCULATIONS ---
                gamma_sub = gamma_sat - gamma_w  # Effective Unit Weight
                
                # Heads
                H_top = val_z + val_y
                H_bot = val_x
                delta_H = H_top - H_bot
                
                # Flow Direction & Gradient
                if delta_H > 0.001:
                    flow_type = "Downward"
                    i = abs(delta_H) / val_z
                elif delta_H < -0.001:
                    flow_type = "Upward"
                    i = abs(delta_H) / val_z
                else:
                    flow_type = "No Flow (Hydrostatic)"
                    i = 0.0

                # Geometry
                depth_A_soil = val_z - val_A

                # --- METHOD 1: Total Stress - Pore Pressure ---
                sigma_total = (val_y * gamma_w) + (depth_A_soil * gamma_sat)
                
                H_A = H_bot + (val_A / val_z) * (H_top - H_bot) 
                h_p_A = H_A - val_A 
                u_val = h_p_A * gamma_w
                
                sigma_prime_1 = sigma_total - u_val

                # --- METHOD 2: Seepage Force Approach ---
                seepage_force = i * gamma_w
                if flow_type == "Downward":
                    bracket_term = gamma_sub + seepage_force
                elif flow_type == "Upward":
                    bracket_term = gamma_sub - seepage_force
                else:
                    bracket_term = gamma_sub
                
                sigma_prime_2 = depth_A_soil * bracket_term

                # --- DISPLAY RESULTS (STACKED FOR VISIBILITY) ---
                st.success(f"**Flow Condition:** {flow_type} ($i = {i:.3f}$)")
                
                # REMOVED st.columns(3) HERE TO FIX TRUNCATION
                st.metric("Total Stress (σ)", f"{sigma_total:.2f} kPa")
                st.metric("Pore Pressure (u)", f"{u_val:.2f} kPa")
                # Highlight the final answer
                st.markdown(f"""
                <div style="padding:10px; border:1px solid #4CAF50; border-radius:5px; background-color:rgba(76, 175, 80, 0.1);">
                    <h3 style="margin:0; color:#4CAF50;">Effective Stress (σ') = {sigma_prime_1:.2f} kPa</h3>
                </div>
                """, unsafe_allow_html=True)

                # --- DETAILED CALCULATION EXPANDER ---
                with st.expander("View Detailed Step-by-Step Derivation (2 Methods)", expanded=True):
                    
                    st.markdown("#### **Method 1: Definition ($\sigma' = \sigma - u$)**")
                    st.latex(rf"\text{{Depth of A into soil }} (z) = {val_z} - {val_A} = {depth_A_soil:.2f} \text{{ m}}")
                    
                    st.markdown("**Step 1: Total Stress ($\sigma$)**")
                    st.latex(rf"\sigma = ({gamma_w} \cdot {val_y}) + ({gamma_sat} \cdot {depth_A_soil:.2f}) = \mathbf{{{sigma_total:.2f} \text{{ kPa}}}}")
                    
                    st.markdown("**Step 2: Pore Water Pressure ($u$)**")
                    st.latex(rf"u = ({H_A:.2f} - {val_A:.2f}) \cdot {gamma_w} = \mathbf{{{u_val:.2f} \text{{ kPa}}}}")
                    
                    st.markdown("**Step 3: Effective Stress**")
                    st.latex(rf"\sigma' = {sigma_total:.2f} - {u_val:.2f} = \mathbf{{{sigma_prime_1:.2f} \text{{ kPa}}}}")

                    st.markdown("---")

                    st.markdown("#### **Method 2: Seepage Force ($\sigma' = z(\gamma' \pm i \gamma_w)$)**")
                    st.markdown(f"**Step 1:** $\gamma' = {gamma_sub:.2f}$ | $i = {i:.3f}$")
                    
                    if flow_type == "Downward":
                        sign_latex = "+"
                    elif flow_type == "Upward":
                        sign_latex = "-"
                    else:
                        sign_latex = "\pm"
                    
                    st.latex(rf"\sigma' = {depth_A_soil:.2f} \cdot [{gamma_sub:.2f} {sign_latex} ({i:.3f} \cdot {gamma_w})]")
                    st.latex(rf"\sigma' = {depth_A_soil:.2f} \cdot [{bracket_term:.2f}] = \mathbf{{{sigma_prime_2:.2f} \text{{ kPa}}}}")

        with col_plot:
            fig, ax = plt.subplots(figsize=(7, 8))
            # ... (Rest of your plotting code remains exactly the same)
            
            datum_y = 0.0
            soil_w = 2.5
            soil_x = 3.5  
            wl_top = val_z + val_y  
            wl_bot = val_x          
            
            if wl_top > wl_bot: flow_arrow = "⬇️"
            elif wl_bot > wl_top: flow_arrow = "⬆️"
            else: flow_arrow = "No Flow"

            ax.add_patch(patches.Rectangle((soil_x, datum_y), soil_w, val_z, 
    # =================================================================
    # TAB 1: 1D SEEPAGE (Effective Stress)
    # =================================================================
    with tab1:
        st.caption("Determine Effective Stress at Point A. (Datum is at the Bottom of Soil)")
        
        col_setup, col_plot = st.columns([1, 1.2])
        
        with col_setup:
            st.markdown("### 1. Problem Setup")
            val_z = st.number_input("Soil Specimen Height (z) [m]", 0.1, step=0.5, value=4.0)
            val_y = st.number_input("Water Height above Soil (y) [m]", 0.0, step=0.5, value=2.0)
            val_x = st.number_input("Piezometer Head at Bottom (x) [m]", 0.0, step=0.5, value=7.5)
            gamma_sat = st.number_input("Saturated Unit Weight (γ_sat) [kN/m³]", 18.0, step=0.1)
            gamma_w = 10
            val_A = st.slider("Height of Point 'A' from Datum [m]", 0.0, val_z, val_z/2)

            st.markdown("---")
            
            # FIXED INDENTATION HERE:
            if st.button("Calculate Effective Stress", type="primary"):
                # --- PRELIMINARY CALCULATIONS ---
                gamma_sub = gamma_sat - gamma_w  # Effective Unit Weight
                
                # Heads
                H_top = val_z + val_y
                H_bot = val_x
                delta_H = H_top - H_bot
                
                # Flow Direction & Gradient
                if delta_H > 0.001:
                    flow_type = "Downward"
                    i = abs(delta_H) / val_z
                elif delta_H < -0.001:
                    flow_type = "Upward"
                    i = abs(delta_H) / val_z
                else:
                    flow_type = "No Flow (Hydrostatic)"
                    i = 0.0

                # Geometry
                depth_A_soil = val_z - val_A

                # --- METHOD 1: Total Stress - Pore Pressure ---
                sigma_total = (val_y * gamma_w) + (depth_A_soil * gamma_sat)
                
                H_A = H_bot + (val_A / val_z) * (H_top - H_bot) 
                h_p_A = H_A - val_A 
                u_val = h_p_A * gamma_w
                
                sigma_prime_1 = sigma_total - u_val

                # --- METHOD 2: Seepage Force Approach ---
                seepage_force = i * gamma_w
                if flow_type == "Downward":
                    bracket_term = gamma_sub + seepage_force
                elif flow_type == "Upward":
                    bracket_term = gamma_sub - seepage_force
                else:
                    bracket_term = gamma_sub
                
                sigma_prime_2 = depth_A_soil * bracket_term

                # --- DISPLAY RESULTS (STACKED FOR VISIBILITY) ---
                st.success(f"**Flow Condition:** {flow_type} ($i = {i:.3f}$)")
                
                # Metrics are stacked vertically now (No columns)
                st.metric("Total Stress (σ)", f"{sigma_total:.2f} kPa")
                st.metric("Pore Pressure (u)", f"{u_val:.2f} kPa")
                
                # Highlight the final answer
                st.markdown(f"""
                <div style="padding:10px; border:1px solid #4CAF50; border-radius:5px; background-color:rgba(76, 175, 80, 0.1);">
                    <h3 style="margin:0; color:#4CAF50;">Effective Stress (σ') = {sigma_prime_1:.2f} kPa</h3>
                </div>
                """, unsafe_allow_html=True)

                # --- DETAILED CALCULATION EXPANDER ---
                with st.expander("View Detailed Step-by-Step Derivation (2 Methods)", expanded=True):
                    
                    st.markdown("#### **Method 1: Definition ($\sigma' = \sigma - u$)**")
                    st.latex(rf"\text{{Depth of A into soil }} (z) = {val_z} - {val_A} = {depth_A_soil:.2f} \text{{ m}}")
                    
                    st.markdown("**Step 1: Total Stress ($\sigma$)**")
                    st.latex(rf"\sigma = ({gamma_w} \cdot {val_y}) + ({gamma_sat} \cdot {depth_A_soil:.2f}) = \mathbf{{{sigma_total:.2f} \text{{ kPa}}}}")
                    
                    st.markdown("**Step 2: Pore Water Pressure ($u$)**")
                    st.latex(rf"u = ({H_A:.2f} - {val_A:.2f}) \cdot {gamma_w} = \mathbf{{{u_val:.2f} \text{{ kPa}}}}")
                    
                    st.markdown("**Step 3: Effective Stress**")
                    st.latex(rf"\sigma' = {sigma_total:.2f} - {u_val:.2f} = \mathbf{{{sigma_prime_1:.2f} \text{{ kPa}}}}")

                    st.markdown("---")

                    st.markdown("#### **Method 2: Seepage Force ($\sigma' = z(\gamma' \pm i \gamma_w)$)**")
                    st.markdown(f"**Step 1:** $\gamma' = {gamma_sub:.2f}$ | $i = {i:.3f}$")
                    
                    if flow_type == "Downward":
                        sign_latex = "+"
                    elif flow_type == "Upward":
                        sign_latex = "-"
                    else:
                        sign_latex = "\pm"
                    
                    st.latex(rf"\sigma' = {depth_A_soil:.2f} \cdot [{gamma_sub:.2f} {sign_latex} ({i:.3f} \cdot {gamma_w})]")
                    st.latex(rf"\sigma' = {depth_A_soil:.2f} \cdot [{bracket_term:.2f}] = \mathbf{{{sigma_prime_2:.2f} \text{{ kPa}}}}")

    # =================================================================
    # TAB 2: PERMEABILITY
    # =================================================================
    with tab2:
        st.caption("Calculate Coefficient of Permeability (k). Input variables are marked on the diagram.")
        col_input_2, col_plot_2 = st.columns([1, 1.2])

        with col_input_2:
            st.markdown("### 1. Test Configuration")
            test_type = st.radio("Select Method", ["Constant Head", "Falling Head"], horizontal=True)
            st.markdown("---")

            if "Constant" in test_type:
                st.latex(r"k = \frac{Q \cdot L}{A \cdot h \cdot t}")
                Q = st.number_input("Collected Volume (Q) [cm³]", value=500.0)
                L = st.number_input("Specimen Length (L) [cm]", value=15.0)
                h = st.number_input("Head Difference (h) [cm]", value=40.0)
                A = st.number_input("Specimen Area (A) [cm²]", value=40.0)
                t = st.number_input("Time Interval (t) [sec]", value=60.0)
                
                st.markdown("---")
                if st.button("Calculate Permeability (k)", type="primary"):
                    if A*h*t > 0: 
                        k_val = (Q*L)/(A*h*t)
                        k_formatted = format_scientific(k_val)
                        st.success(f"**Permeability Coefficient (k)**\n\n$${k_formatted} \\text{{ cm/sec}}$$")
                        st.markdown(f"""
                        <div style="background-color: #d1e7dd; padding: 20px; border-radius: 10px; border: 1px solid #0f5132; text-align: center; margin-top: 20px;">
                            <p style="color: #0f5132; margin-bottom: 8px; font-size: 16px; font-weight: 600;">Permeability Coefficient (k)</p>
                            <h2 style="color: #0f5132; margin: 0; font-size: 28px; font-weight: 800;">
                                $${k_formatted} \\text{{ cm/sec}}$$
                            </h2>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Inputs must be positive.")

            else:
                st.latex(r"k = 2.303 \frac{a \cdot L}{A \cdot t} \log_{10}\left(\frac{h_1}{h_2}\right)")
                a = st.number_input("Standpipe Area (a) [cm²]", format="%.4f", value=0.5)
                A_soil = st.number_input("Soil Specimen Area (A) [cm²]", value=40.0)
                L_fall = st.number_input("Specimen Length (L) [cm]", value=15.0)
                h1 = st.number_input("Initial Head (h1) [cm]", value=50.0)
                h2 = st.number_input("Final Head (h2) [cm]", value=30.0)
                t_fall = st.number_input("Time Interval (t) [sec]", value=300.0)

                st.markdown("---")
                if st.button("Calculate Permeability (k)", type="primary"):
                    if A_soil*t_fall > 0 and h2 > 0: 
                        k_val = (2.303*a*L_fall/(A_soil*t_fall))*np.log10(h1/h2)
                        k_formatted = format_scientific(k_val)
                        st.success(f"**Permeability Coefficient (k)**\n\n$${k_formatted} \\text{{ cm/sec}}$$")
                    else:
                        st.error("Inputs invalid. h2 must be > 0.")

        with col_plot_2:
            fig2, ax2 = plt.subplots(figsize=(6, 8))
            ax2.set_xlim(0, 10); ax2.set_ylim(0, 10); ax2.axis('off')
            soil_color, water_color, wall_color = '#E3C195', '#D6EAF8', 'black'

            if "Constant" in test_type:
                ax2.add_patch(patches.Rectangle((2, 8), 4, 1.5, facecolor=water_color, edgecolor=wall_color))
                ax2.text(2.2, 8.2, "Supply\nTank", fontsize=8)
                ax2.plot([2, 6], [9, 9], 'b-', lw=2); ax2.plot(4, 9, marker='v', color='blue')
                
                ax2.add_patch(patches.Rectangle((3.8, 6), 0.4, 2, facecolor=water_color, edgecolor='none'))
                ax2.plot([3.8, 3.8], [6, 8], 'k-'); ax2.plot([4.2, 4.2], [6, 8], 'k-')

                ax2.add_patch(patches.Rectangle((3, 4), 2, 2, facecolor=soil_color, hatch='X', edgecolor=wall_color, lw=2))
                ax2.text(4, 5, "SOIL\nArea A", ha='center', va='center', fontweight='bold')
                
                ax2.add_patch(patches.Rectangle((3.8, 2.5), 0.4, 1.5, facecolor=water_color, edgecolor='none'))
                ax2.plot([3.8, 3.8], [2.5, 4], 'k-'); ax2.plot([4.2, 4.2], [2.5, 4], 'k-')
                ax2.add_patch(patches.Rectangle((3.5, 1), 3, 1.5, facecolor=water_color, edgecolor=wall_color))
                ax2.text(6, 0.5, "Collection\nTank", ha='center')
                ax2.plot([3.5, 6.5], [2.2, 2.2], 'b-', lw=2); ax2.plot(6, 2.2, marker='v', color='blue')

                ax2.annotate('', xy=(8, 2.2), xytext=(8, 9), arrowprops=dict(arrowstyle='<->', lw=1.5))
                ax2.text(8.2, 5.5, "h (Head Diff)", ha='left', fontweight='bold', fontsize=12, color='blue')
                ax2.plot([6, 8.2], [9, 9], 'k--', lw=0.5); ax2.plot([6.5, 8.2], [2.2, 2.2], 'k--', lw=0.5)

                ax2.annotate('', xy=(1.5, 4), xytext=(1.5, 6), arrowprops=dict(arrowstyle='<->', lw=1.5))
                ax2.text(1.2, 5, "L", ha='right', fontweight='bold', fontsize=12)
                ax2.plot([1.5, 3], [4, 4], 'k--', lw=0.5); ax2.plot([1.5, 3], [6, 6], 'k--', lw=0.5)
                ax2.text(6.8, 1.5, "-> Q (Vol)", ha='left', fontstyle='italic')

            else:
                ax2.add_patch(patches.Rectangle((3.8, 6), 0.4, 3.5, facecolor=water_color, edgecolor=wall_color))
                ax2.text(3.5, 8, "Standpipe\n(Area a)", ha='right', fontsize=9)
                ax2.add_patch(patches.Rectangle((3, 4), 2, 2, facecolor=soil_color, hatch='X', edgecolor=wall_color, lw=2))
                ax2.text(4, 5, "SOIL\nArea A", ha='center', va='center', fontweight='bold')
                ax2.add_patch(patches.Rectangle((3.8, 2), 0.4, 2, facecolor=water_color, edgecolor='none'))
                ax2.plot([3.8, 3.8], [2, 4], 'k-'); ax2.plot([4.2, 4.2], [2, 4], 'k-')
                ax2.add_patch(patches.Rectangle((3.5, 1), 3, 1.5, facecolor=water_color, edgecolor=wall_color))
                ax2.plot([3.5, 6.5], [2, 2], 'b-', lw=2); ax2.plot(6, 2, marker='v', color='blue')

                ax2.plot([3.8, 4.2], [9, 9], 'r-', lw=2); ax2.text(4.4, 9, "Start", fontsize=8, color='red')
                ax2.plot([3.8, 4.2], [7, 7], 'r-', lw=2); ax2.text(4.4, 7, "End", fontsize=8, color='red')

                ax2.annotate('', xy=(8, 2), xytext=(8, 9), arrowprops=dict(arrowstyle='<->', color='red'))
                ax2.text(8.2, 9, "h1", ha='left', fontweight='bold', color='red')
                ax2.plot([4.2, 8.2], [9, 9], 'r--', lw=0.5)
                ax2.annotate('', xy=(7, 2), xytext=(7, 7), arrowprops=dict(arrowstyle='<->', color='red'))
                ax2.text(7.2, 7, "h2", ha='left', fontweight='bold', color='red')
                ax2.plot([4.2, 7.2], [7, 7], 'r--', lw=0.5)
                ax2.plot([6.5, 8.2], [2, 2], 'b--', lw=0.5)

                ax2.annotate('', xy=(1.5, 4), xytext=(1.5, 6), arrowprops=dict(arrowstyle='<->', lw=1.5))
                ax2.text(1.2, 5, "L", ha='right', fontweight='bold', fontsize=12)
                ax2.plot([1.5, 3], [4, 4], 'k--', lw=0.5); ax2.plot([1.5, 3], [6, 6], 'k--', lw=0.5)

            st.pyplot(fig2)

if __name__ == "__main__":
    app()
