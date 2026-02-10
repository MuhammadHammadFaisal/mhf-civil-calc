import streamlit as st

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* ===== BLUEPRINT BACKGROUND ===== */
    .stApp {
        background-color: #0b2a45;
        background-image:
            radial-gradient(circle at 50% 20%, rgba(255,255,255,0.10), transparent 55%),
            radial-gradient(circle at 20% 80%, rgba(255,255,255,0.08), transparent 60%),
            linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px),
            linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
        background-size:
            100% 100%,
            100% 100%,
            24px 24px,
            24px 24px,
            120px 120px,
            120px 120px;
        background-attachment: fixed;
    }

    /* ===== TEXT COLOR (SCOPED – DOES NOT AFFECT STREAMLIT UI) ===== */
    section[data-testid="stMain"] h1,
    section[data-testid="stMain"] h2,
    section[data-testid="stMain"] h3,
    section[data-testid="stMain"] h4,
    section[data-testid="stMain"] h5,
    section[data-testid="stMain"] h6,
    section[data-testid="stMain"] p,
    section[data-testid="stMain"] li,
    section[data-testid="stMain"] span {
        color: #eef3f8;
    }

    section[data-testid="stMain"] a {
        color: #a8d6ff;
    }

    /* ===== CARD STYLE ===== */
    .card {
        background: rgba(255,255,255,0.92);
        color: #212529;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        height: 100%;
    }

    .card h4 {
        color: #212529;
        margin-bottom: 0.5rem;
    }

    .card p {
        color: #212529;
        font-size: 0.95rem;
    }

    /* Remove default padding at top */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# APP CONTENT
# -------------------------------------------------
st.title("MHF Civil Calc")

st.markdown(
    """
    A lightweight civil engineering toolkit designed with a **blueprint-inspired interface**  
    for clarity, precision, and professional presentation.
    """
)

st.markdown("---")

# -------------------------------------------------
# GRID SECTION
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="card">
            <h4>📘 Course Modules</h4>
            <p>
            Structural design tools, reinforced concrete calculators,
            and civil engineering learning modules.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h4>🎯 Purpose</h4>
            <p>
            To provide fast, reliable calculations while maintaining
            professional engineering aesthetics.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="card">
            <h4>💬 Feedback</h4>
            <p>
            Your suggestions help improve accuracy, usability,
            and future feature development.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

st.markdown(
    """
    <small>
    © 2026 MHF Civil Calc — Designed for engineers who value precision.
    </small>
    """,
    unsafe_allow_html=True
)
