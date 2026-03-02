from theme import apply_theme
apply_theme("RC Column Analyst")

import streamlit as st

from topics.concrete.models import ColumnInput
from topics.concrete.domain.axial_capacity import compute_column_capacity
from topics.concrete.viz.cross_section import draw_cross_section
from topics.concrete.viz.load_deformation import plot_load_deformation
from topics.concrete.report.axial_report import render_report


def app():

    st.title("RC Column Analyst")

    # ---------------- INPUT ----------------
    shape = st.selectbox("Shape", ["Rectangular", "Square", "Circular"])

    fc = st.number_input("Concrete fck (MPa)", value=20.0)
    fy = st.number_input("Steel fyk (MPa)", value=420.0)

    cover = st.number_input("Cover (mm)", value=25.0)
    bar_dia = st.number_input("Bar Diameter (mm)", value=16.0)
    num_bars = st.number_input("Number of Bars", value=8)

    confinement_type = st.selectbox(
        "Confinement Type",
        ["Ties", "Spiral"],
    )

    spiral_dia = 0
    spiral_spacing = 0
    core_diameter = 0

    if confinement_type == "Spiral":
        spiral_dia = st.number_input("Spiral Diameter (mm)", value=10.0)
        spiral_spacing = st.number_input("Spiral Spacing (mm)", value=50.0)
        core_diameter = st.number_input("Core Diameter (mm)", value=250.0)

    if shape == "Rectangular":
        b = st.number_input("Width (mm)", value=300.0)
        h = st.number_input("Depth (mm)", value=400.0)
        dims = (b, h)

    elif shape == "Square":
        a = st.number_input("Side (mm)", value=350.0)
        dims = (a, a)

    else:
        D = st.number_input("Diameter (mm)", value=300.0)
        dims = (D,)

    # Build structured input
    inputs = ColumnInput(
        shape=shape,
        dims=dims,
        cover=cover,
        bar_dia=bar_dia,
        num_bars=num_bars,
        spiral_dia=spiral_dia,
        spiral_spacing=spiral_spacing,
        core_diameter=core_diameter,
        fc=fc,
        fy=fy,
        confinement_type=confinement_type,
    )

    # ---------------- CALCULATE ----------------
    if st.button("Analyze Capacity", type="primary"):

        results = compute_column_capacity(inputs)

        render_report(inputs, results)

        fig_section = draw_cross_section(
            shape,
            dims,
            num_bars,
            bar_dia,
            confinement_type,
            True,
            cover,
        )
        st.pyplot(fig_section)

        fig_curve = plot_load_deformation(
            results.Nor1 / 1000,
            results.Nor2 / 1000,
            confinement_type,
        )
        st.pyplot(fig_curve)


if __name__ == "__main__":
    app()
