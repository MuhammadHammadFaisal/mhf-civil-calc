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

            st.markdown("#### 0. Design Parameters")
            c1, c2, _ = st.columns(3)

            c1.metric("Concrete Design ($f_{cd}$)", f"{results.fcd:.2f} MPa", help=f"{fc} / {results.gamma_c}")
            c2.metric("Steel Design ($f_{yd}$)", f"{results.fyd:.2f} MPa", help=f"{fy} / {results.gamma_s}")

            st.write("**Geometric Properties:**")
            st.latex(fr"A_g = {Ag:,.0f} \text{{ mm}}^2")
            st.latex(fr"A_{{st}} = {num_bars} \times \frac{{\pi \cdot {bar_dia}^2}}{{4}} = {Ast:,.0f} \text{{ mm}}^2")

            st.markdown("#### 1. Detailing Checks (Sanity Check)")
            rho_percent = (Ast / Ag) * 100
            chk_col1, chk_col2 = st.columns(2)
            chk_col1.write(f"Reinforcement Ratio ($\\rho_l$): **{rho_percent:.2f}%**")

            if 1.0 <= rho_percent <= 4.0:
                chk_col2.success("✅ OK (1% $\le \rho \le$ 4%)")
            elif rho_percent < 1.0:
                chk_col2.warning("⚠️ Low Reinforcement! (Code Min = 1%)")
            else:
                chk_col2.error("❌ Too High! (Code Max = 4%)")

            st.markdown("#### 2. Unconfined Axial Capacity ($N_{or}$)")
            glass_box("The total load is shared between the concrete area and the steel bars.")

        

        Force_conc = results.Fc
        Force_steel = results.Fs
        Nor1 = results.Nor1

        f1, f2 = st.columns(2)
        with f1:
            st.metric("Concrete Contribution ($F_c$)", f"{Force_conc/1000:,.0f} kN")
            st.latex(r"F_c = 0.85 f_{cd} (A_g - A_{st})")
            st.caption(f"$0.85 \\cdot {results.fcd:.1f} \\cdot ({Ag:.0f} - {Ast:.0f})$")
        with f2:
            st.metric("Steel Contribution ($F_s$)", f"{Force_steel/1000:,.0f} kN")
            st.latex(r"F_s = A_{st} f_{yd}")
            st.caption(f"${Ast:.0f} \\cdot {results.fyd:.1f}$")

        st.markdown("---")
        st.markdown("**Total Capacity Summation:**")
        st.latex(fr"N_{{or}} = F_c + F_s = {Force_conc/1000:.0f} + {Force_steel/1000:.0f} = \mathbf{{{Nor1/1000:.0f} \text{{ kN}}}}")

        graph_N1 = Nor1 / 1000
        graph_N2 = 0

        if "Spiral" in reinf_style:
            st.markdown("#### 3. Confined Core Capacity ($N_{or2}$)")
            glass_box("This calculates if the spiral can hold the core together after the shell spalls off.")

            if results.Ack is not None:
                st.write(f"Core Diameter ($D_k$): **{core_diameter_input:.0f} mm**")
                st.write(f"Core Area ($A_{{ck}}$): **{results.Ack:,.0f} mm²**")

            if results.rho_s is None:
                st.error("Spacing/core geometry invalid (cannot compute).")
            else:
                st.markdown("**B. Confinement Ratio ($\\rho_s$)**")
                st.latex(fr"\rho_s = \mathbf{{{results.rho_s:.4f}}}")

                if results.rho_min_req is not None and results.rho_s >= results.rho_min_req:
                    st.success(f"✅ Confinement Sufficient ($\\rho_s > {results.rho_min_req:.4f}$)")
                    st.markdown("**C. Enhanced Concrete Strength ($f_{ccd}$)**")
                    st.latex(fr"f_{{ccd}} = \mathbf{{{results.f_ccd:.2f} \text{{ MPa}}}}")

                    if results.Nor2 is not None:
                        st.markdown("**D. Final Confined Capacity**")
                        st.latex(fr"N_{{or2}} = \mathbf{{{results.Nor2/1000:.0f} \text{{ kN}}}}")
                        graph_N2 = results.Nor2 / 1000

                        delta = graph_N2 - graph_N1
                        if delta > 0:
                            st.success(f"🎉 **Ductile Design Achieved!** The column gets stronger after spalling (+{delta:.0f} kN).")
                        else:
                            st.warning(f"⚠️ **Brittle Behavior.** The confined core is weaker than the original section (-{abs(delta):.0f} kN).")
                else:
                    st.error(f"❌ **Spiral Too Weak.** $\\rho_s$ ({results.rho_s:.4f}) is less than required ({results.rho_min_req:.4f}). Calculation stops.")

        st.markdown("#### 4. Behavior Graph")
        plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"
        fig = plot_load_deformation(graph_N1, graph_N2, plot_type)
        st.pyplot(fig)
        plt.close(fig)

if __name__ == "__main__":
    app()
