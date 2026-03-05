import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from types import SimpleNamespace
import pandas as pd
from theme import glass_table
from theme import write_text, glass_box
from .diagrams_dynamic.section_preview import draw_cross_section
from .diagrams_results.load_deformation_plot import plot_load_deformation
from .calculator.axial_calculator import compute_axial
import base64
from io import BytesIO
from .calculator.axial_design_helpers import required_Ast_for_load
from .reports.axial_report import build_step_by_step_markdown



def app():
    tab_cap, tab_As, tab_reinf, tab_conc = st.tabs([
    "Axial Capacity",
    "Required Steel (As)",
    "Required Reinforcement (Details)",
    "Required Concrete (Capacity Check)"
])
    with tab_cap:
        col_input, col_viz = st.columns([1.3, 1])
    
        # ================= INPUT =================
        with col_input:
            write_text("section_header", "1. System Properties")
            write_text("subheader", "Materials")
    
            c1, c2 = st.columns(2)
    
            with c1:
                fc = st.number_input("Concrete ($f_{ck}$) [MPa]", value=20.0)
    
            with c2:
                fy_long = st.number_input("Longitudinal Steel ($f_{yk}$) [MPa]", value=420.0)
    
            strength_basis = st.radio(
                "Strength Basis",
                ["Design Values (fcd, fyd)", "Characteristic Values (fck, fyk)"],
                horizontal=True
            )
            
            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:    
                shape = st.selectbox("Column Shape", ["Rectangular", "Circular"])
                
            with c4:
                confinement_options = {
                    "Spiral (Continuous Helix)": "Spiral / Circular",
                    "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                    "Plain Concrete (No Reinforcement)": "None (Plain Concrete)",
                }
    
                selected_label = st.selectbox("Confinement Type", list(confinement_options.keys()))
                reinf_style = confinement_options[selected_label]
    
            write_text("subheader", "Dimensions")
            c5, c6 = st.columns(2)
            Ast = 0.0
            num_bars = 0
            bar_dia = 0.0
    
            spiral_dia = 0.0
            spiral_spacing = 0.0
            core_diameter_input = 0.0
            fywk = 0.0
    
            with c5:
                if "Standard" in reinf_style:
                    cover = st.number_input("Cover [mm]", value=25.0)
                else:
                    cover = 0.0
                if shape == "Rectangular":
                    b = st.number_input("Width (b) (mm)", value=500.0)
                    h = st.number_input("Depth (h) (mm)", value=500.0)
                    Ag = b * h
                    dims = (b, h)
                else:
                    D = st.number_input("Diameter (D) (mm)", value=300.0)
                    Ag = np.pi * D**2 / 4
                    dims = (D,)
            with c6:
                if "None" not in reinf_style:
                    bar_dia = st.number_input("Bar Diameter (mm)", value=20.0)
                    num_bars = st.number_input("Number of Bars", value=8, min_value=4)
                    Ast = num_bars * np.pi * (bar_dia / 2) ** 2
        
                    if "Spiral" in reinf_style:
        
                        spiral_dia = st.number_input("Spiral Bar φ (mm)", value=10.0)
                        spiral_spacing = st.number_input("Spiral Spacing s (mm)", value=50.0)
                        fywk = st.number_input("Spiral Steel ($f_{ywk}$) [MPa]", value=220.0)
                        core_diameter_input = st.number_input(
                            "Core Diameter $D_k$ (mm)",
                            value=300.0,
                            help="Diameter of confined core measured to centerline of spiral."
                        )
                    
                    else:
                        fywk = 0.0
                        core_diameter_input = 0.0
    
        # ================= VISUAL =================
        with col_viz:
            write_text("section_header", "2. Visualization")
            fig1 = draw_cross_section(
            shape,
            dims,
            num_bars,
            bar_dia,
            reinf_style,
            True,          # ← FIXED
            cover,
            core_diameter_input,
        )
            st.pyplot(fig1, width="stretch", clear_figure=True)
            plt.close(fig1)
    
        st.markdown("---")
    
    # ================= CALC =================
        if st.button("Analyze Capacity", type="primary"):
    
            results = compute_axial(
                fc=fc,
                fy_long=fy_long,
                fywk=fywk,
                Ag=Ag,
                Ast=Ast,
                reinf_style=reinf_style,
                core_diameter_input=core_diameter_input,
                spiral_dia=spiral_dia,
                spiral_spacing=spiral_spacing,
                strength_basis=strength_basis
            )
    
            c7, c8 = st.columns(2)
            with c7:
                # 1. Result Summary in Glass Box (Using a Markdown Table String)
                write_text("section_header", "Design Summary")
        
                results_data = []
                results_data.append(["Unconfined Capacity (N_or)", f"{results.Nor1/1000:,.1f} kN"])
                
                if results.Nor2 is not None:
                    results_data.append(["Confined Capacity (N_or2)", f"{results.Nor2/1000:,.1f} kN"])
                    results_data.append(["Capacity Increase (Δ)", f"{(results.Nor2 - results.Nor1)/1000:,.1f} kN"])
                else:
                    results_data.append(["Confined Capacity (N_or2)", "N/A"])
                    results_data.append(["Capacity Increase (Δ)", "N/A"])
                
                df_summary = pd.DataFrame(results_data, columns=["Parameter", "Value"])
                glass_table(df_summary)
                
                st.markdown("<br>", unsafe_allow_html=True)
            with c8:
                # 2. Behavior Graph in Glass Box (Using Base64 HTML Image String)
                write_text("section_header", "Load-Deformation Behavior")
                
                graph_N1 = results.Nor1 / 1000
                graph_N2 = results.Nor2 / 1000 if results.Nor2 is not None else 0
                plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"
        
                fig = plot_load_deformation(graph_N1, graph_N2, plot_type)
                
                # Convert the plot to a base64 HTML string
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                plt.close(fig)
                
                graph_md = f'<img src="data:image/png;base64,{img_base64}" style="width:100%; max-width:700px; border-radius:8px;">'
                
                # Pass the HTML image string into your custom component
                glass_box(graph_md)
        
                st.markdown("<br>", unsafe_allow_html=True)
    
            # 3. Step-by-Step Calculation in Glass Box
            write_text("section_header", "Step-by-Step Calculation")
    
            step_md = build_step_by_step_markdown(
                results,
                fc,
                fy_long,
                Ag,
                Ast,
                reinf_style,
                core_diameter_input,
                strength_basis,
                fywk=fywk,
                spiral_dia=spiral_dia,
                spiral_spacing=spiral_spacing,
            )
            
            glass_box(step_md)
    with tab_As:
        write_text("section_header", "Required Steel (As) — Skeleton")
    
        st.info(
            "This tab will compute minimum As for a given axial load using the same strength basis.\n"
            "For now: it solves Nu = 0.85*f*Ag + As*f_y."
        )
    
        # --- Inputs for Tab 2 (separate) ---
        c1, c2 = st.columns(2)
        with c1:
            fc2 = st.number_input("Concrete (fck) [MPa]", value=20.0, key="as_fc")
            fy2 = st.number_input("Steel (fyk) [MPa]", value=420.0, key="as_fy")
            strength_basis2 = st.radio(
                "Strength Basis",
                ["Design Values (fcd, fyd)", "Characteristic Values (fck, fyk)"],
                horizontal=True,
                key="as_strength_basis",
            )
    
        with c2:
            Ag2 = st.number_input("Gross Area Ag [mm²]", value=250000.0, key="as_Ag")
            Nu_kN = st.number_input("Applied axial load Nu [kN]", value=2000.0, key="as_Nu")
            alpha_cc = st.number_input("αcc", value=0.85, key="as_alpha")
    
        if st.button("Compute As", type="primary", key="as_compute"):
            # Convert load
            Nu_N = Nu_kN * 1000.0  # kN -> N
    
            # Choose strengths based on radio
            if strength_basis2 == "Design Values (fcd, fyd)":
                gamma_c = 1.5
                gamma_s = 1.15
                f_used = fc2 / gamma_c
                fy_used = fy2 / gamma_s
            else:
                f_used = fc2
                fy_used = fy2
    
            # Concrete contribution (course assumption: Ag)
            Fc = alpha_cc * f_used * Ag2  # MPa * mm² = N
    
            # Required As
            if fy_used <= 0:
                Ast_req = 0.0
            else:
                Ast_req = max(0.0, (Nu_N - Fc) / fy_used)  # mm²
    
            # Show results
            rows = [
                ["Nu", f"{Nu_kN:,.1f} kN"],
                ["Concrete force Fc", f"{Fc/1000:,.1f} kN"],
                ["Steel strength used", f"{fy_used:,.1f} MPa"],
                ["Required As", f"{Ast_req:,.0f} mm²"],
            ]
            glass_table(pd.DataFrame(rows, columns=["Item", "Value"]))
    
            # Simple check: if Nu <= Fc then As is zero (concrete alone)
            if Nu_N <= Fc:
                glass_box("✅ Concrete alone can carry Nu (As required = 0 by this simplified equation).")
            else:
                glass_box("✅ As computed from Nu = Fc + As·fy.")
        # =========================================================
    # TAB 3: REQUIRED REINFORCEMENT (DETAILS) — INPUTS ONLY
    # =========================================================
    with tab_reinf:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("section_header", "1. Inputs (Reinforcement Details)")

            write_text("subheader", "Applied Load")
            cL1, cL2 = st.columns(2)
            with cL1:
                Nu_kN_r = st.number_input("Applied axial load Nu [kN]", value=2000.0, key="reinf_Nu")
            with cL2:
                strength_basis_r = st.radio(
                    "Strength Basis",
                    ["Design Values (fcd, fyd)", "Characteristic Values (fck, fyk)"],
                    horizontal=True,
                    key="reinf_strength_basis",
                )

            write_text("subheader", "Materials")
            cM1, cM2 = st.columns(2)
            with cM1:
                fc_r = st.number_input("Concrete (fck) [MPa]", value=20.0, key="reinf_fc")
                fy_long_r = st.number_input("Longitudinal Steel (fyk) [MPa]", value=420.0, key="reinf_fy_long")
            with cM2:
                fywk_r = st.number_input("Transverse/Spiral Steel (fywk) [MPa]", value=220.0, key="reinf_fywk")
                cover_r = st.number_input("Cover [mm]", value=25.0, key="reinf_cover")

            write_text("subheader", "Geometry & Confinement Type")
            cG1, cG2 = st.columns(2)
            with cG1:
                shape_r = st.selectbox("Column Shape", ["Rectangular", "Circular"], key="reinf_shape")
            with cG2:
                confinement_options = {
                    "Spiral (Continuous Helix)": "Spiral / Circular",
                    "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                }
                selected_label_r = st.selectbox(
                    "Confinement Type",
                    list(confinement_options.keys()),
                    key="reinf_confinement_label"
                )
                reinf_style_r = confinement_options[selected_label_r]

            write_text("subheader", "Dimensions")
            cD1, cD2 = st.columns(2)
            with cD1:
                if shape_r == "Rectangular":
                    b_r = st.number_input("Width (b) [mm]", value=500.0, key="reinf_b")
                    h_r = st.number_input("Depth (h) [mm]", value=500.0, key="reinf_h")
                else:
                    D_r = st.number_input("Diameter (D) [mm]", value=300.0, key="reinf_D")

            with cD2:
                # Longitudinal
                bar_dia_r = st.number_input("Longitudinal Bar Diameter (mm)", value=20.0, key="reinf_bar_dia")
                num_bars_r = st.number_input("Number of Longitudinal Bars", value=8, min_value=4, key="reinf_num_bars")

            write_text("subheader", "Transverse Reinforcement Inputs")
            cT1, cT2 = st.columns(2)
            with cT1:
                if "Spiral" in reinf_style_r:
                    spiral_dia_r = st.number_input("Spiral Bar φ (mm)", value=10.0, key="reinf_spiral_dia")
                    spiral_spacing_r = st.number_input("Spiral Spacing s (mm)", value=50.0, key="reinf_spiral_s")
                else:
                    tie_dia_r = st.number_input("Tie Bar φ (mm)", value=10.0, key="reinf_tie_dia")
                    tie_spacing_r = st.number_input("Tie Spacing s (mm)", value=150.0, key="reinf_tie_s")

            with cT2:
                core_diameter_r = st.number_input(
                    "Core Diameter Dk (mm)",
                    value=300.0,
                    help="Confined core measured to centerline of spiral/ties.",
                    key="reinf_core_d"
                )
                st.number_input(
                    "Target confinement peak check (placeholder)",
                    value=1.0,
                    help="Later we’ll enforce: if Spiral, 2nd peak > 1st (your requirement).",
                    key="reinf_peak_placeholder"
                )

        # --- Visualization placeholder (keep empty space like Tab 1) ---
        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (section sketch / confinement layout).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — calculations will be connected later.")


    # =========================================================
    # TAB 4: REQUIRED CONCRETE — INPUTS ONLY
    # =========================================================
    with tab_conc:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("section_header", "1. Inputs (Required Concrete Check)")

            write_text("subheader", "Applied Load")
            c1, c2 = st.columns(2)
            with c1:
                Nu_kN_c = st.number_input("Applied axial load Nu [kN]", value=2000.0, key="conc_Nu")
            with c2:
                strength_basis_c = st.radio(
                    "Strength Basis",
                    ["Design Values (fcd, fyd)", "Characteristic Values (fck, fyk)"],
                    horizontal=True,
                    key="conc_strength_basis",
                )

            write_text("subheader", "Provided Reinforcement (Given)")
            c3, c4 = st.columns(2)
            with c3:
                Ast_prov = st.number_input("Provided As [mm²]", value=2500.0, key="conc_Ast")
                fy_c = st.number_input("Steel (fyk) [MPa]", value=420.0, key="conc_fy")
            with c4:
                shape_c = st.selectbox("Column Shape", ["Rectangular", "Circular"], key="conc_shape")
                cover_c = st.number_input("Cover [mm]", value=25.0, key="conc_cover")

            write_text("subheader", "Concrete / Section Size (Unknown later — for now input)")
            c5, c6 = st.columns(2)
            with c5:
                fc_c = st.number_input("Concrete (fck) [MPa]", value=20.0, key="conc_fc")
            with c6:
                if shape_c == "Rectangular":
                    b_c = st.number_input("Width (b) [mm]", value=500.0, key="conc_b")
                    h_c = st.number_input("Depth (h) [mm]", value=500.0, key="conc_h")
                else:
                    D_c = st.number_input("Diameter (D) [mm]", value=300.0, key="conc_D")

        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (required size / capacity preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required concrete size/strength to resist Nu.")

if __name__ == "__main__":
    app()
