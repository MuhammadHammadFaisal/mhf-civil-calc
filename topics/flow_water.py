import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

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
    # Pile tip location
    pile_tip_x = pile_x
    pile_tip_y = -pile_depth
    
    z = x + 1j * y
    z_tip = pile_tip_x + 1j * pile_tip_y
    z_from_tip = z - z_tip
    
    epsilon = 0.01
    z_from_tip = np.where(np.abs(z_from_tip) < epsilon, epsilon * (1 + 1j), z_from_tip)
    
    with np.errstate(all="ignore"):
        flow_velocity = (h_up - h_down) / 24.0
        W_uniform = flow_velocity * z
        
        source_strength = pile_depth * flow_velocity * 8.0
        W_source = source_strength * np.log(z_from_tip + 0j)
        
        dipole_strength = pile_depth**1.5 * flow_velocity * 6.0
        W_dipole = dipole_strength / z_from_tip
        
        z_from_base = z - (pile_tip_x + 1j * (-soil_depth))
        z_from_base = np.where(np.abs(z_from_base) < epsilon, epsilon * (1 + 1j), z_from_base)
        W_base = -source_strength * 0.3 * np.log(z_from_base + 0j)
        
        W = W_uniform + W_source + W_dipole + W_base
        return W

def get_complex_potential_dam(x, y, dam_width, h_up, h_down):
    b = max(dam_width / 2, 0.1)
    z = x + 1j * y
    
    with np.errstate(all="ignore"):
        zeta = z / b
        w = b * (zeta + np.sqrt(zeta**2 - 1 + 0j))
        flow_scale = (h_up - h_down) / 20.0
        W = flow_scale * w
        return W

def get_complex_potential(x, y, mode, pile_depth, pile_x, dam_width, h_up, h_down, soil_depth):
    if mode == "Sheet Pile Only":
        return get_complex_potential_sheet_pile(x, y, pile_depth, pile_x, h_up, h_down, soil_depth)
    elif mode == "Concrete Dam Only":
        return get_complex_potential_dam(x, y, dam_width, h_up, h_down)
    elif mode == "Combined (Dam + Pile)":
        W_pile = get_complex_potential_sheet_pile(x, y, pile_depth, pile_x, h_up, h_down, soil_depth)
        W_dam = get_complex_potential_dam(x, y, dam_width, h_up, h_down)
        return 0.6 * W_pile + 0.4 * W_dam
    return 0 + 0j

def calculate_pore_pressure(px, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d):
    if py > 0:
        return None
    gamma_w = 10
    w_pt = get_complex_potential(px, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d)
    phi_pt = np.real(w_pt)
    
    w_up = get_complex_potential(-15.0, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d)
    w_down = get_complex_potential(15.0, py, mode, pile_d, pile_x, dam_w, h_up, h_down, soil_d)
    
    phi_up = np.real(w_up)
    phi_down = np.real(w_down)
    
    if not np.isfinite(phi_pt) or not np.isfinite(phi_up) or not np.isfinite(phi_down):
        return None
    
    if abs(phi_up - phi_down) < 1e-6:
        h_total = (h_up + h_down) / 2
    else:
        ratio = (phi_pt - phi_down) / (phi_up - phi_down)
        ratio = np.clip(ratio, 0, 1)
        h_total = h_down + ratio * (h_up - h_down)
    
    pressure_head = h_total - py
    u = pressure_head * gamma_w
    return {"u": u, "h_total": h_total, "pressure_head": pressure_head}

# ============================================================
# MAIN APP
# ============================================================

