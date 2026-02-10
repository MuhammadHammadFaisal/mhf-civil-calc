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
    icon_img = "🛠️"  # fallback emoji

# =========================================================
# App Config
# =========================================================
st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
    page_icon=icon_img
)

# =========================================================
# CSS: Blueprint Background + Framed Content + Cards + Text Colors
# =========================================================
st.markdown("""
<style>
/* ===== Blueprint: Framed with Clean Margins ===== */
.stApp {
    background-color: #031126; /* Deep Navy Base */
    background-image: 
        /* === 1. THE FRAME (Solid Navy Margins + White Border Lines) === */
        /* These layers sit ON TOP of the grid to hide it at the edges */
        
        /* Left Margin: Solid Navy until 40px, then 3px White Line */
        linear-gradient(to right, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 43px, transparent 43px),
        
        /* Right Margin: Solid Navy from right edge */
        linear-gradient(to left, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 43px, transparent 43px),
        
        /* Top Margin: Solid Navy from top */
        linear-gradient(to bottom, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 43px, transparent 43px),
        
        /* Bottom Margin: Solid Navy from bottom */
        linear-gradient(to top, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 43px, transparent 43px),

        /* === 2. Technical Arcs (Behind the frame) === */
        radial-gradient(circle at 100% 0%, transparent 180px, rgba(255,255,255,0.05) 181px, transparent 183px),
        radial-gradient(circle at 0% 100%, transparent 200px, rgba(255,255,255,0.05) 201px, transparent 203px),
        
        /* === 3. Major Grid (75px - Zoomed Out) === */
        linear-gradient(rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
        
        /* === 4. Fine Sub-Grid (15px - Zoomed Out) === */
        linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
        
        /* === 5. Center Glow === */
        radial-gradient(circle at center, rgba(20, 75, 150, 0.4) 0%, #031126 90%);

    background-size: 
        100% 100%, 100% 100%, 100% 100%, 100% 100%, /* Frame Borders */
        100% 100%, 100% 100%,                       /* Arcs */
        75px 75px, 75px 75px,                       /* Major Grid */
        15px 15px, 15px 15px,                       /* Sub Grid */
        100% 100%;                                  /* Glow */
    
    /* Lock the background in place */
    background-attachment: fixed;
}

/* ===== Glassy Card Styling (Unchanged) ===== */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    backdrop-filter: blur(4px);
}

[data-testid="stPageLink-NavLink"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ===== Glassy Card Styling (Unchanged) ===== */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    backdrop-filter: blur(4px);
}

[data-testid="stPageLink-NavLink"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
/* ===== Glassy Card Styling (Kept for consistency) ===== */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    backdrop-filter: blur(4px);
}

[data-testid="stPageLink-NavLink"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ===== Glassy Card Styling ===== */
[data-testid="stPageLink-NavLink"] {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    backdrop-filter: blur(4px);
}

[data-testid="stPageLink-NavLink"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
/* ===== Framed Content Area ===== */
main > div:first-child {
    max-width: 1200px;
    margin: 30px auto;
    padding: 30px 40px;
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    background-color: rgba(26,58,90,0.5);
    box-shadow: 0 0 30px rgba(0,0,0,0.2);
    color: #E2E8F0 !important; 
}

/* Force all text inside content to be the requested color */
main > div:first-child, main > div:first-child * {
    color: #E2E8F0 !important; 
}

/* ===== Card Styling (Course Modules) ===== */
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

/* Keep card text dark so it is readable on white background */
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

/* ===== Button Styling (Feedback & LinkedIn) ===== */
/* This section fixes the invisible text issue */
[data-testid="stLinkButton"] > a {
    background-color: rgba(255, 255, 255, 0.9) !important;
    color: #1a3a5a !important; /* Dark blue text */
    border: 1px solid #dee2e6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stLinkButton"] > a:hover {
    background-color: #ffffff !important;
    border-color: #aad4ff !important;
    box-shadow: 0 0 10px rgba(170, 212, 255, 0.5) !important;
    color: #1a3a5a !important;
}

/* Optional: Standard text link styling (if any exist outside buttons) */
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
             st.image("assets/Sticker.png", use_container_width=True)
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
    st.markdown('<h3 style="color: #E2E8F0;">Course Modules</h3>', unsafe_allow_html=True)
    st.markdown("")
    modules = get_active_modules()
    if modules:
        cols = st.columns(3)
        for idx, (file, title) in enumerate(modules):
            with cols[idx % 3]:
                st.page_link(f"pages/{file}", label=title, use_container_width=True)
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
        use_container_width=True
    )

    # ------------------------- ABOUT -------------------------
    st.markdown('<h3 style="color: #E2E8F0;">About</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #E2E8F0;"><strong>Developed by Muhammad Hammad Faisal</strong> Final-Year Civil Engineering Student, METU</p>', unsafe_allow_html=True)
    
    st.link_button(
        "LinkedIn Profile",
        "https://www.linkedin.com/in/muhammad-hammad-20059a229"
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














