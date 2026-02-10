import streamlit as st
from PIL import Image

# =========================================================
# Load favicon
# =========================================================
def prepare_icon(im_path, final_size=64):
    im = Image.open(im_path).convert("RGBA")
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0,0,0,0))
    new_im.paste(im, ((size-x)//2, (size-y)//2))
    new_im = new_im.resize((final_size, final_size), Image.LANCZOS)
    return new_im

try:
    icon_img = prepare_icon("assets/Sticker.png", 64)
except:
    icon_img = ""

st.set_page_config(page_title="MHF Civil Calc", layout="wide", page_icon=icon_img)

# =========================================================
# CSS for blueprint-like grid background
# =========================================================
st.markdown("""
<style>
/* ===== Background ===== */
.stApp {
    background-color: #1a3a5a; /* base dark blue */
    background-image: 
        linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px),
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 20px 20px, 20px 20px, 100px 100px, 100px 100px;
    background-position: 0 0, 0 0, 0 0, 0 0;
    background-attachment: scroll;
}

/* --- CARD STYLING --- */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255,255,255,0.85) !important;
    border: 1px solid #dee2e6 !important;
    border-radius: 10px !important;
    padding: 18px !important;
    transition: background-color 0.15s ease !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    backdrop-filter: blur(4px);
}

[data-testid="stPageLink-NavLink"]:hover {
    background-color: rgba(255,255,255,0.95) !important;
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
""", unsafe_allow_html=True)

# =========================================================
# Minimal content to test
# =========================================================
st.title("MHF Civil Calc")
st.write("This background is a clean, subtle blueprint grid that scrolls naturally!")