def app():
    # --- MOVED INSIDE THE FUNCTION TO FIX ATTRIBUTE ERROR ---
    if "results" not in st.session_state:
        st.session_state.results = None
    
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
                # Calculate Seepage Force per unit volume (j)
                j_seepage = i * gamma_w
                
                if flow_type == "Downward":
                    # Downward: Gravity + Drag
                    gamma_effective = gamma_sub + j_seepage
                    bracket_term = gamma_effective # for storage
                elif flow_type == "Upward":
                    # Upward: Gravity - Drag
                    gamma_effective = gamma_sub - j_seepage
                    bracket_term = gamma_effective
                else:
                    gamma_effective = gamma_sub
                    bracket_term = gamma_sub
                
                sigma_prime_2 = depth_A_soil * bracket_term

                # STORE RESULTS
                st.session_state.results = {
                    "flow_type": flow_type,
                    "i": i,
                    "depth_A_soil": depth_A_soil,
                    "sigma_total": sigma_total,
                    "H_A": H_A,
                    "u_val": u_val,
                    "sigma_prime_1": sigma_prime_1,
                    "sigma_prime_2": sigma_prime_2,
                    "gamma_sub": gamma_sub,
                    "j_seepage": j_seepage,            # Stored for detail
                    "gamma_effective": gamma_effective, # Stored for detail
                    "val_z_snap": val_z,
                    "val_A_snap": val_A,
                    "val_y_snap": val_y,
                    "H_top": H_top,
                    "H_bot": H_bot,
                    "delta_H": delta_H
                }

        # --- PLOT COLUMN ---
        with col_plot:
            fig, ax = plt.subplots(figsize=(7, 8))
            
            datum_y = 0.0
            soil_w = 2.5
            soil_x = 3.5  
            wl_top = val_z + val_y  
            wl_bot = val_x          
            
            if wl_top > wl_bot: flow_arrow = "⬇️"
            elif wl_bot > wl_top: flow_arrow = "⬆️"
            else: flow_arrow = "No Flow"

            ax.add_patch(patches.Rectangle((soil_x, datum_y), soil_w, val_z, 
                                          facecolor='#E3C195', hatch='...', edgecolor='none', zorder=1))
            ax.text(soil_x + soil_w/2, datum_y + val_z/2, "SOIL", ha='center', fontweight='bold', fontsize=12, zorder=3)
            
            tank_w = 2.0
            tank_x = soil_x + (soil_w - tank_w)/2
            neck_w = 0.8
            neck_x = soil_x + (soil_w - neck_w)/2
            tank_base_y = wl_top - 0.5
            if tank_base_y < datum_y + val_z: tank_base_y = datum_y + val_z 
            
            ax.add_patch(patches.Rectangle((tank_x, tank_base_y), tank_w, wl_top - tank_base_y, facecolor='#D6EAF8', edgecolor='none', zorder=1))
            ax.add_patch(patches.Rectangle((neck_x, datum_y + val_z), neck_w, tank_base_y - (datum_y + val_z) + 0.1, facecolor='#D6EAF8', edgecolor='none', zorder=1))
            
            tube_w = 0.6
            left_tank_x = 0.5
            l_tank_base_y = wl_bot - 0.5
            if l_tank_base_y < datum_y - 1.0: l_tank_base_y = datum_y - 1.0 
            
            tube_start_x = soil_x + (soil_w - tube_w)/2
            ax.add_patch(patches.Rectangle((tube_start_x, datum_y - 1.0), tube_w, 1.0, facecolor='#D6EAF8', edgecolor='none', zorder=1))
            tube_left_end = left_tank_x + (tank_w - tube_w)/2
            ax.add_patch(patches.Rectangle((tube_left_end, datum_y - 1.0), tube_start_x - tube_left_end + tube_w, tube_w, facecolor='#D6EAF8', edgecolor='none', zorder=1))
            ax.add_patch(patches.Rectangle((tube_left_end, datum_y - 1.0), tube_w, l_tank_base_y - (datum_y - 1.0) + 0.1, facecolor='#D6EAF8', edgecolor='none', zorder=1))
            ax.add_patch(patches.Rectangle((left_tank_x, l_tank_base_y), tank_w, wl_bot - l_tank_base_y, facecolor='#D6EAF8', edgecolor='none', zorder=1))

            wall_thick = 2.5
            wall_color = 'black'
            ax.plot([tank_x, tank_x, neck_x, neck_x], [wl_top + 0.5, tank_base_y, tank_base_y, datum_y + val_z], color=wall_color, lw=wall_thick, zorder=2)
            ax.plot([tank_x + tank_w, tank_x + tank_w, neck_x + neck_w, neck_x + neck_w], [wl_top + 0.5, tank_base_y, tank_base_y, datum_y + val_z], color=wall_color, lw=wall_thick, zorder=2)
            ax.plot([soil_x, soil_x], [datum_y + val_z, datum_y], color=wall_color, lw=wall_thick, zorder=2) 
            ax.plot([soil_x + soil_w, soil_x + soil_w], [datum_y + val_z, datum_y], color=wall_color, lw=wall_thick, zorder=2) 
            ax.plot([soil_x, tube_start_x], [datum_y, datum_y], color=wall_color, lw=wall_thick, zorder=2)
            ax.plot([tube_start_x + tube_w, soil_x + soil_w], [datum_y, datum_y], color=wall_color, lw=wall_thick, zorder=2)
            ax.plot([soil_x, neck_x], [datum_y + val_z , datum_y + val_z], color=wall_color, lw=wall_thick, zorder=2)
            ax.plot([neck_x + neck_w, soil_x + soil_w], [datum_y + val_z , datum_y + val_z], color=wall_color, lw=wall_thick, zorder=2) 
            path_outer_x = [tube_start_x , tube_start_x , tube_left_end + tube_w, tube_left_end + tube_w, left_tank_x + tank_w, left_tank_x + tank_w]
            path_outer_y = [datum_y, datum_y - 1.0 + tube_w, datum_y - 1.0 + tube_w, l_tank_base_y, l_tank_base_y, wl_bot + 0.5]
            ax.plot(path_outer_x, path_outer_y, color=wall_color, lw=wall_thick, zorder=2)
            path_inner_x = [tube_start_x + tube_w, tube_start_x + tube_w, tube_left_end, tube_left_end, left_tank_x, left_tank_x]
            path_inner_y = [datum_y, datum_y - 1.0, datum_y - 1.0, l_tank_base_y, l_tank_base_y, wl_bot + 0.5]
            ax.plot(path_inner_x, path_inner_y, color=wall_color, lw=wall_thick, zorder=2)

            ax.plot([tank_x, tank_x + tank_w], [wl_top, wl_top], color='blue', lw=2, zorder=2)
            ax.plot([left_tank_x, left_tank_x + tank_w], [wl_bot, wl_bot], color='blue', lw=2, zorder=2)
            ax.plot(tank_x + tank_w/2, wl_top, marker='v', color='blue', markersize=8, zorder=2)
            ax.plot(left_tank_x + tank_w/2, wl_bot, marker='v', color='blue', markersize=8, zorder=2)

            ax.plot([-0.5, 8], [datum_y, datum_y], 'k-.', lw=1)
            ax.text(soil_x + 0.5 + soil_w, datum_y - 0.25, "Datum (z=0)", va='center', fontsize=10, style='italic')
            
            dim_z_x = soil_x - 0.4
            ax.annotate('', xy=(dim_z_x, datum_y), xytext=(dim_z_x, datum_y + val_z), arrowprops=dict(arrowstyle='<->', color='black'))
            ax.text(dim_z_x - 0.1, val_z/2, f"z = {val_z:.2f}m", fontsize=10, ha='right')
            
            dim_y_x = soil_x + soil_w + 0.8
            ax.annotate('', xy=(dim_y_x, val_z), xytext=(dim_y_x, wl_top), arrowprops=dict(arrowstyle='<->', color='black'))
            ax.text(dim_y_x + 0.1, (val_z + wl_top)/2, f"y = {val_y:.2f}m", fontsize=11, fontweight='bold', color='black', ha='left')
            ax.plot([soil_x + soil_w, dim_y_x + 0.2], [val_z, val_z], 'k--', lw=0.5)
            ax.plot([tank_x + tank_w, dim_y_x + 0.2], [wl_top, wl_top], 'k--', lw=0.5)

            dim_x_loc = left_tank_x - 0.4
            ax.annotate('', xy=(dim_x_loc, datum_y), xytext=(dim_x_loc, wl_bot), arrowprops=dict(arrowstyle='<->'))
            ax.text(dim_x_loc - 0.1, wl_bot/2, f"x = {val_x:.2f}m", fontsize=11, fontweight='bold', ha='right')

            dim_A_x = soil_x + soil_w/2 + 2.0
            ax.annotate('', xy=(dim_A_x, datum_y), xytext=(dim_A_x, datum_y + val_A), arrowprops=dict(arrowstyle='<->', color='black'))
            ax.text(dim_A_x + 0.1, val_A/2, f"A = {val_A:.2f}m", color='black', fontweight='bold', zorder=5)
            ax.plot([soil_x + soil_w/2, dim_A_x], [datum_y + val_A, datum_y + val_A], 'k:', lw=1)
            ax.scatter(soil_x + soil_w/2 + 2.0, datum_y + val_A, color='Black', zorder=5, s=80, edgecolor='black')
            ax.text(soil_x + soil_w/2 + 2.2, datum_y + val_A + 0.1, f"Point A", color='Black', fontweight='bold', zorder=5)

            ax.text(soil_x + soil_w/2, wl_top + 0.5, f"FLOW {flow_arrow}", ha='center', fontsize=12, fontweight='bold')
            ax.set_xlim(-1.5, 9)
            ax.set_ylim(datum_y - 1.5, max(wl_bot, wl_top) + 1)
            ax.axis('off')
            st.pyplot(fig)

        # ------------------------- RESULTS (FULL WIDTH) -------------------------
        if st.session_state.results:
            results = st.session_state.results
            
            st.divider()
            st.success(f"**Flow Condition:** {results['flow_type']} (Gradient i = {results['i']:.3f})")

            res_c1, res_c2, res_c3 = st.columns(3)
            res_c1.metric("Total Stress (σ)", f"{results['sigma_total']:.2f} kPa")
            res_c2.metric("Pore Pressure (u)", f"{results['u_val']:.2f} kPa")
            res_c3.metric("Effective Stress (σ')", f"{results['sigma_prime_1']:.2f} kPa")
            
            # --- DETAILED DERIVATION ---
            with st.expander("View Detailed Step-by-Step Derivation (2 Methods)", expanded=True):
                # Use snapshots
                z_s = results.get('val_z_snap', val_z)
                a_s = results.get('val_A_snap', val_A)
                y_s = results.get('val_y_snap', val_y)
                
                st.markdown("#### Method 1: Definition (σ' = σ − u)")
                st.latex(rf"\text{{Depth}} = {z_s} - {a_s} = {results['depth_A_soil']:.2f} \text{{ m}}")
                
                st.markdown("**Step 1: Total Stress**")
                st.latex(rf"\sigma = ({gamma_w} \cdot {y_s}) + ({gamma_sat} \cdot {results['depth_A_soil']:.2f}) = {results['sigma_total']:.2f} \text{{ kPa}}")
                
                st.markdown("**Step 2: Pore Pressure**")
                st.latex(rf"u = ({results['H_A']:.2f} - {a_s:.2f}) \cdot {gamma_w} = {results['u_val']:.2f} \text{{ kPa}}")
                
                st.markdown("**Step 3: Effective Stress**")
                st.latex(rf"\sigma' = {results['sigma_total']:.2f} - {results['u_val']:.2f} = {results['sigma_prime_1']:.2f} \text{{ kPa}}")
                
                st.markdown("---")
                
                # --- NEW DETAILED SECTION FOR SEEPAGE FORCE ---
                st.markdown("#### Method 2: Seepage Force Approach")
                st.caption("We adjust the submerged weight of the soil by the drag force (j) of the water.")

                # A. Calculate Gradient
                st.markdown("**A. Hydraulic Gradient ($i$)**")
                st.latex(rf"i = \frac{{\Delta H}}{{L}} = \frac{{|{results['H_top']:.2f} - {results['H_bot']:.2f}|}}{{{z_s:.2f}}} = {results['i']:.3f}")

                # 1. Submerged Weight
                st.markdown("**B. Submerged Unit Weight ($\gamma'$)**")
                st.latex(rf"\gamma' = \gamma_{{sat}} - \gamma_w = {gamma_sat} - {gamma_w} = {results['gamma_sub']:.2f} \text{{ kN/m}}^3")
                
                # 2. Seepage Force per unit volume
                st.markdown("**C. Seepage Force per Unit Volume ($j$)**")
                st.latex(rf"j = i \cdot \gamma_w = {results['i']:.3f} \cdot {gamma_w} = {results['j_seepage']:.2f} \text{{ kN/m}}^3")
                
                # 3. Combine
                st.markdown(f"**D. Effective Unit Weight ($\gamma'_{{eff}}$)** ({results['flow_type']} Flow)")
                if results['flow_type'] == "Upward":
                    sign_latex = "-"
                    text_logic = r"\text{Upward flow reduces weight (} \gamma' - j \text{)}"
                elif results['flow_type'] == "Downward":
                    sign_latex = "+"
                    text_logic = r"\text{Downward flow increases weight (} \gamma' + j \text{)}"
                else:
                    sign_latex = "+"
                    text_logic = r"\text{No flow}"

                st.latex(text_logic)
                st.latex(rf"\gamma'_{{eff}} = {results['gamma_sub']:.2f} {sign_latex} {results['j_seepage']:.2f} = {results['gamma_effective']:.2f} \text{{ kN/m}}^3")
                
                # 4. Final
                st.markdown("**E. Calculate Effective Stress**")
                st.latex(rf"\sigma' = z \cdot \gamma'_{{eff}} = {results['depth_A_soil']:.2f} \cdot {results['gamma_effective']:.2f} = \mathbf{{{results['sigma_prime_2']:.2f} \text{{ kPa}}}}")

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
                if st.button("Calculate Permeability (k)", type="primary", key="btn_const"):
                    if A*h*t > 0: 
                        k_val = (Q*L)/(A*h*t)
                        k_formatted = format_scientific(k_val)
                        st.success(f"**Permeability Coefficient (k)**\n\n$${k_formatted} \\text{{ cm/sec}}$$")
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
                if st.button("Calculate Permeability (k)", type="primary", key="btn_fall"):
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
