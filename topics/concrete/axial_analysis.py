import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- SAFE IMPORT FOR CURVE SMOOTHING ---
try:
    from scipy.interpolate import PchipInterpolator
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# ======================================
# 1. HELPER: DRAWING FUNCTIONS
# ======================================
def distribute_bars_rectangular(b, h, cover, num_bars):
    eff_cover = cover 
    xL, xR = eff_cover, b - eff_cover
    yB, yT = eff_cover, h - eff_cover
    
    positions = [(xL, yB), (xR, yB), (xR, yT), (xL, yT)]
    remaining = num_bars - 4
    if remaining <= 0: return positions[:num_bars] 

    if h >= b:
        faces = [("left", xL, yB, yT), ("right", xR, yB, yT), ("bottom", yB, xL, xR), ("top", yT, xL, xR)]
    else:
        faces = [("bottom", yB, xL, xR), ("top", yT, xL, xR), ("left", xL, yB, yT), ("right", xR, yB, yT)]

    face_counts = [0] * 4
    for i in range(remaining): face_counts[i % 4] += 1

    for i, count in enumerate(face_counts):
        if count == 0: continue
        face_name, fixed, start, end = faces[i]
        spacing = (end - start) / (count + 1)
        internal_points = [start + spacing * (j+1) for j in range(count)]
        for p in internal_points:
            if face_name in ["left", "right"]: positions.append((fixed, p)) 
            else: positions.append((p, fixed))
    return positions

def draw_cross_section(shape, dims, num_bars, bar_dia, reinf_style, show_ties, cover):
    # --- PROFESSIONAL SETUP ---
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    bar_r = bar_dia / 2
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # --- 1. DRAW CONCRETE ---
    if shape in ["Rectangular", "Square"]:
        b, h = dims
        ax.add_patch(patches.Rectangle((0, 0), b, h, fill=True, 
                                     facecolor='#e0e0e0', edgecolor='black', linewidth=2))
        ax.set_xlim(-50, b + 50); ax.set_ylim(-50, h + 50)
        cx, cy = b / 2, h / 2
        min_dim = min(b, h)
    else:
        D = dims[0]
        cx, cy = D / 2, D / 2
        ax.add_patch(patches.Circle((cx, cy), D/2, fill=True, 
                                  facecolor='#e0e0e0', edgecolor='black', linewidth=2))
        ax.set_xlim(-50, D + 50); ax.set_ylim(-50, D + 50)
        min_dim = D

    # --- 2. CHECK: SHOULD WE DRAW TIES? ---
    # The fix: If "Longitudinal" or "None" is in the name, turn off ties.
    draw_ties_logic = False
    if show_ties:
        if "Standard" in reinf_style or "Spiral" in reinf_style:
            draw_ties_logic = True

    # --- 3. STOP IF PLAIN CONCRETE ---
    if "None" in reinf_style:
        ax.set_aspect("equal"); ax.axis("off")
        return fig

    # --- 4. CALCULATE POSITIONS ---
    positions = []
    
    # CASE A: Circular / Spiral Logic
    if "Spiral" in reinf_style or shape == "Circular":
        # Calculate Cage Diameter
        if shape == "Circular":
            cage_D = dims[0] - 2*cover
        else:
            cage_D = min_dim - 2*cover
            
        r_bars = cage_D / 2 - bar_r
        angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False)
        if shape != "Circular": angles += np.pi / 4 
        positions = [(cx + r_bars * np.cos(a), cy + r_bars * np.sin(a)) for a in angles]

        # Draw Spiral/Hoop (Only if allowed)
        if draw_ties_logic:
            linestyle = '-' if "Spiral" in reinf_style else '--'
            r_tie = cage_D / 2
            ax.add_patch(patches.Circle((cx, cy), r_tie, fill=False, 
                                      edgecolor='#555', linewidth=1.5, linestyle=linestyle))

    # CASE B: Rectangular Logic
    else: 
        positions = distribute_bars_rectangular(dims[0], dims[1], cover + bar_r, num_bars)
        
        # Draw Rectangular Tie (Only if allowed)
        if draw_ties_logic:
            tie_inset = cover
            w_tie = dims[0] - 2*tie_inset
            h_tie = dims[1] - 2*tie_inset
            ax.add_patch(patches.Rectangle((tie_inset, tie_inset), w_tie, h_tie, 
                                         fill=False, edgecolor='#555', linewidth=1.5, linestyle='--'))

    # --- 5. DRAW BARS ---
    for x, y in positions: 
        ax.add_patch(patches.Circle((x, y), bar_r, color='#d32f2f', zorder=10))

    ax.set_aspect("equal"); ax.axis("off")
    return fig
