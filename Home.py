import streamlit as st
import os
from PIL import Image

# Helper function to make image square and resize
def prepare_icon(im, final_size=64):
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    new_im = new_im.resize((final_size, final_size), Image.LANCZOS)
    return new_im

# Load and fix the image
try:
    icon_img = Image.open("assets/Sticker.png").convert("RGBA")
    icon_img = prepare_icon(icon_img, 64)
except:
    icon_img = "🏗️" # Fallback emoji if image is missing

# =========================================================
# APP CONFIG (MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
    page_icon=icon_img
)

# ==================================================
# CUSTOM CSS (Combined into one block)
# ==================================================
st.markdown("""
<style>
.stApp {
    background: 
        linear-gradient(rgba(26,58,90,0.88), rgba(26,58,90,0.88)),
        url("assets/blueprint.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
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

/* Hover Effect */
[data-testid="stPageLink-NavLink"]:hover {
    background-color: #eef4f1 !important;
    border-color: #ced4da !important;
}

/* --- TEXT STYLING INSIDE CARDS --- */
[data-testid="stPageLink-NavLink"] p {
    color: #212529 !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    line-height: 1.4 !important;
    text-align: center !important;
    width: 100% !important;
}

/* Hide arrow icon inside card */
[data-testid="stPageLink-NavLink"] svg {
    display: none !important;
}

/* Hide header link icon */
[data-testid="stHeaderAction"] {
    display: none !important;
}

/* General link button */
[data-testid="stLinkButton"] > a {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)
