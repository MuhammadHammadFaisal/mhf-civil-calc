import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
from theme import write_text, glass_box, glass_table

def app():
    # =================================================================
    # 1. HEADER & MODE
    # =================================================================
    write_text("section_header", "Shear Strength Analysis (Mohr-Coulomb)")
    st.markdown("---")

    calc_mode = st.radio(
        "**Calculation Goal:**",
        ["1. Check Stability (Forward Calculation)", "2. Derive Parameters from Lab Data (Back Analysis)"],
        horizontal=True
    )
    st.markdown("---")

    # =================================================================
    # 2. INPUTS & LAYOUT
    # =================================================================
    col_input, col_viz = st.columns([1.2, 1.5])
    test_data = []
    global_params = {}

    with col_input:
        if "1. Check" in calc_mode:
            write_text("subheader", "1. Soil Strength Parameters")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                c_val = st.number_input("Cohesion ($c$) [kPa]", value=10.0, step=1.0)
            with col_g2:
                phi_val = st.number_input("Friction Angle ($\phi$) [deg]", value=30.0, step=1.0)
            global_params = {"c": c_val, "phi": phi_val}
            
            st.markdown("---")
            write_text("subheader", "2. Applied Stress State")
            c1, c2 = st.columns(2)
            sig3 = c1.number_input("Confining Stress ($\sigma_3$) [kPa]", value=50.0, step=10.0)
            sig1 = c2.number_input("Applied Axial ($\sigma_1$) [kPa]", value=120.0, step=10.0)
            
            test_data.append({
                "id": 1, "sig3": sig3, "sig1": sig1, 
                "center": (sig1 + sig3) / 2, "radius": (sig1 - sig3) / 2
            })
            
            calc_trigger = st.button("Check Stability", type="primary")

        else:
            write_text("subheader", "1. Triaxial Test Results (Failure States)")
            st.caption("Enter the principal stresses at failure for two separate test specimens.")
            
            for i in range(2):
                with st.expander(f"Test Specimen #{i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    sig3 = c1.number_input(f"$\sigma_3$ (Confining) [kPa]", value=50.0 + (i*100), step=10.0, key=f"s3_{i}")
                    sig1 = c2.number_input(f"$\sigma_{{1f}}$ (Failure) [kPa]", value=180.0 + (i*250), step=10.0, key=f"s1_{i}")
                    
                    test_data.append({
                        "id": i+1, "sig3": sig3, "sig1": sig1, 
                        "center": (sig1 + sig3) / 2, "radius": (sig1 - sig3) / 2
                    })
            
            calc_trigger = st.button("Derive c & \phi", type="primary")

    # =================================================================
    # 3. CALCULATION ENGINE
    # =================================================================
    res = {}
    if calc_trigger:
        if "1. Check" in calc_mode:
            t = test_data[0]
            c, phi = global_params['c'], global_params['phi']
            
            tan_term = math.tan(math.radians(45 + phi/2))
            sig1_failure = (t['sig3'] * (tan_term**2)) + (2 * c * tan_term)
            
            tau_max = (sig1_failure - t['sig3']) / 2
            tau_current = t['radius']
            
            is_safe = t['sig1'] < sig1_failure
            fs = sig1_failure / t['sig1'] if t['sig1'] > 0 else 999
            
            res = {
                "safe": is_safe, "fs": fs, "sig1_fail": sig1_failure, 
                "tau_max": tau_max, "tau_cur": tau_current, "tan_term": tan_term, "error": False
            }
        else:
            t1, t2 = test_data[0], test_data[1]
            dy = t2['sig1'] - t1['sig1']
            dx = t2['sig3'] - t1['sig3']
            
            if dx == 0:
                res = {"error": True, "log": "Confining pressures must be different."}
            else:
                m = dy / dx 
                if m < 1:
                    res = {"error": True, "log": "Slope < 1 (Material cannot have negative friction)."}
                else:
                    term = math.atan(math.sqrt(m)) 
                    phi_val = math.degrees(2 * (term - (math.pi/4)))
                    b = t1['sig1'] - (m * t1['sig3'])
                    c_val = b / (2 * math.sqrt(m))
                    res = {"error": False, "c": c_val, "phi": phi_val, "m": m, "b": b}

    # =================================================================
    # 4. VISUALIZER (MOHR CIRCLES)
    # =================================================================
    with col_viz:
        write_text("subheader", "Mohr Circle Diagram")
        
        # Display data table before plot (Level-up feature)
        df_display = pd.DataFrame([{ 
            "Test": f"State {t['id']}", "σ3 (kPa)": t['sig3'], "σ1 (kPa)": t['sig1'], "Radius (τ)": t['radius']
        } for t in test_data])
        glass_table(df_display.set_index("Test"))
        
        fig, ax = plt.subplots(figsize=(7, 5))
        max_stress = max([t['sig1'] for t in test_data]) if test_data else 100
        limit = max_stress * 1.2
        ax.set_xlim(0, limit)
        ax.set_ylim(0, limit * 0.6) 
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlabel("Normal Stress $\sigma$ (kPa)", fontweight='bold')
        ax.set_ylabel("Shear Stress $\\tau$ (kPa)", fontweight='bold')
        
        # Plot Circles
        colors = ['#1E3A8A', '#059669']
        for i, t in enumerate(test_data):
            c_color = colors[i % len(colors)]
            arc = patches.Arc((t['center'], 0), t['radius']*2, t['radius']*2, 
                              theta1=0, theta2=180, edgecolor=c_color, linewidth=2, label=f"State {t['id']}")
            ax.add_patch(arc)
            ax.plot([t['sig3'], t['sig1']], [0, 0], 'o', color=c_color, markersize=5)
        
        # Plot Failure Envelope
        c_plot, phi_plot = 0, 0
        if calc_trigger and not res.get('error', False):
            if "1. Check" in calc_mode:
                c_plot, phi_plot = global_params['c'], global_params['phi']
            else:
                c_plot, phi_plot = res['c'], res['phi']
                
            x_vals = np.array([0, limit])
            y_vals = c_plot + x_vals * np.tan(math.radians(phi_plot))
            ax.plot(x_vals, y_vals, color='#D97706', linewidth=2.5, linestyle='-', label='Failure Envelope')
            
            # Fill safe zone
            ax.fill_between(x_vals, 0, y_vals, color='#D97706', alpha=0.05)
            
            # Envelope Equation Label
            label_x = limit * 0.3
            label_y = c_plot + label_x * np.tan(math.radians(phi_plot))
            ax.text(label_x, label_y + (limit*0.03), f"$\\tau_f = {c_plot:.1f} + \\sigma \\tan({phi_plot:.1f}^\\circ)$", 
                    color='#D97706', fontsize=10, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

        ax.legend(loc="upper left")
        st.pyplot(fig)

    # =================================================================
    # 5. RESULTS & MATH LOGS (FULL WIDTH)
    # =================================================================
    if calc_trigger:
        st.divider()
        if res.get('error', False):
            st.error(res['log'])
        else:
            if "1. Check" in calc_mode:
                # Custom HTML Box for Factor of Safety (Like Heave Check)
                bg_color = "#ccFFcc" if res['safe'] else "#FFcccc"
                status_txt = "SAFE: No Shear Failure" if res['safe'] else "UNSAFE: Shear Failure Occurs"
                
                c_res, c_math = st.columns([1, 1.5])
                with c_res:
                    html_box = f"""
                    <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #ccc; height: 100%;">
                        <h4 style="margin: 0; color: #333;">Factor of Safety ($\\sigma_1$)</h4>
                        <h1 style="margin: 10px 0; color: black; font-size: 3em;">{res['fs']:.2f}</h1>
                        <p style="margin: 0; color: #555; font-weight: bold;">{status_txt}</p>
                    </div>
                    """
                    st.markdown(html_box, unsafe_allow_html=True)
                    if res['safe']: st.balloons()
                    
                with c_math:
                    write_text("subheader", "Failure Criteria Derivation")
                    math_log = f"""
**1. Max Sustainable Principal Stress ($\\sigma_{{1,max}}$):**
$$\\sigma_{{1,max}} = \\sigma_3 \\tan^2(45^\\circ+\\phi/2) + 2c\\tan(45^\\circ+\\phi/2)$$
$$\\sigma_{{1,max}} = {test_data[0]['sig3']:.1f} \\cdot ({res['tan_term']:.3f})^2 + 2({global_params['c']:.1f})({res['tan_term']:.3f}) = \\mathbf{{{res['sig1_fail']:.2f} \\, kPa}}$$

**2. Shear Stress Analysis:**
$$\\tau_{{current}} = \\frac{{\\sigma_1 - \\sigma_3}}{{2}} = \\frac{{{test_data[0]['sig1']} - {test_data[0]['sig3']}}}{{2}} = \\mathbf{{{res['tau_cur']:.2f} \\, kPa}}$$
$$\\tau_{{max}} = \\frac{{\\sigma_{{1,max}} - \\sigma_3}}{{2}} = \\frac{{{res['sig1_fail']:.2f} - {test_data[0]['sig3']}}}{{2}} = \\mathbf{{{res['tau_max']:.2f} \\, kPa}}$$
"""
                    glass_box(math_log)

            else:
                # Mode 2: Back Analysis Results
                c_res, c_math = st.columns([1, 1.5])
                with c_res:
                    html_box = f"""
                    <div style="background-color: #E0F2FE; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #BAE6FD; height: 100%;">
                        <h4 style="margin: 0; color: #0369A1;">Derived Soil Parameters</h4>
                        <h2 style="margin: 10px 0; color: #075985;">$c = {res['c']:.2f}$ kPa</h2>
                        <h2 style="margin: 10px 0; color: #075985;">$\\phi = {res['phi']:.2f}^\\circ$</h2>
                    </div>
                    """
                    st.markdown(html_box, unsafe_allow_html=True)
                    
                with c_math:
                    write_text("subheader", "Back-Calculation Derivation")
                    m_log = f"""
**1. Slope of $\\sigma_1$ vs $\\sigma_3$ line ($m$):**
$$m = \\frac{{\\sigma_{{1,T2}} - \\sigma_{{1,T1}}}}{{\\sigma_{{3,T2}} - \\sigma_{{3,T1}}}} = \\frac{{{test_data[1]['sig1']} - {test_data[0]['sig1']}}}{{{test_data[1]['sig3']} - {test_data[0]['sig3']}}} = \\mathbf{{{res['m']:.3f}}}$$

**2. Friction Angle ($\\phi$):**
$$\\phi = 2 \\cdot \\left( \\tan^{{-1}}(\\sqrt{{m}}) - 45^\\circ \\right) = 2 \\cdot \\left( \\tan^{{-1}}(\\sqrt{{{res['m']:.3f}}}) - 45^\\circ \\right) = \\mathbf{{{res['phi']:.2f}^\\circ}}$$

**3. Cohesion ($c$):**
$$c = \\frac{{\\sigma_{{1,T1}} - (m \\cdot \\sigma_{{3,T1}})}}{{2\\sqrt{{m}}}} = \\frac{{{test_data[0]['sig1']} - ({res['m']:.3f} \\cdot {test_data[0]['sig3']})}}{{2\\sqrt{{{res['m']:.3f}}}}} = \\mathbf{{{res['c']:.2f} \\, kPa}}$$
"""
                    glass_box(m_log)

if __name__ == "__main__":
    app()
