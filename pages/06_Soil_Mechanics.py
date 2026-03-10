import streamlit as st
from PIL import Image
from theme import apply_theme, render_page_header, write_text, inject_ga

apply_theme("Soil Mechanics")
inject_ga()
def app():
    render_page_header("Soil Mechanics")
    # --- TOPIC SELECTION MENU ---
    topic = st.selectbox(
        "Select Chapter:", 
        [
            "Phase Relationships",
            "Effective Stress",
            "Flow of Water in Soils",
            "Consolidation Theory",
            "Shear Strength of Soils",
            "Lateral Earth Pressure",
            "Stability of Slopes"
        ]
    )

    if topic == "Phase Relationships":
        from topics import soil_phase
        soil_phase.app()

    elif topic == "Effective Stress":
        from topics import effective_stress
        effective_stress.app()

    elif topic == "Flow of Water in Soils":
        from topics import flow_water
        flow_water.app()
        
    elif topic == "Consolidation Theory":
        from topics import consolidation
        consolidation.app()
        
    elif topic == "Shear Strength of Soils":
        from topics import shear_strength
        shear_strength.app()
        
    elif topic == "Lateral Earth Pressure":
        from topics import lateral_earth_pressure
        lateral_earth_pressure.app()

    elif topic == "Stability of Slopes":
        from topics import Stability_of_Slopes
        Stability_of_Slopes.app()


if __name__ == "__main__":
    app()
