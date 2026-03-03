import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from theme import write_text, glass_box

from .diagrams_dynamic.section_preview import draw_cross_section
from .diagrams_results.load_deformation_plot import plot_load_deformation
from .calculator.axial_calculator import compute_axial


def _build_step_by_step_markdown(results, fc, fy, Ag, Ast, reinf_style, core_diameter_input):
    """
    Returns ONE markdown string (with $$ $$ blocks) to be displayed inside glass_box()
    so the whole step-by-step sits on a continuous glass background.
    """
    # Base (always)
    md = f"""
### 0. Design Strengths

$$
f_{{cd}} = \\frac{{f_{{ck}}}}{{\\gamma_c}}
= \\frac{{{fc:.1f}}}{{{results.gamma_c}}}
= \\mathbf{{{results.fcd:.2f}}}\\,\\text{{MPa}}
$$

$$
f_{{yd}} = \\frac{{f_{{yk}}}}{{\\gamma_s}}
= \\frac{{{fy:.1f}}}{{{results.gamma_s}}}
= \\mathbf{{{results.fyd:.2f}}}\\,\\text{{MPa}}
$$


### 1. Concrete Contribution

$$
F_c = 0.85\\, f_{{cd}}\\, (A_g - A_{{st}})
$$

$$
F_c = 0.85({results.fcd:.2f})({Ag:.0f}-{Ast:.0f})
= \\mathbf{{{results.Fc/1000:.0f}}}\\,\\text{{kN}}
$$


### 2. Steel Contribution

$$
F_s = A_{{st}}\\, f_{{yd}}
$$

$$
F_s = ({Ast:.0f})({results.fyd:.2f})
= \\mathbf{{{results.Fs/1000:.0f}}}\\,\\text{{kN}}
$$


### 3. Total Capacity

$$
N_{{or}} = F_c + F_s
$$

$$
N_{{or}} = {results.Fc/1000:.0f} + {results.Fs/1000:.0f}
= \\mathbf{{{results.Nor1/1000:.0f}}}\\,\\text{{kN}}
$$
"""

    # Spiral (optional)
    if "Spiral" in reinf_style:
        md += "\n\n---\n\n### 4. Spiral Check (Confined Core)\n\n"

        if results.rho_s is None or results.rho_min_req is None:
            md += "**❌ Spiral geometry/spacing invalid — cannot compute confinement ratio.**\n"
        else:
            md += f"""
**Core diameter used:** **{core_diameter_input:.0f} mm**

$$
\\rho_s = \\mathbf{{{results.rho_s:.4f}}}
\\qquad
\\rho_{{min}} = \\mathbf{{{results.rho_min_req:.4f}}}
$$
"""
            if results.rho_s >= results.rho_min_req and results.Nor2 is not None:
                md += "\n**✅ Confinement sufficient.**\n"
                md += f"""
$$
N_{{or2}} = \\mathbf{{{results.Nor2/1000:.0f}}}\\,\\text{{kN}}
$$
"""
            else:
                md += "\n**❌ Confinement NOT sufficient.**\n"

    # Clean up extra leading spaces that might turn into code blocks
    return "\n".join(line.rstrip() for line in md.strip().splitlines())


