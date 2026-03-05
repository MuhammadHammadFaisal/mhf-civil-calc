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

from .reports.axial_report import build_step_by_step_markdown



def app():
    tab1, tab2 = st.tabs(["Axial Capacity", "Required Steel (As)"])
    with tab1:
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
    with tab2:
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
        

if __name__ == "__main__":
    app()
