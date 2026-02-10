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
# CSS: Instagram Blueprint Style Background
# =========================================================
st.markdown("""
<style>

/* ===== INSTAGRAM BLUEPRINT BACKGROUND ===== */
.stApp {
    background-color: #0b2a45;
    background-image:
        linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        radial-gradient(circle at 85% 15%, rgba(255,255,255,0.08), transparent 35%),
        radial-gradient(circle at 15% 85%, rgba(255,255,255,0.08), transparent 35%);
    background-size:
        24px 24px,
        24px 24px,
        120px 120px,
        120px 120px,
        100% 100%,
        100% 100%;
    background-attachment: fixed;
}

/* ===== Framed Content Area ===== */
main > div:first-child {
    max-width: 1200px;
    margin: 30px auto;
    padding: 30px 40px;
    border: 2px solid rgba(255,255,255,0.18);
    border-radius: 12px;
    background-color: rgba(11,42,69,0.55);
    box-shadow: 0 0 35px rgba(0,0,0,0.35);
}

/* ===== FORCE TEXT COLOR (LIGHT MODE SAFE) ===== */
h1, h2, h3, h4, h5, h6,
p, li, span, label {
    color: #eef3f8 !important;
}

/* Links */
a {
    color: #a8d6ff !important;
    text-decoration: none;
}

/* ===== Module Cards ===== */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255,255,255,0.9) !important;
    border-radius: 10px !important;
    padding: 18px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    backdrop-filter: blur(6px);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

[data-testid="stPageLink-NavLink"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

[data-testid="stPageLink-NavLink"] p {
    color: #1f2d3a !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    text-align: center !important;
    margin: 0 !important;
}

[data-testid="stPageLink-NavLink"] svg {
    display: none !important;
}

/* Hide Streamlit icons */
[data-testid="stHeaderAction"] {
    display: none !important;
}

[data-testid="stLinkButton"] > a {
    border-radius: 8px !important;
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
                            name = file.replace(".py", "").replace("_", " ").replace("-", " ")
                            parts = name.split(" ", 1)
                            if parts[0].isdigit():
                                name = parts[1]
                            modules.append((file, name.title()))
                except:
                    pass
    return sorted(modules, key=lambda x: x[1])

# =========================================================
# Main Application
# =========================================================
def main():

    # ---------- HEADER ----------
    col_logo, col_text = st.columns([1, 3])
    with col_logo:
        st.image("assets/Sticker.png", use_container_width=True)
    with col_text:
        st.markdown("""
        <h1 style="font-size:46px; margin-bottom:6px;">MHF Civil Calc</h1>
        <p style="font-size:18px; line-height:1.5; max-width:700px;">
            Civil Engineering Calculation Workspace
        </p>
        <p style="font-size:14px; max-width:700px;">
            Verified numerical solvers aligned with standard undergraduate civil engineering coursework.
        </p>
        """, unsafe_allow_html=True)

    # ---------- MODULES ----------
    st.subheader("Course Modules")
    modules = get_active_modules()
    if modules:
        cols = st.columns(3)
        for idx, (file, title) in enumerate(modules):
            with cols[idx % 3]:
                st.page_link(
                    f"pages/{file}",
                    label=title,
                    use_container_width=True
                )

    # ---------- PURPOSE ----------
    st.subheader("Purpose")
    st.markdown("""
    MHF Civil provides transparent numerical solutions to standard civil engineering problems.
    Each module follows established theory, clearly states assumptions, and presents intermediate
    steps to support learning, verification, and exam preparation.
    """)

    # ---------- FEEDBACK ----------
    st.subheader("Feedback")
    st.write(
        "If you identify an incorrect result, unclear assumption, or missing topic, "
        "your feedback helps improve the reliability of this platform."
    )
    st.link_button(
        "Open Feedback Form",
        "https://docs.google.com/forms/d/e/1FAIpQLSfKtE2MK_2JZxEK4SzyjEhjdb8PKEC8-dN5az82MaIoPZzMsg/viewform",
        use_container_width=True
    )

    # ---------- ABOUT ----------
    st.subheader("About")
    st.markdown("""
    **Developed by Muhammad Hammad Faisal**  
    Final-Year Civil Engineering Student, METU
    """)

    # ---------- FOOTER ----------
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#bcd4e6; font-size:12px;">
        © 2026 MHF Civil · Ankara, Turkey
    </div>
    """, unsafe_allow_html=True)

# =========================================================
if __name__ == "__main__":
    main()
