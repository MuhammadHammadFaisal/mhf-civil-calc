import streamlit as st
from PIL import Image

# Helper function to make image square and resize
def prepare_icon(im, final_size=64):
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    new_im = new_im.resize((final_size, final_size), Image.LANCZOS)
    return new_im

# Load and fix the image icon
try:
    icon_img = Image.open("assets/Sticker.png").convert("RGBA")
    icon_img = prepare_icon(icon_img, 64)
except:
    icon_img = "🏗️"  # Fallback emoji if image is missing

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
    page_icon=icon_img
)

# ==================================================
# CUSTOM CSS FOR BACKGROUND
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        /* Background image with overlay */
        background: 
            linear-gradient(rgba(26,58,90,0.88), rgba(26,58,90,0.88)),
            url("assets/blueprint.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Optional: make content slightly transparent */
    .css-1d391kg { 
        background-color: rgba(255,255,255,0.0);
    }

    /* --- CARD CONTAINER --- */
    [data-testid="stPageLink-NavLink"] {
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
        padding: 18px !important;
        transition: background-color 0.15s ease !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    [data-testid="stPageLink-NavLink"]:hover {
        background-color: #eef4f1 !important;
        border-color: #ced4da !important;
    }

    [data-testid="stPageLink-NavLink"] p {
        color: #212529 !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        margin: 0 !important;
        line-height: 1.4 !important;
        text-align: center !important;
        width: 100% !important;
    }

    [data-testid="stPageLink-NavLink"] svg {
        display: none !important;
    }

    [data-testid="stHeaderAction"] {
        display: none !important;
    }

    [data-testid="stLinkButton"] > a {
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# ADD SOME CONTENT TO SEE THE BACKGROUND
# ==================================================
st.title("Welcome to MHF Civil Calc")
st.write("This is your homepage with a custom background image!")
