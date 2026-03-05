import streamlit as st

# IMPORT MODULES
from topics.concrete import axial_analysis
from topics.concrete import axial_design
from topics.concrete import bending_analysis
from topics.concrete import bending_design
from topics.concrete import combined_analysis
from topics.concrete import combined_design
from topics.concrete import shear_design

from theme import apply_theme, render_page_header, write_text

# IMPORTANT: must be called before any Streamlit UI
apply_theme("Reinforced Concrete Fundamentals")


def app():
    # Use theme header (consistent with your app style)
    render_page_header("Reinforced Concrete Fundamentals")

    write_text("subheader", "Select Calculation Module")

    topic = st.selectbox(
        label="",
        options=[
            "Analysis of Axial Load",
            "Design of Axial Members",
            "Analysis of Bending (Flexure)",
            "Design of Bending (Flexure)",
            "Analysis of Combined Loading",
            "Design of Combined Loading",
            "Shear Design",
        ],
        key="rc_topic_select",
    )

    # --- ROUTING LOGIC ---
    if topic == "Analysis of Axial Load":
        axial_analysis.app()

    elif topic == "Design of Axial Members":
        axial_design.app()

    elif topic == "Analysis of Bending (Flexure)":
        bending_analysis.app()

    elif topic == "Design of Bending (Flexure)":
        bending_design.app()

    elif topic == "Analysis of Combined Loading":
        combined_analysis.app()

    elif topic == "Design of Combined Loading":
        combined_design.app()

    elif topic == "Shear Design":
        shear_design.app()


if __name__ == "__main__":
    app()
