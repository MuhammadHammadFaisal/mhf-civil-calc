import streamlit as st
import os
from PIL import Image

# =========================================================
# Helper function to make image square and resize
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
    icon_img = ""  # fallback

# =========================================================
# App Config
# =========================================================
st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
    page_icon=icon_img
)

# =========================================================
# CSS: Card styling (for modules + feedback + LinkedIn)
# =========================================================
st.markdown("""
<style>
/* App Background */
.stApp {
    background-color: #031126;
    background-image: 
        radial-gradient(circle at 100% 0%, transparent 180px, rgba(255,255,255,0.05) 181px, transparent 183px),
        radial-gradient(circle at 100% 0%, transparent 240px, rgba(255,255,255,0.03) 241px, transparent 245px),
        radial-gradient(circle at 0% 100%, transparent 200px, rgba(255,255,255,0.05) 201px, transparent 203px),
        radial-gradient(circle at 0% 100%, transparent 300px, rgba(255,255,255,0.02) 301px, transparent 305px),
        radial-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
        linear-gradient(rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
        linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
        radial-gradient(circle at center, rgba(20, 75, 150, 0.4) 0%, #031126 90%);
    background-size: 
        100% 100%, 100% 100%, 100% 100%, 100% 100%,
        40px 40px,
        200px 200px, 200px 200px,
        40px 40px, 40px 40px,
        100% 100%;
    background-attachment: fixed;
}

/* Card container */
[data-testid="stPageLink-NavLink"] {
    background-color: #f8f9fa !important;
    border: 1px solid #dee2e6 !important;
    border-radius: 10px !important;
    padding: 18px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    transition: all 0.2s ease !important;
}

/* Hover effect */
[data-testid="stPageLink-NavLink"]:hover {
    background-color: #eef4f1 !important;
    border-color: #ced4da !important;
    box-shadow: 0 0 10px rgba(0,0,0,0.05) !important;
}

/* Text inside card */
[data-testid="stPageLink-NavLink"] p {
    color: #212529 !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    text-align: center !important;
    margin: 0 !important;
}

/* Hide arrow icon */
[data-testid="stPageLink-NavLink"] svg {
    display: none !important;
}

/* Link button styling */
[data-testid="stLinkButton"] > a {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# Scan active modules
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
                except Exception:
                    pass
    return sorted(modules, key=lambda x: x[1])

# =========================================================
# Main application
# =========================================================
def main():
    # ------------------------- HEADER -------------------------
    col_logo, col_text = st.columns([1, 3], vertical_alignment="center")
    with col_logo:
        st.image("assets/Sticker.png", use_container_width=True)
    with col_text:
        st.markdown("""
        <h1 style="font-size:46px; margin-bottom:6px;">MHF Civil Calc</h1>
        <p style="color:#555; font-size:18px; line-height:1.5; max-width:700px;">
            Civil Engineering Calculation Workspace
        </p>
        <p style="color:#777; font-size:14px; max-width:700px;">
            Verified numerical solvers aligned with standard undergraduate civil engineering coursework.
        </p>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ------------------------- MODULES -------------------------
    st.subheader("Course Modules")
    st.markdown("")
    modules = get_active_modules()
    if modules:
        cols = st.columns(3)
        for idx, (file, title) in enumerate(modules):
            with cols[idx % 3]:
                st.page_link(f"pages/{file}", label=title, use_container_width=True)
                st.markdown("")

    # ------------------------- PURPOSE -------------------------
    st.markdown("")
    st.subheader("Purpose")
    st.markdown("""
    MHF Civil provides transparent numerical solutions to standard civil engineering problems.
    Each module follows established theory, clearly states assumptions, and presents intermediate
    steps to support learning, verification, and exam preparation.
    """)

    # ------------------------- FEEDBACK + LINKEDIN -------------------------
    st.markdown("")
    st.subheader("Feedback & Connect")
    st.markdown("")

    # Display side by side like cards
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            "https://docs.google.com/forms/d/e/1FAIpQLSfKtE2MK_2JZxEK4SzyjEhjdb8PKEC8-dN5az82MaIoPZzMsg/viewform",
            label="Open Feedback Form",
            use_container_width=True
        )
    with col2:
        st.page_link(
            "https://www.linkedin.com/in/muhammad-hammad-20059a229",
            label="LinkedIn Profile",
            use_container_width=True
        )

    # ------------------------- FOOTER -------------------------
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#777; font-size:12px;">
        © 2026 MHF Civil · Ankara, Turkey
    </div>
    """, unsafe_allow_html=True)

# =========================================================
if __name__ == "__main__":
    main()

