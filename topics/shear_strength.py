import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
# --- 1. THEME IMPORT ---
from theme import write_text, glass_box

def app():
    # =================================================================
    # HEADER & MODE
    # =================================================================
    write_text("section_header", "Shear Strength Analysis")
    st.markdown("---")

    calc_mode = st.radio(
        "**Calculation Goal:**",
        ["1. Calculate Shear Strength (Forward)", "2. Find Parameters from Lab Data (Back Analysis)"],
        horizontal=True
    )
    st.markdown("---")

    # =================================================================
    # GLOBAL PARAMETERS (Generic)
    # =================================================================
    global_params = {}
    col_g1, col_g2 = st.columns(2)
    
    if "1. Calculate" in calc_mode:
        with col_g1:
            c_val = st.number_input("Cohesion ($c$) [kPa]", value=10.0, step=1.0)
        with col_g2:
            phi_val = st.number_input("Friction Angle ($\phi$) [deg]", value=30.0, step=1.0)
        global_params = {"c": c_val, "phi": phi_val}
    else:
        st.info("Enter results from **2 Failure Tests** (e.g., Triaxial) to find $c$ and $\phi$.")

    # =================================================================
    # LAYOUT: INPUTS (Left) - VISUALIZATION (Right)
    # =================================================================
    col_input, col_viz = st.columns([1.5, 1])
    test_data = []
    
    with col_input:
        write_text("subheader", "Stress State Data")
        
        num_tests = 1 if "1. Calculate" in calc_mode else 2
        
        for i in range(num_tests):
            title = "State of Stress" if num_tests == 1 else f"Test Sample #{i+1} (Failure)"
            
            with st.expander(title, expanded=True):
                c1, c2 = st.columns(2)
                sig3 = c1.number_input(f"$\sigma_3$ (Confining) [kPa]", value=50.0 + (i*50), key=f"s3_{i}")
                
                if "1. Calculate" in calc_mode:
                    sig1 = c2.number_input(f"$\sigma_1$ (Applied) [kPa]", value=120.0, key=f"s1_{i}", help="Enter the axial stress applied to the soil.")
                else:
                    sig1 = c2.number_input(f"$\sigma_{{1f}}$ (Failure) [kPa]", value=150.0 + (i*150), key=f"s1f_{i}")

                center = (sig1 + sig3) / 2
                radius = (sig1 - sig3) / 2
                
                test_data.append({
                    "id": i+1, "sig3": sig3, "sig1": sig1, "center": center, "radius": radius
                })

    # =================================================================
    # HELPER: CALCULATION ENGINE
    # =================================================================
    def calculate_strength_at_state(test, g_params):
        s3 = test['sig3']
        s1_applied = test['sig1']
        c = g_params['c']
        phi = g_params['phi']
        
        tan_term = math.tan(math.radians(45 + phi/2))
        sig1_failure = (s3 * (tan_term**2)) + (2 * c * tan_term)
        
        is_safe = s1_applied < sig1_failure
        status_text = "STABLE" if is_safe else "FAILURE"
        
        # --- 3. REFACTORED LOG (DOUBLE BACKSLASHES FOR LATEX) ---
        math_log = f"""
**1. Input Parameters:**
$c = {c}$ kPa, $\\phi = {phi}^\\circ$
Confining Stress $\\sigma_3 = {s3}$ kPa

**2. Calculation (Mohr-Coulomb):**
The max axial stress $\\sigma_1$ before failure is defined by:
$$\\sigma_{{1,max}} = \\sigma_3 \\tan^2(45+\\phi/2) + 2c\\tan(45+\\phi/2)$$
$$\\sigma_{{1,max}} = {s3:.1f} ({tan_term:.2f})^2 + 2({c:.1f})({tan_term:.2f})$$
$$\\sigma_{{1,max}} = \\mathbf{{{sig1_failure:.2f} \\, kPa}}$$
"""
        return {"status": status_text, "sig1_failure": sig1_failure, "log": math_log}

    def solve_parameters(tests):
        t1, t2 = tests[0], tests[1]
        dy = t2['sig1'] - t1['sig1']
        dx = t2['sig3'] - t1['sig3']
        
        if dx == 0:
            return {"c": 0, "phi": 0, "log": "Error: Confining pressures must be different."}
            
        m = dy / dx 
        
        if m < 1:
            phi_val = 0
            log = "Slope < 1 (Physics error: Material cannot have negative friction)."
            c_val = 0
        else:
            term = math.atan(math.sqrt(m)) 
            phi_rad = 2 * (term - (math.pi/4))
            phi_val = math.degrees(phi_rad)
            b = t1['sig1'] - (m * t1['sig3'])
            c_val = b / (2 * math.sqrt(m))
        
            # --- 3. REFACTORED LOG (DOUBLE BACKSLASHES FOR LATEX) ---
            log = f"""
**1. Determine Slope ($m$):**
$$m = \\frac{{\\sigma_{{1,Test2}} - \\sigma_{{1,Test1}}}}{{\\sigma_{{3,Test2}} - \\sigma_{{3,Test1}}}}$$
$$m = \\frac{{{t2['sig1']} - {t1['sig1']}}}{{{t2['sig3']} - {t1['sig3']}}} = {m:.3f}$$

**2. Calculate Friction Angle ($\\phi$):**
$$\\phi = 2 \\left( \\tan^{{-1}}(\\sqrt{{m}}) - 45^\\circ \\right)$$
$$\\phi = \\mathbf{{{phi_val:.2f}^\\circ}}$$

**3. Calculate Cohesion ($c$):**
$$c = \\frac{{\\text{{Intercept}}}}{{2\\sqrt{{m}}}} = \\frac{{{b:.2f}}}{{2\\sqrt{{{m:.3f}}}}}$$
$$c = \\mathbf{{{c_val:.2f} \\, kPa}}$$
"""
        return {"c": c_val, "phi": phi_val, "log": log}

    # --- VISUALIZER ---
    with col_viz:
        write_text("subheader", "Mohr Circle Diagram")
        fig, ax = plt.subplots(figsize=(6, 6))
        
        max_stress = max([t['sig1'] for t in test_data]) if test_data else 100
        limit = max_stress * 1.2
        ax.set_xlim(0, limit)
        ax.set_ylim(0, limit * 0.6) 
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_xlabel("Normal Stress $\sigma$ (kPa)")
        ax.set_ylabel("Shear Stress $\\tau$ (kPa)")
        
        for t in test_data:
            arc = patches.Arc((t['center'], 0), t['radius']*2, t['radius']*2, 
                              theta1=0, theta2=180, edgecolor='#1E3A8A', linewidth=2)
            ax.add_patch(arc)
            ax.plot([t['sig3'], t['sig1']], [0, 0], 'o', color='#1E3A8A', markersize=5)
        
        if "1. Calculate" in calc_mode:
            c_plot = global_params['c']
            phi_plot = global_params['phi']
            color = '#D97706' # Dark amber for limit line
        elif len(test_data) == 2:
            res = solve_parameters(test_data)
            c_plot = res['c']
            phi_plot = res['phi']
            color = '#059669' # Green for solved line
        else:
            c_plot, phi_plot = 0, 0
            color = 'gray'

        if phi_plot >= 0:
            x_vals = np.array([0, limit])
            y_vals = c_plot + x_vals * np.tan(math.radians(phi_plot))
            ax.plot(x_vals, y_vals, color=color, linewidth=2, linestyle='-', label='Failure Envelope')
            
            label_x = limit * 0.4
            label_y = c_plot + label_x * np.tan(math.radians(phi_plot))
            ax.text(label_x, label_y + (limit*0.03), 
                    f"$\\tau_f = {c_plot:.1f} + \\sigma \\tan({phi_plot:.1f}^\\circ)$", 
                    color=color, fontsize=11, fontweight='bold')

        st.pyplot(fig)

    # =================================================================
    # RESULTS SECTION (FULL WIDTH)
    # =================================================================
    st.divider()

    if "1. Calculate" in calc_mode:
        if st.button("Calculate Strength", type="primary"):
            t = test_data[0]
            res = calculate_strength_at_state(t, global_params)
            
            # --- 4. CONSOLIDATED RESULTS ---
            res_summary = f"""
### Current State: {res['status']}
**Max Sustainable Axial Stress ($\\sigma_{{1,max}}$):** {res['sig1_failure']:.2f} kPa
"""
            glass_box(res_summary)
            
            with st.expander("Show Step-by-Step Calculation", expanded=True):
                glass_box(res['log'])

    else:
        if st.button("Calculate Soil Parameters", type="primary"):
            if len(test_data) < 2:
                st.error("You need 2 tests to find the parameters.")
            else:
                res = solve_parameters(test_data)
                
                # --- 4. CONSOLIDATED RESULTS ---
                res_summary = f"""
### Derived Soil Parameters
**Cohesion ($c$):** {res['c']:.2f} kPa

**Friction Angle ($\\phi$):** {res['phi']:.2f}$^\\circ$
"""
                glass_box(res_summary)
                
                with st.expander("Show Derivation", expanded=True):
                    glass_box(res['log'])

if __name__ == "__main__":
    app()
