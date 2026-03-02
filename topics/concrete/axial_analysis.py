from theme import apply_theme
apply_theme("RC Column Analyst")

import streamlit as st
import numpy as np

from topics.concrete.models import ColumnInput, CapacityResult
from topics.concrete.domain.materials import design_strengths
from topics.concrete.domain.geometry import gross_area, steel_area, core_area, spiral_area
from topics.concrete.domain.detailing import reinforcement_ratio, spiral_min_ratio
from topics.concrete.domain.axial_capacity import unconfined_capacity
from topics.concrete.domain.confinement import spiral_ratio, confined_strength, confined_capacity
from topics.concrete.visualization.cross_section import draw_cross_section
from topics.concrete.visualization.load_deformation import plot_load_deformation
from topics.concrete.report.axial_report import render_report

def app():

    st.title("RC Column Analyst")

    # --- INPUT SECTION ---
    shape = st.selectbox("Shape", ["Rectangular", "Square", "Circular"])
    fc = st.number_input("fck (MPa)", value=20.0)
    fy = st.number_input("fyk (MPa)", value=420.0)

    cover = st.number_input("Cover (mm)", value=25.0)
    bar_dia = st.number_input("Bar Diameter (mm)", value=16.0)
    num_bars = st.number_input("Number of Bars", value=8)

    spiral_dia = st.number_input("Spiral Diameter (mm)", value=10.0)
    spiral_spacing = st.number_input("Spiral Spacing (mm)", value=50.0)
    core_diameter = st.number_input("Core Diameter (mm)", value=250.0)

    if shape == "Rectangular":
        b = st.number_input("Width", value=300.0)
        h = st.number_input("Depth", value=400.0)
        dims = (b, h)
    elif shape == "Square":
        a = st.number_input("Side", value=350.0)
        dims = (a, a)
    else:
        D = st.number_input("Diameter", value=300.0)
        dims = (D,)

    if st.button("Analyze Capacity"):

        Ag = gross_area(shape, dims)
        Ast = steel_area(num_bars, bar_dia)

        fcd, fyd = design_strengths(fc, fy)

        Nor1 = unconfined_capacity(fcd, fyd, Ag, Ast)

        rho_percent = reinforcement_ratio(Ast, Ag)

        Nor2 = 0
        rho_s = 0
        rho_min_req = 0
        fccd = 0

        if spiral_spacing > 0:
            Ack = core_area(core_diameter)
            Asp = spiral_area(spiral_dia)

            rho_s = spiral_ratio(Asp, core_diameter - spiral_dia, spiral_spacing)
            rho_min_req = spiral_min_ratio(fc, fy, Ag, Ack)

            if rho_s >= rho_min_req:
                fccd = confined_strength(fcd, rho_s, fy)
                Nor2 = confined_capacity(fccd, Ack, Ast, fyd)

        results = CapacityResult(
            Nor1=Nor1,
            Nor2=Nor2,
            rho_percent=rho_percent,
            rho_s=rho_s,
            rho_min_req=rho_min_req,
            fcd=fcd,
            fyd=fyd,
            fccd=fccd
        )

        render_report(None, results)

        fig1 = draw_cross_section(shape, dims, num_bars, bar_dia, "Spiral", True, cover)
        st.pyplot(fig1)

        fig2 = plot_load_deformation(Nor1/1000, Nor2/1000, "Spiral")
        st.pyplot(fig2)

if __name__ == "__main__":
    app()
