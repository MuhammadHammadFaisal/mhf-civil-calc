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
from .ui.axial_inputs import (
    input_strength_basis,
    input_materials_basic,
    input_geometry_config,
    input_section_dimensions,
    input_longitudinal_steel,
    input_spiral_details,
)

def app():
    tab_cap, tab_As, tab_reinf, tab_conc = st.tabs([
        "Axial Capacity",
        "Required Reinforcement Steel (As)",
        "Required Confinement Steel (Details)",
        "Required Concrete (Capacity Check)"
    ])

    # =========================================================
    # TAB 1: AXIAL CAPACITY
    # =========================================================
    with tab_cap:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("subheader", "Materials")
            fc, fy_long = input_materials_basic("cap", steel_label="Longitudinal Steel ($f_{yk}$) [MPa]")
            strength_basis = input_strength_basis("cap")
            
            write_text("subheader", "Geometry & Configuration")
            shape, reinf_style = input_geometry_config("cap", allow_plain=True)
            
            write_text("subheader", "Dimensions")
            dims, Ag = input_section_dimensions("cap", shape)
            
            write_text("subheader", "Steel")
            bar_dia, num_bars, Ast = input_longitudinal_steel("cap", reinf_style)
            
            write_text("subheader", "Spiral (if selected)")
            spiral_dia, spiral_spacing, fywk, core_diameter_input = input_spiral_details("cap", shape, reinf_style)
            
        with col_viz:
            write_text("section_header", "2. Visualization")
            fig1 = draw_cross_section(
                shape,
                dims,
                num_bars,
                bar_dia,
                reinf_style,
                True,
                core_diameter_input,
            )
            st.pyplot(fig1, width="stretch", clear_figure=True)
            plt.close(fig1)

        st.markdown("---")

        if st.button("Analyze Capacity", type="primary", key="cap_btn"):
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

            c_res1, c_res2 = st.columns(2)

            with c_res1:
                write_text("section_header", "Design Summary")
                results_data = [
                    ["Unconfined Capacity (N_or)", f"{results.Nor1 / 1000:,.1f} kN"]
                ]

                if results.Nor2 is not None:
                    results_data.append(["Confined Capacity (N_or2)", f"{results.Nor2 / 1000:,.1f} kN"])
                    results_data.append(["Capacity Increase (Δ)", f"{(results.Nor2 - results.Nor1) / 1000:,.1f} kN"])
                else:
                    results_data.append(["Confined Capacity (N_or2)", "N/A"])
                    results_data.append(["Capacity Increase (Δ)", "N/A"])

                df_summary = pd.DataFrame(results_data, columns=["Parameter", "Value"])
                glass_table(df_summary)
                st.markdown("<br>", unsafe_allow_html=True)

            with c_res2:
                write_text("section_header", "Load-Deformation Behavior")

                graph_N1 = results.Nor1 / 1000
                graph_N2 = results.Nor2 / 1000 if results.Nor2 is not None else 0
                plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"

                fig = plot_load_deformation(graph_N1, graph_N2, plot_type)
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                plt.close(fig)

                graph_md = f'<img src="data:image/png;base64,{img_base64}" style="width:100%; max-width:700px; border-radius:8px;">'
                glass_box(graph_md)
                st.markdown("<br>", unsafe_allow_html=True)

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

    # =========================================================
    # TAB 2: REQUIRED LONGITUDINAL STEEL (As)
    # =========================================================
    with tab_As:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("section_header", "1. Inputs (Required Longitudinal Steel As)")

            write_text("subheader", "Applied Load")
            cL1, cL2 = st.columns(2)
            with cL1:
                Nu_kN_req = st.number_input(
                    "Applied axial load Nu [kN]",
                    value=2000.0,
                    key="as_Nu"
                )
            with cL2:
                strength_basis_as = st.radio(
                    "Strength Basis",
                    ["Design Values (fcd, fyd)", "Characteristic Values (fck, fyk)"],
                    horizontal=True,
                    key="as_strength_basis",
                )

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape_as = st.selectbox(
                    "Column Shape",
                    ["Rectangular", "Circular"],
                    key="as_shape"
                )
            with c4:
                confinement_options_as = {
                    "Spiral (Continuous Helix)": "Spiral / Circular",
                    "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                }
                selected_label_as = st.selectbox(
                    "Confinement Type",
                    list(confinement_options_as.keys()),
                    key="as_conf_label"
                )
                reinf_style_as = confinement_options_as[selected_label_as]

            write_text("subheader", "Materials")
            cM1, cM2 = st.columns(2)
            with cM1:
                fc_as = st.number_input("Concrete (fck) [MPa]", value=20.0, key="as_fc")
            with cM2:
                fy_as = st.number_input("Steel (fyk) [MPa]", value=420.0, key="as_fy")
                fywk_as = 0.0
                if "Spiral" in reinf_style_as:
                    fywk_as = st.number_input(
                        "Spiral Steel ($f_{ywk}$) [MPa]",
                        value=220.0,
                        key="as_fywk"
                    )

            write_text("subheader", "Dimensions")
            cG1, cG2 = st.columns(2)
            Dk_as = 0.0

            with cG1:
                if shape_as == "Rectangular":
                    b_as = st.number_input("Width (b) [mm]", value=500.0, key="as_b")
                else:
                    D_as = st.number_input("Diameter (D) [mm]", value=300.0, key="as_D")

            with cG2:
                if shape_as == "Rectangular":
                    h_as = st.number_input("Depth (h) [mm]", value=500.0, key="as_h")
                elif "Spiral" in reinf_style_as:
                    Dk_as = st.number_input(
                        "Core Diameter $D_k$ [mm]",
                        value=250.0,
                        help="Confined core diameter measured to tie/spiral centerline.",
                        key="as_Dk"
                    )

            if "Spiral" in reinf_style_as:
                write_text("subheader", "Spiral Geometry")
                cS1, cS2 = st.columns(2)
                with cS1:
                    tie_bar_dia_as = st.number_input("Spiral bar diameter [mm]", value=10.0, key="as_tie_dia")
                with cS2:
                    spiral_spacing_as = st.number_input("Spiral spacing s [mm]", value=50.0, key="as_spiral_s")

        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (interaction diagram / section preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required As for given Nu.")

    # =========================================================
    # TAB 3: REQUIRED TRANSVERSE REINFORCEMENT (TIES)
    # =========================================================
    with tab_reinf:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("section_header", "1. Inputs (Transverse Reinforcement - Ties)")

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

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape_r = st.selectbox(
                    "Column Shape",
                    ["Rectangular", "Circular"],
                    key="reinf_shape"
                )
            with c4:
                st.selectbox(
                    "Confinement Type",
                    ["Tied (Standard Hoops)"],
                    index=0,
                    key="reinf_conf_label"
                )

            write_text("subheader", "Materials")
            cM1, cM2 = st.columns(2)
            with cM1:
                fc_r = st.number_input("Concrete (fck) [MPa]", value=20.0, key="reinf_fc")
            with cM2:
                fywk_r = st.number_input("Tie Steel ($f_{ywk}$) [MPa]", value=220.0, key="reinf_fywk")

            write_text("subheader", "Section Dimensions (Gross)")
            cG1, cG2 = st.columns(2)
            with cG1:
                if shape_r == "Rectangular":
                    b_r = st.number_input("Width (b) [mm]", value=500.0, key="reinf_b")
                else:
                    D_r = st.number_input("Diameter (D) [mm]", value=300.0, key="reinf_D")
            with cG2:
                if shape_r == "Rectangular":
                    h_r = st.number_input("Depth (h) [mm]", value=500.0, key="reinf_h")

            write_text("subheader", "Cover & Tie Geometry (for Confined Core)")
            cC1, cC2 = st.columns(2)
            with cC1:
                cover_r = st.number_input("Clear cover to ties [mm]", value=25.0, key="reinf_cover")
            with cC2:
                tie_bar_dia_r = st.number_input("Tie bar diameter [mm]", value=10.0, key="reinf_tie_dia")

            write_text("subheader", "Longitudinal Reinforcement (Given)")
            cR1, cR2 = st.columns(2)
            with cR1:
                fy_long_r = st.number_input("Longitudinal Steel (fyk) [MPa]", value=420.0, key="reinf_fy_long")
                bar_dia_r = st.number_input("Longitudinal Bar Diameter [mm]", value=20.0, key="reinf_bar_dia")
            with cR2:
                num_bars_r = st.number_input("Number of Longitudinal Bars", value=8, min_value=4, key="reinf_num_bars")
                Ast_r = st.number_input(
                    "Provided longitudinal steel As [mm²] (optional)",
                    value=0.0,
                    help="Optional. Later this can be computed automatically from bar diameter and count.",
                    key="reinf_Ast_opt"
                )

        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (confined core / tie layout preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required tie area (Ash) and spacing (s).")

    # =========================================================
    # TAB 4: REQUIRED CONCRETE
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

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape_c = st.selectbox(
                    "Column Shape",
                    ["Rectangular", "Circular"],
                    key="conc_shape"
                )
            with c4:
                confinement_options_c = {
                    "Spiral (Continuous Helix)": "Spiral / Circular",
                    "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                }
                selected_label_c = st.selectbox(
                    "Confinement Type",
                    list(confinement_options_c.keys()),
                    key="conc_conf_label"
                )
                reinf_style_c = confinement_options_c[selected_label_c]

            write_text("subheader", "Materials & Provided Reinforcement (Given)")
            c5, c6 = st.columns(2)
            with c5:
                fc_c = st.number_input("Concrete (fck) [MPa]", value=20.0, key="conc_fc")
                Ast_prov = st.number_input("Provided As [mm²]", value=2500.0, key="conc_Ast")
            with c6:
                fy_c = st.number_input("Steel (fyk) [MPa]", value=420.0, key="conc_fy")
                cover_c = st.number_input("Cover [mm]", value=25.0, key="conc_cover")
                fywk_c = 0.0
                if "Spiral" in reinf_style_c:
                    fywk_c = st.number_input("Spiral Steel ($f_{ywk}$) [MPa]", value=220.0, key="conc_fywk")

            write_text("subheader", "Dimensions / Size (Trial for now)")
            c7, c8 = st.columns(2)
            with c7:
                if shape_c == "Rectangular":
                    b_c = st.number_input("Width (b) [mm]", value=500.0, key="conc_b")
                else:
                    D_c = st.number_input("Diameter (D) [mm]", value=300.0, key="conc_D")
            with c8:
                if shape_c == "Rectangular":
                    h_c = st.number_input("Depth (h) [mm]", value=500.0, key="conc_h")

        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (required size / capacity preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required concrete size/strength to resist Nu.")


if __name__ == "__main__":
    app()
