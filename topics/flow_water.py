import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ============================================================
# SESSION STORAGE
# ============================================================
if "results" not in st.session_state:
    st.session_state.results = None

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

# ============================================================
# MAIN APP
# ============================================================

def app():

    tab1, tab2 = st.tabs(["1D Seepage", "Permeability"])

# =================================================================
# TAB 1: 1D SEEPAGE
# =================================================================
    with tab1:

        st.caption("Determine Effective Stress at Point A. (Datum is at the Bottom of Soil)")

        col_setup, col_plot = st.columns([1, 1.2])

        # ------------------------- LEFT COLUMN: INPUTS -------------------------
        with col_setup:

            st.markdown("### 1. Problem Setup")

            val_z = st.number_input("Soil Specimen Height (z) [m]", 0.1, step=0.5, value=4.0)
            val_y = st.number_input("Water Height above Soil (y) [m]", 0.0, step=0.5, value=2.0)
            val_x = st.number_input("Piezometer Head at Bottom (x) [m]", 0.0, step=0.5, value=7.5)

            gamma_sat = st.number_input("Saturated Unit Weight (γ_sat) [kN/m³]", 18.0, step=0.1)
            gamma_w = 10.0

            val_A = st.slider("Height of Point 'A' from Datum [m]", 0.0, val_z, val_z/2)

            st.markdown("---")

            if st.button("Calculate Effective Stress", type="primary"):

                gamma_sub = gamma_sat - gamma_w

                H_top = val_z + val_y
                H_bot = val_x
                delta_H = H_top - H_bot

                if delta_H > 0.001:
                    flow_type = "Downward"
                    i = abs(delta_H) / val_z
                elif delta_H < -0.001:
                    flow_type = "Upward"
                    i = abs(delta_H) / val_z
                else:
                    flow_type = "No Flow (Hydrostatic)"
                    i = 0.0

                depth_A_soil = val_z - val_A

                sigma_total = (val_y * gamma_w) + (depth_A_soil * gamma_sat)

                H_A = H_bot + (val_A / val_z) * (H_top - H_bot)
                h_p_A = H_A - val_A
                u_val = h_p_A * gamma_w

                sigma_prime_1 = sigma_total - u_val

                seepage_force = i * gamma_w

                if flow_type == "Downward":
                    bracket_term = gamma_sub + seepage_force
                elif flow_type == "Upward":
                    bracket_term = gamma_sub - seepage_force
                else:
                    bracket_term = gamma_sub

                sigma_prime_2 = depth_A_soil * bracket_term

                # STORE RESULTS (AND INPUT SNAPSHOTS TO PREVENT GLITCHES)
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
                    "bracket_term": bracket_term,
                    # Snapshots of inputs at calculation time
                    "z_snap": val_z,
                    "y_snap": val_y,
                    "A_snap": val_A
                }

        # ------------------------- RIGHT COLUMN: PLOT -------------------------
        with col_plot:

            fig, ax = plt.subplots(figsize=(7, 8))

            datum_y = 0.0
            soil_w = 2.5
            soil_x = 3.5

            wl_top = val_z + val_y
            wl_bot = val_x

            if wl_top > wl_bot:
                flow_arrow = "⬇️"
            elif wl_bot > wl_top:
                flow_arrow = "⬆️"
            else:
                flow_arrow = "No Flow"

            ax.add_patch(patches.Rectangle((soil_x, datum_y), soil_w, val_z,
                                           facecolor='#E3C195', hatch='...', edgecolor='none'))

            ax.text(soil_x + soil_w/2, val_z/2, "SOIL", ha='center', fontweight='bold')

            ax.text(soil_x + soil_w/2, wl_top + 0.5, f"FLOW {flow_arrow}",
                    ha='center', fontweight='bold')

            ax.set_xlim(-1.5, 9)
            ax.set_ylim(datum_y - 1.5, max(wl_bot, wl_top) + 1)
            ax.axis('off')

            st.pyplot(fig)

        # ------------------------- FULL WIDTH RESULTS (BELOW COLUMNS) -------------------------
        # This block is now OUTSIDE 'with col_setup:' and 'with col_plot:'
        
        results = st.session_state.results
        
        if results:
            st.divider() # Adds a nice line separator
            st.markdown("### Results")
            
            st.success(f"Flow Condition: {results['flow_type']} (i = {results['i']:.3f})")

            # Create 3 new wide columns just for results
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Total Stress (σ)", f"{results['sigma_total']:.2f} kPa")
            res_col2.metric("Pore Pressure (u)", f"{results['u_val']:.2f} kPa")
            res_col3.metric("Effective Stress (σ')", f"{results['sigma_prime_1']:.2f} kPa")

            # Derivation Expander (Full Width)
            with st.expander("View Detailed Step-by-Step Derivation (2 Methods)", expanded=True):
                
                # Retrieve snapshots so derivation matches the answer even if you move sliders
                z_s = results['z_snap']
                y_s = results['y_snap']
                A_s = results['A_snap']

                st.markdown("#### Method 1: Definition (σ' = σ − u)")

                st.latex(rf"Depth = {z_s} - {A_s} = {results['depth_A_soil']:.2f} m")

                st.markdown("Step 1: Total Stress")
                st.latex(rf"\sigma = ({gamma_w} \cdot {y_s}) + ({gamma_sat} \cdot {results['depth_A_soil']:.2f}) = {results['sigma_total']:.2f} kPa")

                st.markdown("Step 2: Pore Pressure")
                st.latex(rf"u = ({results['H_A']:.2f} - {A_s:.2f}) \cdot {gamma_w} = {results['u_val']:.2f} kPa")

                st.markdown("Step 3: Effective Stress")
                st.latex(rf"\sigma' = {results['sigma_total']:.2f} - {results['u_val']:.2f} = {results['sigma_prime_1']:.2f} kPa")

                st.markdown("---")

                st.markdown("#### Method 2: Seepage Force")

                st.latex(rf"\sigma' = {results['depth_A_soil']:.2f} \times {results['bracket_term']:.2f} = {results['sigma_prime_2']:.2f} kPa")

