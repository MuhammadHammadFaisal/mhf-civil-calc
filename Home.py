import streamlit as st
import os
from PIL import Image

# =========================================================
# Helper: Make Image Square and Resize for Favicon
# =========================================================
def prepare_icon(im, final_size=64):
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    new_im = new_im.resize((final_size, final_size), Image.LANCZOS)
    return new_im

# Load favicon
try:
    icon_img = Image.open("assets/Sticker.png").convert("RGBA")
    icon_img = prepare_icon(icon_img, 64)
except:
    icon_img = "🛠️"

# =========================================================
# App Config
# =========================================================
st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
    page_icon=icon_img
)

# =========================================================
# CSS Styling
# =========================================================
st.markdown("""
<style>

/* ===== Blueprint Background ===== */
.stApp {
    background-color: #031126;
    background-image: 

        /* Frame */
        linear-gradient(to right, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 43px, transparent 43px),
        linear-gradient(to left, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 43px, transparent 43px),
        linear-gradient(to bottom, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 43px, transparent 43px),

        /* Arcs */
        radial-gradient(circle at 100% 0%, transparent 180px, rgba(255,255,255,0.05) 181px, transparent 183px),
        radial-gradient(circle at 0% 100%, transparent 200px, rgba(255,255,255,0.05) 201px, transparent 203px),

        /* Grid */
        linear-gradient(rgba(255,255,255,0.08) 1.5px, transparent 1.5px),
        linear-gradient(90deg, rgba(255,255,255,0.08) 1.5px, transparent 1.5px),

        /* Sub Grid */
        linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px),

        /* Glow */
        radial-gradient(circle at center, rgba(20,75,150,0.4) 0%, #031126 90%);

    background-size:
        100% 100%,100% 100%,100% 100%,
        100% 100%,100% 100%,
        75px 75px,75px 75px,
        15px 15px,15px 15px,
        100% 100%;

    background-attachment: fixed;
}

/* ===== Content Container ===== */
section.main > div.block-container {
    max-width: 1200px;
    margin: 30px auto;

    padding-top: 30px;
    padding-bottom: 30px;

    /* Keep content inside frame */
    padding-left: calc(40px + 20px);
    padding-right: calc(40px + 20px);

    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    background-color: rgba(26,58,90,0.5);
    box-shadow: 0 0 30px rgba(0,0,0,0.2);
    color: #E2E8F0 !important;
}

section.main > div.block-container * {
    color: #E2E8F0 !important;
}

/* ===== Module Cards ===== */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255,255,255,0.9) !important;
    border-radius: 10px !important;
    padding: 18px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

[data-testid="stPageLink-NavLink"] p {
    color: #212529 !important;
    font-weight: 600 !important;
    text-align: center !important;
}

[data-testid="stPageLink-NavLink"] svg {
    display: none !important;
}

/* ===== Buttons ===== */
[data-testid="stLinkButton"] > a {
    background-color: white !important;
    color: #1a3a5a !important;
    font-weight: 600 !important;
}

/* ===== MOBILE RESPONSIVE ===== */
@media (max-width: 768px){

    /* Thinner frame */
    .stApp {
        background-image: 
            linear-gradient(to right, #031126 0%, #031126 18px, rgba(255,255,255,0.5) 18px, rgba(255,255,255,0.5) 20px, transparent 20px),
            linear-gradient(to left, #031126 0%, #031126 18px, rgba(255,255,255,0.5) 18px, rgba(255,255,255,0.5) 20px, transparent 20px),
            linear-gradient(to bottom, #031126 0%, #031126 18px, rgba(255,255,255,0.5) 18px, rgba(255,255,255,0.5) 20px, transparent 20px),

            radial-gradient(circle at center, rgba(20,75,150,0.4) 0%, #031126 90%);
    }

    /* Content padding */
    section.main > div.block-container {
        margin: 15px 8px;
        padding-top: 20px;
        padding-bottom: 20px;
        padding-left: calc(20px + 12px);
        padding-right: calc(20px + 12px);
    }

    h1 {
        font-size: 36px !important;
    }

    /* Stack header columns */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# Scan Active Modules
# =========================================================
def get_active_modules():
    modules = []
    if os.path.exists("pages"):
        for file in os.listdir("pages"):
            if file.endswith(".py") and file != "__init__.py":
                try:
                    with open(os.path.join("pages", file), "r", encoding="utf-8") as f:
                        content = f.read()
                        if "Module Under Construction" not in content:
                            name = file.replace(".py", "").replace("_", " ")
                            modules.append((file, name.title()))
                except:
                    pass
    return sorted(modules, key=lambda x: x[1])

# =========================================================
# Main Application
# =========================================================
def main():

    # HEADER
    col_logo, col_text = st.columns([1, 3], vertical_alignment="center")

    with col_logo:
        if os.path.exists("assets/Sticker.png"):
            st.image("assets/Sticker.png", use_container_width=True)

    with col_text:
        st.markdown("""
        <h1 style="color:white;">MHF Civil Calc</h1>
        <p>Civil Engineering Calculation Workspace</p>
        <p style="font-size:14px;">
        Verified numerical solvers aligned with standard undergraduate civil engineering coursework.
        </p>
        """, unsafe_allow_html=True)

    st.markdown("")

    # MODULES
    st.markdown("### Course Modules")
    modules = get_active_modules()

    if modules:
        cols = st.columns(3)
        for idx, (file, title) in enumerate(modules):
            with cols[idx % 3]:
                st.page_link(f"pages/{file}", label=title, use_container_width=True)

    # PURPOSE
    st.markdown("### Purpose")
    st.write(
        "MHF Civil provides transparent numerical solutions to standard civil engineering problems. "
        "Each module follows established theory and presents intermediate steps to support learning."
    )

    # FEEDBACK
    st.markdown("### Feedback")
    st.link_button(
        "Open Feedback Form",
        "https://docs.google.com/forms/d/e/1FAIpQLSfKtE2MK_2JZxEK4SzyjEhjdb8PKEC8-dN5az82MaIoPZzMsg/viewform"
    )

    # ABOUT
    st.markdown("### About")
    st.write("Developed by Muhammad Hammad Faisal – Civil Engineering Student, METU")

    st.link_button(
        "LinkedIn Profile",
        "https://www.linkedin.com/in/muhammad-hammad-20059a229"
    )

    # FOOTER
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; font-size:12px;'>© 2026 MHF Civil</div>",
        unsafe_allow_html=True
    )

# =========================================================
if __name__ == "__main__":
    main()
