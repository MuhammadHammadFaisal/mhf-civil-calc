import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from types import SimpleNamespace

from theme import write_text, glass_box
from .diagrams_dynamic.section_preview import draw_cross_section
from .diagrams_results.load_deformation_plot import plot_load_deformation
from .calculator.axial_calculator import compute_axial


from .reports.axial_report import build_step_by_step_markdown



def app():
    write_text("page_title", "RC Column Analyst")

    col_input, col_viz = st.columns([1.3, 1])

    # ================= INPUT =================
    with col_input:
        write_text("section_header", "1. System Properties")

        st.markdown("**Materials**")
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

        with st.expander("Geometry & Configuration", expanded=True):
            shape = st.selectbox("Column Shape", ["Rectangular", "Circular"])

            confinement_options = {
                "Spiral (Continuous Helix)": "Spiral / Circular",
                "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                "Plain Concrete (No Reinforcement)": "None (Plain Concrete)",
            }

            selected_label = st.selectbox("Confinement Type", list(confinement_options.keys()))
            reinf_style = confinement_options[selected_label]

        st.markdown("**Dimensions**")
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

        Ast = 0.0
        num_bars = 0
        bar_dia = 0.0

        spiral_dia = 0.0
        spiral_spacing = 0.0
        core_diameter_input = 0.0
        fywk = 0.0

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
        st.pyplot(fig1, width="stretch")

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

        write_text("section_header", "Result Summary")

        s1, s2, s3 = st.columns(3)

        s1.metric("Unconfined $N_{or}$", f"{results.Nor1/1000:,.0f} kN")

        if results.Nor2 is not None:
            s2.metric("Confined $N_{or2}$", f"{results.Nor2/1000:,.0f} kN")
            delta = (results.Nor2 - results.Nor1) / 1000
            s3.metric("Δ (Nor2 - Nor)", f"{delta:,.0f} kN")
        else:
            s2.metric("Confined $N_{or2}$", "—")
            s3.metric("Δ (Nor2 - Nor)", "—")

        st.markdown("---")

        write_text("section_header", "Behavior Graph")

        graph_N1 = results.Nor1 / 1000
        graph_N2 = results.Nor2 / 1000 if results.Nor2 is not None else 0

        plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"

        fig = plot_load_deformation(graph_N1, graph_N2, plot_type)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("---")

        write_text("section_header", "Step-by-Step Calculation")

        step_md = build_step_by_step_markdown(
            results,
            fc,
            fy_long,
            Ag,
            Ast,
            reinf_style,
            core_diameter_input,
        )
        
        glass_box(step_md)

if __name__ == "__main__":
    app()
