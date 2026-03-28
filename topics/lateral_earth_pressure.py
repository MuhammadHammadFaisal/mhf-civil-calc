import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from theme import write_text, glass_box, glass_table




# =========================================================
# HELPER FUNCTIONS
# =========================================================
def build_coulomb_cracked_wedge(H_c, alpha, beta_c, phi_c, delta, gamma_c, c_c):
    phi_r = np.radians(phi_c)
    del_r = np.radians(delta)
    alp_r = np.radians(alpha)
    bet_r = np.radians(beta_c)

    theta_fail_deg = 45.0 + phi_c / 2.0
    theta_fail_r = np.radians(theta_fail_deg)

    m_ground = np.tan(bet_r)
    top_x_full = -H_c * np.tan(alp_r)

    denom_x = np.tan(theta_fail_r) - m_ground
    if abs(denom_x) < 1e-9:
        return {"valid": False, "reason": "Failure plane and ground surface are nearly parallel."}

    # ---------------------------------------------------------
    # 1. FULL COHESIONLESS WEDGE -> ONLY TO GET Ka_dry FOR z_t
    # ---------------------------------------------------------
    x_c_full = (H_c - top_x_full * m_ground) / denom_x
    y_c_full = x_c_full * np.tan(theta_fail_r)

    area_full = abs(
        top_x_full * (y_c_full - 0.0) +
        x_c_full * (0.0 - H_c) +
        0.0 * (H_c - y_c_full)
    ) / 2.0

    W_full = gamma_c * area_full

    wall_face_ang = np.arctan2(H_c, top_x_full if abs(top_x_full) > 1e-9 else 1e-9)
    wall_normal_ang = wall_face_ang - np.pi / 2.0
    theta_p = wall_normal_ang + del_r
    p_dir = np.array([np.cos(theta_p), np.sin(theta_p)])

    failure_face_ang_full = np.arctan2(y_c_full, x_c_full if abs(x_c_full) > 1e-9 else 1e-9)
    failure_normal_ang_full = failure_face_ang_full + np.pi / 2.0
    t_dir_full = np.array([np.cos(failure_face_ang_full), np.sin(failure_face_ang_full)])
    n_dir_full = np.array([np.cos(failure_normal_ang_full), np.sin(failure_normal_ang_full)])

    A_eq_full = np.column_stack((p_dir, n_dir_full + np.tan(phi_r) * t_dir_full))
    b_eq_full = np.array([0.0, W_full])

    try:
        P_dry, N_dry = np.linalg.solve(A_eq_full, b_eq_full)
    except np.linalg.LinAlgError:
        return {"valid": False, "reason": "Dry reference wedge could not be solved."}

    if gamma_c <= 0 or H_c <= 0 or P_dry <= 0:
        return {"valid": False, "reason": "Invalid dry reference wedge."}

    Ka_dry = (2.0 * P_dry) / (gamma_c * H_c**2)

    # ---------------------------------------------------------
    # 2. TENSION CRACK DEPTH
    # ---------------------------------------------------------
    if c_c > 0 and Ka_dry > 0:
        zt = min(H_c, (2.0 * c_c) / (gamma_c * np.sqrt(Ka_dry)))
    else:
        zt = 0.0

    H_eff = max(H_c - zt, 1e-6)

       # ---------------------------------------------------------
    # 3. CRACKED / EFFECTIVE WEDGE GEOMETRY
    # ---------------------------------------------------------
    # Keep the ORIGINAL ground intersection C.
    # Only the left/top wall point moves downward by z_t.
    y_d = max(H_c - zt, 1e-6)
    x_d = -y_d * np.tan(alp_r)

    x_c = x_c_full
    y_c = y_c_full

    # Effective cracked wedge = triangle B-D-C
    # B = (0, 0)
    # D = (x_d, y_d) on wall
    # C = (x_c, y_c) original ground/failure intersection
    area_eff = abs(x_d * y_c - x_c * y_d) / 2.0
    W_eff = gamma_c * area_eff

    # Cohesion acts along the full failure plane B-C
    L_fail_eff = np.hypot(x_c, y_c)
    C_plane = c_c * L_fail_eff

    failure_face_ang = np.arctan2(y_c, x_c if abs(x_c) > 1e-9 else 1e-9)
    failure_normal_ang = failure_face_ang + np.pi / 2.0

    t_dir = np.array([np.cos(failure_face_ang), np.sin(failure_face_ang)])
    n_dir = np.array([np.cos(failure_normal_ang), np.sin(failure_normal_ang)])

    A_eq = np.column_stack((p_dir, n_dir + np.tan(phi_r) * t_dir))
    b_eq = np.array([
        -C_plane * t_dir[0],
        W_eff - C_plane * t_dir[1]
    ])

    try:
        sol = np.linalg.solve(A_eq, b_eq)
        P = sol[0]
        N = sol[1]
    except np.linalg.LinAlgError:
        return {"valid": False, "reason": "Cracked cohesive wedge could not be solved."}

    R_vec = N * n_dir + (N * np.tan(phi_r)) * t_dir
    R = np.linalg.norm(R_vec)
    theta_r_plot = np.arctan2(R_vec[1], R_vec[0])

    Ka_eff = (2.0 * P) / (gamma_c * H_c**2)

    return {
        "valid": True,
        "reason": "",
        "theta_fail_deg": theta_fail_deg,
        "theta_fail_r": theta_fail_r,
        "m_ground": m_ground,
        "top_x_full": top_x_full,
        "x_c_full": x_c_full,
        "y_c_full": y_c_full,
        "x_d": x_d,
        "y_d": y_d,
        "x_c": x_c,
        "y_c": y_c,
        "area_eff": area_eff,
        "W_eff": W_eff,
        "L_fail_eff": L_fail_eff,
        "C_plane": C_plane,
        "zt": zt,
        "H_eff": H_c - zt,
        "Ka_dry": Ka_dry,
        "Ka_eff": Ka_eff,
        "P": P,
        "N": N,
        "R": R,
        "theta_p": theta_p,
        "theta_r_plot": theta_r_plot,
        "wall_face_ang": wall_face_ang,
        "wall_normal_ang": wall_normal_ang,
        "failure_face_ang": failure_face_ang,
        "failure_normal_ang": failure_normal_ang,
        "t_dir": t_dir,
        "n_dir": n_dir,
    }
