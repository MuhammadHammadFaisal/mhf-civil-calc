import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from theme import write_text, glass_box, glass_table

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

    tab1, tab2= st.tabs(["1D Seepage", "Permeability"])
    
    # =================================================================
    # TAB 1: 1D SEEPAGE (Effective Stress)
    # =================================================================
    with tab1:
        st.caption("Determine Effective Stress at Point A. (Datum is at the Bottom of Soil)")
        
        col_setup, col_plot = st.columns([2, 1])
        
        with col_setup:
            write_text("subheader", "1. Problem Setup")
            c1, c2= st.columns(2)
            with c1:
                val_z = st.number_input("Soil Specimen Height (z) [m]", 0.1, step=0.5, value=4.0)
                gamma_sat = st.number_input("Saturated Unit Weight (γ_sat) [kN/m³]", 18.0, step=0.1)
                val_A = st.number_input("Height of Point 'A' from Datum [m]", 0.0, val_z, val_z/2)
            with c2:
                val_y = st.number_input("Water Height above Soil (y) [m]", 0.0, step=0.5, value=2.0)
                val_x = st.number_input("Piezometer Head at Bottom (x) [m]", 0.0, step=0.5, value=7.5)
                gamma_w = st.radio("γw [kN/m³]", [9.81, 10.0], index=1, horizontal=True)
          
            
            st.markdown("---")
            
            if st.button("Calculate Effective Stress", type="primary"):
                # --- PRELIMINARY CALCULATIONS ---
                gamma_sub = gamma_sat - gamma_w
                
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
                
                sigma_prime_2 = depth_A_soil * gamma_effective

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
                    "j_seepage": j_seepage,            
                    "gamma_effective": gamma_effective, 
                    "val_z_snap": val_z,
                    "val_A_snap": val_A,
                    "val_y_snap": val_y,
                    "H_top": H_top,
                    "H_bot": H_bot,
                    "gamma_sat_snap": gamma_sat
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
            plt.close(fig)

        # ------------------------- RESULTS (FULL WIDTH) -------------------------
                # ------------------------- RESULTS (FULL WIDTH) -------------------------
        if "results" in st.session_state and st.session_state.results:
            results = st.session_state.results  # FIXED: Unified variable name
            st.divider()
            
            # CHANGED: Consolidated summary into a single premium glass_box
            summary_text = f"""
### Analysis Results: {results['flow_type']}
**Hydraulic Gradient (i):** {results['i']:.3f}

**Total Stress ($\\sigma$):** {results['sigma_total']:.2f} kPa

**Pore Pressure ($u$):** {results['u_val']:.2f} kPa

**Effective Stress ($\\sigma'$):** {results['sigma_prime_1']:.2f} kPa
"""
            glass_box(summary_text)
            
            # --- DETAILED DERIVATION ---
            with st.expander("View Detailed Step-by-Step Derivation (2 Methods)", expanded=True):
                # Fetching snapshots for consistency
                z_s = results.get('val_z_snap')
                a_s = results.get('val_A_snap')
                y_s = results.get('val_y_snap')
                g_sat_s = results.get('gamma_sat_snap')

                # --- METHOD 1 ---
                # Use double backslashes (\\) so Streamlit renders the Greek symbols correctly
                write_text("subheader", "Method 1: Stress Definition (Effective Stress = Total - Pore)")
                
                m1_text = f"""
**Step 1: Calculate Depth of Point A below Soil Surface**
$$z_A = {z_s:.2f} - {y_s:.2f} = {results['depth_A_soil']:.2f} \\, m$$

**Step 2: Total Stress ($\\sigma$)**
$$\\sigma = (\\gamma_w \\cdot y) + (\\gamma_{{sat}} \\cdot z_A) = ({gamma_w} \\cdot {y_s:.2f}) + ({g_sat_s:.2f} \\cdot {results['depth_A_soil']:.2f}) = \\mathbf{{{results['sigma_total']:.2f} \\, kPa}}$$

**Step 3: Pore Water Pressure ($u$)**
$$u = (H_A - \\text{{Elevation}}_A) \\cdot \\gamma_w = ({results['H_A']:.2f} - {a_s:.2f}) \\cdot {gamma_w} = \\mathbf{{{results['u_val']:.2f} \\, kPa}}$$

**Step 4: Effective Stress ($\\sigma'$)**
$$\\sigma' = \\sigma - u = {results['sigma_total']:.2f} - {results['u_val']:.2f} = \\mathbf{{{results['sigma_prime_1']:.2f} \\, kPa}}$$
"""
                glass_box(m1_text)

                st.markdown("---")

                # --- METHOD 2 ---
                write_text("subheader", "Method 2: Seepage Force Approach")
                st.caption("Adjusting submerged weight by the hydraulic drag force (j).")

                # Logic for sign based on flow direction
                if results['flow_type'] == "Upward":
                    sign, logic = "-", r"\text{Upward flow reduces effective weight: } (\\gamma' - j)"
                elif results['flow_type'] == "Downward":
                    sign, logic = "+", r"\text{Downward flow increases effective weight: } (\\gamma' + j)"
                else:
                    sign, logic = "+", r"\text{Hydrostatic condition: } (\\gamma')"

                # Use DOUBLE BACKSLASHES (\\) for all LaTeX commands
                m2_text = f"""
**Step A: Hydraulic Gradient ($i$)**
$$i = \\frac{{\\Delta H}}{{L}} = \\frac{{|{results['H_top']:.2f} - {results['H_bot']:.2f}|}}{{{z_s:.2f}}} = {results['i']:.3f}$$

**Step B: Submerged Unit Weight ($\\gamma'$)**
$$\\gamma' = \\gamma_{{sat}} - \\gamma_w = {g_sat_s:.2f} - {gamma_w} = {results['gamma_sub']:.2f} \\, kN/m^3$$

**Step C: Seepage Force per Unit Volume ($j$)**
$$j = i \\cdot \\gamma_w = {results['i']:.3f} \\cdot {gamma_w} = {results['j_seepage']:.2f} \\, kN/m^3$$

**Step D: Effective Unit Weight ($\\gamma'_{{eff}}$)**
$${logic}$$
$$\\gamma'_{{eff}} = \\gamma' {sign} j = {results['gamma_sub']:.2f} {sign} {results['j_seepage']:.2f} = {results['gamma_effective']:.2f} \\, kN/m^3$$

**Step E: Final Effective Stress ($\\sigma'$)**
$$\\sigma' = z_A \\cdot \\gamma'_{{eff}} = {results['depth_A_soil']:.2f} \\cdot {results['gamma_effective']:.2f} = \\mathbf{{{results['sigma_prime_2']:.2f} \\, kPa}}$$
"""
                glass_box(m2_text)
    # =================================================================
    # TAB 2: PERMEABILITY
    # =================================================================
    with tab2:
        st.caption("Calculate Coefficient of Permeability (k). Input variables are marked on the diagram.")
        col_input_2, col_plot_2 = st.columns([1, 1.2])

        with col_input_2:
            write_text("subheader", "1. Test Configuration")
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
            plt.close(fig2)
