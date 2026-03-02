from theme import apply_theme
apply_theme("Axial Analysis")

import streamlit as st

from topics.concrete.ui.inputs_axial import get_axial_inputs
from topics.concrete.core.axial_models import compute_axial_capacity
from topics.concrete.viz.cross_section import draw_cross_section
from topics.concrete.viz.load_deformation import plot_load_deformation

def app():

    st.title("Axial Capacity Analysis")

    inputs = get_axial_inputs()

    if st.button("Calculate"):

        results = compute_axial_capacity(inputs)

        st.success("Calculation Complete")

        st.write(f"N1 = {results.N1:.2f} kN")
        st.write(f"N2 = {results.N2:.2f} kN")
        st.write(f"Behavior: {results.transition}")

        fig_section = draw_cross_section(inputs)
        st.pyplot(fig_section)

        fig_ld = plot_load_deformation(results)
        st.pyplot(fig_ld)

if __name__ == "__main__":
    app()