def load_coulomb_soil_defaults():
    defaults = {
        "Sand": {
            "phi_c_val": 32.0,
            "delta_c_val": 20.0,
            "gamma_c_val": 18.0,
            "c_c_val": 0.0,
        },
        "Clay": {
            "phi_c_val": 24.0,
            "delta_c_val": 8.0,
            "gamma_c_val": 19.0,
            "c_c_val": 20.0,
        },
    }

    soil = st.session_state.get("c_soil_type", "Sand")
    for key, value in defaults[soil].items():
        st.session_state[key] = value
def tension_crack_depth(layer):
    phi_r = np.radians(layer['phi'])
    Ka = (1 - np.sin(phi_r)) / (1 + np.sin(phi_r))
    
    if layer['c'] == 0:
        return 0.0
    
    z_t = (2 * layer['c']) / (layer['gamma_dry'] * np.sqrt(Ka))
    return z_t
    
def render_layers_input(prefix, label, default_layers):
    """Renders the input fields for soil layers dynamically."""
    write_text("subheader", label)
    num = st.number_input(f"No. of Layers ({prefix})", 1, 5, len(default_layers), key=f"{prefix}_num")
    layers = []
    current_z = 0.0
    
    for i in range(int(num)):
        with st.expander(f"Layer {i+1} ({prefix})", expanded=False):
            # Safely get defaults
            def_h = default_layers[i].get('H', 3.0) if i < len(default_layers) else 3.0
            def_gb = default_layers[i].get('g_dry', 18.0) if i < len(default_layers) else 18.0
            def_gs = default_layers[i].get('g_sat', 20.0) if i < len(default_layers) else 20.0
            def_p = default_layers[i].get('p', 30.0) if i < len(default_layers) else 30.0
            def_c = default_layers[i].get('c', 0.0) if i < len(default_layers) else 0.0

            type_key = f"{prefix}_type_{i}"
            soil_type = st.selectbox("Soil Type", ["Sand", "Clay", "Custom"], key=type_key)
            
            h = st.number_input(f"H (m)", 0.1, 20.0, def_h, key=f"{prefix}_h_{i}")
            
            c1, c2 = st.columns(2)
            gamma_dry = c1.number_input(f"γ_dry (kN/m³)", 10.0, 25.0, def_gb, key=f"{prefix}_gb_{i}", help="Dry/dry weight above WT")
            gamma_sat = c2.number_input(f"γ_sat (kN/m³)", 10.0, 25.0, def_gs, key=f"{prefix}_gs_{i}", help="Saturated weight below WT")
            
            c3, c4 = st.columns(2)
            phi = c3.number_input(f"ϕ' (deg)", 0.0, 45.0, def_p, key=f"{prefix}_p_{i}")
            c = c4.number_input(f"c' (kPa)", 0.0, 100.0, def_c, key=f"{prefix}_c_{i}")
            
            layers.append({
                "id": i+1, 
                "H": h, 
                "gamma_dry": gamma_dry, 
                "gamma_sat": gamma_sat, 
                "phi": phi, 
                "c": c, 
                "top": current_z, 
                "bottom": current_z + h, 
                "type": soil_type
            })
            current_z += h
    return layers
    
