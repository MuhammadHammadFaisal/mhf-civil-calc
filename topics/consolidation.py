import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from theme import write_text, glass_box, glass_table
# ================================================================
# FOURIER SOLUTION FUNCTIONS
# ================================================================
def local_degree_consolidation(z, Hdr, Tv, terms=100):
    """Calculate local degree of consolidation Uz at depth z (from drainage face)."""
    summation = 0
    for n in range(terms):
        m = 2*n + 1
        M = m * np.pi / 2
        term = (2/m) * np.sin(M * z / Hdr) * np.exp(-(m**2)*(np.pi**2)*Tv/4)
        summation += term
    ue_ratio = summation
    return max(0.0, min(1.0, 1 - ue_ratio))


def pore_pressure_ratio(z, Hdr, Tv, terms=100):
    """Calculate excess pore pressure ratio (ue/ui) at depth z."""
    summation = 0
    for n in range(terms):
        m = 2*n + 1
        M = m * np.pi / 2
        term = (2/m) * np.sin(M * z / Hdr) * np.exp(-(m**2)*(np.pi**2)*Tv/4)
        summation += term
    return max(0.0, min(1.0, summation))


# ================================================================
# APP
# ================================================================
def app():

    # ================================================================
    # TABS
    # ================================================================
    tab_settlement, tab_time = st.tabs(["Settlement Calculation", "Time Rate Analysis"])

