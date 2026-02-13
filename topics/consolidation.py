import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def app():
    # ================================================================
    # CONFIG & SIDEBAR
    # ================================================================
    st.set_page_config(page_title="1D Consolidation Calculator", layout="wide")
    
    st.write("""
        **Assumptions:**
        - 1D Terzaghi Consolidation
        - Immediate Settlement ignored
        - Uniform surface surcharge
        - Stress evaluated at layer midpoint
        """)

    # ================================================================
    # HEADER
    # ================================================================
    st.title("1D Soil Consolidation Analyzer")
    
    calc_mode = st.radio(
        "**Calculation Goal:**",
        ["1. Final Ultimate Settlement ($S_{final}$)", "2. Time Rate of Consolidation ($t$ for $U_{avg}$)"],
        horizontal=True
    )

    st.markdown("---")

    # ================================================================
    # GLOBAL PARAMETERS
    # ================================================================
    col_g1, col_g2 = st.columns(3)

    with col_g1:
        water_depth = st.number_input("Water Table Depth [m]", value=2.0, step=0.5, 
                                    help="Depth from ground surface to Phreatic Surface")

    with col_g2:
        surcharge_q = st.number_input("Surface Surcharge Δσ [kPa]", value=50.0, step=10.0)
    with col_g3:
        # Moved from sidebar to here
        gamma_w = st.radio(
            "Unit Weight of Water ($γ_w$)",
            [9.81, 10.0],
            horizontal=True # Optional: makes it side-by-side
        )
    # ================================================================
    # INPUT SECTION
    # ================================================================
    col_input, col_viz = st.columns([1.5, 1])

    layers_data = []

    with col_input:
        st.subheader("Soil Stratigraphy")
        num_layers = st.number_input("Number of Layers", 1, 10, 3)

        current_depth = 0.0

        for i in range(int(num_layers)):
            with st.expander(f"Layer {i+1} (Top: {current_depth:.1f} m)", expanded=(i==0)):
                
                c1, c2, c3 = st.columns(3)
                thickness = c1.number_input(f"Thickness [m]", value=4.0, key=f"h_{i}", min_value=0.1)
                gamma = c2.number_input(f"γsat [kN/m³]", value=19.0, key=f"g_{i}")
                soil_type = c3.selectbox(f"Type", ["Clay", "Sand"], key=f"type_{i}")

                mid_depth = current_depth + thickness/2

                # --- Consolidation Parameters (Only for Clay) ---
                method = "None"
                params = {}

                if soil_type == "Clay":
                    st.caption("Consolidation Parameters")
                    method = st.radio(
                        f"Method (L{i+1})",
                        ["Method A: Cc/Cr (e-log p)", "Method B: mv (Linear)", "Method C: Δe (Direct)"],
                        key=f"m_{i}",
                        horizontal=True
                    )

                    if "Method A" in method:
                        rc1, rc2, rc3 = st.columns(3)
                        e0 = rc1.number_input("Initial e0", 0.85, key=f"e0_{i}")
                        Cc = rc2.number_input("Cc", 0.32, key=f"cc_{i}")
                        Cr = rc3.number_input("Cr", 0.05, key=f"cr_{i}")
                        sig_p = st.number_input("Preconsolidation σ'p [kPa]", 100.0, key=f"sp_{i}")
                        params = {"e0": e0, "Cc": Cc, "Cr": Cr, "sigma_p": sig_p}

                    elif "Method B" in method:
                        mv = st.number_input("Coefficient mv [1/kPa]", 0.0005, format="%.5f", key=f"mv_{i}")
                        params = {"mv": mv}

                    elif "Method C" in method:
                        rc1, rc2 = st.columns(2)
                        e0 = rc1.number_input("Initial e0", 0.9, key=f"e0c_{i}")
                        ef = rc2.number_input("Final ef", 0.82, key=f"efc_{i}")
                        params = {"e0": e0, "e_final": ef}

                layers_data.append({
                    "id": i+1,
                    "type": soil_type,
                    "thickness": thickness,
                    "gamma": gamma,
                    "top": current_depth,
                    "bottom": current_depth + thickness,
                    "mid": mid_depth,
                    "method": method,
                    "params": params
                })

                current_depth += thickness

    # ================================================================
    # VISUALIZATION (Fixed Memory Issue)
    # ================================================================
    with col_viz:
        st.subheader("Soil Profile")
        
        # Increased figure size for better readability
        fig, ax = plt.subplots(figsize=(6, 10))
        
        # Colors: Brownish for Clay, Yellowish for Sand
        colors = {"Clay": "#D7CCC8", "Sand": "#FFF9C4"}

        for l in layers_data:
            # Draw Layer Rectangle
            rect = patches.Rectangle((0, l["top"]), 5, l["thickness"],
                                     facecolor=colors[l["type"]],
                                     edgecolor="black", linewidth=1)
            ax.add_patch(rect)
            
            # Label Layer
            ax.text(2.5, l["mid"], f"L{l['id']}\n{l['type']}",
                    ha="center", va="center", fontsize=10, fontweight='bold', color="#3e2723")
            
            # Label Depth Lines
            ax.text(-0.2, l["bottom"], f"{l['bottom']:.1f} m", ha="right", fontsize=9)
            
        # Draw Water Table
        ax.axhline(water_depth, color="blue", linestyle="--", linewidth=2)
        ax.text(5.2, water_depth, f"WT\n({water_depth}m)", color="blue", va="center")

        # Plot settings
        ax.set_ylim(current_depth * 1.05, -1) # Invert Y axis
        ax.set_xlim(0, 5)
        ax.axis("off")
        ax.set_title(f"Total Depth: {current_depth:.1f} m")

        st.pyplot(fig)
        plt.close(fig) # CLEANUP: Close figure to prevent memory leak

    # ================================================================
    # CALCULATION ENGINE
    # ================================================================
    def calculate_layer(l, all_layers, w_depth, q, gw):
        """
        Calculates stress and settlement for a single layer.
        gw = unit weight of water (user selected)
        """
        
        # 1. TOTAL STRESS (σ_v)
        sigma_val = 0.0
        sigma_str = []

        # Stress from layers above
        for above in all_layers:
            if above["id"] < l["id"]:
                sigma_val += above["thickness"] * above["gamma"]
                sigma_str.append(f"{above['thickness']}×{above['gamma']}")

        # Stress to midpoint of current layer
        sigma_val += (l["thickness"]/2) * l["gamma"]
        sigma_str.append(f"{l['thickness']/2}×{l['gamma']}")
        
        sigma_expr = " + ".join(sigma_str)

        # 2. PORE PRESSURE (u)
        # Check if midpoint is below water table
        if l["mid"] > w_depth:
            u_val = (l["mid"] - w_depth) * gw
            u_str = f"({l['mid']:.2f} - {w_depth}) × {gw}"
        else:
            u_val = 0.0
            u_str = "0 (Above WT)"

        # 3. EFFECTIVE STRESSES
        sig_0 = sigma_val - u_val
        sig_f = sig_0 + q

        # Logging for "Show Calculations"
        log = []
        log.append("### Effective Stress Calculation")
        log.append(f"**σ_total** = {sigma_expr} = **{sigma_val:.2f} kPa**")
        log.append(f"**u** = {u_str} = **{u_val:.2f} kPa**")
        log.append(f"**σ'₀** = {sigma_val:.2f} - {u_val:.2f} = **{sig_0:.2f} kPa**")
        log.append(f"**σ'_final** = {sig_0:.2f} + {q} = **{sig_f:.2f} kPa**")

        # 4. SETTLEMENT CALCULATION
        settlement = 0.0
        status = "Skipped"

        if l["type"] == "Sand":
            log.append("Sand layer → Consolidation settlement assumed negligible.")
            return {"settlement": 0.0, "status": "Sand", "log": log}

        H = l["thickness"]
        
        # --- Method A: Cc/Cr ---
        if "Method A" in l["method"]:
            p = l["params"]
            log.append(f"### Settlement (Method A)")
            log.append(f"Compare σ'₀ ({sig_0:.2f}) with σ'p ({p['sigma_p']})")

            # Case 1: Normally Consolidated
            if sig_0 >= p["sigma_p"]:
                status = "Normally Consolidated (NC)"
                log.append(f"**State:** {status}")
                term = np.log10(sig_f/sig_0)
                settlement = (p["Cc"] * H / (1 + p["e0"])) * term
                log.append(f"S = [{p['Cc']}×{H} / (1+{p['e0']})] × log({sig_f:.2f}/{sig_0:.2f})")

            # Case 2: Over Consolidated (Recompression Only)
            elif sig_f <= p["sigma_p"]:
                status = "Over Consolidated (OC)"
                log.append(f"**State:** {status} (Recompression Only)")
                term = np.log10(sig_f/sig_0)
                settlement = (p["Cr"] * H / (1 + p["e0"])) * term
                log.append(f"S = [{p['Cr']}×{H} / (1+{p['e0']})] × log({sig_f:.2f}/{sig_0:.2f})")

            # Case 3: Mixed (Recompression + Virgin Compression)
            else:
                status = "OC to NC Transition"
                log.append(f"**State:** {status} (Crosses Preconsolidation Pressure)")
                
                # Part 1: Recompression up to sigma_p
                s1 = (p["Cr"] * H / (1 + p["e0"])) * np.log10(p["sigma_p"]/sig_0)
                # Part 2: Virgin compression beyond sigma_p
                s2 = (p["Cc"] * H / (1 + p["e0"])) * np.log10(sig_f/p["sigma_p"])
                
                settlement = s1 + s2
                log.append(f"S_recomp = {s1:.4f} m (using Cr up to {p['sigma_p']})")
                log.append(f"S_virgin = {s2:.4f} m (using Cc beyond {p['sigma_p']})")

        # --- Method B: mv ---
        elif "Method B" in l["method"]:
            status = "mv Method"
            log.append("### Settlement (Method B)")
            settlement = l["params"]["mv"] * q * H
            log.append(f"S = mv × Δσ × H = {l['params']['mv']} × {q} × {H}")

        # --- Method C: Delta e ---
        elif "Method C" in l["method"]:
            status = "Δe Method"
            p = l["params"]
            de = p["e0"] - p["e_final"]
            log.append("### Settlement (Method C)")
            settlement = (de/(1+p["e0"])) * H
            log.append(f"S = [({p['e0']} - {p['e_final']}) / (1 + {p['e0']})] × {H}")

        log.append(f"**Layer Settlement = {settlement:.5f} m**")

        return {
            "settlement": settlement,
            "status": status,
            "log": log
        }

    # ================================================================
    # RESULTS TAB
    # ================================================================
    
    # --- Mode 1: Final Settlement ---
    if "Final" in calc_mode:
        if st.button("Calculate Final Settlement", type="primary"):
            st.markdown("### Results")
            total = 0.0

            for l in layers_data:
                res = calculate_layer(l, layers_data, water_depth, surcharge_q, gamma_w)
                total += res["settlement"]
                
                # Display individual layer result
                if res["settlement"] > 0:
                    st.success(f"**Layer {l['id']} ({l['type']})** → {res['settlement']*1000:.2f} mm | {res['status']}")
                    with st.expander(f"View Calculations for Layer {l['id']}"):
                        for line in res["log"]:
                            st.write(line)
                else:
                    st.info(f"Layer {l['id']} ({l['type']}) → Negligible Settlement")

            st.markdown("---")
            st.metric("Total Settlement", f"{total*1000:.2f} mm", delta_color="inverse")

    # --- Mode 2: Time Rate ---
    else:
        st.subheader("Time Rate of Consolidation")
        
        clay_layers = [l for l in layers_data if l["type"] == "Clay"]

        if not clay_layers:
            st.warning("No Clay layers found. Time rate calculation is not applicable.")
        else:
            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                choice = st.selectbox("Select Critical Clay Layer", [f"Layer {l['id']}" for l in clay_layers])
                crit_layer = next(l for l in clay_layers if f"Layer {l['id']}" == choice)
                
                # --- AUTO-DRAINAGE DETECTION LOGIC ---
                idx = crit_layer['id'] - 1 # 0-based index
                is_top_drained = True # Assume surface is permeable
                is_bot_drained = False

                # Check layer above
                if idx > 0:
                    if layers_data[idx-1]['type'] == 'Sand': is_top_drained = True
                    else: is_top_drained = False
                
                # Check layer below
                if idx < len(layers_data) - 1:
                    if layers_data[idx+1]['type'] == 'Sand': is_bot_drained = True
                    else: is_bot_drained = False
                
                suggestion = "Double Drainage" if (is_top_drained and is_bot_drained) else "Single Drainage"
                suggested_hdr = crit_layer["thickness"]/2 if suggestion == "Double Drainage" else crit_layer["thickness"]

                st.info(f"**Drainage Suggestion:** {suggestion}\n\nBased on adjacent Sand layers.")

            with col_t2:
                cv = st.number_input("Coefficient of Consolidation $C_v$ [m²/year]", value=2.0)
                dr = st.number_input("Drainage Path $H_{dr}$ [m]", value=suggested_hdr, 
                                   help="Distance water must travel to exit. H/2 for Double, H for Single.")

            if st.button("Calculate Time", type="primary"):
                U_target = st.slider("Target Degree of Consolidation U (%)", 0, 99, 90) / 100.0

                # Time Factor Tv Calculation
                if U_target <= 0.6:
                    Tv = (np.pi/4) * (U_target**2)
                else:
                    Tv = -0.933 * np.log10(1 - U_target) - 0.085
                
                # t = Tv * d^2 / Cv
                t_req = (Tv * dr**2) / cv
                
                st.success(f"Time for **Layer {crit_layer['id']}** to reach **{U_target*100:.0f}%** Consolidation:")
                st.metric("Time Required", f"{t_req:.2f} years")
                st.write(f"*Calculated using $T_v = {Tv:.4f}$*")

if __name__ == "__main__":
    app()
