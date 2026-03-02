"""
KPI card components -- dark theme styling.
"""
import streamlit as st


def kpi_card(label: str, value: str, delta=None, delta_color: str = "normal"):
    """Render a single metric card."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def kpi_row(metrics: list[dict]):
    """
    Render a row of KPI cards.
    Each dict: {"label": str, "value": str, "delta": str|None, "delta_color": str}
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            kpi_card(
                label=m["label"],
                value=m["value"],
                delta=m.get("delta"),
                delta_color=m.get("delta_color", "normal"),
            )


def business_impact_callout(text: str, icon: str = "\U0001f4a1"):
    """Render a prominent callout box with gold border on dark background."""
    st.markdown(f"""
    <div style="
        background: #1c2333;
        border: 2px solid #FFD700;
        border-left: 6px solid #FFD700;
        border-radius: 10px;
        padding: 20px 24px;
        margin: 16px 0;
        font-size: 1.05rem;
    ">
        <span style="font-size:1.4rem;">{icon}</span>&nbsp;
        <strong style="color:#FFD700;">Business Impact:</strong>
        <span style="color:#e6edf3;">{text}</span>
    </div>
    """, unsafe_allow_html=True)
