import streamlit as st
from topics.concrete.schemas.axial import AxialInputs

def get_axial_inputs():

    section_type = st.selectbox("Section Type", ["Rectangular"])
    width = st.number_input("Width (mm)", 100.0, 2000.0, 400.0)
    height = st.number_input("Height (mm)", 100.0, 2000.0, 400.0)
    cover = st.number_input("Cover (mm)", 10.0, 100.0, 40.0)
    bar_diameter = st.number_input("Bar Diameter (mm)", 8.0, 40.0, 16.0)
    num_bars = st.number_input("Number of Bars", 4, 20, 8)
    fck = st.number_input("Concrete Strength fck (MPa)", 10.0, 90.0, 30.0)
    fyk = st.number_input("Steel Strength fyk (MPa)", 200.0, 600.0, 420.0)
    confinement = st.radio("Confinement Type", ["Tied", "Spiral"])

    return AxialInputs(
        section_type,
        width,
        height,
        cover,
        bar_diameter,
        num_bars,
        fck,
        fyk,
        confinement
    )
