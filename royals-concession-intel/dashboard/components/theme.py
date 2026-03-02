"""
Single source of truth for all dashboard styling.
Dark sports-analytics theme with Royals purple & gold accents.
"""
import streamlit as st

# ── Design tokens ─────────────────────────────────────────────────────────────
BG_PRIMARY = "#0d1117"
BG_SECONDARY = "#161b22"
BG_CARD = "#1c2333"
PURPLE = "#7c3aed"
PURPLE_DARK = "#4B0082"
GOLD = "#FFD700"
GOLD_DIM = "#b8960c"
TEXT_PRIMARY = "#e6edf3"
TEXT_SECONDARY = "#8b949e"
BORDER_SUBTLE = "rgba(255,255,255,0.08)"
SUCCESS = "#2ea043"
WARNING = "#d29922"
ERROR = "#f85149"


def apply_theme():
    """Inject all global CSS. Call once from app.py after set_page_config."""
    st.markdown("""
    <style>
        /* ── Global dark overrides ─────────────────────────────── */
        .stApp {
            background-color: #0d1117 !important;
        }

        /* ── Hide sidebar completely ───────────────────────────── */
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }

        /* ── Headers ───────────────────────────────────────────── */
        h1 { color: #FFD700 !important; font-weight: 800 !important; }
        h2, h3 { color: #e6edf3 !important; font-weight: 700 !important; }
        h4, h5, h6 { color: #8b949e !important; }

        /* ── Metric cards ──────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: #1c2333;
            border: 1px solid rgba(255,255,255,0.08);
            border-left: 4px solid #FFD700;
            padding: 14px 18px;
            border-radius: 10px;
        }
        [data-testid="stMetric"] label {
            color: #8b949e !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #e6edf3 !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {
            color: #2ea043 !important;
        }

        /* ── Tabs ──────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background: #161b22;
            border-radius: 8px;
            padding: 4px;
            gap: 4px;
        }
        .stTabs [data-baseweb="tab-list"] button {
            color: #8b949e !important;
            border-radius: 6px;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background: #1c2333 !important;
            color: #FFD700 !important;
            border-bottom-color: #FFD700 !important;
        }

        /* ── Dataframes ────────────────────────────────────────── */
        [data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
        }

        /* ── Dividers ──────────────────────────────────────────── */
        hr { border-color: rgba(255,255,255,0.08) !important; }

        /* ── Gold accent dividers ──────────────────────────────── */
        .gold-divider {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #FFD700, transparent);
            margin: 1.5rem 0;
        }

        /* ── Selectbox / Input styling ─────────────────────────── */
        [data-baseweb="select"] {
            background: #1c2333 !important;
        }
        .stSelectbox label, .stSlider label, .stToggle label,
        .stRadio label, .stTextInput label, .stNumberInput label {
            color: #8b949e !important;
            font-weight: 600 !important;
        }

        /* ── streamlit-option-menu horizontal nav ──────────────── */
        .nav-link {
            color: #8b949e !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
        }
        .nav-link.active, .nav-link:hover {
            color: #FFD700 !important;
        }

        /* ── Containers / bordered containers ──────────────────── */
        [data-testid="stExpander"] {
            background: #161b22;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
        }

        /* ── Chat messages (Advisor) ───────────────────────────── */
        [data-testid="stChatMessage"] {
            background: #161b22 !important;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 8px;
        }

        /* ── Buttons ───────────────────────────────────────────── */
        .stButton > button {
            background: #1c2333 !important;
            color: #e6edf3 !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 8px !important;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            border-color: #FFD700 !important;
            color: #FFD700 !important;
        }

        /* ── Download button ───────────────────────────────────── */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #7c3aed, #4B0082) !important;
            color: white !important;
            border: none !important;
        }
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #9b5de5, #6A0DAD) !important;
        }

        /* ── Animations ────────────────────────────────────────── */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.3); }
            50% { box-shadow: 0 0 20px 4px rgba(255, 215, 0, 0.15); }
        }
        .fade-in { animation: fadeIn 0.5s ease-out; }
        .pulse { animation: pulse 2s ease-in-out infinite; }

        /* ── Hide default hamburger & footer ───────────────────── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* ── Info/warning/error boxes ──────────────────────────── */
        [data-testid="stAlert"] {
            background: #161b22 !important;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
        }

        /* ── Spinner ───────────────────────────────────────────── */
        .stSpinner > div > div {
            border-top-color: #FFD700 !important;
        }

        /* ── Container with border ─────────────────────────────── */
        [data-testid="stVerticalBlock"] > div:has(> [data-testid="stVerticalBlockBorderWrapper"]) {
            background: #161b22;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a consistent page header with gold accent."""
    icon_html = f'<span style="font-size:1.8rem; margin-right:8px;">{icon}</span>' if icon else ""
    sub_html = f'<p style="color:#8b949e; font-size:1rem; margin:4px 0 0 0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="fade-in" style="margin-bottom: 1.5rem;">
        <div style="display:flex; align-items:center;">
            {icon_html}
            <h1 style="margin:0; font-size:2rem;">{title}</h1>
        </div>
        {sub_html}
        <div class="gold-divider"></div>
    </div>
    """, unsafe_allow_html=True)


def dark_card(html: str, accent_color: str = GOLD):
    """Render content in a styled dark card with accent border."""
    st.markdown(f"""
    <div style="
        background: {BG_CARD};
        border: 1px solid {BORDER_SUBTLE};
        border-left: 4px solid {accent_color};
        border-radius: 10px;
        padding: 20px 24px;
        margin: 12px 0;
    ">
        {html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = ""):
    """Render a section header with subtle styling."""
    sub_html = f'<span style="color:#8b949e; font-size:0.85rem; margin-left:12px;">{subtitle}</span>' if subtitle else ""
    st.markdown(f"""
    <div style="margin: 1.5rem 0 0.8rem 0;">
        <h3 style="margin:0; display:inline;">{title}</h3>{sub_html}
    </div>
    """, unsafe_allow_html=True)
