import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# =========================================================
# APP CONFIG & GLOBAL STYLING
# =========================================================
st.set_page_config(page_title="MHF Soil Mechanics", layout="wide")

# Inject our custom glassmorphism CSS globally so it works on all tabs
st.markdown(
    """
    <style>
    /* Transparent Table Styling */
    .glass-table {
        width: 100%;
        background-color: rgba(0, 0, 0, 0.2) !important;
        color: #E0E0E0;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 20px;
        font-size: 14px;
    }
    .glass-table th, .glass-table td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        text-align: left;
    }
    .glass-table th {
        background-color: rgba(0, 0, 0, 0.4) !important;
        font-weight: 600;
        color: #FFFFFF;
    }
    .glass-table tr:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Transparent Box Styling for Logs & Math */
    .glass-box {
        background-color: rgba(0, 0, 0, 0.2) !important;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
        color: #E0E0E0;
    }
    .glass-box h3, .glass-box h4 {
        margin-top: 0px;
        color: #FFFFFF;
    }
    </style>
    """, 
    unsafe_allow_html=True
)


# =========================================================
# MAIN APP
# =========================================================
def app():
    # 1. Define the variable FIRST
    gamma_option = st.radio(
        "Unit Weight of Water (γ_w)",
        [9.81, 10.0],
        index=0,
        horizontal=True, 
        help="Select 9.81 for precise calc or 10 for simplified exams."
    )
    GAMMA_W = gamma_option

    # 2. NOW you can use it in a caption
    st.caption(f"Current Calculation uses: γ_w = {GAMMA_W} kN/m³")

    # 3. Then create your tabs
    tab1, tab2 = st.tabs(["Stress Profile Calculator", "Heave Check"])
    
    # =====================================================
    # TAB 1 — STRESS PROFILE
    # =====================================================
    with tab1:
        st.caption("Define soil layers, water table, and surcharge to calculate the stress profile.")

        col_input, col_viz = st.columns([1.5, 1])

        # -------------------------------------------------
        # INPUTS
        # -------------------------------------------------
        with col_input:
            st.markdown("### A. Global Parameters")
            c1, c2, c3 = st.columns(3)
            with c1:
                water_depth = st.number_input("Water Table Depth (m)", value=3.0, step=0.5)
            with c2:
                hc = st.number_input("Capillary Rise (m)", value=0.0, step=0.1)
            with c3:
                surcharge = st.number_input("Surcharge q (kPa)", value=50.0, step=5.0)

            st.markdown("### B. Soil Properties & Artesian Conditions")
            num_layers = st.number_input("Number of Layers", 1, 5, 3)
            
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                artesian_layer_id = st.number_input("Artesian Layer ID", 0, int(num_layers), 0, 
                                                    help="The layer number where artesian pressure begins. Set to 0 for no artesian pressure.")
            with c_a2:
                artesian_head = st.number_input("Extra Artesian Head (m)", value=0.0, step=0.5, 
                                                help="Additional piezometric head above the hydrostatic water table.")
            st.markdown("---")

            layers = []
            colors = {"Sand": "#E6D690", "Clay": "#B0A494", "Gravel": "#A89F91", "Rock": "#6D6D6D"}
            depth_tracker = 0.0

            for i in range(int(num_layers)):
                layer_title = f"Layer {i+1} (Top at {depth_tracker:.1f}m)"
                if (i + 1) == artesian_layer_id:
                    layer_title += " - **[ARTESIAN]**"

                with st.expander(layer_title, expanded=True):
                    cols = st.columns(4)
                    soil_type = cols[0].selectbox("Type", ["Sand", "Clay", "Gravel", "Rock"], key=f"t{i}")
                    thickness = cols[1].number_input("Height (m)", 0.1, 20.0, 4.0, step=0.5, key=f"h{i}")

                    layer_top = depth_tracker
                    layer_bot = depth_tracker + thickness

                    eff_wt = water_depth - hc
                    needs_dry = layer_top < eff_wt
                    needs_sat = layer_bot > eff_wt

                    g_dry_input = 17.0
                    g_sat_input = 20.0

                    if needs_sat:
                        g_sat_input = cols[2].number_input("γ_sat", value=20.0, key=f"gs{i}")
                    else:
                        cols[2].text_input("γ_sat", value="N/A", disabled=True, key=f"gs_dis{i}")

                    if needs_dry:
                        g_dry_input = cols[3].number_input("γ_dry", value=17.0, key=f"gd{i}")
                    else:
                        cols[3].text_input("γ_dry", value="N/A", disabled=True, key=f"gd_dis{i}")

                    layers.append({
                        "id": i+1, "type": soil_type, "top": layer_top, "bot": layer_bot,
                        "H": thickness, "g_sat": g_sat_input, "g_dry": g_dry_input, "color": colors[soil_type]
                    })

                    depth_tracker += thickness

            total_depth = depth_tracker

        # -------------------------------------------------
        # SOIL PROFILE VISUALIZER
        # -------------------------------------------------
        with col_viz:
            st.markdown("### Soil Profile Preview")
            
            # Apply dark transparent styling to the plot
            with plt.style.context('dark_background'):
                fig, ax = plt.subplots(figsize=(6, 5), facecolor='none')
                ax.set_facecolor('none')

                current_depth = 0
                for lay in layers:
                    rect = patches.Rectangle((0, current_depth), 5, lay['H'],
                                             facecolor=lay['color'], edgecolor='#E0E0E0')
                    ax.add_patch(rect)
                    mid_y = current_depth + lay['H'] / 2
                    label_text = lay['type']
                    if lay['id'] == artesian_layer_id:
                        label_text += "\n(Artesian)"
                    # Changed text to black for readability inside the colored soil blocks
                    ax.text(2.5, mid_y, label_text, ha='center', va='center', fontweight='bold', color='black')
                    current_depth += lay['H']

                # Surcharge arrows (Bright Red)
                if surcharge > 0:
                    for x in np.linspace(0.5, 4.5, 8):
                        ax.arrow(x, -0.5, 0, 0.4, head_width=0.15, head_length=0.1, fc='#ff4b4b', ec='#ff4b4b')
                    ax.text(2.5, -0.6, f"q = {surcharge} kPa", ha='center', color='#ff4b4b', fontweight='bold')

                # Water table (Bright Blue)
                ax.axhline(water_depth, color='#00bfff', linestyle='--', linewidth=2)
                ax.text(5.1, water_depth, "WT ▽", color='#00bfff', va='center')
                
                # Piezometric Line (Cyan)
                if artesian_layer_id > 0 and artesian_head > 0:
                    piezo_level = water_depth - artesian_head
                    ax.axhline(piezo_level, color='#00ffaa', linestyle='-.', linewidth=2)
                    ax.text(5.1, piezo_level, "Piez. WT ▽", color='#00ffaa', va='center')

                # Capillary zone
                if hc > 0:
                    cap_top = max(0, water_depth - hc)
                    rect_cap = patches.Rectangle((0, cap_top), 5, water_depth - cap_top,
                                                 hatch='///', fill=False, edgecolor='#00bfff')
                    ax.add_patch(rect_cap)

                ax.set_xlim(-1, 6)
                ax.set_ylim(total_depth * 1.1, -2.0)
                ax.axis('off')
                ax.plot([0, 5], [0, 0], color='#E0E0E0', linewidth=2)
                
                st.pyplot(fig, transparent=True)

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------
        st.markdown("---")
        if st.button("Calculate Stress Profiles", type="primary"):

            def calculate_profile(mode_name, load_q):
                results = []
                math_logs = []
                sigma_prev = load_q
                
                for layer in layers:
                    z_in_layer = {layer['top'], layer['bot']}
                    for d in range(int(layer['top']), int(layer['bot']) + 1):
                        if layer['top'] < d < layer['bot']:
                            z_in_layer.add(float(d))
                            
                    if layer['top'] < water_depth < layer['bot']: z_in_layer.add(water_depth)
                    cap_top = water_depth - hc
                    if layer['top'] < cap_top < layer['bot']: z_in_layer.add(cap_top)
                        
                    sorted_z = sorted(list(z_in_layer))
                    z_internal_prev = layer['top']
                    
                    for i, z in enumerate(sorted_z):
                        dz = z - z_internal_prev
                        z_mid = (z + z_internal_prev) / 2
                        eff_wt_boundary = water_depth - hc
                        
                        if z_mid > eff_wt_boundary:
                            gam = layer['g_sat']
                            g_sym = "\\gamma_{sat}"
                        else:
                            gam = layer['g_dry']
                            g_sym = "\\gamma_{dry}"
                            
                        sigma = sigma_prev + (gam * dz)
                        
                        if dz > 0.0001:
                            math_logs.append(f"**Layer {layer['id']} ({layer['type']}): {z_internal_prev:.2f}m to {z:.2f}m** (${g_sym}={gam}$)")
                            math_logs.append(f"$\\sigma = {sigma_prev:.2f} + ({gam} \\times {dz:.2f}) = {sigma:.2f}$")

                        u_h = 0.0
                        u_calc_text = "0"

                        if z < water_depth and z >= (water_depth - hc):
                            u_h = -(water_depth - z) * GAMMA_W
                            u_calc_text = f"-({water_depth} - {z:.2f}) \\times {GAMMA_W}"
                        
                        elif artesian_layer_id > 1 and layer['id'] == artesian_layer_id - 1 and z >= water_depth:
                            z_top = layer['top']
                            z_bot = layer['bot']
                            u_top = max(0.0, (z_top - water_depth) * GAMMA_W)
                            u_bot = (z_bot - water_depth + artesian_head) * GAMMA_W
                            
                            if z_bot > z_top:
                                u_h = u_top + (z - z_top) * (u_bot - u_top) / (z_bot - z_top)
                                u_calc_text = f"Linear: {u_top:.1f} + ({z:.1f}-{z_top:.1f}) \\times \\frac{{{u_bot:.1f}-{u_top:.1f}}}{{{z_bot:.1f}-{z_top:.1f}}}"
                            else:
                                u_h = u_bot
                                u_calc_text = f"{u_h:.2f}"

                        elif artesian_layer_id > 0 and layer['id'] >= artesian_layer_id and z >= water_depth:
                            u_h = (z - water_depth + artesian_head) * GAMMA_W
                            u_calc_text = f"(({z:.2f} - {water_depth}) + {artesian_head}) \\times {GAMMA_W}"

                        elif z >= water_depth:
                            u_h = (z - water_depth) * GAMMA_W
                            u_calc_text = f"({z:.2f} - {water_depth}) \\times {GAMMA_W}"
                            
                        else:
                            u_h = 0.0
                            u_calc_text = "0"
                            
                        u_excess = 0.0
                        u_calc_add = ""
                        
                        if mode_name == "Short Term" and load_q > 0 and layer['type'] == 'Clay':
                            u_excess = load_q
                            u_calc_add = f" + {load_q} (Excess)"
                            
                        u_tot = u_h + u_excess
                        sig_eff = sigma - u_tot
                        
                        math_logs.append(f"**@ z={z:.2f}m ({layer['type']}):**")
                        math_logs.append(f"$u = {u_calc_text}{u_calc_add} = {u_tot:.2f}$")
                        math_logs.append(f"$\\sigma' = {sigma:.2f} - {u_tot:.2f} = \\mathbf{{{sig_eff:.2f}}}$")
                        math_logs.append("---")
                        
                        pos_tag = ""
                        if abs(z - layer['top']) < 0.001: pos_tag = " (Top)"
                        elif abs(z - layer['bot']) < 0.001: pos_tag = " (Bottom)"
                        
                        results.append({
                            "Depth (z)": z,
                            "Soil Type": f"{layer['type']}{pos_tag}",
                            "Total Stress (σ)": sigma,
                            "Pore Pressure (u)": u_tot,
                            "Eff. Stress (σ')": sig_eff
                        })
                        
                        sigma_prev = sigma
                        z_internal_prev = z

                return pd.DataFrame(results), math_logs

            df_init, log_init = calculate_profile("Initial", 0.0)
            df_long, log_long = calculate_profile("Long Term", surcharge)
            df_short, log_short = calculate_profile("Short Term", surcharge)

            def plot_results(df, title, ax):
                # Adjusted to bright neon colors for dark backgrounds
                ax.plot(df["Total Stress (σ)"], df["Depth (z)"], color='#00bfff', marker='o', linewidth=2, label="Total σ")
                ax.plot(df["Pore Pressure (u)"], df["Depth (z)"], color='#ff4b4b', marker='x', linestyle='--', linewidth=2, label="Pore u")
                ax.plot(df["Eff. Stress (σ')"], df["Depth (z)"], color='#00ffaa', marker='s', linewidth=2, label="Effective σ'")
                ax.invert_yaxis()
                ax.set_xlabel("Stress (kPa)")
                ax.set_ylabel("Depth (m)")
                ax.grid(True, linestyle='--', alpha=0.3)
                ax.legend(facecolor='rgba(0,0,0,0.5)', edgecolor='none')

            st.markdown("### Results Comparison")
            c1, c2, c3 = st.columns(3)

            for col, df, title in zip([c1, c2, c3],
                                      [df_init, df_long, df_short],
                                      ["Initial", "Long Term", "Short Term"]):
                with col:
                    st.subheader(title)
                    
                    # Apply Transparent HTML Table Rendering
                    html_table = df.to_html(index=False, classes="glass-table", border=0, float_format="%.2f")
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                    # Apply Transparent Dark Background Plotting
                    with plt.style.context('dark_background'):
                        fig, ax = plt.subplots(figsize=(5, 6), facecolor='none')
                        ax.set_facecolor('none')
                        plot_results(df, title, ax)
                        st.pyplot(fig, transparent=True)
                        plt.close(fig)
                    
            with st.expander("Show Calculation Logs", expanded=True):
                # We combine the logs and wrap them in the glass-box
                init_log_str = "\n".join([line for line in log_init if line != "---"])
                long_log_str = "\n".join([line for line in log_long if line != "---"])
                
                st.markdown(
                    f"""
<div class="glass-box">
<h3>Initial State Logs</h3>

{init_log_str}

</div>

<div class="glass-box">
<h3>Long Term State Logs</h3>

{long_log_str}

</div>
                    """, 
                    unsafe_allow_html=True
                )

    # =====================================================
    # TAB 2 — HEAVE CHECK
    # =====================================================
    with tab2:
        st.subheader("Heave & Piping Analysis")
        st.caption("Checks safety against bottom heave for excavations in Clay over Artesian Sand.")
        st.info("Note: This tab uses a simplified single-layer model and is separate from the multi-layer stress profile calculator in Tab 1.")
        
        col_h_input, col_h_viz = st.columns([1, 2])

        with col_h_input:
            st.markdown("#### Soil Parameters")
            h_clay = st.number_input("Total Clay Thickness (m)", value=8.0, step=0.5)
            d_exc = st.number_input("Excavation Depth (m)", value=5.0, step=0.5)
            g_clay = st.number_input("Clay Sat. Unit Weight (kN/m³)", value=19.0, step=0.1)
            h_art_heave = st.number_input("Artesian Head Above Surface (m)", value=2.0, step=0.5, key="h_art_heave")
            
            rem_clay = h_clay - d_exc
            st.info(f"Resisting Clay Plug: **{rem_clay:.2f} m**")
            
            calc_trigger = st.button("Calculate Factor of Safety", type="primary")

        with col_h_viz:
            st.markdown("#### Geotechnical Profile & Failure Analysis")
            
            # Apply transparent dark styling
            with plt.style.context('dark_background'):
                fig_h, (ax_geo, ax_stress) = plt.subplots(1, 2, figsize=(10, 5), sharey=True, gridspec_kw={'width_ratios': [1.6, 1]}, facecolor='none')
                ax_geo.set_facecolor('none')
                ax_stress.set_facecolor('none')
                plt.subplots_adjust(wspace=0.05)

                # --- 1. GEOMETRY (LEFT) ---
                color_clay = '#4E342E'  # Darker clay for dark mode
                color_sand = '#827717'  # Darker sand for dark mode
                color_plug = '#3E2723'  
                
                ax_geo.add_patch(patches.Rectangle((0, 0), 10, h_clay, facecolor=color_clay, edgecolor='#8D6E63', linewidth=1))
                ax_geo.add_patch(patches.Rectangle((4, 0), 6, d_exc, facecolor='none', edgecolor='#E0E0E0', linewidth=1.5))
                ax_geo.add_patch(patches.Rectangle((0, h_clay), 10, 4, facecolor=color_sand, edgecolor='#FBC02D', hatch='..'))
                
                if rem_clay > 0:
                    ax_geo.add_patch(patches.Rectangle((4, d_exc), 6, rem_clay, facecolor=color_plug, edgecolor='#E0E0E0', hatch='//', alpha=0.8))
                    ax_geo.text(7, d_exc + rem_clay/2, "CLAY PLUG\n(Resistance)", ha='center', va='center', color='white', fontweight='bold', fontsize=8)

                ax_geo.text(1, h_clay/2, "CLAY LAYER", fontsize=10, fontweight='bold', color='#E0E0E0')
                ax_geo.text(5, h_clay + 2, "SAND LAYER (Artesian)", ha='center', fontsize=10, color='#FBC02D')

                pipe_x = 2
                ax_geo.plot([pipe_x, pipe_x], [-2, h_clay+1], color='#E0E0E0', linewidth=1.5)
                ax_geo.plot([pipe_x+0.3, pipe_x+0.3], [-2, h_clay+1], color='#E0E0E0', linewidth=1.5)
                ax_geo.fill_between([pipe_x, pipe_x+0.3], -h_art_heave, h_clay+1, color='#00bfff', alpha=0.6)
                ax_geo.plot(pipe_x+0.45, -h_art_heave, marker='v', color='#00ffaa', markersize=8)
                ax_geo.text(pipe_x+0.6, -h_art_heave, f"Piezometric Head\n(+{h_art_heave}m)", color='#00ffaa', va='center', fontsize=9, fontweight='bold')

                ax_geo.set_ylim(h_clay + 3, -h_art_heave - 2)
                ax_geo.set_xlim(0, 10)
                ax_geo.axis('off')

                # --- 2. STRESS DIAGRAM (RIGHT) ---
                ax_stress.axis('off')
                
                if calc_trigger and rem_clay > 0:
                    ax_stress.axis('on')
                    ax_stress.spines['top'].set_visible(True)
                    ax_stress.spines['left'].set_visible(True)
                    ax_stress.spines['right'].set_visible(False)
                    ax_stress.spines['bottom'].set_visible(False)
                    ax_stress.spines['top'].set_color('#E0E0E0')
                    ax_stress.spines['left'].set_color('#E0E0E0')
                    
                    sigma_val = rem_clay * g_clay
                    u_val = (h_clay + h_art_heave) * GAMMA_W
                    
                    ax_stress.axvline(0, color='#E0E0E0', linewidth=1)
                    ax_stress.set_xlabel("Stress (kPa)", fontweight='bold', color='#E0E0E0')
                    ax_stress.xaxis.set_label_position('top')
                    ax_stress.xaxis.tick_top()
                    ax_stress.tick_params(colors='#E0E0E0')
                    
                    ax_stress.plot([0, u_val], [-h_art_heave, h_clay], color='#ff4b4b', linewidth=2, label="U (Uplift)")
                    ax_stress.plot([0, u_val], [h_clay, h_clay], color='#ff4b4b', linestyle='--', linewidth=1)
                    ax_stress.text(u_val, h_clay, f" {u_val:.1f}", color='#ff4b4b', va='bottom', fontsize=9, fontweight='bold')
                    
                    ax_stress.plot([0, sigma_val], [d_exc, h_clay], color='#00bfff', linewidth=2, label="σ (Weight)")
                    ax_stress.plot([0, sigma_val], [h_clay, h_clay], color='#00bfff', linestyle='--', linewidth=1)
                    ax_stress.text(sigma_val, h_clay, f" {sigma_val:.1f}", color='#00bfff', va='top', fontsize=9, fontweight='bold')

                    ax_stress.axhline(h_clay, color='#E0E0E0', linestyle='--', linewidth=1)
                    ax_geo.axhline(h_clay, color='#E0E0E0', linestyle='--', linewidth=1)
                    
                    ax_stress.legend(loc='lower right', fontsize=8, facecolor='rgba(0,0,0,0.5)', edgecolor='none')
                    ax_stress.set_xlim(0, max(u_val, sigma_val)*1.3)
                    ax_stress.grid(True, axis='x', linestyle=':', alpha=0.3)

                st.pyplot(fig_h, transparent=True)

        # -------------------------------------------------
        # 3. CALCULATION OUTPUT
        # -------------------------------------------------
        if calc_trigger:
            if rem_clay <= 0:
                st.error("Invalid: Excavation deeper than clay layer.")
            else:
                sigma_val = rem_clay * g_clay
                u_val = (h_clay + h_art_heave) * GAMMA_W
                fs = sigma_val / u_val
                
                c_res_l, c_res_r = st.columns([1, 1.5])
                
                with c_res_l:
                    if fs < 1.0:
                        st.error(f"**FS = {fs:.3f}** (UNSAFE)")
                        st.warning("⚠️ CRITICAL FAILURE: Bottom Heave Expected.")
                    elif fs < 1.2:
                        st.warning(f"**FS = {fs:.3f}** (MARGINAL)")
                        st.info("⚠️ Risk is high. Increase plug thickness or lower water table.")
                    else:
                        st.success(f"**FS = {fs:.3f}** (SAFE)")
                        st.balloons()

                with c_res_r:
                    # Wrapped Detailed Math in a glass-box
                    st.markdown(
                        f"""
<div class="glass-box">
<h4>1. Downward Resistance (Weight of Clay Plug)</h4>

$$ \sigma_v = H_{{plug}} \\times \gamma_{{clay}} = {rem_clay:.2f} \\times {g_clay} = \mathbf{{{sigma_val:.2f} \, kPa}} $$

<h4>2. Upward Uplift Pressure (Artesian)</h4>

$$ u = (H_{{clay}} + h_{{art}}) \\times \gamma_w = ({h_clay} + {h_art_heave}) \\times {GAMMA_W} = \mathbf{{{u_val:.2f} \, kPa}} $$

<h4>3. Factor of Safety</h4>

$$ FS = \\frac{{\sigma_v}}{{u}} = \\frac{{{sigma_val:.2f}}}{{{u_val:.2f}}} = \mathbf{{{fs:.3f}}} $$
</div>
                        """, 
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    app()
