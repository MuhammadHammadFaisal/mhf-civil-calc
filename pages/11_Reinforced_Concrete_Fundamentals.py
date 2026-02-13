import streamlit as st
# IMPORT MODULES
from topics.concrete import axial_analysis
from topics.concrete import axial_design
from topics.concrete import bending_analysis
from topics.concrete import bending_design
from topics.concrete import combined_analysis
from topics.concrete import combined_design
from topics.concrete import shear_design

from PIL import Image

# Helper function to make image square and resize
def prepare_icon(im, final_size=64):
    x, y = im.size
    size = max(x, y)

    # Create square transparent canvas
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))

    # Resize to favicon friendly size
    new_im = new_im.resize((final_size, final_size), Image.LANCZOS)

    return new_im


# Load and fix the image
try:
    icon_img = Image.open("assets/Sticker.png").convert("RGBA")
    icon_img = prepare_icon(icon_img, 64)   # <-- IMPORTANT
except:
    icon_img = ""   # fallback emoji


# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(
    page_title="MHF Reinforced Concrete Fundamentals",
    layout="wide",
    page_icon=icon_img
)


def app():
# =========================================================
    # PASTE THIS RIGHT AT THE START OF YOUR app() FUNCTION
    # =========================================================
    st.markdown("""
    <style>
        /* 1. Fix the Sidebar Color to match the Blueprint theme */
        [data-testid="stSidebar"] {
            background-color: #031126;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* 2. Your Blueprint Background Code */
        [data-testid="stAppViewContainer"] {
            background-color: #031126;
            background-image: 
                linear-gradient(to bottom, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 42px, transparent 42px),
                radial-gradient(circle at 50% 40vh, rgba(20, 75, 150, 0.4) 0%, transparent 70%),
                linear-gradient(rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
                linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
                radial-gradient(circle at 100% 0%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
                radial-gradient(circle at 100% 0%, transparent 220px, rgba(255,255,255,0.05) 221px, transparent 222px),
                radial-gradient(circle at 0% 100%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
                radial-gradient(circle at 0% 100%, transparent 50px, rgba(255,255,255,0.15) 51px, transparent 53px);
            background-size: 
                100% 100%, 100% 100%,
                75px 75px, 75px 75px,
                15px 15px, 15px 15px,
                100% 100%, 100% 100%,
                100% 100%, 100% 100%;
            background-repeat: 
                no-repeat, no-repeat, repeat, repeat, repeat, repeat, no-repeat, no-repeat, no-repeat, no-repeat;
            background-attachment: local;
        }

        /* 3. Make text readable on the dark background */
        h1, h2, h3, h4, p, li, .stMarkdown {
            color: #E2E8F0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    # --- PROFESSIONAL HEADER SECTION ---
    # Adjusted column ratio to give the bigger logo enough space
    col_logo, col_text = st.columns([1, 5], vertical_alignment="center")

    with col_logo:
        # Increased logo width slightly to make it "a little big"
        st.image("assets/Sticker.png")

    with col_text:
        # Font size set to 55px (Professional look: smaller than logo, but distinct)
        st.markdown(
            """
            <div style="padding-left: 15px;">
                <h1 style='font-size: 55px; margin: 0; line-height: 1.0; font-weight: 700;'>Reinforced Concrete Fundamentals</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    # --- TOPIC SELECTION MENU ---
    topic = st.selectbox(
        "Select Calculation Module:", 
        [
            "Analysis of Axial Load",
            "Design of Axial Members",
            "Analysis of Bending (Flexure)",
            "Design of Bending (Flexure)",
            "Analysis of Combined Loading",
            "Design of Combined Loading",
            "Shear Design"
        ]
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