# =================================================================
    # TAB 3: MULTI-LAYER SEEPAGE (EXAM QUESTIONS)
    # =================================================================
#     with tab3:
        
#         col_setup, col_viz = st.columns([2, 1.2])
        
        
#         with col_setup:
#             write_text("subheader", "1. Global Parameters")
#             c_g1, c_g2, c_g3 = st.columns(3)
#             with c_g1:
#                 n_layers = st.number_input("Number of Soil Layers", 1, 6, value=5, key="t3_layers")
#                 gamma_w = st.radio("Unit Weight of Water (γw)", [9.81, 10.0], index=1, horizontal=True, key="t3_gw_radio")
#             with c_g2:
#                 water_depth = st.number_input("Water Table Depth (m)", value=1.0, step=0.5, key="t3_wt")
#                 h_surface = st.number_input("Total Head at Top (m)", value=5.0, key="t3_htop")
#             with c_g3:
#                 surcharge = st.number_input("Surcharge q (kPa)", value=0.0, step=5.0, key="t3_q")
            
#             st.markdown("---")
#             write_text("subheader", "2. Stratigraphy")
            
#             layers = []
#             depth_tracker = 0.0
#             colors = {"Sand": "#E6D690", "Clay": "#B0A494", "Gravel": "#A89F91", "Silt": "#D2B48C"}

