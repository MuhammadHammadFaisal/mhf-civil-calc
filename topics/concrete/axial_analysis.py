import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from textwrap import dedent

from theme import write_text, glass_box

from .diagrams_dynamic.section_preview import draw_cross_section
from .diagrams_results.load_deformation_plot import plot_load_deformation
from .calculator.axial_calculator import compute_axial


def app():
    write_text("page_title", "RC Column Analyst")

    col_input, col_viz = st.columns([1.3, 1])

    # =========================
    # INPUTS (LEFT)
    # =========================
    with col_input:
        write_text("section_header", "1. System Properties")

        design_code = "TS 500 (Lecture Notes)"  # kept for future expansion

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

        Ag = 0.0
        dims = (0.0, 0.0)

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

        # Reinforcement
        Ast = 0.0
        num_bars = 0
        bar_dia = 0.0

        # Spiral inputs (only used if spiral)
        spiral_dia = 0.0
        spiral_spacing = 0.0
        core_diameter_input = 0.0

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
                    if shape == "Circular":
                        default_core = dims[0] - 2 * cover
                    else:
                        default_core = min(dims[0], dims[1]) - 2 * cover

                    core_diameter_input = st.number_input(
                        "Core Diam ($D_{k}$)",
                        value=float(default_core),
                        help="Outer diameter of the spiral ring. Usually Column Width - 2*Cover.",
                    )

    # =========================
    # VISUALIZATION (RIGHT)
    # =========================
    with col_viz:
        write_text("section_header", "2. Visualization")

        fig1 = draw_cross_section(shape, dims, num_bars, bar_dia, reinf_style, True, cover)
        st.pyplot(fig1, width="stretch")

        if Ag > 0:
            st.caption(f"**Section Data:** $A_g = {Ag:,.0f}$ mm², $\\rho = {(Ast/Ag)*100:.2f}\\%$")

    st.markdown("---")

    # =========================
    # CALCULATION OUTPUT
    # =========================
    if st.button("Analyze Capacity", type="primary"):
        with st.container(border=True):
            write_text("section_header", "Step-by-Step Calculation Report")

            # Safety check
            if Ag <= 0:
                st.error("Invalid section area (Ag <= 0). Please check your geometry inputs.")
                return

            results = compute_axial(
                fc=fc,
                fy=fy,
                Ag=Ag,
                Ast=Ast,
                reinf_style=reinf_style,
                core_diameter_input=core_diameter_input,
                spiral_dia=spiral_dia,
                spiral_spacing=spiral_spacing,
            )

            # -----------------------------------------
            # SUMMARY + DETAILED MATH (Effective Stress style)
            # -----------------------------------------
            c_res_l, c_res_r = st.columns([1, 1.5])

                        with c_res_r:
                with st.expander("Show Detailed Math", expanded=True):
                    math_logs = []

                    # 0. Design Strengths
                    math_logs.append("**0. Design Strengths**")
                    math_logs.append(f"$f_{{cd}} = \\frac{{f_{{ck}}}}{{\\gamma_c}} = \\frac{{{fc:.1f}}}{{{results.gamma_c}}} = \\mathbf{{{results.fcd:.2f}}}\\,\\text{{MPa}}$")
                    math_logs.append(f"$f_{{yd}} = \\frac{{f_{{yk}}}}{{\\gamma_s}} = \\frac{{{fy:.1f}}}{{{results.gamma_s}}} = \\mathbf{{{results.fyd:.2f}}}\\,\\text{{MPa}}$")
                    math_logs.append("---")

                    # 1. Concrete Contribution
                    math_logs.append("**1. Concrete Contribution**")
                    math_logs.append("$F_c = 0.85 f_{{cd}} (A_g - A_{{st}})$")
                    math_logs.append(f"$F_c = 0.85({results.fcd:.2f})({Ag:.0f}-{Ast:.0f}) = \\mathbf{{{results.Fc/1000:.0f}}}\\,\\text{{kN}}$")
                    math_logs.append("---")

                    # 2. Steel Contribution
                    math_logs.append("**2. Steel Contribution**")
                    math_logs.append("$F_s = A_{{st}} f_{{yd}}$")
                    math_logs.append(f"$F_s = ({Ast:.0f})({results.fyd:.2f}) = \\mathbf{{{results.Fs/1000:.0f}}}\\,\\text{{kN}}$")
                    math_logs.append("---")

                    # 3. Total Capacity
                    math_logs.append("**3. Total Capacity**")
                    math_logs.append("$N_{{or}} = F_c + F_s$")
                    math_logs.append(f"$N_{{or}} = {results.Fc/1000:.0f} + {results.Fs/1000:.0f} = \\mathbf{{{results.Nor1/1000:.0f}}}\\,\\text{{kN}}$")

                    # Optional: Dynamically add Spiral math if applicable
                    if "Spiral" in reinf_style and results.rho_s is not None and results.rho_min_req is not None:
                        math_logs.append("---")
                        math_logs.append("**4. Spiral Confinement Check**")
                        math_logs.append(f"$\\rho_s = \\mathbf{{{results.rho_s:.4f}}}$ (Computed)")
                        math_logs.append(f"$\\rho_{{min}} = \\mathbf{{{results.rho_min_req:.4f}}}$ (Required)")
                        
                        if results.rho_s >= results.rho_min_req:
                            math_logs.append("✅ Confinement sufficient. Confined capacity applies:")
                            math_logs.append(f"$N_{{or2}} = \\mathbf{{{results.Nor2/1000:.0f}}}\\,\\text{{kN}}$")
                        else:
                            math_logs.append("❌ Confinement insufficient. Only unconfined capacity applies.")

                    # Join and display
                    math_content = "\n\n".join(math_logs)
                    glass_box(math_content)


            # -----------------------------------------
            # Optional Spiral Details (keep widgets normal)
            # -----------------------------------------
            if "Spiral" in reinf_style:
                st.markdown("#### Spiral Check (Confined Core)")

                if results.rho_s is None or results.rho_min_req is None:
                    st.error("Spiral geometry/spacing invalid (cannot compute confinement ratio).")
                else:
                    st.write(f"Computed $\\rho_s$: **{results.rho_s:.4f}**")
                    st.write(f"Required $\\rho_{{min}}$: **{results.rho_min_req:.4f}**")

                    if results.rho_s >= results.rho_min_req and results.Nor2 is not None:
                        st.success("✅ Confinement sufficient.")
                    else:
                        st.error("❌ Confinement not sufficient.")

            # -----------------------------------------
            # Behavior Graph
            # -----------------------------------------
            st.markdown("#### Behavior Graph")

            graph_N1 = results.Nor1 / 1000
            graph_N2 = (results.Nor2 / 1000) if (results.Nor2 is not None) else 0

            plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"
            fig = plot_load_deformation(graph_N1, graph_N2, plot_type)

            st.pyplot(fig)
            plt.close(fig)


if __name__ == "__main__":
    app()
