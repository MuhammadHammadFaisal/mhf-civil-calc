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
    input_strength_basis,input_nu_requirment,
    input_materials_concrete, input_materials_steel_fyk, input_materials_steel_fywk,
    input_column_geometry,
    input_confinement_type_capacity, input_confinement_type_ast, input_confinement_type_ao, input_confinement_type_ac, input_confinement_type_ack,
    input_section_dimensions,
    input_bar_diameter,
    input_num_bars,
    calc_Ast,
    input_spiral_bar_dia, input_spiral_spacing, input_core_diameter)

def app():
    tab_cap, tab_As, tab_Ao, tab_Ac, tab_Ack = st.tabs([
        "Axial Capacity",
        "Required Reinforcement Steel (As)",
        "Required Confinement Steel (Details)",
        "Required Concrete (Capacity Check)",
        "Required Core (Ack)"
    ])

    # =========================================================
    # TAB 1: AXIAL CAPACITY
    # =========================================================
    with tab_cap:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("subheader", "Materials")
            c1, c2 = st.columns(2)
            with c1:
                fc = input_materials_concrete("cap")
            with c2:
                fy_long = input_materials_steel_fyk("cap")
            strength_basis = input_strength_basis("cap")

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape = input_column_geometry("cap")
            with c4:
                reinf_style = input_confinement_type_capacity("cap")

            write_text("subheader", "Dimensions")
            dims, Ag = input_section_dimensions("cap", shape)

            write_text("subheader", "Steel")
            bar_dia = 0.0
            num_bars = 0
            Ast = 0.0
            if "Plain Concrete" not in reinf_style:
                c1, c2 = st.columns(2)
                with c1:
                    bar_dia = input_bar_diameter("cap")
                with c2:
                    num_bars = input_num_bars("cap")
                Ast = calc_Ast(num_bars, bar_dia)
            spiral_dia = 0.0
            spiral_spacing = 0.0
            fywk = 0.0
            core_diameter_input = 0.0
            if "Spiral" in reinf_style:
                write_text("subheader", "Spiral (if selected)")
                c1, c2 = st.columns(2)
                with c1:
                    spiral_dia = input_spiral_bar_dia("cap")
                    fywk = input_materials_steel_fywk("cap")  # fywk input
                with c2:
                    spiral_spacing = input_spiral_spacing("cap")
                    core_diameter_input = input_core_diameter("cap")
            
        with col_viz:
            write_text("section_header", "2. Visualization")
            fig1 = draw_cross_section(
            shape,
            dims,
            num_bars,
            bar_dia,
            reinf_style,
            True,
            0.0,                 # cover_unused dummy
            core_diameter_input  # Ack/Dk
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
            write_text("subheader", "Materials")
            c1, c2 = st.columns(2)
            with c1:
                fc = input_materials_concrete("as")
                fy_long = input_materials_steel_fyk("as")
            with c2:
                strength_basis = input_strength_basis("as")
                Nu_kN_req = input_nu_requirment("as")

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape = input_column_geometry("as")
            with c4:
                reinf_style = input_confinement_type_ast("as")

            write_text("subheader", "Dimensions")
            dims, Ag = input_section_dimensions("as", shape)
            spiral_dia = 0.0
            spiral_spacing = 0.0
            fywk = 0.0
            core_diameter_input = 0.0

            if "Spiral" in reinf_style:
           
            
                c3, c4 = st.columns(2)
                with c3:
                    spiral_dia = input_spiral_bar_dia("as")
                    fywk = input_materials_steel_fywk("as")  # fywk input
                with c4:
                    spiral_spacing = input_spiral_spacing("as")
                    core_diameter_input = input_core_diameter("as")
        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (interaction diagram / section preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required As for given Nu.")

    # =========================================================
    # TAB 3: REQUIRED TRANSVERSE REINFORCEMENT (TIES)
    # =========================================================
    with tab_Ao:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("subheader", "Materials")
            c1, c2 = st.columns(2)
            with c1:
                fc = input_materials_concrete("reinf")
                fy_long = input_materials_steel_fyk("reinf")
            with c2:
                strength_basis = input_strength_basis("reinf")
                Nu_kN_req = input_nu_requirment("reinf")

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape = input_column_geometry("reinf")
            with c4:
                reinf_style = input_confinement_type_ao("reinf")

            write_text("subheader", "Dimensions")
            dims, Ag = input_section_dimensions("reinf", shape)

            spiral_dia = 0.0
            spiral_spacing = 0.0
            fywk = 0.0
            core_diameter_input = 0.0

            if "Spiral" in reinf_style:
            
            
                c3, c4 = st.columns(2)
                with c3:
                    spiral_dia = input_spiral_bar_dia("reinf")
                    fywk = input_materials_steel_fywk("reinf")  # fywk input
                with c4:
                    spiral_spacing = input_spiral_spacing("reinf")
                    core_diameter_input = input_core_diameter("reinf")
        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (confined core / tie layout preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required tie area (Ash) and spacing (s).")

    # =========================================================
    # TAB 4: REQUIRED CONCRETE
    # =========================================================
    with tab_Ac:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("subheader", "Materials")
            c1, c2 = st.columns(2)
            with c1:
                fc = input_materials_concrete("ac")
                fy_long = input_materials_steel_fyk("ac")
            with c2:
                strength_basis = input_strength_basis("ac")
                Nu_kN_req = input_nu_requirment("ac")

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape = input_column_geometry("ac")
            with c4:
                reinf_style = input_confinement_type_ac("ac")

            write_text("subheader", "Dimensions")
            dims, Ag = input_section_dimensions("ac", shape)

            write_text("subheader", "Steel")
            bar_dia = 0.0
            num_bars = 0
            Ast = 0.0
            if "Plain Concrete" not in reinf_style:
                c1, c2 = st.columns(2)
                with c1:
                    bar_dia = input_bar_diameter("ac")
                with c2:
                    num_bars = input_num_bars("ac")
                Ast = calc_Ast(num_bars, bar_dia)
            spiral_dia = 0.0
            spiral_spacing = 0.0
            fywk = 0.0
            core_diameter_input = 0.0
            if "Spiral" in reinf_style:
                write_text("subheader", "Spiral")

            
                c3, c4 = st.columns(2)
                with c3:
                    spiral_dia = input_spiral_bar_dia("ac")
                    fywk = input_materials_steel_fywk("ac")  # fywk input
                with c4:
                    spiral_spacing = input_spiral_spacing("ac")

                    core_diameter_input = input_core_diameter("ac")
        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (required size / capacity preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required concrete size/strength to resist Nu.")
    # =========================================================
    # TAB 5: REQUIRED Confinment CONCRETE
    # =========================================================
    with tab_Ack:
        col_input, col_viz = st.columns([1.3, 1])

        with col_input:
            write_text("subheader", "Materials")
            c1, c2 = st.columns(2)
            with c1:
                fc = input_materials_concrete("ack")
                fy_long = input_materials_steel_fyk("ack")
            with c2:
                strength_basis = input_strength_basis("ack")
                Nu_kN_req = input_nu_requirment("ack")

            write_text("subheader", "Geometry & Configuration")
            c3, c4 = st.columns(2)
            with c3:
                shape = input_column_geometry("ack")
            with c4:
                reinf_style = input_confinement_type_ack("ack")

            write_text("subheader", "Dimensions")
            dims, Ag = input_section_dimensions("ack", shape)
            spiral_dia = 0.0
            spiral_spacing = 0.0
            fywk = 0.0
            core_diameter_input = 0.0

            if "Spiral" in reinf_style:
                write_text("subheader", "Spiral")

            
                c3, c4 = st.columns(2)
                with c3:
                    spiral_dia = input_spiral_bar_dia("ack")
                    fywk = input_materials_steel_fywk("ack")  # fywk input
                with c4:
                    spiral_spacing = input_spiral_spacing("ack")
                    core_diameter_input = input_core_diameter("ack")
        with col_viz:
            write_text("section_header", "2. Visualization")
            glass_box("Visualization will be added here (required size / capacity preview).")

        st.markdown("---")
        glass_box("✅ Inputs only for now — next step: compute required concrete size/strength to resist Nu.")

if __name__ == "__main__":
    app()