# ======================================
# 2. PLOT: LOAD vs DEFORMATION
# ======================================
def plot_load_deformation(N1, N2, trans_type):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    
    # --- STYLING FOR DARK MODE ---
    text_color = "white"
    ax.spines['bottom'].set_color(text_color)
    ax.spines['left'].set_color(text_color)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)
    ax.yaxis.label.set_color(text_color)
    ax.xaxis.label.set_color(text_color)

    if trans_type == "Spiral":
        if N2 > N1:
            x = np.array([0, 1.0, 2.0, 3.5, 5.5, 6.5]) 
            y = np.array([0, N1,  0.85*N1, N2, N2, N2*0.9]) 
            color = "#00BFFF" 
            ax.annotate('First Peak\n(Shell Spalls)', xy=(1.0, N1), xytext=(0.5, N1+N1*0.1),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
            ax.annotate('Second Peak\n(Confined Core)', xy=(3.5, N2), xytext=(3.5, N2+N2*0.1),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
            ax.annotate('Ductile Plateau', xy=(5.5, N2), xytext=(5.5, N2-N2*0.15),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
            ax.axhline(y=N1, color='gray', linestyle='--', alpha=0.5)
        else:
            x = np.array([0, 1.0, 2.0, 3.5, 5.0])
            y = np.array([0, N1,  0.80*N1, N2, N2*0.8]) 
            color = "#FF4B4B" 
            ax.annotate('First Peak\n(Governs)', xy=(1.0, N1), xytext=(1.5, N1+N1*0.15),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), color=text_color)
            ax.annotate('Spiral too weak', xy=(3.5, N2), xytext=(3.5, N2+N2*0.15),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
    else: 
        x = np.array([0, 1.0, 2.5, 4.0])
        y = np.array([0, N1, 0.5*N1, 0.3*N1])
        color = "#FFA500" 
        ax.annotate('Failure ($N_{max}$)', xy=(1.0, N1), xytext=(1.5, N1),
                    arrowprops=dict(facecolor=text_color, arrowstyle='->'), color=text_color)

    if HAS_SCIPY:
        try:
            interpolator = PchipInterpolator(x, y)
            x_smooth = np.linspace(x.min(), x.max(), 300)
            y_smooth = interpolator(x_smooth)
            ax.plot(x_smooth, y_smooth, color=color, linewidth=3)
        except:
            ax.plot(x, y, color=color, linewidth=3)
    else:
        ax.plot(x, y, color=color, linewidth=3, linestyle='-')
    
    ax.set_xlabel(r"Axial Shortening ($\delta$)", fontsize=11)
    ax.set_ylabel("Axial Load (N)", fontsize=11)
    ax.set_ylim(bottom=0, top=max(N1, N2)*1.3)
    ax.set_xlim(left=0)
    return fig

# ======================================
# 3. MAIN APP (FIXED & POLISHED)
# ======================================
def app():
    st.title("RC Column Analyst")

    # Layout: Input Column (Left) | Viz Column (Right)
    col_input, col_viz = st.columns([1.3, 1])

    with col_input:
        st.subheader("1. System Properties")
        
        # --- A. DESIGN CODE (Hidden/Hardcoded) ---
        design_code = "TS 500 (Lecture Notes)" 
        # st.caption("Standard: **TS 500**") 

        # --- B. MATERIALS (RESTORED!) ---
        # These were missing in your snippet!
        st.markdown("**Materials**")
        c1, c2 = st.columns(2)
        with c1: fc = st.number_input("Concrete ($f_{ck}$) [MPa]", value=20.0, step=5.0)
        with c2: fy = st.number_input("Steel ($f_{yk}$) [MPa]", value=420.0, step=10.0)

        # --- C. GEOMETRY & REINFORCEMENT ---
        # --- GEOMETRY & REINFORCEMENT ---
        with st.expander("Geometry & Configuration", expanded=True):
            shape = st.selectbox("Column Shape", ["Rectangular", "Square", "Circular"])
            
            # 1. DEFINE THE MAPPING (User Friendly Name -> Code Logic Name)
            # This allows us to show clear names without breaking the drawing function
            confinement_options = {
                "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                "Spiral (Continuous Helix)": "Spiral / Circular",
                "Unconfined (Longitudinal Bars Only)": "Longitudinal Only (No Ties)",
                "Plain Concrete (No Reinforcement)": "None (Plain Concrete)"
            }
            
            # 2. SHOW THE USER FRIENDLY NAMES
            selected_label = st.selectbox(
                "Confinement Type", 
                list(confinement_options.keys())
            )
            
            # 3. CONVERT BACK TO LOGIC FOR CODE
            reinf_style = confinement_options[selected_label]

        # --- D. DIMENSIONS ---
        st.markdown("**Dimensions**")
        cover = st.number_input("Cover [mm]", value=25.0)
        
        Ag = 0; dims = (0,0)
        
        if shape == "Rectangular":
            cc1, cc2 = st.columns(2)
            with cc1: b = st.number_input("Width (b)", value=300.0)
            with cc2: h = st.number_input("Depth (h)", value=400.0)
            Ag = b*h; dims = (b, h)
        elif shape == "Square":
            a = st.number_input("Side (a)", value=350.0)
            Ag = a**2; dims = (a, a)
        else:
            D = st.number_input("Diameter (D)", value=300.0)
            Ag = np.pi * D**2 / 4; dims = (D,)

        # --- E. REINFORCEMENT DETAILS ---
       # --- REINFORCEMENT INPUTS (NO ASSUMPTIONS) ---
        Ast = 0; num_bars = 0; bar_dia = 0
        spiral_dia = 0; spiral_spacing = 0; core_diameter_input = 0 # Initialize

        if "None" not in reinf_style:
            st.markdown("##### Longitudinal Reinforcement")
            rc1, rc2 = st.columns(2)
            with rc1: bar_dia = st.number_input("Bar Diameter ($d_b$)", value=16.0)
            with rc2: num_bars = st.number_input("Number of Bars", value=8, min_value=4)
            Ast = num_bars * np.pi * (bar_dia / 2) ** 2
            
            # --- CONFINEMENT (SPIRAL) ---
            if "Spiral" in reinf_style:
                st.markdown("##### Spiral Confinement Settings")
                st.info("🌀 Hybrid/Spiral Mode Active")
                
                sc1, sc2, sc3 = st.columns(3)
                with sc1: 
                    spiral_dia = st.number_input("Spiral Bar $\phi$", value=10.0)
                with sc2: 
                    spiral_spacing = st.number_input("Spiral Spacing $s$", value=50.0)
                with sc3:
                    # NO ASSUMPTIONS: User must define the core size
                    # Default is suggested (Width - 2*Cover), but user can change it
                    default_core = 0.0
                    if shape == "Circular": default_core = dims[0] - 2*cover
                    else: default_core = min(dims[0], dims[1]) - 2*cover
                    
                    core_diameter_input = st.number_input(
                        "Core Diam ($D_{k}$)", 
                        value=default_core,
                        help="Outer diameter of the spiral ring. Usually Column Width - 2*Cover."
                    )

        # Map to calculation variable safely
        trans_type = "Ties"
        if "Spiral" in reinf_style: trans_type = "Spiral"
    # --- VISUALIZATION COLUMN ---
    with col_viz:
        st.subheader("2. Visualization")
        # Ensure we pass the variables correctly
        fig1 = draw_cross_section(shape, dims, num_bars, bar_dia, reinf_style, True, cover)
        st.pyplot(fig1, use_container_width=True)
        st.caption(f"**Section Data:** $A_g = {Ag:,.0f}$ mm², $\\rho = {(Ast/Ag)*100:.2f}\\%$")

    st.markdown("---")

# ======================================
    # 3. CALCULATION REPORT (STUDENT MODE)
    # ======================================
    if st.button("Analyze Capacity", type="primary"):
        st.markdown("---")
        st.subheader("📝 Step-by-Step Calculation Report")

        # --- STEP 0: CONSTANTS & MATERIALS ---
        st.markdown("#### 0. Design Parameters")
        c1, c2, c3 = st.columns(3)
        
        # Design Strengths
        if "TS 500" in design_code:
            gamma_c, gamma_s = 1.5, 1.15
            fcd = fc / gamma_c
            fyd = fy / gamma_s
            c1.metric("Concrete Design ($f_{cd}$)", f"{fcd:.2f} MPa", help=f"{fc} / 1.5")
            c2.metric("Steel Design ($f_{yd}$)", f"{fyd:.2f} MPa", help=f"{fy} / 1.15")
        
        # Geometry Properties
        st.write("**Geometric Properties:**")
        st.latex(fr"A_g = {Ag:,.0f} \text{{ mm}}^2")
        st.latex(fr"A_{{st}} = {num_bars} \times \frac{{\pi \cdot {bar_dia}^2}}{{4}} = {Ast:,.0f} \text{{ mm}}^2")

        # --- STEP 1: DETAILING CHECKS (CRITICAL FOR STUDENTS) ---
        st.markdown("#### 1. Detailing Checks (Sanity Check)")
        rho_percent = (Ast / Ag) * 100
        
        # Check against TS 500 Limits (1% to 4%)
        chk_col1, chk_col2 = st.columns(2)
        chk_col1.write(f"Reinforcement Ratio ($\\rho_l$): **{rho_percent:.2f}%**")
        
        if 1.0 <= rho_percent <= 4.0:
            chk_col2.success("✅ OK (1% $\le \rho \le$ 4%)")
        elif rho_percent < 1.0:
            chk_col2.warning("⚠️ Low Reinforcement! (Code Min = 1%)")
        else:
            chk_col2.error("❌ Too High! (Code Max = 4%)")

        # --- STEP 2: UNCONFINED CAPACITY ---
        st.markdown("#### 2. Unconfined Axial Capacity ($N_{or}$)")
        st.info("This is the capacity when the concrete shell is still intact.")

        # Breakdown Forces
        Force_conc = 0.85 * fcd * (Ag - Ast)
        Force_steel = Ast * fyd
        Nor1 = Force_conc + Force_steel

        # Display as "Force Components"
        f1, f2 = st.columns(2)
        f1.metric("Concrete Contribution", f"{Force_conc/1000:,.0f} kN", help="0.85 * fcd * (Ag - Ast)")
        f2.metric("Steel Contribution", f"{Force_steel/1000:,.0f} kN", help="Ast * fyd")
        
        st.markdown("**Total Unconfined Capacity:**")
        st.latex(r"N_{or} = F_{conc} + F_{steel}")
        st.latex(fr"N_{{or}} = {Force_conc/1000:.0f} + {Force_steel/1000:.0f} = \mathbf{{{Nor1/1000:.0f} \text{{ kN}}}}")

        graph_N1 = Nor1 / 1000
        graph_N2 = 0

        # --- STEP 3: CONFINED CAPACITY (IF SPIRAL) ---
        if "Spiral" in reinf_style:
            st.markdown("#### 3. Confined Core Capacity ($N_{or2}$)")
            st.info("This calculates if the spiral can hold the core together after the shell spalls off.")
            
            # A. GEOMETRY OF CORE
            d_outer = core_diameter_input 
            d_center = d_outer - spiral_dia
            Ack = np.pi * d_outer**2 / 4
            Asp = np.pi * spiral_dia**2 / 4

            col_geom1, col_geom2 = st.columns(2)
            col_geom1.write(f"Core Diameter ($D_k$): **{d_outer:.0f} mm**")
            col_geom2.write(f"Core Area ($A_{{ck}}$): **{Ack:,.0f} mm²**")

            # B. VOLUMETRIC RATIO
            st.markdown("**B. Confinement Ratio ($\rho_s$)**")
            if spiral_spacing > 0:
                rho_s = (4 * Asp) / (d_center * spiral_spacing)
                st.latex(fr"\rho_s = \frac{{4 A_{{sp}}}}{{D_{{core}} s}} = \frac{{4 ({Asp:.1f})}}{{{d_center:.0f} \cdot {spiral_spacing:.0f}}} = \mathbf{{{rho_s:.4f}}}")
            else:
                rho_s = 0; st.error("Spacing cannot be zero.")

            # Check Min Rho_s
            rho_min_calc = 0.45 * (fc/fy) * ((Ag/Ack)-1)
            rho_min_abs = 0.12 * (fc/fy)
            rho_min_req = max(rho_min_calc, rho_min_abs)
            
            if rho_s >= rho_min_req:
                st.success(f"✅ Confinement Sufficient ($\rho_s > {rho_min_req:.4f}$)")
                
                # C. ENHANCED STRENGTH
                st.markdown("**C. Enhanced Concrete Strength ($f_{ccd}$)**")
                # Calculate the boost
                confinement_stress = (2 * rho_s * fy) / 1.5 
                f_ccd = (0.85 * fc / 1.5) + confinement_stress
                
                st.write("The spiral acts like a belt, increasing the concrete's strength:")
                st.latex(fr"f_{{ccd}} = f_{{cd}} + \text{{Confinement Boost}}")
                st.latex(fr"f_{{ccd}} = {fcd:.2f} + \frac{{2 \cdot {rho_s:.4f} \cdot {fy}}}{{1.5}} = \mathbf{{{f_ccd:.2f} \text{{ MPa}}}}")

                # D. FINAL CAPACITY
                term_core = f_ccd * Ack
                term_steel_2 = Ast * fyd
                Nor2 = term_core + term_steel_2

                st.markdown("**D. Final Confined Capacity**")
                st.latex(fr"N_{{or2}} = (f_{{ccd}} \cdot A_{{ck}}) + (A_{{st}} \cdot f_{{yd}})")
                st.latex(fr"N_{{or2}} = ({f_ccd:.2f} \cdot {Ack:.0f}) + {term_steel_2:.0f} = \mathbf{{{Nor2/1000:.0f} \text{{ kN}}}}")
                
                graph_N2 = Nor2 / 1000
                delta = graph_N2 - graph_N1
                
                if delta > 0:
                    st.success(f"🎉 **Ductile Design Achieved!** The column gets stronger after spalling (+{delta:.0f} kN).")
                else:
                    st.warning(f"⚠️ **Brittle Behavior.** The confined core is weaker than the original section (-{abs(delta):.0f} kN).")
            else:
                st.error(f"❌ **Spiral Too Weak.** $\rho_s$ ({rho_s:.4f}) is less than required ({rho_min_req:.4f}). Calculation stops.")
                graph_N2 = 0

        # --- STEP 4: VISUALIZATION ---
        st.markdown("#### 4. Behavior Graph")
        plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"
        fig = plot_load_deformation(graph_N1, graph_N2, plot_type)
        st.pyplot(fig)
        plt.close(fig)

if __name__ == "__main__":
    app()
