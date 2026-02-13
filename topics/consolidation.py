import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ================================================================
# FOURIER SOLUTION FUNCTIONS
# ================================================================

def local_degree_consolidation(z, Hdr, Tv, terms=100):
    """
    Calculates local degree of consolidation Uz at depth z (from drainage face).
    z should be between 0 and Hdr.
    """
    summation = 0
    for n in range(terms):
        m = 2*n + 1
        M = m * np.pi / 2
        # Sin argument: (m * pi * z) / (2 * Hdr)
        term = (2/m) * np.sin(M * z / Hdr) * np.exp(-(m**2)*(np.pi**2)*Tv/4)
        summation += term
    
    # Avoid small numerical noise giving values slightly > 1 or < 0
    ue_ratio = summation
    return max(0.0, min(1.0, 1 - ue_ratio))


def pore_pressure_ratio(z, Hdr, Tv, terms=100):
    """
    Calculates excess pore pressure ratio (ue/ui) at depth z.
    """
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

    st.set_page_config(page_title="Advanced 1D Consolidation", layout="wide")

    st.title("Advanced 1D Terzaghi Consolidation Analyzer")

    st.info("""
    **Reference Guidelines (Based on Course Notes):**
    1. **Unit Weights:** If a layer straddles the Water Table, split it into two layers (one above, one below) to use the correct unit weights (Dry/Bulk vs Saturated).
    2. **Time Factors:** Uses the piecewise equations from Source 60 ($2\sqrt{T_v/\pi}$ and standard log approximation).
    """)

    # ================================================================
    # GLOBAL INPUT
    # ================================================================
    col_g1, col_g2, col_g3 = st.columns(3)

    with col_g1:
        water_depth = st.number_input("Water Table Depth [m]", 2.0)

    with col_g2:
        surcharge_q = st.number_input("Surface Surcharge Δσ [kPa]", 50.0)

    with col_g3:
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
                    params={"e0":e0,"Cc":Cc,"Cr":Cr,"sp":sp}

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
    # STRESS FUNCTION
    # ================================================================
    def effective_stress(z):
        sigma = 0
        
        # Accumulate total stress
        for L in layers:
            if z > L["bottom"]:
                sigma += L["h"] * L["gamma"]
            elif L["top"] < z <= L["bottom"]:
                sigma += (z - L["top"]) * L["gamma"]
                break # Reached the depth z
        
        # Calculate pore pressure
        if z > water_depth:
            u = (z - water_depth) * gamma_w
        else:
            u = 0

        return max(0.001, sigma - u) # Prevent log(0) or negative stress

    # ================================================================
    # PROFILE PLOT (Visual Feedback)
    # ================================================================
    col_res1, col_res2 = st.columns([1, 2])

    with col_res1:
        st.subheader("Soil Profile")
        fig,ax = plt.subplots(figsize=(4,6))
        colors={"Clay":"#D7CCC8","Sand":"#FFF9C4"}
        
        for L in layers:
            rect = patches.Rectangle((0, L["top"]), 4, L["h"],
                                     facecolor=colors[L["type"]],
                                     edgecolor="black")
            ax.add_patch(rect)
            ax.text(2, L["mid"], f"L{L['id']}\n{L['type']}", ha='center', va='center')

        ax.axhline(water_depth, color="blue", linestyle="--", linewidth=2, label="Water Table")
        ax.set_ylim(current_depth*1.05, -1) # Invert y axis
        ax.set_xlim(0, 4)
        ax.legend(loc='upper right')
        ax.axis("off")
        st.pyplot(fig)
        plt.close(fig)

    # ================================================================
    # FINAL SETTLEMENT CALCULATION
    # ================================================================
    with col_res2:
        st.subheader("Calculation Results")
        
        if st.button("Calculate Final Settlement", type="primary"):
            st.markdown("#### Final Consolidation Settlement (S_c)")
            total=0
            
            results_data = []

            for L in layers:
                if L["type"]=="Sand":
                    continue

                sig0 = effective_stress(L["mid"])
                sigf = sig0 + surcharge_q
                H = L["h"]
                S = 0

                if L["method"] == "Method A (Cc/Cr)":
                    p = L["params"]
                    # Logic per Source 33, 80
                    if sig0 >= p["sp"]:
                        # Normally Consolidated Case
                        S = (p["Cc"] * H / (1 + p["e0"])) * np.log10(sigf / sig0)
                    elif sigf <= p["sp"]:
                        # Over Consolidated (Remaining OC)
                        S = (p["Cr"] * H / (1 + p["e0"])) * np.log10(sigf / sig0)
                    else:
                        # Over Consolidated (Becoming NC)
                        s1 = (p["Cr"] * H / (1 + p["e0"])) * np.log10(p["sp"] / sig0)
                        s2 = (p["Cc"] * H / (1 + p["e0"])) * np.log10(sigf / p["sp"])
                        S = s1 + s2

                if L["method"] == "Method B (mv)":
                    # Source 24
                    S = L["params"]["mv"] * surcharge_q * H

                if L["method"] == "Method C (Δe)":
                    # Source 6
                    p = L["params"]
                    S = ((p["e0"] - p["ef"]) / (1 + p["e0"])) * H

                total += S
                results_data.append([f"Layer {L['id']}", f"{sig0:.1f}", f"{sigf:.1f}", f"{S*1000:.2f}"])

            # Display Results Table
            st.table([["Layer", "σ'₀ (kPa)", "σ'₁ (kPa)", "Settlement (mm)"]] + results_data)
            st.success(f"**Total Consolidation Settlement = {total*1000:.2f} mm**")

    # ================================================================
    # TIME RATE + LOCAL CONSOLIDATION
    # ================================================================
    st.markdown("---")
    st.header("Time Rate Analysis (Terzaghi Theory)")

    clay_layers = [L for L in layers if L["type"] == "Clay"]

    if clay_layers:
        c_t1, c_t2, c_t3 = st.columns(3)
        
        with c_t1:
            choice = st.selectbox("Select Critical Clay Layer for Analysis", 
                                  [f"Layer {L['id']}" for L in clay_layers])
            crit = next(L for L in clay_layers if f"Layer {L['id']}" == choice)

        with c_t2:
            Cv = st.number_input("Coefficient of Consolidation Cv (m²/year)", 2.0)
            double = st.checkbox("Double Drainage?", value=True)

        # Determine Drainage Height
        H_total = crit["h"]
        Hdr = H_total / 2 if double else H_total

        with c_t3:
            time_val = st.slider("Time elapsed (years)", 0.1, 50.0, 1.0)
            Tv = Cv * time_val / (Hdr**2)
            st.metric("Time Factor (Tv)", f"{Tv:.3f}")

        # ================================================================
        # PROFILE GENERATION
        # ================================================================
        
        # We plot the FULL layer depth (0 to H_total)
        # If Double Drainage: Hdr = H/2. 
        #   Top half (0 to Hdr): z_drain = z
        #   Bottom half (Hdr to H_total): z_drain = 2*Hdr - z (Symmetry)
        
        plot_depths = np.linspace(0, H_total, 100)
        Uz_vals = []
        u_vals = []

        for z in plot_depths:
            if double:
                # Map actual depth to drainage distance (symmetry)
                if z <= Hdr:
                    z_drain = z
                else:
                    z_drain = 2*Hdr - z
            else:
                z_drain = z
                
            Uz_vals.append(local_degree_consolidation(z_drain, Hdr, Tv))
            u_vals.append(pore_pressure_ratio(z_drain, Hdr, Tv))

        # ================================================================
        # PLOTS
        # ================================================================
        tab1, tab2, tab3 = st.tabs(["Degree of Consolidation (Uz)", "Excess Pore Pressure (ue/ui)", "Average U% vs Time"])

        with tab1:
            fig1, ax1 = plt.subplots()
            ax1.plot(Uz_vals, plot_depths, color='green', linewidth=2)
            ax1.set_ylim(H_total, 0)
            ax1.set_xlim(0, 1.05)
            ax1.grid(True, which='both', linestyle='--', alpha=0.6)
            ax1.set_xlabel("Local Degree of Consolidation, Uz")
            ax1.set_ylabel("Depth within Layer (m)")
            ax1.set_title(f"Isochrone at t = {time_val} years")
            if double:
                ax1.axhline(H_total/2, color='red', linestyle=':', label='Centerline')
                ax1.legend()
            st.pyplot(fig1)

        with tab2:
            fig2, ax2 = plt.subplots()
            ax2.plot(u_vals, plot_depths, color='blue', linewidth=2)
            ax2.set_ylim(H_total, 0)
            ax2.set_xlim(0, 1.05)
            ax2.grid(True, which='both', linestyle='--', alpha=0.6)
            ax2.set_xlabel("Excess Pore Pressure Ratio (ue / ui)")
            ax2.set_ylabel("Depth within Layer (m)")
            ax2.set_title(f"Isochrone at t = {time_val} years")
            st.pyplot(fig2)

        with tab3:
            # ================================================================
            # U_avg CALCULATION (Exact Formula from Source 60)
            # ================================================================
            t_max = time_val * 2 if time_val > 5 else 10.0
            times = np.linspace(0.01, t_max, 100)
            Uavg_vals = []

            for t in times:
                Tv_t = Cv * t / (Hdr**2)
                
                # Source 60 Equations
                if Tv_t <= 0.28:  # Changed threshold slightly to match standard intersection
                    U = 2 * np.sqrt(Tv_t / np.pi)
                else:
                    exponent = -(Tv_t + 0.085) / 0.933
                    U = 1 - 10**(exponent)
                
                Uavg_vals.append(min(1.0, U) * 100) # Convert to %

            fig3, ax3 = plt.subplots()
            ax3.plot(times, Uavg_vals, color='purple')
            ax3.scatter([time_val], [np.interp(time_val, times, Uavg_vals)], color='red', zorder=5)
            ax3.set_xlabel("Time (years)")
            ax3.set_ylabel("Average Consolidation U (%)")
            ax3.set_title("Rate of Settlement")
            ax3.grid(True)
            st.pyplot(fig3)
            
            # Current U_avg
            Tv_curr = Cv * time_val / (Hdr**2)
            if Tv_curr <= 0.28:
                U_curr = 2 * np.sqrt(Tv_curr / np.pi)
            else:
                U_curr = 1 - 10**(-(Tv_curr + 0.085) / 0.933)
            st.metric("Current Average Consolidation", f"{U_curr*100:.1f}%")

    else:
        st.warning("No Clay layers defined. Define a Clay layer to perform Time Rate analysis.")

if __name__=="__main__":
    app()