#             def_types = ["Sand", "Gravel", "Clay", "Sand", "Silt"]
#             def_h = [4.0, 2.0, 4.0, 3.0, 10.0]
#             def_g_sat = [20.0, 21.0, 18.0, 21.0, 20.0]
#             def_g_dry = [18.0, 19.0, 16.0, 18.0, 17.0]
#             def_k = [10.0, 80.0, 0.00088, 9.0, 0.0028]

#             for i in range(int(n_layers)):
#                 layer_top = depth_tracker
#                 t_val = def_types[i] if i < len(def_types) else "Sand"
#                 h_val = def_h[i] if i < len(def_h) else 2.0
#                 gsat_val = def_g_sat[i] if i < len(def_g_sat) else 20.0
#                 gdry_val = def_g_dry[i] if i < len(def_g_dry) else 17.0
#                 k_val = def_k[i] if i < len(def_k) else 10.0

#                 with st.expander(f"Layer {i+1} (Top at {layer_top:.1f}m)", expanded=(i < 2)):
#                     cl = st.columns(5)
#                     s_type = cl[0].selectbox("Type", ["Sand", "Clay", "Gravel", "Silt"], 
#                                              index=["Sand", "Clay", "Gravel", "Silt"].index(t_val), key=f"t3_type{i}")
#                     thickness = cl[1].number_input("H (m)", 0.1, value=h_val, key=f"t3_h{i}")
                    
#                     layer_bot = layer_top + thickness
#                     needs_dry = layer_top < water_depth
#                     needs_sat = layer_bot > water_depth

#                     # Logic to mirror Effective Stress module behavior
#                     if needs_sat:
#                         g_sat_in = cl[2].number_input("γ_sat", value=gsat_val, key=f"t3_gsat{i}")
#                     else:
#                         cl[2].text_input("γ_sat", value="N/A", disabled=True, key=f"t3_gsat_dis{i}")
#                         g_sat_in = gsat_val

#                     if needs_dry:
#                         g_dry_in = cl[3].number_input("γ_dry", value=gdry_val, key=f"t3_gdry{i}")
#                     else:
#                         cl[3].text_input("γ_dry", value="N/A", disabled=True, key=f"t3_gdry_dis{i}")
#                         g_dry_in = gdry_val
                        
#                     perm = cl[4].number_input("k (m/d)", value=k_val, format="%.5f", key=f"t3_k{i}")
                    
#                     layers.append({
#                         "id": i+1, "type": s_type, "H": thickness, "g_sat": g_sat_in, "g_dry": g_dry_in, 
#                         "k": perm, "top": layer_top, "bot": layer_bot, "color": colors[s_type]
#                     })
#                     depth_tracker += thickness

#             write_text("subheader", "3. Artesian Measurement & Calculation Point")
#             c_calc1, c_calc2 = st.columns(2)
#             with c_calc1:
#                 target_depth = st.number_input("Calculate Stresses at Depth (m)", 0.0, depth_tracker, value=11.0, key="t3_target")
#             with c_calc2:
#                 art_p = st.number_input("Measured Pore Pressure (kPa)", value=150.0, key="t3_artp")
#                 art_depth = st.number_input("At Measuring Depth (m)", value=6.0, key="t3_artz")
#                 art_head = (art_p / gamma_w) + (depth_tracker - art_depth)
#             solve_clicked = st.button("Solve Seepage Problem", type="primary", key="t3_solve")

#         with col_viz:
#             write_text("subheader", "Soil Profile Preview")
            
#             # Dynamically set figure height based on total depth to prevent squashing
#             fig_h = max(8, depth_tracker / 2)
#             fig3, ax3 = plt.subplots(figsize=(5, fig_h))
            
#             # Using your established color palette
#             colors = {"Sand": "#E6D690", "Clay": "#B0A494", "Gravel": "#A89F91", "Silt": "#D2B48C"}
            