# ================================================================
    # GLOBAL INPUTS & STRATIGRAPHY (UPDATED DEFAULTS)
    # ================================================================
    with tab_settlement:
        # Main split: Inputs take up roughly 70% of the screen, Diagram takes 30%
        col_input, col_profile = st.columns([2.2, 1])

        with col_input:
            write_text("section_header","Global Inputs")
            # Create a 2-column grid for Global Inputs
            g_col1, g_col2 = st.columns(2)
            
            with g_col1:
                water_depth = st.number_input("Water Table Depth [m]", value=2.0)
                gamma_w = st.radio("γw [kN/m³]", [9.81, 10.0], index=1, horizontal=True)
                
            with g_col2:
                surcharge_q = st.number_input("Surface Surcharge Δσ [kPa]", value=100.0)
                n_layers = st.number_input("Number of Layers", 1, 50, value=2)

            st.markdown("---")
            write_text("section_header", "Stratigraphy")
            
            # Create a 2-column grid for the Layer Expanders
            s_col1, s_col2 = st.columns(2)
            
            layers = []
            current_depth = 0.0

            # --- DEFINE DEFAULT VALUES BASED ON YOUR EXAM NOTES ---
            def_h = [6.0, 6.0]
            def_gamma = [20.0, 20.0]
            def_e0 = [0.80, 0.60]
            def_cc = [0.15, 0.10]
            def_cr = [0.05, 0.03]
            def_ocr = [1.0, 3.5]   # Layer 1 uses exact sp, Layer 2 uses OCR
            def_sp = [80.0, 0.0]   # Layer 1 sp = 80 kPa
            # -------------------------------------------------------

            for i in range(int(n_layers)):
                # Alternate placing layers in the left and right columns
                target_col = s_col1 if i % 2 == 0 else s_col2
                
                # Safely fetch defaults (fallback to standard values if user adds >2 layers)
                h_val = def_h[i] if i < len(def_h) else 4.0
                g_val = def_gamma[i] if i < len(def_gamma) else 19.0
                
                with target_col:
                    with st.expander(f"Layer {i+1} Definition", expanded=True):
                        c1, c2 = st.columns(2)
                        h = c1.number_input(f"Thickness [m]", 0.1, 100.0, h_val, key=f"h{i}")
                        gamma = c2.number_input(f"γ [kN/m³]", 0.0, 30.0, g_val, key=f"g{i}")
                        soil = st.selectbox("Soil Type", ["Clay","Sand"], index=0, key=f"t{i}")

                        mid = current_depth + h/2
                        method = "None"
                        params = {}

                        if soil == "Clay":
                            st.markdown("---")
                            method = st.radio(
                                f"Method (L{i+1})",
                                ["Method A (Cc/Cr)", "Method B (mv)", "Method C (Δe)"],
                                index=0, 
                                key=f"m{i}",
                            )

                            if method == "Method A (Cc/Cr)":
                                cp1, cp2 = st.columns(2)
                                
                                # Fetch parameter defaults
                                e0_val = def_e0[i] if i < len(def_e0) else 0.9
                                cc_val = def_cc[i] if i < len(def_cc) else 0.3
                                cr_val = def_cr[i] if i < len(def_cr) else 0.05
                                ocr_val = def_ocr[i] if i < len(def_ocr) else 1.0
                                sp_val = def_sp[i] if i < len(def_sp) else 0.0

                                e0 = cp1.number_input("e0", 0.0, 5.0, e0_val, key=f"e{i}")
                                Cc = cp2.number_input("Cc", 0.0, 5.0, cc_val, key=f"cc{i}")
                                Cr = cp1.number_input("Cr", 0.0, 5.0, cr_val, key=f"cr{i}")
                                ocr = cp2.number_input("OCR", 1.0, 10.0, ocr_val, key=f"ocr{i}")
                                sp = st.number_input("Precon. Pressure σ'p [kPa] (Opt.)", 0.0, 1000.0, sp_val, key=f"sp{i}")
                                params = {"e0":e0,"Cc":Cc,"Cr":Cr,"sp":sp,"OCR":ocr}

                            if method == "Method B (mv)":
                                mv = st.number_input("mv [1/kPa]", 0.0, 1.0, 0.0005, format="%.5f", key=f"mv{i}")
                                params = {"mv":mv}

                            if method == "Method C (Δe)":
                                cp1, cp2 = st.columns(2)
                                e0_c = cp1.number_input("Initial e0", 0.0, 5.0, 0.9, key=f"e0c{i}")
                                ef = cp2.number_input("Final ef", 0.0, 5.0, 0.8, key=f"ef{i}")
                                params = {"e0":e0_c,"ef":ef}

                        layers.append({
                            "id":i+1, "type":soil, "h":h, "gamma":gamma, 
                            "top":current_depth, "bottom":current_depth+h, 
                            "mid":mid, "method":method, "params":params
                        })
                        
                        current_depth += h
        # ================================================================
        # DYNAMIC PROFILE DIAGRAM
        # ================================================================
        with col_profile:
            write_text("section_header","Soil Profile Preview")
            fig, ax = plt.subplots(figsize=(4,6))
            colors={"Clay":"#D7CCC8","Sand":"#FFF9C4"}

            for L in layers:
                rect = patches.Rectangle((0, L["top"]), 4, L["h"],
                                         facecolor=colors[L["type"]],
                                         edgecolor="black")
                ax.add_patch(rect)
                ax.text(2, L["mid"], f"L{L['id']}\n{L['type']}", ha='center', va='center')

            ax.axhline(water_depth, color="blue", linestyle="--", linewidth=2, label="Water Table")
            ax.set_ylim(current_depth*1.05, -1)
            ax.set_xlim(0,4)
            ax.legend(loc='upper right')
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig)

        # ================================================================
        # EFFECTIVE STRESS FUNCTION
        # ================================================================
        def effective_stress(z):
            sigma = 0
            for L in layers:
                if z > L["bottom"]:
                    sigma += L["h"] * L["gamma"]
                elif L["top"] < z <= L["bottom"]:
                    sigma += (z - L["top"]) * L["gamma"]
                    break
            u = (z - water_depth)*gamma_w if z>water_depth else 0
            return max(0.001, sigma-u)

                # ================================================================
        # STEP-BY-STEP SETTLEMENT CALCULATION (UPDATED)
        # ================================================================
        write_text("section_header","Calculation Results")
        if st.button("Calculate Settlement", type="primary"):

            total_settlement = 0
            results_data = []
            
            # Container for detailed steps
            step_details = []

            for L in layers:
                if L["type"] == "Sand":
                    step_details.append(f"### Layer {L['id']} (Sand)\n*Immediate settlement in sand is not calculated in this consolidation module.*")
                    continue
                
                # Stress Calculations
                sigma0 = effective_stress(L["mid"])
                sigma_f = sigma0 + surcharge_q
                H = L["h"]
                S = 0
                p = L["params"]
                
                # Header for the layer
                details = f"### Layer {L['id']} ({L['type']})\n"
                details += rf"**Given:** Thickness $H = {H}m$, Initial Void Ratio $e_0 = {p.get('e0', 'N/A')}$\n\n"
                details += rf"**Stress Analysis:**\n"
                details += rf"- Initial Effective Stress $\sigma'_0 = {sigma0:.2f} \ kPa$\n"
                details += rf"- Stress Increment $\\Delta\sigma = {surcharge_q:.2f} \ kPa$\n"
                details += rf"- Final Effective Stress $\sigma'_f = \\sigma'_0 + \\Delta\sigma = {sigma_f:.2f} \ kPa$\n\n"

                calc_type = "Unknown"

                # -------------------------------------------------------
                # METHOD A: Cc / Cr
                # -------------------------------------------------------
                if L["method"] == "Method A (Cc/Cr)":
                    ocr = p.get("OCR", 1.0) 
                    sp_input = p.get("sp", 0)  # If OCR provided → Calculate σ'p 
                    if ocr > 1:     
                        sp = ocr * sigma0  # If OCR = 1 and σ'p given → Use σ'p 
                    elif sp_input > 0:     
                        sp = sp_input  # Otherwise assume NC 
                    else:     
                        sp = sigma0
                    Cc = p["Cc"]
                    Cr = p["Cr"]
                    e0 = p["e0"]
                    
                    details += rf"**Consolidation State Analysis:**\n"
                    details += rf"- Preconsolidation Pressure $\sigma'_p = {sp} \ kPa$\n"

                    # Case 1: Normally Consolidated
                    if sigma0 >= sp:
                        calc_type = "Normally Consolidated (NC)"
                        details += rf"- Since $\sigma'_0 \ge \\sigma'_p$ ({sigma0:.1f} $\ge$ {sp}), the soil is **Normally Consolidated**.\n"
                        details += rf"- We use the Compression Index ($C_c$) for the full range.\n\n"
                        details += r"$$S = \frac{C_c \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_f}{\sigma'_0}\right)$$"
                        
                        S = (Cc * H / (1 + e0)) * np.log10(sigma_f / sigma0)
                        
                        details += rf"\n\n**Substitution:**\n"
                        details += rf"$$S = \\frac{{{Cc} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sigma_f:.1f}}}{{{sigma0:.1f}}}\\right)$$"
                        details += rf"\n$$S = {S:.5f} m$$"

                    # Case 2: Over Consolidated (Remains OC)
                    elif sigma_f <= sp:
                        calc_type = "Over Consolidated (OC)"
                        details += rf"- Since $\sigma'_f \le \\sigma'_p$ ({sigma_f:.1f} $\le$ {sp}), the soil remains **Over Consolidated**.\n"
                        details += rf"- We use the Recompression Index ($C_r$) only.\n\n"
                        details += r"$$S = \frac{C_r \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_f}{\sigma'_0}\right)$$"
                        
                        S = (Cr * H / (1 + e0)) * np.log10(sigma_f / sigma0)
                        
                        details += rf"\n\n**Substitution:**\n"
                        details += rf"$$S = \\frac{{{Cr} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sigma_f:.1f}}}{{{sigma0:.1f}}}\\right)$$"
                        details += rf"\n$$S = {S:.5f} m$$"

                    # Case 3: Transition (OC -> NC)
                    else:
                        calc_type = "Transition (OC to NC)"
                        details += rf"- Since $\sigma'_0 < \\sigma'_p < \\sigma'_f$ ({sigma0:.1f} < {sp} < {sigma_f:.1f}), the loading pushes the soil past the preconsolidation pressure.\n"
                        details += rf"- **Part 1 (Recompression):** From $\sigma'_0$ to $\sigma'_p$ using $C_r$.\n"
                        details += rf"- **Part 2 (Virgin Compression):** From $\sigma'_p$ to $\sigma'_f$ using $C_c$.\n\n"
                        
                        # Part 1
                        s1 = (Cr * H / (1 + e0)) * np.log10(sp / sigma0)
                        details += r"**Step 1:** $$S_1 = \frac{C_r \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_p}{\sigma'_0}\right)$$"
                        details += rf"\n$$S_1 = \\frac{{{Cr} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sp}}}{{{sigma0:.1f}}}\\right) = {s1:.5f} m$$"

                        # Part 2
                        s2 = (Cc * H / (1 + e0)) * np.log10(sigma_f / sp)
                        details += r"**Step 2:** $$S_2 = \frac{C_c \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_f}{\sigma'_p}\right)$$"
                        details += rf"\n$$S_2 = \\frac{{{Cc} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sigma_f:.1f}}}{{{sp}}}\\right) = {s2:.5f} m$$"

                        S = s1 + s2
                        details += rf"\n\n**Total:** $$S = S_1 + S_2 = {s1:.5f} + {s2:.5f} = {S:.5f} m$$"

                # -------------------------------------------------------
                # METHOD B: mv
                # -------------------------------------------------------
                if L["method"] == "Method B (mv)":
                    mv = p["mv"]
                    calc_type = "Coefficient of Volume Compressibility ($m_v$)"
                    
                    details += rf"**Formula:**\n"
                    details += r"$$S = m_v \cdot \\Delta\sigma \cdot H$$"
                    
                    S = mv * surcharge_q * H
                    
                    details += rf"\n\n**Substitution:**\n"
                    details += rf"$$S = {mv:.5f} \\cdot {surcharge_q:.2f} \\cdot {H} = {S:.5f} m$$"

                # -------------------------------------------------------
                # METHOD C: Delta e
                # -------------------------------------------------------
                if L["method"] == "Method C (Δe)":
                    ef = p["ef"]
                    e0 = p["e0"]
                    calc_type = "Void Ratio Change ($\\Delta e$)"
                    
                    details += rf"**Formula:**\n"
                    details += r"$$S = \frac{e_0 - e_f}{1+e_0} \cdot H$$"
                    
                    S = ((e0 - ef) / (1 + e0)) * H
                    
                    details += rf"\n\n**Substitution:**\n"
                    details += rf"$$S = \\frac{{{e0} - {ef}}}{{1+{e0}}} \cdot {H} = {S:.5f} m$$"

                total_settlement += S
                results_data.append([f"Layer {L['id']}", f"{sigma0:.1f}", f"{sigma_f:.1f}", f"{S*1000:.2f}", calc_type])
                
                step_details.append(details)
                step_details.append("---")