# =================================================================
# TAB 2: PERMEABILITY
# =================================================================
    with tab2:

        st.caption("Calculate Coefficient of Permeability (k).")

        test_type = st.radio("Select Method", ["Constant Head", "Falling Head"], horizontal=True)

# ---------------- CONSTANT HEAD ----------------
        if "Constant" in test_type:

            st.latex(r"k = \frac{Q \cdot L}{A \cdot h \cdot t}")

            Q = st.number_input("Collected Volume (Q) [cm³]", value=500.0)
            L = st.number_input("Specimen Length (L) [cm]", value=15.0)
            h = st.number_input("Head Difference (h) [cm]", value=40.0)
            A = st.number_input("Specimen Area (A) [cm²]", value=40.0)
            t = st.number_input("Time Interval (t) [sec]", value=60.0)

            if st.button("Calculate Permeability (k)", key="btn_const"):

                if A*h*t > 0:
                    k_val = (Q*L)/(A*h*t)
                    st.success(f"k = {format_scientific(k_val)} cm/sec")

# ---------------- FALLING HEAD ----------------
        else:

            st.latex(r"k = 2.303 \frac{aL}{At} \log_{10}(h_1/h_2)")

            a = st.number_input("Standpipe Area (a) [cm²]", value=0.5)
            A_soil = st.number_input("Soil Specimen Area (A) [cm²]", value=40.0)
            L_fall = st.number_input("Specimen Length (L) [cm]", value=15.0)
            h1 = st.number_input("Initial Head (h1) [cm]", value=50.0)
            h2 = st.number_input("Final Head (h2) [cm]", value=30.0)
            t_fall = st.number_input("Time Interval (t) [sec]", value=300.0)

            if st.button("Calculate Permeability (k)", key="btn_fall"):

                if h1 > h2 > 0 and A_soil*t_fall > 0:
                    k_val = (2.303*a*L_fall/(A_soil*t_fall))*np.log10(h1/h2)
                    st.success(f"k = {format_scientific(k_val)} cm/sec")
                else:
                    st.error("Ensure h1 > h2 > 0")

# ============================================================
if __name__ == "__main__":
    app()