#             for i, L in enumerate(layers):
#                 # Draw the soil layer
#                 rect = patches.Rectangle((0, L['top']), 4, L['H'], 
#                                          facecolor=L['color'], edgecolor='black', alpha=0.9, linewidth=1.5)
#                 ax3.add_patch(rect)
                
#                 # Label the layer centered vertically in the layer thickness
#                 ax3.text(2, L['top'] + L['H']/2, f"{L['type']}\n(L{L['id']})", 
#                          ha='center', va='center', fontweight='bold', fontsize=10)
                
#                 # Add dimension lines for thickness on the left side
#                 ax3.annotate('', xy=(-0.5, L['top']), xytext=(-0.5, L['bot']),
#                              arrowprops=dict(arrowstyle='<->', color='black', lw=1))
#                 ax3.text(-0.6, L['top'] + L['H']/2, f"{L['H']}m", ha='right', va='center', fontsize=9)

#             # Draw Water Table line with standard blue dashed style
#             ax3.axhline(water_depth, color='blue', linestyle='-.', linewidth=2)
#             ax3.text(4.2, water_depth, "WT ▽", color='blue', fontweight='bold', fontsize=10)

#             # Draw the Calculation Point with high-visibility red
#             ax3.axhline(target_depth, color='red', linestyle='--', linewidth=2.5)
#             ax3.text(4.2, target_depth, "CALC POINT", color='red', fontweight='bold', fontsize=10)
            
#             # Styling to match textbook diagrams
#             ax3.set_ylim(depth_tracker + 1, -1) # Buffer at top and bottom
#             ax3.set_xlim(-2, 7) # Extra space for labels
#             ax3.axis('off')
            
#             # Ensure the plot fits the Streamlit container perfectly
#             st.pyplot(fig3, width="stretch")
#             plt.close(fig3, width="stretch")
# # === CRITICAL CHANGE: Indent the RESULTS block so it is inside the tab3 block ===
#         if solve_clicked:
#             # --- PHASE 1: MATHEMATICAL SOLVER ---
#             # 1. Establish Datum and Boundary Heads (Datum at z=0, downwards is positive depth)
#             h_top = h_surface
            
#             # Elevation head is negative depth. Total Head = Pressure Head + Elevation Head
#             z_elev_art = -art_depth
#             h_bot = (art_p / gamma_w) + z_elev_art 
            
#             # 2. Total Hydraulic Resistance
#             sum_h_k = sum(L['H'] / L['k'] for L in layers)
            
#             # 3. Flow Velocity (Positive v = Downward, Negative v = Upward)
#             delta_h_total = h_top - h_bot
#             v_seepage = delta_h_total / sum_h_k
            
#             # Determine flow direction for clean UI display
#             if v_seepage > 1e-6:
#                 flow_dir = "Downward ⬇️"
#             elif v_seepage < -1e-6:
#                 flow_dir = "Upward ⬆️"
#             else:
#                 flow_dir = "No Flow (Hydrostatic)"

#             # 4. Stress and Head at Target Depth
#             sigma_total = surcharge
#             sum_h_k_above = 0.0
            
#             for L in layers:
#                 # Determine how much of the current layer is above the target calculation point
#                 if target_depth <= L['top']:
#                     thick_above = 0.0
#                 elif target_depth >= L['bot']:
#                     thick_above = L['H']
#                 else:
#                     thick_above = target_depth - L['top']
                
#                 if thick_above > 0:
#                     # Calculate Total Stress Contribution for this slice
#                     z_top_slice = L['top']
#                     z_bot_slice = z_top_slice + thick_above
                    
#                     if z_bot_slice <= water_depth:
#                         # Slice is entirely above the water table (Dry)
#                         sigma_total += thick_above * L['g_dry']
#                     elif z_top_slice >= water_depth:
#                         # Slice is entirely below the water table (Saturated)
#                         sigma_total += thick_above * L['g_sat']
#                     else:
#                         # Water table intersects this slice; split into dry and sat parts
#                         dry_thick = water_depth - z_top_slice
#                         sat_thick = z_bot_slice - water_depth
#                         sigma_total += (dry_thick * L['g_dry']) + (sat_thick * L['g_sat'])
                    
