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
        col_input, col_profile = st.columns([1, 1])

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
            n_layers = st.number_input("Number of Layers", 1, 10, 3)

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
                            sp = c_p4.number_input("Precon. Pressure σ'p [kPa]", 0.0, 1000.0, 100.0, key=f"sp{i}")
                            ocr = c_p4.number_input("OCR", 1.0, 10.0, 1.0, key=f"ocr{i}")
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
        # STEP-BY-STEP SETTLEMENT CALCULATION
        # ================================================================
        st.subheader("Calculation Results")
        if st.button("Calculate Settlement", type="primary"):

            calculation_steps = []
            total_settlement = 0
            results_data = []

            for L in layers:
                if L["type"]=="Sand":
                    continue
                sigma0 = effective_stress(L["mid"])
                sigma_f = sigma0 + surcharge_q
                H = L["h"]
                S = 0

                p = L["params"]

                # Method A
                if L["method"]=="Method A (Cc/Cr)":
                    if sigma0 >= p["sp"]:
                        S = (p["Cc"]*H/(1+p["e0"]))*np.log10(sigma_f/sigma0)
                        calc_type = "Normally Consolidated"
                    elif sigma_f <= p["sp"]:
                        S = (p["Cr"]*H/(1+p["e0"]))*np.log10(sigma_f/sigma0)
                        calc_type = "Over Consolidated"
                    else:
                        s1 = (p["Cr"]*H/(1+p["e0"]))*np.log10(p["sp"]/sigma0)
                        s2 = (p["Cc"]*H/(1+p["e0"]))*np.log10(sigma_f/p["sp"])
                        S = s1 + s2
                        calc_type = "OC to NC Transition"

                # Method B
                if L["method"]=="Method B (mv)":
                    S = p["mv"] * surcharge_q * H
                    calc_type = "mv Method"

                # Method C
                if L["method"]=="Method C (Δe)":
                    S = ((p["e0"]-p["ef"])/ (1+p["e0"])) * H
                    calc_type = "Δe Method"

                total_settlement += S
                results_data.append([f"Layer {L['id']}", f"{sigma0:.1f}", f"{sigma_f:.1f}", f"{S*1000:.2f}", calc_type])

                # Add step explanation
                calculation_steps.append(f"""
**Layer {L['id']} ({calc_type}):**
- Initial effective stress σ'₀ = {sigma0:.2f} kPa  
- Final effective stress σ'₁ = {sigma_f:.2f} kPa  
- Settlement S = {S:.4f} m ({S*1000:.2f} mm)
""")

            st.table([["Layer","σ'₀","σ'₁","Settlement (mm)","Method"]]+results_data)
            st.markdown("---")
            st.markdown("### Step-by-Step Calculation")
            for step in calculation_steps:
                st.markdown(step)

            st.success(f"**Total Settlement = {total_settlement*1000:.2f} mm**")


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