def calculate_stress(z_local, layers, wt_depth, surcharge, gamma_w, mode="Active"):
    """Calculates lateral stress dynamically splitting layers at the Water Table."""
    if not layers: return 0, 0, 0, "None", 0
    
    active_layer = layers[-1]
    total_defined_depth = layers[-1]['bottom']
    
    for l in layers:
        if z_local <= l['bottom']: 
            active_layer = l
            break
            
    # 3. Calculate Total Vertical Stress (Splitting at WT)
    sig_v = surcharge
    
    for l in layers:
        layer_top = l['top']
        layer_bottom = l['bottom']
        
        if z_local <= layer_top:
            break
            
        segment_bottom = min(z_local, layer_bottom)
        
        if wt_depth <= layer_top:
            # Entirely below WT
            sig_v += (segment_bottom - layer_top) * l['gamma_sat']
        elif wt_depth >= segment_bottom:
            # Entirely above WT
            sig_v += (segment_bottom - layer_top) * l['gamma_dry']
        else:
            # Water table splits this segment!
            dry_thick = wt_depth - layer_top
            sat_thick = segment_bottom - wt_depth
            sig_v += (dry_thick * l['gamma_dry']) + (sat_thick * l['gamma_sat'])
            
    # Extrapolate if depth exceeds defined layers
    if z_local > total_defined_depth:
        extra_depth = z_local - total_defined_depth
        if total_defined_depth >= wt_depth:
            sig_v += extra_depth * layers[-1]['gamma_sat']
        else:
            sig_v += extra_depth * layers[-1]['gamma_dry']

    # 4. Pore Water Pressure
    u = (z_local - wt_depth) * gamma_w if z_local > wt_depth else 0.0
    sig_v_eff = sig_v - u
    
    # 5. Lateral Earth Pressure Coefficient
    phi_r = np.radians(active_layer['phi'])
    c_val = active_layer['c']
    
    if mode == "Active":
        K = (1 - np.sin(phi_r)) / (1 + np.sin(phi_r))
        sig_lat_eff = (sig_v_eff * K) - (2 * c_val * np.sqrt(K))
    else: 
        K = (1 + np.sin(phi_r)) / (1 - np.sin(phi_r))
        sig_lat_eff = (sig_v_eff * K) + (2 * c_val * np.sqrt(K))
        
    sig_lat_tot = sig_lat_eff + u
    
    return sig_lat_eff, sig_lat_tot, u, K, active_layer['id'], sig_v
    
