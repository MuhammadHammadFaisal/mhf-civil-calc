import streamlit as st
import os
import base64
from PIL import Image

# Helper function to convert local image to base64 for CSS background
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Helper function to make image square and resize
def prepare_icon(im, final_size=64):
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    new_im = new_im.resize((final_size, final_size), Image.LANCZOS)
    return new_im

# --- Image Loading Logic ---
blueprint_path = "1000075782 (1).jpg" # Ensure this filename matches your file in the directory
bin_str = ""
if os.path.exists(blueprint_path):
    bin_str = get_base64_of_bin_file(blueprint_path)

try:
    icon_img = Image.open("assets/Sticker.png").convert("RGBA")
    icon_img = prepare_icon(icon_img, 64)
except:
    icon_img = "🏗️"

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
    page_icon=icon_img
)

# ==================================================
# CUSTOM CSS (Now with Base64 Background)
# ==================================================
st.markdown(f"""
<style>
/* --- 0. BACKGROUND SETUP --- */
.stApp {{
    background-image: url("data:image/jpg;base64,{bin_str}");
    background-attachment: fixed;
    background-size: cover;
    background-position: center;
}}

/* Overlay to improve readability */
.stApp::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(15, 32, 54, 0.7); /* Deep blue tint */
    z-index: -1;
}}

/* Making headings and text white/readable */
h1, h2, h3, p, span, label {{
    color: white !important;
}}

/* --- 1. CARD CONTAINER (Module Links) --- */
[data-testid="stPageLink-NavLink"] {{
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 12px !important;
    padding: 18px !important;
    transition: all 0.3s ease !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    backdrop-filter: blur(5px); /* Glassmorphism effect */
}}

[data-testid="stPageLink-NavLink"]:hover {{
    background-color: rgba(255, 255, 255, 0.2) !important;
    border-color: #00d4ff !important;
    transform: translateY(-3px);
}}

[data-testid="stPageLink-NavLink"] p {{
    color: #ffffff !important;
    font-size: 17px !important;
    font-weight: 600 !important;
}}

/* --- 2. HIDE DEFAULTS --- */
[data-testid="stPageLink-NavLink"] svg {{ display: none !important; }}
[data-testid="stHeaderAction"] {{ display: none !important; }}
header {{ visibility: hidden; }} /* Hides the top bar for a cleaner look */

</style>
""", unsafe_allow_html=True)

# ==================================================
# MODULE DISCOVERY
# ==================================================
def get_active_modules():
    modules = []
    if os.path.exists("pages"):
        for file in os.listdir("pages"):
            if file.endswith(".py") and file != "__init__.py":
                try:
                    with open(os.path.join("pages", file), "r", encoding="utf-8") as f:
                        content = f.read()
                        if "Module Under Construction" not in content:
                            name = file.replace(".py", "").replace("_", " ").replace("-", " ")
                            parts = name.split(" ", 1)
                            if parts[0].isdigit(): name = parts[1]
                            modules.append((file, name.title()))
                except: pass
    return sorted(modules, key=lambda x: x[1])

# ==================================================
# MAIN APPLICATION
# ==================================================
def main():
    # HEADER
    col_logo, col_text = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        st.image("assets/Sticker.png", width=120)
    with col_text:
        st.markdown('<h1 style="font-size:50px; margin-bottom:0;">MHF Civil Calc</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:20px; opacity:0.8;">Civil Engineering Calculation Workspace</p>', unsafe_allow_html=True)

    st.divider()

    # MODULES
    st.subheader("Course Modules")
    modules = get_active_modules()
    if modules:
        cols = st.columns(3)
        for idx, (file, title) in enumerate(modules):
            with cols[idx % 3]:
                st.page_link(f"pages/{file}", label=title, use_container_width=True)

    # PURPOSE & INFO
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Purpose")
        st.write("Transparent numerical solutions for engineering theory and exam preparation.")
    with col2:
        st.subheader("Feedback")
        st.link_button("Open Feedback Form", "https://docs.google.com/forms/...", use_container_width=True)

    # ABOUT & FOOTER
    st.divider()
    st.markdown("""
    <div style="text-align:center; opacity:0.6; font-size:14px;">
        Developed by Muhammad Hammad Faisal · METU <br>
        © 2026 MHF Civil · Ankara, Turkey
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
