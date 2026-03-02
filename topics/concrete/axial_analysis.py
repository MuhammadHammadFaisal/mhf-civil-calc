import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from theme import write_text, glass_box, glass_table
from .diagrams_dynamic.section_preview import draw_cross_section
from .diagrams_results.load_deformation_plot import plot_load_deformation
from .calculator.axial_calculator import compute_axial

def app():
    write_text("page_title", "RC Column Analyst")

    col_input, col_viz = st.columns([1.3, 1])

    with col_input:
        write_text("section_header", "1. System Properties")

        design_code = "TS 500 (Lecture Notes)"

        st.markdown("**Materials**")
        c1, c2 = st.columns(2)
        with c1:
            fc = st.number_input("Concrete ($f_{ck}$) [MPa]", value=20.0, step=5.0)
        with c2:
            fy = st.number_input("Steel ($f_{yk}$) [MPa]", value=420.0, step=10.0)

        with st.expander("Geometry & Configuration", expanded=True):
            shape = st.selectbox("Column Shape", ["Rectangular", "Square", "Circular"])
            confinement_options = {
                "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                "Spiral (Continuous Helix)": "Spiral / Circular",
                "Unconfined (Longitudinal Bars Only)": "Longitudinal Only (No Ties)",
                "Plain Concrete (No Reinforcement)": "None (Plain Concrete)",
            }
            selected_label = st.selectbox("Confinement Type", list(confinement_options.keys()))
            reinf_style = confinement_options[selected_label]

        st.markdown("**Dimensions**")
        cover = st.number_input("Cover [mm]", value=25.0)

        Ag = 0
        dims = (0, 0)

        if shape == "Rectangular":
            cc1, cc2 = st.columns(2)
            with cc1:
                b = st.number_input("Width (b)", value=300.0)
            with cc2:
                h = st.number_input("Depth (h)", value=400.0)
            Ag = b * h
            dims = (b, h)
        elif shape == "Square":
            a = st.number_input("Side (a)", value=350.0)
            Ag = a**2
            dims = (a, a)
        else:
            D = st.number_input("Diameter (D)", value=300.0)
            Ag = np.pi * D**2 / 4
            dims = (D,)

        Ast = 0
        num_bars = 0
        bar_dia = 0
        spiral_dia = 0
        spiral_spacing = 0
        core_diameter_input = 0

        if "None" not in reinf_style:
            st.markdown("##### Longitudinal Reinforcement")
            rc1, rc2 = st.columns(2)
            with rc1:
                bar_dia = st.number_input("Bar Diameter ($d_b$)", value=16.0)
            with rc2:
                num_bars = st.number_input("Number of Bars", value=8, min_value=4)
            Ast = num_bars * np.pi * (bar_dia / 2) ** 2

            if "Spiral" in reinf_style:
                st.markdown("##### Spiral Confinement Settings")
                st.info("🌀 Hybrid/Spiral Mode Active")

                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    spiral_dia = st.number_input("Spiral Bar $\phi$", value=10.0)
                with sc2:
                    spiral_spacing = st.number_input("Spiral Spacing $s$", value=50.0)
                with sc3:
                    default_core = dims[0] - 2 * cover if shape == "Circular" else min(dims[0], dims[1]) - 2 * cover
                    core_diameter_input = st.number_input(
                        "Core Diam ($D_{k}$)",
                        value=float(default_core),
                        help="Outer diameter of the spiral ring. Usually Column Width - 2*Cover.",
                    )

    with col_viz:
        write_text("section_header", "2. Visualization")
        fig1 = draw_cross_section(shape, dims, num_bars, bar_dia, reinf_style, True, cover)
        st.pyplot(fig1, width="stretch")
        if Ag > 0:
            st.caption(f"**Section Data:** $A_g = {Ag:,.0f}$ mm², $\\rho = {(Ast/Ag)*100:.2f}\\%$")

    st.markdown("---")

    if st.button("Analyze Capacity", type="primary"):
    

        with st.container(border=True):
            

            write_text("section_header", "Step-by-Step Calculation Report")

            results = compute_axial(
                fc=fc, fy=fy, Ag=Ag, Ast=Ast,
                reinf_style=reinf_style,
                core_diameter_input=core_diameter_input,
                spiral_dia=spiral_dia,
                spiral_spacing=spiral_spacing
            )

            # -------------------------------------------------
            # 1. SUMMARY (LEFT) + DETAILED MATH (RIGHT)
            # -------------------------------------------------

            c_res_l, c_res_r = st.columns([1, 1.5])

            # ---------------- LEFT SIDE (RESULT SUMMARY) ----------------
            with c_res_l:
                st.markdown("#### Summary")

                st.metric("Unconfined Capacity (Nor)", f"{results.Nor1/1000:,.0f} kN")

                if "Spiral" in reinf_style and results.Nor2 is not None:
                    st.metric("Confined Capacity (Nor2)", f"{results.Nor2/1000:,.0f} kN")

                    delta = (results.Nor2 - results.Nor1) / 1000
                    if delta > 0:
                        st.success(f"Ductile (+{delta:,.0f} kN)")
                    else:
                        st.warning(f"Brittle ({delta:,.0f} kN)")

            # ---------------- RIGHT SIDE (GLASS MATH BOX) ----------------
            with c_res_r:
                with st.expander("Show Detailed Math", expanded=True):

                    math_content = f"""
    **0. Design Strengths**

    $$f_{{cd}} = \\frac{{f_{{ck}}}}{{\\gamma_c}} = \\frac{{{fc:.1f}}}{{{results.gamma_c}}}
    = \\mathbf{{{results.fcd:.2f}}}\\,\\text{{MPa}}$$

    $$f_{{yd}} = \\frac{{f_{{yk}}}}{{\\gamma_s}} = \\frac{{{fy:.1f}}}{{{results.gamma_s}}}
    = \\mathbf{{{results.fyd:.2f}}}\\,\\text{{MPa}}$$


    **1. Concrete Contribution**

    $$F_c = 0.85 f_{{cd}} (A_g - A_{{st}})$$

    $$F_c = 0.85({results.fcd:.2f})({Ag:.0f}-{Ast:.0f})
    = \\mathbf{{{results.Fc/1000:.0f}}}\\,\\text{{kN}}$$


    **2. Steel Contribution**

    $$F_s = A_{{st}} f_{{yd}}$$

    $$F_s = ({Ast:.0f})({results.fyd:.2f})
    = \\mathbf{{{results.Fs/1000:.0f}}}\\,\\text{{kN}}$$


    **3. Total Capacity**

    $$N_{{or}} = F_c + F_s$$

    $$N_{{or}} = {results.Fc/1000:.0f} + {results.Fs/1000:.0f}
    = \\mathbf{{{results.Nor1/1000:.0f}}}\\,\\text{{kN}}$$
    """
                    glass_box(math_content)

            # -------------------------------------------------
            # 2. BEHAVIOR GRAPH
            # -------------------------------------------------

            st.markdown("#### Behavior Graph")

            graph_N1 = results.Nor1 / 1000
            graph_N2 = results.Nor2 / 1000 if results.Nor2 else 0

            plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"

            fig = plot_load_deformation(graph_N1, graph_N2, plot_type)
            st.pyplot(fig)
            plt.close(fig)
if __name__ == "__main__":
    app()