#                     # Accumulate hydraulic resistance down to the target point
#                     sum_h_k_above += thick_above / L['k']
            
#             # Calculate Total Head at target depth
#             # v_seepage carries the sign automatically, so head drops correctly in flow direction
#             h_target = h_top - (v_seepage * sum_h_k_above)
            
#             # Calculate Pore Pressure
#             z_elev_target = -target_depth
#             # h = (u / gamma_w) + z_elev  =>  u = (h - z_elev) * gamma_w
#             u_target = (h_target - z_elev_target) * gamma_w
            
#             # Calculate Effective Stress
#             sigma_eff = sigma_total - u_target

#             # --- PHASE 2: DISPLAY RESULTS ---
#             st.divider()
            
#             v_display = abs(v_seepage) # Display velocity as a positive magnitude
            
#             res_sum = f"""
# ### Analysis Results (@ z = {target_depth:.2f}m)
# **Flow Direction:** {flow_dir}
# **Flow Velocity (|v|):** {v_display:.6f} m/day

# **Total Vertical Stress ($\\sigma$):** {sigma_total:.2f} kPa
# **Pore Water Pressure ($u$):** {u_target:.2f} kPa
# **Effective Vertical Stress ($\\sigma'$):** {sigma_eff:.2f} kPa
# """
#             glass_box(res_sum)
            
#             # --- PHASE 3: DETAILED CALCULATION LOG ---
#             with st.expander("Detailed Calculation Log", expanded=False):
#                 write_text("subheader", "1. Head Distribution & Flow Rate")
#                 head_log = [
#                     f"**Datum Setup:** $z=0$ at Top Surface. Elevation Head = $-z$.",
#                     f"**Total Head at Top Boundary ($h_{{top}}$):** {h_top:.2f} m",
#                     f"**Total Head at Base Aquifer ($h_{{bot}}$):** $({art_p:.2f} / {gamma_w}) + ({-art_depth:.2f}) = {h_bot:.2f}$ m",
#                     f"**Total Resistance ($\\sum H/k$):** {sum_h_k:.4f} day",
#                     f"**Total Head Difference ($\\Delta H$):** $|{h_top:.2f} - {h_bot:.2f}| = {abs(delta_h_total):.4f}$ m"
#                 ]
                
#                 curr_h = h_top
#                 for L in layers:
#                     # Head loss magnitude for the layer
#                     dh = v_seepage * (L['H'] / L['k'])
#                     curr_h -= dh
#                     head_log.append(f"**Layer {L['id']} ({L['type']}):** $\\Delta h = {abs(dh):.4f}$m → Head at Bottom ($z={L['bot']}$m) = {curr_h:.4f}m")
                
#                 glass_box("\n\n".join(head_log))

#                 write_text("subheader", "2. Stress Derivation at Target")
#                 stress_log = [
#                     f"**Total Stress ($\\sigma$):** {sigma_total:.2f} kPa (Includes {surcharge} kPa Surcharge)",
#                     f"**Hydraulic Resistance to Target ($\\sum H/k$):** {sum_h_k_above:.4f} day",
#                     f"**Total Head at Target ($h_{{target}}$):** ${h_top:.2f} - ({v_seepage:.6f} \\times {sum_h_k_above:.4f}) = {h_target:.4f}$ m",
#                     f"**Elevation Head ($z_{{elev}}$):** {-target_depth:.2f} m",
#                     f"**Pore Pressure ($u$):** $(h_{{target}} - z_{{elev}}) \\cdot \\gamma_w = ({h_target:.4f} - ({-target_depth:.2f})) \\cdot {gamma_w} = \\mathbf{{{u_target:.2f} \\, kPa}}$",
#                     f"**Effective Stress ($\\sigma'$):** ${sigma_total:.2f} - {u_target:.2f} = \\mathbf{{{sigma_eff:.2f} \\, kPa}}$"
#                 ]
#                 glass_box("\n\n".join(stress_log))

if __name__ == "__main__":
    app()
