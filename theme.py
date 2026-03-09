import streamlit as st
from PIL import Image
import os
def inject_ga():
    GA_ID = "G-3NKWXNDFY7"
    st.markdown(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
        </script>
        """,
        unsafe_allow_html=True
    )

def prepare_icon(im, final_size=64):
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    return new_im.resize((final_size, final_size), Image.LANCZOS)

def load_icon():
    try:
        if ICON_PATH.is_file():
            icon_img = Image.open(ICON_PATH).convert("RGBA")
            return prepare_icon(icon_img, 64)
        return "🛠️"
    except Exception:
        return "🛠️"

def apply_theme(page_title="MHF Civil Calc"):
    # Must be the very first Streamlit command called on the page
    st.set_page_config(page_title=page_title, layout="wide",page_icon=load_icon())

    st.markdown("""
    <style>
    /* 1. Hide Default Streamlit Branding */
    /* Keep Streamlit header visible (sidebar toggle + settings live here) */
    header {visibility: visible;}

    /* Optional: hide footer only */
    html, body, .stApp {
        height: 100%;
    }

    /* 2. Blueprint Background */
    /* Blueprint background should follow full-page scroll */
    .stApp,
    [data-testid="stAppViewContainer"] {
        /* keep your same background-color + background-image + sizes etc */

        background-color: #031126;
        background-image: 
            linear-gradient(to bottom, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 42px, transparent 42px),
            radial-gradient(circle at 50% 40vh, rgba(20, 75, 150, 0.4) 0%, transparent 70%),
            linear-gradient(rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
            linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            radial-gradient(circle at 100% 0%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
            radial-gradient(circle at 100% 0%, transparent 220px, rgba(255,255,255,0.05) 221px, transparent 222px),
            radial-gradient(circle at 0% 100%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
            radial-gradient(circle at 0% 100%, transparent 50px, rgba(255,255,255,0.15) 51px, transparent 53px);
        background-size: 100% 100%, 100% 100%, 75px 75px, 75px 75px, 15px 15px, 15px 15px, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
        background-repeat: no-repeat, no-repeat, repeat, repeat, repeat, repeat, no-repeat, no-repeat, no-repeat, no-repeat;
        background-attachment: scroll;
        background-position: 0 0;
    }

    /* 3. Sidebar and Global Text */
    [data-testid="stSidebar"] {
        background-color: #031126;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3, h4, p, li {
        color: #E2E8F0 !important;
    }

    /* 4. Glassy Cards and Links */
    [data-testid="stPageLink-NavLink"] {
        background-color: rgba(255,255,255,0.85) !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
        padding: 18px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    [data-testid="stPageLink-NavLink"] p {
        color: #212529 !important; 
        font-size: 17px !important;
        font-weight: 600 !important;
        text-align: center !important;
        width: 100% !important;
    }
    [data-testid="stPageLink-NavLink"] svg, [data-testid="stHeaderAction"] {
        display: none !important;
    }
    
    /* 5. Buttons */
    [data-testid="stLinkButton"] > a {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
    }
    [data-testid="stLinkButton"] > a, [data-testid="stLinkButton"] > a * {
        color: #1a3a5a !important; 
    }

    /* =========================================
       BULLETPROOF GLASS TABLES
       ========================================= */
    
    .glass-table-wrapper th {
        background-color: rgba(0, 0, 0, 0.5) !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        padding: 12px 15px !important;
        border: none !important;
    }
    .glass-table-wrapper td {
        padding: 12px 15px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        color: #E0E0E0 !important;
    }
    .glass-table-wrapper tbody tr:hover td {
        background-color: rgba(255, 255, 255, 0.08) !important;
    }
    /* 3b. Framed Content Area (global) */
    main > div:first-child {
        max-width: 1200px;
        margin: 30px auto;
        padding: 30px 40px;
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        background-color: rgba(26,58,90,0.5);
        box-shadow: 0 0 30px rgba(0,0,0,0.2);
    }
    
    /* Optional: Standard text link styling */
    a {
        color: #aad4ff !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    /* =========================
       PRINT FIX (Chrome multi-page PDF)
       ========================= */
    @media print {
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
    
      /* Remove container backgrounds so they don't cover the print layer */
      .stApp,
      [data-testid="stAppViewContainer"],
      [data-testid="stSidebar"],
      main {
        background: transparent !important;
        background-color: transparent !important;
      }
    
      /* Repeating background for ALL printed pages */
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
    
        background-color: #031126;
        background-image:
          linear-gradient(to bottom, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 42px, transparent 42px),
          radial-gradient(circle at 50% 40vh, rgba(20, 75, 150, 0.35) 0%, transparent 70%),
          linear-gradient(rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
          linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
          linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
          radial-gradient(circle at 100% 0%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
          radial-gradient(circle at 100% 0%, transparent 220px, rgba(255,255,255,0.05) 221px, transparent 222px),
          radial-gradient(circle at 0% 100%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
          radial-gradient(circle at 0% 100%, transparent 50px, rgba(255,255,255,0.15) 51px, transparent 53px);
    
        background-size:
          100% 100%,
          100% 100%,
          75px 75px, 75px 75px,
          15px 15px, 15px 15px,
          100% 100%, 100% 100%,
          100% 100%, 100% 100%;
    
        background-repeat:
          no-repeat, no-repeat,
          repeat, repeat,
          repeat, repeat,
          no-repeat, no-repeat,
          no-repeat, no-repeat;
    
        background-position: 0 0;
      }
    
      /* Optional: remove the framed box for print */
      main > div:first-child {
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
      }
    }
    /* Make st.container(border=True) look like glass */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 16px 16px !important;
        backdrop-filter: blur(6px) !important;
    }
        
    </style>
    """, unsafe_allow_html=True)

def render_page_header(title):
    col_logo, col_text = st.columns([1, 5], vertical_alignment="center")
    with col_logo:
        try:
            st.image(os.path.join("assets", "Sticker.png"))
        except:
            pass 
    with col_text:
        st.markdown(
            f"""
            <div style="padding-left: 15px;">
                <h1 style='font-size: 55px; margin: 0; line-height: 1.0; font-weight: 700;'>{title}</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

# =========================================================
# TYPOGRAPHY REGISTRY
# =========================================================

TEXT_STYLES = {
    "page_title": {"size": "42px", "weight": "800", "color": "#FFFFFF", "margin": "0px 0px 20px 0px"},
    "section_header": {"size": "24px", "weight": "700", "color": "#FFFFFF", "margin": "25px 0px 15px 0px"},
    "subheader": {"size": "20px", "weight": "600", "color": "#E2E8F0", "margin": "15px 0px 10px 0px"},
    "body": {"size": "16px", "weight": "400", "color": "#CBD5E1", "margin": "5px 0px 10px 0px"},
    "caption": {"size": "14px", "weight": "400", "color": "#94A3B8", "margin": "0px 0px 15px 0px", "font-style": "italic"},
    "math_log": {"size": "15px", "weight": "500", "color": "#FDE047", "margin": "8px 0px 4px 0px"}
}

def write_text(text_type, content):
    style = TEXT_STYLES.get(text_type, TEXT_STYLES["body"]) 
    font_style = style.get("font-style", "normal")
    html = f"""
    <div style="font-size: {style['size']}; font-weight: {style['weight']}; color: {style['color']}; margin: {style['margin']}; font-style: {font_style};">
        {content}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# =========================================================
# BULLETPROOF GLASS BOX
# =========================================================
def glass_box(content):
    """
    Uses inline styling to guarantee Streamlit renders the dark glassy background.
    Flattened to strictly prevent Markdown from treating indented HTML as code blocks.
    
    WARNING: Do NOT place Streamlit widgets (st.button, st.text_input, etc.) inside this box. 
    It is strictly for text, warnings, or raw HTML/Markdown logs.
    """
    html = f"""<div style="background-color: rgba(0, 0, 0, 0.35); padding: 20px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.15); margin-bottom: 15px;">\n\n{content}\n\n</div>"""
    st.markdown(html, unsafe_allow_html=True)

# =========================================================
# BULLETPROOF GLASS TABLE (SCROLL FIXED)
# =========================================================
def glass_table(df):
    table_style = "width: 100%; min-width: 600px; background-color: rgba(0, 0, 0, 0.35); color: #E0E0E0; border-collapse: collapse; font-family: sans-serif;"
    th_style = "background-color: rgba(0, 0, 0, 0.5); font-weight: 600; color: #FFFFFF; padding: 12px 15px; text-align: left; border-bottom: 2px solid rgba(255,255,255,0.1); white-space: nowrap;"
    td_style = "padding: 12px 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: #E0E0E0; white-space: nowrap;"

    html = f"""
    <div style="
        overflow-x: auto; 
        display: block; 
        width: 100%; 
        border: 1px solid rgba(255, 255, 255, 0.15); 
        border-radius: 8px; 
        margin-bottom: 20px;
    ">
        <table style='{table_style}'>
    """

    # Headers
    html += "<thead><tr>"
    for col in df.columns:
        html += f"<th style='{th_style}'>{col}</th>"
    html += "</tr></thead><tbody>"

    # Rows
    for _, row in df.iterrows():
        html += "<tr>"
        for val in row:
            html += f"<td style='{td_style}'>{val}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"

    st.markdown(html, unsafe_allow_html=True)