def app():
    write_text("page_title", "RC Column Analyst")

    col_input, col_viz = st.columns([1.3, 1])

    # =========================
    # INPUTS (LEFT)
    # =========================
    with col_input:
        write_text("section_header", "1. System Properties")

        st.markdown("**Materials**")
        c1, c2 = st.columns(2)
        with c1:
            fc = st.number_input("Concrete ($f_{ck}$) [MPa]", value=20.0, step=5.0)
        with c2:
            fy = st.number_input("Steel ($f_{yk}$) [MPa]", value=220.0, step=10.0)

        with st.expander("Geometry & Configuration", expanded=True):
            shape = st.selectbox("Column Shape", ["Rectangular", "Circular"])

            confinement_options = {
                "Spiral (Continuous Helix)": "Spiral / Circular",
                "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
                "Unconfined (Longitudinal Bars Only)": "Longitudinal Only (No Ties)",
                "Plain Concrete (No Reinforcement)": "None (Plain Concrete)",
            }
            selected_label = st.selectbox("Confinement Type", list(confinement_options.keys()))
        
            reinf_style = confinement_options[selected_label]
        st.markdown("**Strength Basis**")
        strength_basis = st.radio(
            "Use which strengths for capacity calculation?",
            ["Design values (fcd, fyd)", "Characteristic values (fck, fyk)"],
            index=0,
            horizontal=True,
        )
        use_design_values = (strength_basis == "Design values (fcd, fyd)")
        st.markdown("**Dimensions**")
        cover = st.number_input("Cover [mm]", value=25.0)

        Ag = 0.0
        dims = (0.0, 0.0)

        if shape == "Rectangular":
            cc1, cc2 = st.columns(2)
            with cc1:
                b = st.number_input("Width (b) (mm)", value=300.0)
            with cc2:
                h = st.number_input("Depth (h) (mm)", value=400.0)
            Ag = b * h
            dims = (b, h)

        else:
            D = st.number_input("Diameter (D) (mm)", value=300.0)
            Ag = np.pi * D**2 / 4
            dims = (D,)

        # Reinforcement
        Ast = 0.0
        num_bars = 0
        bar_dia = 0.0

        # Spiral inputs
        spiral_dia = 0.0
        spiral_spacing = 0.0
        core_diameter_input = 0.0
        fywk = 0.0
        if "None" not in reinf_style:
            st.markdown("##### Longitudinal Reinforcement")
            rc1, rc2 = st.columns(2)
            with rc1:
                bar_dia = st.number_input("Bar Diameter ($d_b$) (mm)", value=20.0)
            with rc2:
                num_bars = st.number_input("Number of Bars", value=8, min_value=4)

            Ast = num_bars * np.pi * (bar_dia / 2) ** 2

            if "Spiral" in reinf_style:
                st.markdown("##### Spiral Confinement Settings")
                st.info("Hybrid/Spiral Mode Active")

                sc1, sc2, sc3, sc4 = st.columns(4)

                with sc1:
                    spiral_dia = st.number_input("Spiral Bar φ (mm)", value=10.0)

                with sc2:
                    spiral_spacing = st.number_input("Spiral Spacing s (mm)", value=50.0)

                with sc3:
                    fywk = st.number_input("Spiral Steel $f_{ywk}$ (MPa)", value=220.0)

                with sc4:
                    if shape == "Circular":
                        default_core = dims[0] - 2 * cover
                    else:
                        default_core = min(dims[0], dims[1]) - 2 * cover

                    core_diameter_input = st.number_input(
                        "Core Diam ($D_k$)",
                        value=float(default_core),
                    )
    # =========================
    # VISUALIZATION (RIGHT)
    # =========================
    with col_viz:
        write_text("section_header", "2. Visualization")
        fig1 = draw_cross_section(shape, dims, num_bars, bar_dia, reinf_style, True, cover)
        st.pyplot(fig1, width="stretch")

        if Ag > 0:
            st.caption(
                f"**Section Data:** $A_g = {Ag:,.0f}$ mm², "
                f"$\\rho = {(Ast/Ag)*100:.2f}\\%$"
            )

    st.markdown("---")

    # =========================
    # CALCULATION OUTPUT
    # =========================
    if st.button("Analyze Capacity", type="primary"):
        # Safety check
        if Ag <= 0:
            st.error("Invalid section area (Ag <= 0). Please check your geometry inputs.")
            return

        results = compute_axial(
        fc=fc,
        fy=fy,
        fywk=fywk,
        Ag=Ag,
        Ast=Ast,
        reinf_style=reinf_style,
        core_diameter_input=core_diameter_input,
        spiral_dia=spiral_dia,
        spiral_spacing=spiral_spacing,
        use_design_values=use_design_values,
    )

        # -----------------------------
        # 1) RESULT SUMMARY (FIRST)
        # -----------------------------
        write_text("section_header", "Result Summary")

        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("Unconfined $N_{or}$", f"{results.Nor1/1000:,.0f} kN")
        with s2:
            if results.Nor2 is not None:
                st.metric("Confined $N_{or2}$", f"{results.Nor2/1000:,.0f} kN")
            else:
                st.metric("Confined $N_{or2}$", "—")
        with s3:
            if results.Nor2 is not None:
                delta = (results.Nor2 - results.Nor1) / 1000
                st.metric("Δ (Nor2 - Nor)", f"{delta:,.0f} kN")
            else:
                st.metric("Δ (Nor2 - Nor)", "—")

        st.markdown("---")

        # -----------------------------
        # 2) GRAPH (SECOND)
        # -----------------------------
        write_text("section_header", "Behavior Graph")

        graph_N1 = results.Nor1 / 1000
        graph_N2 = (results.Nor2 / 1000) if (results.Nor2 is not None) else 0
        plot_type = "Spiral" if "Spiral" in reinf_style else "Ties"

        fig = plot_load_deformation(graph_N1, graph_N2, plot_type)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("---")

        # -----------------------------
        # 3) STEP-BY-STEP (THIRD) — CONTINUOUS GLASS
        # -----------------------------
        write_text("section_header", "Step-by-Step Calculation")

        step_md = _build_step_by_step_markdown(
            results=results,
            fc=fc,
            fy=fy,
            Ag=Ag,
            Ast=Ast,
            reinf_style=reinf_style,
            core_diameter_input=core_diameter_input,
        )
        glass_box(step_md)


if __name__ == "__main__":
    app()
