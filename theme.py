import streamlit as st
from PIL import Image
import os

def prepare_icon(im, final_size=64):
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    return new_im.resize((final_size, final_size), Image.LANCZOS)

def load_icon():
    try:
        icon_path = os.path.join("assets", "Sticker.png")
        icon_img = Image.open(icon_path).convert("RGBA")
        return prepare_icon(icon_img, 64)
    except:
        return "🛠️"

def apply_theme(page_title="MHF Civil Calc"):
    # Must be the very first Streamlit command called on the page
    st.set_page_config(page_title=page_title, layout="wide", page_icon=load_icon())

    st.markdown("""
    <style>
    /* 1. Hide Default Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 2. Blueprint Background */
    [data-testid="stAppViewContainer"] {
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
        background-attachment: local;
    }

    /* 3. Sidebar and Global Text */
    [data-testid="stSidebar"] {
        background-color: #031126;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3, h4, p, li, .stMarkdown {
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
    .glass-table-wrapper table {
        width: 100% !important;
        background-color: rgba(0, 0, 0, 0.35) !important;
        color: #E0E0E0 !important;
        border-collapse: collapse !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        margin-bottom: 20px !important;
        border: none !important;
    }
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
# BULLETPROOF GLASS TABLE
# =========================================================
def glass_table(df):
    # Convert dataframe to HTML without the index
    html_table = df.to_html(index=False, escape=False)
    
    # Wrap it in a scrollable glassmorphism container
    custom_html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        overflow-x: auto; /* THIS ADDS THE HORIZONTAL SCROLLBAR */
        width: 100%;
    ">
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            /* Prevent text from stacking on top of itself */
            th, td {{ white-space: nowrap; padding: 8px 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        </style>
        {html_table}
    </div>
    """
    st.markdown(custom_html, unsafe_allow_html=True)