# =========================================================
# MAIN APP
# =========================================================
def app():
    
    tab_rankine, tab_coulomb = st.tabs(["1. Rankine's Theory (Wall Profile)", "2. Coulomb's Wedge Theory"])

    # ---------------------------------------------------------
    # TAB 1: RANKINE (Standard)
    # ---------------------------------------------------------
    with tab_rankine:
        col_input, col_viz = st.columns([1.5, 1])

        with col_input:
            write_text("subheader", "1. Wall Geometry")
            c1, c2= st.columns(2)
            with c1:
                wall_height = st.number_input("Total Wall Height (m)", 1.0, 30.0, 9.0, step=0.5)
                gamma_w = st.radio("γw [kN/m³]", [9.81, 10.0], index=1, horizontal=True)
            with c2:
                excavation_depth = st.number_input("Excavation Depth (Left) (m)", 0.0, wall_height, 4.5, step=0.5)

            write_text("subheader", "2. Soil Properties")
            c1, c2= st.columns(2)
            with c1:
                with st.container(border=True):
                    write_text("caption"," Left Side (Passive / Excavated)")
                    left_q = st.number_input("Surcharge q (kPa)", 0.0, 100.0, 50.0)
                    left_wt = st.number_input("Left WT Depth (m)", 0.0, 20.0, 1.5)
                    def_left = [
                        {'H': 1.5, 'g_dry': 18.0, 'g_sat': 18.0, 'p': 38.0, 'c': 0.0}, 
                        {'H': 3.0, 'g_dry': 20.0, 'g_sat': 20.0, 'p': 28.0, 'c': 10.0}
                    ]
                    left_layers = render_layers_input("L", "Passive Layers", def_left)
                
            st.write("")
            
            with c2:
                with st.container(border=True):
                    write_text("caption"," Right Side (Active / Backfill)")
                    right_q = st.number_input("Surcharge q (kPa)", min_value=0.0, value=10.0, step=5.0)
                    right_wt = st.number_input("Right WT Depth (m)", 0.0, 20.0, 6.0)    
                    def_right = [
                        {'H': 6.0, 'g_dry': 18.0, 'g_sat': 18.0, 'p': 38.0, 'c': 0.0}, 
                        {'H': 3.0, 'g_dry': 20.0, 'g_sat': 20.0, 'p': 28.0, 'c': 10.0}
                    ]
                    right_layers = render_layers_input("R", "Active Layers", def_right)
            
            st.markdown("---")
            calc_trigger = st.button("Calculate Pressure Profile", type="primary", width="stretch")

        with col_viz:
            write_text("subheader", "Soil Profile Preview")
            fig_profile, ax_p = plt.subplots(figsize=(15, 6))
            wall_width = 1.0
            
            # Draw Wall (Hatched)
            # Wall goes from 0 down to wall_height
            rect_wall = patches.Rectangle((-wall_width/2, 0), wall_width, wall_height, facecolor='lightgrey', edgecolor='black', hatch='//')
            ax_p.add_patch(rect_wall)
            
            Y_top = wall_height
            Y_exc = wall_height - excavation_depth 
            
            # --- DRAW RIGHT SIDE LAYERS (ACTIVE) ---
            current_y = Y_top
            for l in right_layers:
                h = l['H']
                color = '#E6D690' if l['type'] == "Sand" else ('#B0A494' if l['type'] == "Clay" else '#C1B088')
                rect = patches.Rectangle((wall_width/2, current_y - h), 6, h, facecolor=color, edgecolor='gray', alpha=0.6)
                ax_p.add_patch(rect)
                ax_p.text(wall_width/2 + 3, current_y - h/2, f"{l['type']}\n$\\gamma_b={l['gamma_dry']}$", ha='center', va='center', fontsize=9)
                current_y -= h
            
            # [FIX] Right Side Extrapolation (Fill to bottom)
            if current_y > -2:
                last_l = right_layers[-1] if right_layers else {'type': 'Sand', 'gamma_dry': 18.0}
                color = '#E6D690' if last_l['type'] == "Sand" else ('#B0A494' if last_l['type'] == "Clay" else '#C1B088')
                rect = patches.Rectangle((wall_width/2, -2), 6, current_y - (-2), facecolor=color, edgecolor='gray', alpha=0.4)
                ax_p.add_patch(rect)

            # --- DRAW LEFT SIDE LAYERS (PASSIVE) ---
            current_y = Y_exc
            for l in left_layers:
                h = l['H']
                color = '#E6D690' if l['type'] == "Sand" else ('#B0A494' if l['type'] == "Clay" else '#C1B088')
                rect = patches.Rectangle((-wall_width/2 - 6, current_y - h), 6, h, facecolor=color, edgecolor='gray', alpha=0.6)
                ax_p.add_patch(rect)
                ax_p.text(-wall_width/2 - 3, current_y - h/2, f"{l['type']}\n$\\gamma_b={l['gamma_dry']}$", ha='center', va='center', fontsize=9)
                current_y -= h
                
            # [FIX] Left Side Extrapolation (Mandatory touch bottom)
            if current_y > -2:
                last_l = left_layers[-1] if left_layers else {'type': 'Sand', 'gamma_dry': 18.0}
                color = '#E6D690' if last_l['type'] == "Sand" else ('#B0A494' if last_l['type'] == "Clay" else '#C1B088')
                
                rect = patches.Rectangle((-wall_width/2 - 6, -2), 6, current_y - (-2), facecolor=color, edgecolor='gray', alpha=0.6)
                ax_p.add_patch(rect)
                ax_p.text(-wall_width/2 - 3, (current_y + 0)/2, f"(Extrapolated)\n{last_l['type']}", ha='center', va='center', fontsize=8, style='italic', color='#333')
            
            # Surcharge Arrows
            if right_q > 0:
                for x in np.linspace(wall_width/2 + 0.5, wall_width/2 + 5.5, 6):
                    ax_p.arrow(x, Y_top + 0.5, 0, -0.4, head_width=0.2, fc='red', ec='red')
                ax_p.text(wall_width/2 + 3, Y_top + 0.6, f"q = {right_q} kPa", color='red', ha='center', fontweight='bold')
            
            # Ground Lines
            ax_p.plot([wall_width/2, wall_width/2 + 6], [Y_top, Y_top], 'k-', linewidth=2) 
            ax_p.plot([-wall_width/2 - 6, -wall_width/2], [Y_exc, Y_exc], 'k-', linewidth=2) 
            
            ax_p.set_xlim(-8, 8)
            ax_p.set_ylim(-2, wall_height + 2)
            ax_p.set_aspect('equal')
            ax_p.axis('off')
            st.pyplot(fig_profile)
            plt.close(fig_profile)

        # --- RESULT GRAPH ---
        if calc_trigger:
            st.markdown("---")
            
            # =========================================
            # 1. RUN ALL CALCULATIONS FIRST
            # =========================================
            # --- Graph Data ---
            y_steps = np.linspace(0, wall_height, 100)
            p_right_raw = [calculate_stress(y, right_layers, right_wt, right_q, gamma_w, "Active")[0] for y in y_steps]
            p_right_calc = [max(0, p) for p in p_right_raw]
            
            y_steps_l = np.linspace(0, wall_height - excavation_depth, 100)
            p_left_raw = [calculate_stress(y, left_layers, left_wt, left_q, gamma_w, "Passive")[0] for y in y_steps_l]
            p_left_calc = [max(0, p) for p in p_left_raw]
            
            # --- Tension Crack ---
            zt = 0
            if right_layers:
                top_active_layer = right_layers[0]
                zt = tension_crack_depth(top_active_layer)

            # --- Active Force (Pa) ---
            y_array = np.array(y_steps)
            p_array = np.array(p_right_calc)
            
            trapz_func = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
            
            Pa = trapz_func(p_array, y_array)
            moment_about_top = trapz_func(p_array * y_array, y_array)
            
            y_bar = moment_about_top / Pa if Pa != 0 else 0
            h_from_base = wall_height - y_bar
            
            # --- Hydrostatic Crack Thrust ---
            Pw_crack = 0
            h_Pw_from_base = 0
            if zt > 0:
                Pw_crack = 0.5 * gamma_w * (zt**2)
                h_Pw_from_base = wall_height - ((2/3) * zt)
                
            # --- Passive Force (Pp) ---
            y_array_l = np.array(y_steps_l)
            p_array_l = np.array(p_left_calc)
            
            Pp = trapz_func(p_array_l, y_array_l)
            moment_top_p = trapz_func(p_array_l * y_array_l, y_array_l)
            
            y_bar_p = moment_top_p / Pp if Pp != 0 else 0
            passive_height = wall_height - excavation_depth
            h_p = passive_height - y_bar_p
            
            # --- Overturning & Stability (No Wall Weight) ---
            Mo = (Pa * h_from_base) + (Pw_crack * h_Pw_from_base) 
            Mr = Pp * h_p  # Only passive soil pressure resisting
            FS_ot = Mr / Mo if Mo != 0 else 0

            # =========================================
            # 2. BUILD THE GRAPH (Don't display it yet)
            # =========================================
            fig_stress, ax_s = plt.subplots(figsize=(6, 8)) 
            ax_s.plot(p_right_raw, y_steps, 'r-')
            ax_s.plot(p_left_raw, y_steps_l + excavation_depth, 'g-')
            
            ax_s.fill_betweenx(y_steps, 0, p_right_calc, alpha=0.1, color='red')
            ax_s.fill_betweenx(y_steps_l + excavation_depth, 0, p_left_calc, alpha=0.1, color='green')
            
            ax_s.axvline(0, color='black', linewidth=1, linestyle='--')
            ax_s.invert_yaxis()
            ax_s.set_title("Pressure Graph")

            # =========================================
            # 3. DISPLAY UI: LEFT (TEXT) & RIGHT (GRAPH)
            # =========================================
            col_text, col_graph = st.columns([1.2, 1]) 
            
            with col_text:
                write_text("subheader", "Analysis Results")
                
                if zt > 0:
                    st.warning(f"⚠️ Tension Crack Depth ≈ {zt:.2f} m. (Water-filled assumption applied)")
                else:
                    st.success("No tension crack")
                
                # Combine all results into a single formatted string, left-aligned to match your step-by-step logs
                results_summary = f"""<div style='text-align: left;'>

#### Resultant Forces
* **Active Force $P_a$**: {Pa:.2f} kN/m (at {h_from_base:.2f} m from base)
* **Passive Force $P_p$**: {Pp:.2f} kN/m (at {h_p:.2f} m from base)

#### Stability Check
* **Overturning Moment $M_o$**: {Mo:.2f} kNm/m
* **Resisting Moment $M_r$**: {Mr:.2f} kNm/m
* **FS against Overturning**: {FS_ot:.2f}

</div>"""
                glass_box(results_summary)
            with col_graph:
                st.pyplot(fig_stress)
                plt.close(fig_stress) 

        # --- DATA TABLE & DETAILED LOGS ---
        if calc_trigger:
            st.markdown("---")
            write_text("subheader", "Stress Calculation Table")
            table_data = []
            
            right_logs = []
            left_logs = []
            
            depths_to_check = [float(z) for z in range(0, int(wall_height) + 1)]
            for l in right_layers:
                if l['bottom'] < wall_height:
                    depths_to_check.append(l['bottom'] + 0.001) 
            depths_to_check = sorted(list(set(depths_to_check)))

            for z in depths_to_check:
                row = {"Depth (m)": round(z, 2)}
                
                # --- RIGHT SIDE (ACTIVE) ---
                r_sig_eff, r_sig_tot, r_u, r_K, r_L, r_sig_v = calculate_stress(z, right_layers, right_wt, right_q, gamma_w, "Active")
                row["[R] Layer"] = r_L
                row["[R] Eff Stress"] = max(0, r_sig_eff) 
                row["[R] u (Water)"] = r_u
                row["[R] Ka"] = r_K
                
                r_c = [layer['c'] for layer in right_layers if layer['id'] == r_L][0] if r_L != "None" else 0
                r_sig_v_eff = r_sig_v - r_u
                
                r_log = f"**@ Depth $z = {z:.2f}$ m** (Layer {r_L})\n"
                r_log += f"- Total Vertical: $\\sigma_v = {r_sig_v:.2f}$ kPa\n"
                r_log += f"- Pore Pressure: $u = {r_u:.2f}$ kPa\n"
                r_log += f"- Eff Vertical: $\\sigma_v' = \\sigma_v - u = {r_sig_v_eff:.2f}$ kPa\n"
                r_log += f"- Eff Horizontal: $\\sigma_h' = (\\sigma_v' \\times K_a) - 2c'\\sqrt{{K_a}}$\n"
                r_log += f"- $\\sigma_h' = ({r_sig_v_eff:.2f} \\times {r_K:.3f}) - 2({r_c})\\sqrt{{{r_K:.3f}}} = \\mathbf{{{r_sig_eff:.2f} \\text{{ kPa}}}}$\n"
                right_logs.append(r_log)
                
                # --- LEFT SIDE (PASSIVE) ---
                local_z_left = z - excavation_depth
                if local_z_left >= 0:
                    l_sig_eff, l_sig_tot, l_u, l_K, l_L, l_sig_v = calculate_stress(local_z_left, left_layers, left_wt, left_q, gamma_w, "Passive")
                    row["[L] Layer"] = l_L
                    row["[L] Eff Stress"] = l_sig_eff
                    row["[L] u (Water)"] = l_u
                    row["[L] Kp"] = l_K
                    
                    l_c = [layer['c'] for layer in left_layers if layer['id'] == l_L][0] if l_L != "None" else 0
                    l_sig_v_eff = l_sig_v - l_u
                    
                    l_log = f"**@ Depth $z = {z:.2f}$ m** (Local $z_{{exc}} = {local_z_left:.2f}$ m, Layer {l_L})\n"
                    l_log += f"- Total Vertical: $\\sigma_v = {l_sig_v:.2f}$ kPa\n"
                    l_log += f"- Pore Pressure: $u = {l_u:.2f}$ kPa\n"
                    l_log += f"- Eff Vertical: $\\sigma_v' = \\sigma_v - u = {l_sig_v_eff:.2f}$ kPa\n"
                    l_log += f"- Eff Horizontal: $\\sigma_h' = (\\sigma_v' \\times K_p) + 2c'\\sqrt{{K_p}}$\n"
                    l_log += f"- $\\sigma_h' = ({l_sig_v_eff:.2f} \\times {l_K:.3f}) + 2({l_c})\\sqrt{{{l_K:.3f}}} = \\mathbf{{{l_sig_eff:.2f} \\text{{ kPa}}}}$\n"
                    left_logs.append(l_log)
                else:
                    row["[L] Layer"] = "-"
                    row["[L] Eff Stress"] = 0.0
                    row["[L] u (Water)"] = 0.0
                    row["[L] Kp"] = 0.0
                    
                table_data.append(row)
            
            df = pd.DataFrame(table_data)
            
            df = df.round({
                "Depth (m)": 2,
                "[R] Eff Stress": 2,
                "[R] u (Water)": 2,
                "[R] Ka": 3,
                "[L] Eff Stress": 2,
                "[L] u (Water)": 2,
                "[L] Kp": 3
            })
            
            glass_table(df)
            
            with st.expander("Show Detailed Step-by-Step Calculations"):
                for log in right_logs:
                    glass_box(log)
                for log in left_logs:
                    glass_box(log)

    # ---------------------------------------------------------
    # TAB 2: COULOMB (Wedge Theory)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # TAB 2: COULOMB (Wedge Theory)
    # ---------------------------------------------------------
    with tab_coulomb:
        write_text("section_header", "Coulomb's Wedge Theory")
        
        col_c_in, col_c_viz = st.columns([0.6, 0.4], gap="medium")

        with col_c_in:
            write_text("subheader", "1. Wall & Geometry")
            c1, c2 = st.columns(2)
            with c1:
                H_c = st.number_input("Wall Height (H) [m]", 1.0, 20.0, 6.0)
                alpha = st.number_input("Wall Batter (α) [deg]", 0.0, 30.0, 10.0, help="Angle from vertical")
            with c2:
                beta_c = st.number_input("Backfill Slope (β) [deg]", 0.0, 30.0, 15.0)

            write_text("subheader", "2. Soil & Interface")
            c3, c4 = st.columns(2)
            with c3:
                c_soil_type = st.selectbox("Soil Type", ["Sand", "Clay"], key="c_soil_type")
                if c_soil_type == "Sand":
                    d_phi, d_delta, d_gam, d_c = 32.0, 20.0, 18.0, 0.0
                else:
                    d_phi, d_delta, d_gam, d_c = 24.0, 8.0, 19.0, 20.0

                phi_c = st.number_input("Friction Angle (ϕ') [deg]", 0.0, 45.0, d_phi)
                c_c = st.number_input("Cohesion (c') [kPa]", 0.0, 100.0, d_c)

            with c4:
                delta = st.number_input("Wall Friction (δ) [deg]", 0.0, 30.0, d_delta)
                gamma_c = st.number_input("Unit Weight (γ) [kN/m³]", 10.0, 25.0, d_gam)

            c_calc_btn = st.button("Calculate Wedge Forces", type="primary", width="stretch")

        # ---------------------------------------------------------
        # BUILD CRACKED WEDGE MODEL ONCE
        # ---------------------------------------------------------
        cw = build_coulomb_cracked_wedge(H_c, alpha, beta_c, phi_c, delta, gamma_c, c_c)

        with col_c_viz:
            write_text("subheader", "Failure Wedge Diagram (FBD)")

            phi_r = np.radians(phi_c)
            alp_r = np.radians(alpha)
            bet_r = np.radians(beta_c)

            top_x_full = -H_c * np.tan(alp_r)

            wall_base_width = 2.2
            wall_top_width = 0.8
            front_base_x = -wall_base_width
            front_top_x = top_x_full - wall_top_width

            wall_poly = np.array([
                [0.0, 0.0],
                [top_x_full, H_c],
                [front_top_x, H_c],
                [front_base_x, 0.0],
            ])

            fig_w, ax_w = plt.subplots(figsize=(7.4, 6.2))
            ax_w.set_facecolor("#efefef")

            # Wall
            ax_w.add_patch(
                patches.Polygon(
                    wall_poly,
                    closed=True,
                    facecolor="lightgrey",
                    edgecolor="black",
                    hatch="//",
                    linewidth=1.6,
                    zorder=2
                )
            )

            # Wall back face
            ax_w.plot([0, top_x_full], [0, H_c], color="black", linewidth=2.2, zorder=4)

            if cw["valid"]:
                x_c_full = cw["x_c_full"]
                y_c_full = cw["y_c_full"]
                x_d = cw["x_d"]
                y_d = cw["y_d"]
                x_c = cw["x_c"]
                y_c = cw["y_c"]
                zt = cw["zt"]

                x_ground_end = x_c_full + max(1.2, 0.35 * H_c)
                y_ground_end = H_c + (x_ground_end - top_x_full) * cw["m_ground"]

                # Ground surface (full)
                ax_w.plot(
                    [top_x_full, x_ground_end],
                    [H_c, y_ground_end],
                    color="black",
                    linewidth=2.2,
                    zorder=4
                )

                # Active cracked wedge only
                                # Active cracked wedge only
                active_wedge_poly = np.array([
                    [0.0, 0.0],
                    [x_d, y_d],
                    [x_c, y_c],
                ])
                ax_w.add_patch(
                    patches.Polygon(
                        active_wedge_poly,
                        closed=True,
                        facecolor="#e9dcc2",
                        edgecolor="none",
                        alpha=0.95,
                        zorder=1
                    )
                )

                # Excluded zone due to tension crack
                if zt > 1e-6:
                    excluded_poly = np.array([
                        [top_x_full, H_c],
                        [x_c, y_c],
                        [x_d, y_d],
                    ])
                    ax_w.add_patch(
                        patches.Polygon(
                            excluded_poly,
                            closed=True,
                            facecolor="#fff4b8",
                            edgecolor="#d8b400",
                            hatch="///",
                            alpha=0.85,
                            linewidth=1.0,
                            zorder=1.5
                        )
                    )
                
                    crack_x = top_x_full + 0.12
                    ax_w.plot(
                        [crack_x, crack_x],
                        [H_c, y_d],
                        linestyle="--",
                        color="royalblue",
                        linewidth=2.0,
                        zorder=6
                    )
                    ax_w.text(
                        crack_x + 0.08,
                        (H_c + y_d) / 2.0,
                        f"zₜ={zt:.2f} m",
                        fontsize=10,
                        color="royalblue",
                        va="center"
                    )

                    # Crack depth marker beside wall
                    crack_x = top_x_full + 0.12
                    ax_w.plot(
                        [crack_x, crack_x],
                        [H_c, y_d],
                        linestyle="--",
                        color="royalblue",
                        linewidth=2.0,
                        zorder=6
                    )
                    ax_w.text(
                        crack_x + 0.08,
                        (H_c + y_d) / 2.0,
                        f"zₜ={zt:.2f} m",
                        fontsize=10,
                        color="royalblue",
                        va="center"
                    )

                # Excluded zone due to tension crack
                if zt > 1e-6:
                    excluded_poly = np.array([
                        [top_x_eff, H_eff],
                        [top_x_full, H_c],
                        [x_c_full, y_c_full],
                        [x_c_eff, y_c_eff],
                    ])
                    ax_w.add_patch(
                        patches.Polygon(
                            excluded_poly,
                            closed=True,
                            facecolor="#fff4b8",
                            edgecolor="#d8b400",
                            hatch="///",
                            alpha=0.85,
                            linewidth=1.0,
                            zorder=1.5
                        )
                    )

                    # Crack depth marker
                    crack_x = top_x_full + 0.15
                    ax_w.plot(
                        [crack_x, crack_x],
                        [H_c, H_eff],
                        linestyle="--",
                        color="royalblue",
                        linewidth=2.0,
                        zorder=6
                    )
                    ax_w.text(
                        crack_x + 0.08,
                        (H_c + H_eff) / 2.0,
                        f"zₜ={zt:.2f} m",
                        fontsize=10,
                        color="royalblue",
                        va="center"
                    )

                # Failure plane for cracked wedge
                ax_w.plot(
                    [0, x_c],
                    [0, y_c],
                    linestyle="--",
                    color="red",
                    linewidth=2.4,
                    zorder=3
                )

                # Base reference
                ax_w.plot(
                    [front_base_x - 0.2, x_c_full + 0.8],
                    [0, 0],
                    linestyle="--",
                    color="gray",
                    linewidth=1.0,
                    alpha=0.35,
                    zorder=0
                )

                # ---------------------------------------------------------
                # FORCE LOCATIONS
                # ---------------------------------------------------------
                cx, cy = (0 + x_d + x_c) / 3.0, (0 + y_d + y_c) / 3.0

                force_len = 0.95
                ms = 18
                norm_len = 0.70

                # P location on active wall contact only
                t_p = 0.45
                px = t_p * x_d
                py = t_p * y_d

                # R location on failure plane
                t_r = 0.56
                rx = t_r * x_c
                ry = t_r * y_c

                # Cohesion location on failure plane
                t_c = 0.74
                cxp = t_c * x_c
                cyp = t_c * y_c
                # Normals
                ax_w.plot(
                    [px, px + norm_len * np.cos(cw["wall_normal_ang"])],
                    [py, py + norm_len * np.sin(cw["wall_normal_ang"])],
                    linestyle="--",
                    color="gray",
                    linewidth=1.2,
                    zorder=5
                )
                ax_w.plot(
                    [rx, rx + norm_len * np.cos(cw["failure_normal_ang"])],
                    [ry, ry + norm_len * np.sin(cw["failure_normal_ang"])],
                    linestyle="--",
                    color="gray",
                    linewidth=1.2,
                    zorder=5
                )

                # P
                ax_w.annotate(
                    "",
                    xy=(px + force_len * np.cos(cw["theta_p"]), py + force_len * np.sin(cw["theta_p"])),
                    xytext=(px, py),
                    arrowprops=dict(arrowstyle="-|>", color="red", lw=3, mutation_scale=ms),
                    zorder=8
                )
                ax_w.text(
                    px + force_len * np.cos(cw["theta_p"]) + 0.05,
                    py + force_len * np.sin(cw["theta_p"]) - 0.02,
                    "P",
                    color="red",
                    fontsize=13,
                    fontweight="bold"
                )

                # R (normal + friction only)
                ax_w.annotate(
                    "",
                    xy=(rx + force_len * np.cos(cw["theta_r_plot"]), ry + force_len * np.sin(cw["theta_r_plot"])),
                    xytext=(rx, ry),
                    arrowprops=dict(arrowstyle="-|>", color="green", lw=3, mutation_scale=ms),
                    zorder=8
                )
                ax_w.text(
                    rx + force_len * np.cos(cw["theta_r_plot"]) - 0.12,
                    ry + force_len * np.sin(cw["theta_r_plot"]) + 0.08,
                    "R",
                    color="green",
                    fontsize=13,
                    fontweight="bold"
                )

                # Cohesive force along failure plane
                ax_w.annotate(
                    "",
                    xy=(cxp + 0.85 * cw["t_dir"][0], cyp + 0.85 * cw["t_dir"][1]),
                    xytext=(cxp, cyp),
                    arrowprops=dict(arrowstyle="-|>", color="darkorange", lw=3, mutation_scale=ms),
                    zorder=8
                )
                ax_w.text(
                    cxp + 0.85 * cw["t_dir"][0] + 0.06,
                    cyp + 0.85 * cw["t_dir"][1] + 0.02,
                    "C",
                    color="darkorange",
                    fontsize=13,
                    fontweight="bold"
                )

                # W
                ax_w.annotate(
                    "",
                    xy=(cx, cy - 0.95),
                    xytext=(cx, cy + 0.55),
                    arrowprops=dict(arrowstyle="-|>", color="purple", lw=3, mutation_scale=ms),
                    zorder=8
                )
                ax_w.text(
                    cx + 0.15,
                    cy - 0.10,
                    "W",
                    color="purple",
                    fontsize=13,
                    fontweight="bold"
                )

                # Labels
                ax_w.text(px - 0.18, py + 0.18, f"δ={delta:.1f}°", fontsize=10, color="#333333")
                ax_w.text(rx + 0.12, ry + 0.15, f"ϕ={phi_c:.1f}°", fontsize=10, color="#333333")
                ax_w.text(0.65, 0.30, f"θ={cw['theta_fail_deg']:.1f}°", fontsize=10, color="#333333")

                min_x = min(front_base_x, top_x_full) - 0.55
                max_x = max(x_c, x_ground_end) + 0.55
                max_y = max(y_c, y_ground_end, H_c) + 0.55

                ax_w.set_xlim(min_x, max_x)
                ax_w.set_ylim(-0.35, max_y)
            else:
                ax_w.text(0.5, 0.5, cw["reason"], ha="center", va="center", transform=ax_w.transAxes)

            ax_w.set_aspect("equal", adjustable="box")
            ax_w.axis("off")
            st.pyplot(fig_w, use_container_width=True)
            plt.close(fig_w)

        # ---------------------------------------------------------
        # CALCULATION PANEL
        # ---------------------------------------------------------
        if c_calc_btn:
            if not cw["valid"]:
                st.error(cw["reason"])
            else:
                write_text("subheader", "Final Answers")

                final_answers_df = pd.DataFrame({
                    "Result": [
                        "Tension crack depth, zₜ",
                        "Cohesive force on failure plane, C",
                        "Wall force on wedge, P",
                        "Equivalent active coefficient, Kₐ",
                    ],
                    "Value": [
                        f"{cw['zt']:.2f} m",
                        f"{cw['C_plane']:.2f} kN/m",
                        f"{cw['P']:.2f} kN/m",
                        f"{cw['Ka_eff']:.4f}",
                    ]
                })
                glass_table(final_answers_df)

                report_md = (
                    f"### Short Calculation Summary\n"
                    f"- First, a dry reference wedge is solved only to estimate the tension crack depth.\n"
                    f"- Then the wedge height is reduced to:\n\n"
                    f"$$H_{{eff}} = H - z_t = {H_c:.2f} - {cw['zt']:.2f} = \\mathbf{{{cw['H_eff']:.2f}\\,\\mathrm{{m}}}}$$\n\n"
                    f"- The cracked wedge area actually used in equilibrium is:\n\n"
                    f"$$A_{{eff}} = \\mathbf{{{cw['area_eff']:.3f}\\,\\mathrm{{m^2/m}}}}$$\n\n"
                    f"- Its weight is:\n\n"
                    f"$$W = \\gamma A_{{eff}} = ({gamma_c:.2f})({cw['area_eff']:.3f}) = \\mathbf{{{cw['W_eff']:.2f}\\,\\mathrm{{kN/m}}}}$$\n\n"
                    f"- Cohesion along the cracked failure plane is:\n\n"
                    f"$$C = c' L = \\mathbf{{{cw['C_plane']:.2f}\\,\\mathrm{{kN/m}}}}$$\n\n"
                    f"- Final wall force from cracked c-ϕ wedge equilibrium:\n\n"
                    f"$$P = \\mathbf{{{cw['P']:.2f}\\,\\mathrm{{kN/m}}}}$$\n\n"
                    f"- Equivalent active coefficient based on full wall height:\n\n"
                    f"$$K_a = \\mathbf{{{cw['Ka_eff']:.4f}}}$$"
                )

                with st.expander("Detailed Calculation Steps", expanded=True):
                    glass_box(report_md)


if __name__ == "__main__":
    app()
