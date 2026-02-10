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
    background-color: #1a3a5a;
    background-image:
        linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px),
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px),
        radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 20px 20px, 20px 20px, 100px 100px, 100px 100px, 500px 500px;
}

/* ===== Content Frame ===== */
.content-frame {
    max-width: 1200px;
    margin: 30px auto;
    padding: 30px 40px;
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    background-color: rgba(26,58,90,0.55);
    box-shadow: 0 0 30px rgba(0,0,0,0.25);
}

.content-frame h1,
.content-frame h2,
.content-frame h3,
.content-frame p,
.content-frame li,
.content-frame span {
    color: #eee;
}

/* ===== Page Cards ===== */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255,255,255,0.9) !important;
    border-radius: 10px !important;
    padding: 18px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

[data-testid="stPageLink-NavLink"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

[data-testid="stPageLink-NavLink"] p {
    color: #212529 !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    text-align: center !important;
    margin: 0 !important;
}

[data-testid="stPageLink-NavLink"] svg {
    display: none !important;
}

/* ===== Hide Streamlit Icons ===== */
[data-testid="stHeaderAction"] {
    display: none !important;
}

/* ===== Footer ===== */
.footer {
    margin-top: 40px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.15);
    text-align: center;
    color: #bbb;
    font-size: 12px;
}

/* ===== Links ===== */
a {
    color: #aad4ff !important;
    text-decoration: none;
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
# Main App
# =========================================================
def main():

    st.markdown('<div class="content-frame">', unsafe_allow_html=True)

    # ---------- HEADER ----------
    col_logo, col_text = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        st.image("assets/Sticker.png", width=120)
    with col_text:
        st.markdown("""
        <h1 style="font-size:46px; margin-bottom:6px;">MHF Civil Calc</h1>
        <p style="font-size:18px;">
            Civil Engineering Calculation Workspace
        </p>
        <p style="font-size:14px; color:#ddd;">
            Verified numerical solvers aligned with standard undergraduate civil engineering coursework.
        </p>
        """, unsafe_allow_html=True)

    # ---------- MODULES ----------
    st.subheader("Course Modules")
    modules = get_active_modules()
    if modules:
        cols = st.columns(3, gap="large")
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
    st.link_button(
        "LinkedIn Profile",
        "https://www.linkedin.com/in/muhammad-hammad-20059a229"
    )

    # ---------- FOOTER ----------
    st.markdown("""
    <div class="footer">
        © 2026 MHF Civil · Ankara, Turkey
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
if __name__ == "__main__":
    main()
