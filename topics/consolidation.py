import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

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

    st.set_page_config(page_title="1D Consolidation", layout="wide")

    # ================================================================
    # TABS
    # ================================================================
    tab_settlement, tab_time = st.tabs(["Settlement Calculation", "Time Rate Analysis"])

    # ================================================================
    # GLOBAL INPUTS
    # ================================================================
    with tab_settlement:
        col_input, col_profile = st.columns([2, 1])

        with col_input:
            st.subheader("Global Inputs")
            water_depth = st.number_input("Water Table Depth [m]", 2.0)
            surcharge_q = st.number_input("Surface Surcharge Δσ [kPa]", 50.0)
            gamma_w = st.radio("γw [kN/m³]", [9.81, 10.0], horizontal=True)

            # ================================================================
            # SOIL LAYERS
            # ================================================================
            layers = []
            current_depth = 0.0

            st.subheader("Stratigraphy")
            n_layers = st.number_input("Number of Layers", 1, 50, 3)

            for i in range(int(n_layers)):

                with st.expander(f"Layer {i+1} Definition", expanded=True):

                    c1,c2,c3 = st.columns(3)

                    h = c1.number_input(f"Thickness [m]", 0.1, 100.0, 4.0, key=f"h{i}")
                    gamma = c2.number_input(f"Unit Weight (γ) [kN/m³]", 0.0, 30.0, 19.0, key=f"g{i}")
                    soil = c3.selectbox("Soil Type", ["Clay","Sand"], key=f"t{i}")

                    mid = current_depth + h/2

                    method="None"
                    params={}

                    if soil == "Clay":
                        st.markdown("---")
                        method = st.radio(
                            f"Settlement Method (Layer {i+1})",
                            ["Method A (Cc/Cr)","Method B (mv)","Method C (Δe)"],
                            key=f"m{i}",
                            horizontal=True
                        )

                        c_p1, c_p2, c_p3, c_p4 = st.columns(4)

                        if method == "Method A (Cc/Cr)":
                            e0 = c_p1.number_input("e0", 0.0, 5.0, 0.9, key=f"e{i}")
                            Cc = c_p2.number_input("Cc", 0.0, 5.0, 0.3, key=f"cc{i}")
                            Cr = c_p3.number_input("Cr", 0.0, 5.0, 0.05, key=f"cr{i}")
                            sp = c_p4.number_input("Precon. Pressure σ'p [kPa] (Optional)", 0.0, 1000.0, 0.0, key=f"sp{i}")
                            ocr = c_p4.number_input("OCR (Optional)", 1.0, 10.0, 1.0, key=f"ocr{i}")
   
                            params={"e0":e0,"Cc":Cc,"Cr":Cr,"sp":sp,"OCR":ocr}

                        if method == "Method B (mv)":
                            mv = c_p1.number_input("mv [1/kPa]", 0.0, 1.0, 0.0005, format="%.5f", key=f"mv{i}")
                            params={"mv":mv}

                        if method == "Method C (Δe)":
                            e0 = c_p1.number_input("Initial e0", 0.0, 5.0, 0.9, key=f"e0c{i}")
                            ef = c_p2.number_input("Final ef", 0.0, 5.0, 0.8, key=f"ef{i}")
                            params={"e0":e0,"ef":ef}

                    layers.append({
                        "id":i+1,
                        "type":soil,
                        "h":h,
                        "gamma":gamma,
                        "top":current_depth,
                        "bottom":current_depth+h,
                        "mid":mid,
                        "method":method,
                        "params":params
                    })

                    current_depth += h

        # ================================================================
        # DYNAMIC PROFILE DIAGRAM
        # ================================================================
        with col_profile:
            st.subheader("Soil Profile Preview")
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
        st.subheader("Calculation Results")
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
                details += f"**Given:** Thickness $H = {H}m$, Initial Void Ratio $e_0 = {p.get('e0', 'N/A')}$\n\n"
                details += f"**Stress Analysis:**\n"
                details += f"- Initial Effective Stress $\sigma'_0 = {sigma0:.2f} \ kPa$\n"
                details += f"- Stress Increment $\Delta\sigma = {surcharge_q:.2f} \ kPa$\n"
                details += f"- Final Effective Stress $\sigma'_f = \sigma'_0 + \Delta\sigma = {sigma_f:.2f} \ kPa$\n\n"

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
                    
                    details += f"**Consolidation State Analysis:**\n"
                    details += f"- Preconsolidation Pressure $\sigma'_p = {sp} \ kPa$\n"

                    # Case 1: Normally Consolidated
                    if sigma0 >= sp:
                        calc_type = "Normally Consolidated (NC)"
                        details += f"- Since $\sigma'_0 \ge \sigma'_p$ ({sigma0:.1f} $\ge$ {sp}), the soil is **Normally Consolidated**.\n"
                        details += f"- We use the Compression Index ($C_c$) for the full range.\n\n"
                        details += r"$$S = \frac{C_c \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_f}{\sigma'_0}\right)$$"
                        
                        S = (Cc * H / (1 + e0)) * np.log10(sigma_f / sigma0)
                        
                        details += f"\n\n**Substitution:**\n"
                        details += f"$$S = \\frac{{{Cc} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sigma_f:.1f}}}{{{sigma0:.1f}}}\\right)$$"
                        details += f"\n$$S = {S:.5f} m$$"

                    # Case 2: Over Consolidated (Remains OC)
                    elif sigma_f <= sp:
                        calc_type = "Over Consolidated (OC)"
                        details += f"- Since $\sigma'_f \le \sigma'_p$ ({sigma_f:.1f} $\le$ {sp}), the soil remains **Over Consolidated**.\n"
                        details += f"- We use the Recompression Index ($C_r$) only.\n\n"
                        details += r"$$S = \frac{C_r \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_f}{\sigma'_0}\right)$$"
                        
                        S = (Cr * H / (1 + e0)) * np.log10(sigma_f / sigma0)
                        
                        details += f"\n\n**Substitution:**\n"
                        details += f"$$S = \\frac{{{Cr} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sigma_f:.1f}}}{{{sigma0:.1f}}}\\right)$$"
                        details += f"\n$$S = {S:.5f} m$$"

                    # Case 3: Transition (OC -> NC)
                    else:
                        calc_type = "Transition (OC to NC)"
                        details += f"- Since $\sigma'_0 < \sigma'_p < \sigma'_f$ ({sigma0:.1f} < {sp} < {sigma_f:.1f}), the loading pushes the soil past the preconsolidation pressure.\n"
                        details += f"- **Part 1 (Recompression):** From $\sigma'_0$ to $\sigma'_p$ using $C_r$.\n"
                        details += f"- **Part 2 (Virgin Compression):** From $\sigma'_p$ to $\sigma'_f$ using $C_c$.\n\n"
                        
                        # Part 1
                        s1 = (Cr * H / (1 + e0)) * np.log10(sp / sigma0)
                        details += r"**Step 1:** $$S_1 = \frac{C_r \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_p}{\sigma'_0}\right)$$"
                        details += f"\n$$S_1 = \\frac{{{Cr} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sp}}}{{{sigma0:.1f}}}\\right) = {s1:.5f} m$$"

                        # Part 2
                        s2 = (Cc * H / (1 + e0)) * np.log10(sigma_f / sp)
                        details += r"**Step 2:** $$S_2 = \frac{C_c \cdot H}{1+e_0} \cdot \log_{10}\left(\frac{\sigma'_f}{\sigma'_p}\right)$$"
                        details += f"\n$$S_2 = \\frac{{{Cc} \cdot {H}}}{{1+{e0}}} \cdot \log_{{10}}\\left(\\frac{{{sigma_f:.1f}}}{{{sp}}}\\right) = {s2:.5f} m$$"

                        S = s1 + s2
                        details += f"\n\n**Total:** $$S = S_1 + S_2 = {s1:.5f} + {s2:.5f} = {S:.5f} m$$"

                # -------------------------------------------------------
                # METHOD B: mv
                # -------------------------------------------------------
                if L["method"] == "Method B (mv)":
                    mv = p["mv"]
                    calc_type = "Coefficient of Volume Compressibility ($m_v$)"
                    
                    details += f"**Formula:**\n"
                    details += r"$$S = m_v \cdot \Delta\sigma \cdot H$$"
                    
                    S = mv * surcharge_q * H
                    
                    details += f"\n\n**Substitution:**\n"
                    details += f"$$S = {mv:.5f} \\cdot {surcharge_q:.2f} \\cdot {H} = {S:.5f} m$$"

                # -------------------------------------------------------
                # METHOD C: Delta e
                # -------------------------------------------------------
                if L["method"] == "Method C (Δe)":
                    ef = p["ef"]
                    e0 = p["e0"]
                    calc_type = "Void Ratio Change ($\Delta e$)"
                    
                    details += f"**Formula:**\n"
                    details += r"$$S = \frac{e_0 - e_f}{1+e_0} \cdot H$$"
                    
                    S = ((e0 - ef) / (1 + e0)) * H
                    
                    details += f"\n\n**Substitution:**\n"
                    details += f"$$S = \\frac{{{e0} - {ef}}}{{1+{e0}}} \cdot {H} = {S:.5f} m$$"

                total_settlement += S
                results_data.append([f"Layer {L['id']}", f"{sigma0:.1f}", f"{sigma_f:.1f}", f"{S*1000:.2f}", calc_type])
                
                step_details.append(details)
                step_details.append("---")

            # OUTPUT DISPLAY
            st.markdown(f"## Total Settlement: :red[{total_settlement*1000:.2f} mm]")
            
            # Summary Table
            st.table([["Layer", "σ'₀ (kPa)", "σ'₁ (kPa)", "Settlement (mm)", "Method"]] + results_data)
            
            # Detailed Steps
            st.markdown("###  Detailed Calculation Log")
            for step in step_details:
                st.markdown(step)



    # ================================================================
    # TIME RATE ANALYSIS TAB
    # ================================================================
    with tab_time:
        st.subheader("Time Rate Analysis (Terzaghi Theory)")

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
            with tab2_plot:
                fig2, ax2 = plt.subplots()
                ax2.plot(u_vals, plot_depths, color='blue')
                ax2.set_ylim(H_total,0)
                ax2.set_xlim(0,1.05)
                ax2.set_xlabel("Excess Pore Pressure ue/ui")
                ax2.set_ylabel("Depth (m)")
                ax2.grid(True, linestyle='--', alpha=0.6)
                st.pyplot(fig2)
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
                # Current U_avg metric
                Tv_curr = Cv*time_val/(Hdr**2)
                U_curr = 2*np.sqrt(Tv_curr/np.pi) if Tv_curr<=0.28 else 1-10**(-(Tv_curr+0.085)/0.933)
                st.metric("Current Average Consolidation", f"{U_curr*100:.1f}%")
        else:
            st.warning("No clay layers defined. Define a clay layer for time rate analysis.")

if __name__=="__main__":
    app()
