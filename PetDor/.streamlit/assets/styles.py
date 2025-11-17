# styles.py
import streamlit as st

def carregar_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    :root {
        --pd-bg: #0F172A;
        --pd-panel: #0B1220;
        --pd-accent: #7DD3FC;
        --pd-accent-2: #60A5FA;
        --pd-text: #E6EEF8;
        --pd-muted: #94A3B8;
        --pd-success: #34D399;
        --pd-warning: #FBBF24;
        --pd-radius: 12px;
    }

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        color: var(--pd-text);
        background-color: var(--pd-bg);
    }

    .petdor-card {
        background: linear-gradient(180deg, var(--pd-panel), #071026);
        border-radius: var(--pd-radius);
        padding: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        color: var(--pd-text);
    }

    .petdor-cta > button, .stButton>button.petdor-cta {
        background: linear-gradient(90deg, var(--pd-accent), var(--pd-accent-2)) !important;
        color: #021124 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-weight: 600;
        width: 100% !important;
    }

    .muted { color: var(--pd-muted); }

    /* Responsividade extra: garante largura total em telas pequenas */
    @media (max-width: 640px) {
        .petdor-card { padding: 14px; }
        .stMarkdown p { font-size: 0.95rem; }
    }

    /* Small helper for compact metrics */
    .compact-metric { font-size: 0.9rem; color:var(--pd-muted); }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
