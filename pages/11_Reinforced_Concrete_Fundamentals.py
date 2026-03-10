import streamlit as st

from theme import apply_theme, render_page_header, write_text, inject_ga

# IMPORTANT: must be called before any Streamlit UI
apply_theme("Reinforced Concrete Fundamentals")
inject_ga()

def app():
    # Use theme header (consistent with your app style)
    render_page_header("Reinforced Concrete Fundamentals")

    write_text("subheader", "Select Calculation Module")

    topic = st.selectbox(
        label="Calculation module",
        options=[
            "Analysis of Axial Load",
            "Analysis of Bending (Flexure)",
            "Design of Bending (Flexure)",
            "Analysis of Combined Loading",
            "Design of Combined Loading",
            "Shear Design",
        ],
        label_visibility="collapsed",
        key="rc_topic_select",
    )

    # --- ROUTING LOGIC ---
    if topic == "Analysis of Axial Load":
        from topics.concrete import axial_analysis
        axial_analysis.app()

    elif topic == "Analysis of Bending (Flexure)":
        from topics.concrete import bending_analysis
        bending_analysis.app()

    elif topic == "Design of Bending (Flexure)":
        from topics.concrete import bending_design
        bending_design.app()

    elif topic == "Analysis of Combined Loading":
        from topics.concrete import combined_analysis
        combined_analysis.app()

    elif topic == "Design of Combined Loading":
        from topics.concrete import combined_design
        combined_design.app()

    elif topic == "Shear Design":
        from topics.concrete import shear_design
        shear_design.app()


if __name__ == "__main__":
    app()
