import streamlit as st
from PIL import Image
from theme import apply_theme, inject_ga
apply_theme("Soil Mechanics")
inject_ga()
def app():
    col_logo, col_text = st.columns([1, 5], vertical_alignment="center")

    with col_logo:
        # Increased logo width slightly to make it "a little big"
        st.image("assets/Sticker.png")

    with col_text:
        # Font size set to 55px (Professional look: smaller than logo, but distinct)
        st.markdown(
            """
            <div style="padding-left: 15px;">
                <h1 style='font-size: 55px; margin: 0; line-height: 1.0; font-weight: 700;'>Soil Mechanics</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)
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
