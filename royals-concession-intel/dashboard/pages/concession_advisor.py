"""
Concession Advisor -- AI-powered chat interface for Victoria Royals concession intelligence.
Dark-theme router version.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import streamlit as st

from dashboard.components.theme import (
    page_header, dark_card, GOLD, TEXT_PRIMARY, TEXT_SECONDARY, BG_CARD,
)


# ---------------------------------------------------------------------------
# Gold divider helper
# ---------------------------------------------------------------------------
def _gold_divider():
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Suggested follow-up prompts based on context
# ---------------------------------------------------------------------------
def _get_follow_ups(last_response: str) -> list[str]:
    """Return 3 contextual follow-up suggestions based on the last response."""
    lower = last_response.lower()

    if any(w in lower for w in ["prep", "prepare", "staff", "game day"]):
        return [
            "What inventory quantities should we order for this game?",
            "Which stands should we open and how many staff per stand?",
            "What were sales like for similar past games?",
        ]
    elif any(w in lower for w in ["revenue", "per-cap", "benchmark", "gap"]):
        return [
            "What specific items could help close the per-cap gap?",
            "How does our revenue compare on weekends vs weekdays?",
            "What would a $2 per-cap improvement mean in total revenue?",
        ]
    elif any(w in lower for w in ["combo", "bundle", "deal", "promotion"]):
        return [
            "What price points work best for combo deals?",
            "Which items are most frequently purchased together?",
            "How have past promotions impacted revenue?",
        ]
    elif any(w in lower for w in ["stand", "location", "canteen", "bar"]):
        return [
            "What menu changes would you suggest for this stand?",
            "How does this stand compare to others on busy nights?",
            "What are the peak hours for this stand?",
        ]
    elif any(w in lower for w in ["forecast", "predict", "expect", "demand"]):
        return [
            "What factors have the biggest impact on demand?",
            "How accurate have past forecasts been?",
            "What should we prepare differently for playoff games?",
        ]
    else:
        return [
            "What are the top 3 revenue opportunities we should act on?",
            "Show me a prep sheet for our next home game.",
            "Which menu items have the highest profit margin?",
        ]


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def render():
    page_header(
        "Concession Advisor",
        "AI-powered strategic recommendations",
        "\U0001f916",
    )

    # --- Settings expander (replaces sidebar controls) ---
    with st.expander("Settings", expanded=False):
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.environ.get("ANTHROPIC_API_KEY", ""),
            help="Required for the AI advisor. Set ANTHROPIC_API_KEY env var or enter here.",
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.advisor_messages = []
            st.session_state.advisor_display = []
            st.rerun()

    _gold_divider()

    # --- Session State ---
    if "advisor_messages" not in st.session_state:
        st.session_state.advisor_messages = []  # API message format
    if "advisor_display" not in st.session_state:
        st.session_state.advisor_display = []   # Display format: (role, content, tool_calls)

    # --- Starter Prompts ---
    if not st.session_state.advisor_display:
        st.markdown("#### Try asking:")

        # Dark-theme styling for starter buttons
        st.markdown('''<style>
        div[data-testid="stHorizontalBlock"] .stButton > button {
            background: #1c2333 !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-left: 4px solid #FFD700 !important;
            color: #e6edf3 !important;
            text-align: left !important;
        }
        </style>''', unsafe_allow_html=True)

        cols = st.columns(3)
        starters = [
            "What should we prepare for Friday's game against Vancouver with 4,200 expected fans?",
            "Which stand has the biggest missed opportunity and what should we do about it?",
            "What combo deals would you recommend based on our sales data?",
        ]
        for i, (col, prompt) in enumerate(zip(cols, starters)):
            with col:
                if st.button(prompt, key=f"starter_{i}"):
                    st.session_state.pending_prompt = prompt
                    st.rerun()

    # --- Render Chat History ---
    for idx, (role, content, tool_calls) in enumerate(st.session_state.advisor_display):
        with st.chat_message(role):
            if tool_calls:
                for tc in tool_calls:
                    with st.expander(f"\U0001f527 Tool: {tc['name']}", expanded=False):
                        st.markdown("**Input:**")
                        st.json(tc["input"])
                        st.markdown("**Result:**")
                        result = tc["result"]
                        if isinstance(result, dict) and "rows" in result and len(result.get("rows", [])) > 10:
                            st.markdown(f"*{result.get('row_count', '?')} rows returned*")
                            st.json({k: v for k, v in result.items() if k != "rows"})
                            st.dataframe(
                                [dict(zip(result["columns"], row)) for row in result["rows"][:20]],
                                use_container_width=True,
                            )
                        else:
                            st.json(result)
            st.markdown(content)

        # Show follow-up suggestions after each assistant response
        if role == "assistant" and idx == len(st.session_state.advisor_display) - 1:
            follow_ups = _get_follow_ups(content)
            st.markdown(
                f'<p style="color:{TEXT_SECONDARY}; font-size:0.85rem; margin-top:8px;">'
                f'Suggested follow-ups:</p>',
                unsafe_allow_html=True,
            )
            fu_cols = st.columns(3)
            for fi, (fu_col, fu_prompt) in enumerate(zip(fu_cols, follow_ups)):
                with fu_col:
                    if st.button(fu_prompt, key=f"followup_{idx}_{fi}"):
                        st.session_state.pending_prompt = fu_prompt
                        st.rerun()

    # --- Run Advisor ---
    def _run_advisor(user_prompt: str):
        """Send a user message to the advisor and display the response."""
        # Check API key
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Please enter your Anthropic API key in the Settings expander to use the Advisor.")
            return

        # Add user message
        st.session_state.advisor_messages.append({"role": "user", "content": user_prompt})
        st.session_state.advisor_display.append(("user", user_prompt, []))

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Call advisor
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    from advisor.claude_advisor import chat

                    response_text, updated_messages, tool_calls = chat(
                        st.session_state.advisor_messages
                    )

                    # Display tool calls
                    if tool_calls:
                        for tc in tool_calls:
                            with st.expander(f"\U0001f527 Tool: {tc['name']}", expanded=False):
                                st.markdown("**Input:**")
                                st.json(tc["input"])
                                st.markdown("**Result:**")
                                result = tc["result"]
                                if isinstance(result, dict) and "rows" in result and len(result.get("rows", [])) > 10:
                                    st.markdown(f"*{result.get('row_count', '?')} rows returned*")
                                    st.json({k: v for k, v in result.items() if k != "rows"})
                                    st.dataframe(
                                        [dict(zip(result["columns"], row)) for row in result["rows"][:20]],
                                        use_container_width=True,
                                    )
                                else:
                                    st.json(result)

                    # Display response
                    st.markdown(response_text)

                    # Update state
                    st.session_state.advisor_messages = updated_messages
                    st.session_state.advisor_display.append(("assistant", response_text, tool_calls))

                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.advisor_display.append(("assistant", error_msg, []))

    # --- Handle pending prompt from starter / follow-up buttons ---
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt
        _run_advisor(prompt)

    # --- Chat Input ---
    if user_input := st.chat_input("Ask about concessions, game prep, revenue opportunities..."):
        _run_advisor(user_input)