# ================================================================
            # OUTPUT DISPLAY
            # ================================================================
            st.markdown("---") # Visual divider before results
            
            # This creates a visually distinct "card" with a background
            with st.container(border=True):
                
                # 1. Total Settlement Header
                st.markdown(f"## Total Settlement: :red[{total_settlement*1000:.2f} mm]")
                
                # 2. Clean Summary Table (Using our custom inline component)
                df_results = pd.DataFrame(
                    results_data, 
                    columns=["Layer", "σ'₀ (kPa)", "σ'₁ (kPa)", "Settlement (mm)", "Method"]
                )
                
                # Render the bulletproof glass table
                glass_table(df_results)
                
                # 3. Detailed Steps
                write_text("subheader", "Detailed Calculation Log")
                
                # THIS LOOP MUST BE ALIGNED HERE:
                for step in step_details:
                    if step == "---":
                        continue
                    else:
                        glass_box(step)



    # ================================================================
    # TIME RATE ANALYSIS TAB
    # ================================================================
    with tab_time:
        write_text("section_header","Time Rate Analysis (Terzaghi Theory)")

        clay_layers = [L for L in layers if L["type"]=="Clay"]
        if clay_layers:
            c1,c2,c3 = st.columns(3)
            with c1:
                choice = st.selectbox("Select Critical Clay Layer", [f"Layer {L['id']}" for L in clay_layers])
                crit = next(L for L in clay_layers if f"Layer {L['id']}"==choice)
            with c2:
                Cv = st.number_input("Coefficient of Consolidation Cv (m²/year)", 2.0)
                double = st.checkbox("Double Drainage?", value=True)
            H_total = crit["h"]
            Hdr = H_total/2 if double else H_total
            with c3:
                time_val = st.slider("Time elapsed (years)", 0.1, 50.0, 1.0)
                Tv = Cv*time_val/(Hdr**2)
                st.metric("Time Factor (Tv)", f"{Tv:.3f}")

            # Local degree and pore pressure
            plot_depths = np.linspace(0,H_total,100)
            Uz_vals, u_vals = [], []
            for z in plot_depths:
                z_d = z if not double else (z if z<=Hdr else 2*Hdr-z)
                Uz_vals.append(local_degree_consolidation(z_d, Hdr, Tv))
                u_vals.append(pore_pressure_ratio(z_d, Hdr, Tv))

            tab1_plot, tab2_plot, tab3_plot = st.tabs(["Uz vs Depth","ue/ui vs Depth","Average U% vs Time"])
            with tab1_plot:
                fig1, ax1 = plt.subplots()
                ax1.plot(Uz_vals, plot_depths, color='green')
                ax1.set_ylim(H_total,0)
                ax1.set_xlim(0,1.05)
                ax1.grid(True, linestyle='--', alpha=0.6)
                ax1.set_xlabel("Local Degree of Consolidation, Uz")
                ax1.set_ylabel("Depth (m)")
                st.pyplot(fig1)
                plt.close(fig1)
            with tab2_plot:
                fig2, ax2 = plt.subplots()
                ax2.plot(u_vals, plot_depths, color='blue')
                ax2.set_ylim(H_total,0)
                ax2.set_xlim(0,1.05)
                ax2.set_xlabel("Excess Pore Pressure ue/ui")
                ax2.set_ylabel("Depth (m)")
                ax2.grid(True, linestyle='--', alpha=0.6)
                st.pyplot(fig2)
                plt.close(fig2)
            with tab3_plot:
                t_max = max(time_val*2, 10)
                times = np.linspace(0.01,t_max,100)
                Uavg_vals = []
                for t in times:
                    Tv_t = Cv*t/(Hdr**2)
                    if Tv_t<=0.28:
                        U = 2*np.sqrt(Tv_t/np.pi)
                    else:
                        U = 1-10**(-(Tv_t+0.085)/0.933)
                    Uavg_vals.append(min(1.0,U)*100)
                fig3,ax3 = plt.subplots()
                ax3.plot(times,Uavg_vals,color='purple')
                ax3.scatter([time_val],[np.interp(time_val,times,Uavg_vals)],color='red',zorder=5)
                ax3.set_xlabel("Time (years)")
                ax3.set_ylabel("Average Consolidation U (%)")
                ax3.grid(True)
                st.pyplot(fig3)
                plt.close(fig3)
                # Current U_avg metric
                Tv_curr = Cv*time_val/(Hdr**2)
                U_curr = 2*np.sqrt(Tv_curr/np.pi) if Tv_curr<=0.28 else 1-10**(-(Tv_curr+0.085)/0.933)
                st.metric("Current Average Consolidation", f"{U_curr*100:.1f}%")
        else:
            st.warning("No clay layers defined. Define a clay layer for time rate analysis.")

if __name__=="__main__":
    app()
