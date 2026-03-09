import streamlit as st
import os
from PIL import Image
from theme import apply_theme, inject_ga

apply_theme("MHF CIVIL CALC")
inject_ga()


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
                            if parts and parts[0].isdigit() and len(parts) > 1:
                                name = parts[1]
                            modules.append((file, name.title()))
                except Exception:
                    pass
    return sorted(modules, key=lambda x: x[1])

# =========================================================
# Main Application
# =========================================================
def main():
    # ------------------------- HEADER -------------------------
    col_logo, col_text = st.columns([1, 3])
    with col_logo:
        # Assuming asset exists
        if "assets/Sticker.png" and os.path.exists("assets/Sticker.png"):
             st.image("assets/Sticker.png", width="stretch")
        else:
             st.write("🛠️") # Fallback if image missing

    with col_text:
        st.markdown("""
        <h1 style="color: #FFFFFF; font-size:60px; margin-bottom:6px;">MHF Civil Calc</h1>
        <p style="color: #E2E8F0; font-size:18px; line-height:1.5; max-width:700px;">
            Civil Engineering Calculation Workspace
        </p>
        <p style="color: #E2E8F0; font-size:14px; max-width:700px;">
            Verified numerical solvers aligned with standard undergraduate civil engineering coursework.
        </p>
        """, unsafe_allow_html=True)

    st.markdown("") 

    # ------------------------- MODULES -------------------------
    st.markdown('<h3 style="color: #E2E8F0;">Available Course Calculators</h3>', unsafe_allow_html=True)
    st.markdown("")
    modules = get_active_modules()
    if modules:
        cols = st.columns(4)
        for idx, (file, title) in enumerate(modules):
            with cols[idx % 4]:
                st.page_link(f"pages/{file}", label=title, width="stretch")
                st.markdown("")

    # ------------------------- PURPOSE -------------------------
    st.markdown(
        '<h3 style="color: #E2E8F0;">Purpose</h3>', 
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p style="color: #E2E8F0;">'
        f'MHF Civil provides transparent numerical solutions to standard civil engineering problems. '
        f'Each module follows established theory, clearly states assumptions, and presents intermediate '
        f'steps to support learning, verification, and exam preparation.'
        f'</p>', 
        unsafe_allow_html=True
    )

    # ------------------------- FEEDBACK -------------------------
    st.markdown('<h3 style="color: #E2E8F0;">Feedback</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #E2E8F0;">If you identify an incorrect result, unclear assumption, or missing topic, your feedback helps improve the reliability of this platform.</p>', unsafe_allow_html=True)
    
    st.link_button(
        "Open Feedback Form",
        "https://docs.google.com/forms/d/e/1FAIpQLSfKtE2MK_2JZxEK4SzyjEhjdb8PKEC8-dN5az82MaIoPZzMsg/viewform",
        width="stretch"
    )

    # ------------------------- ABOUT -------------------------
    st.markdown('<h3 style="color: #E2E8F0;">About</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #E2E8F0;"><strong>Developed by Muhammad Hammad Faisal</strong> Final-Year Civil Engineering Student, METU</p>', unsafe_allow_html=True)
    
    st.link_button(
        "LinkedIn Profile",
        "https://www.linkedin.com/in/muhammad-hammad-20059a229",
        width="stretch"
    )

    # ------------------------- FOOTER -------------------------
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color: #E2E8F0; font-size:12px;">
        © 2026 MHF Civil · Ankara, Turkey
    </div>
    """, unsafe_allow_html=True)

# =========================================================
if __name__ == "__main__":
    main()



