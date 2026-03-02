"""
Concession Advisor -- AI-powered chat interface for Victoria Royals concession intelligence.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Concession Advisor", page_icon="\U0001f916", layout="wide")

# --- Advisor styling: distinct from other pages ---
st.markdown("""
<style>
    /* Advisor page background accent */
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f0eef5 100%);
    }

    /* Chat message styling */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4B0082 0%, #2D004F 100%);
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* Tool expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f6ff;
        border-left: 3px solid #FFD700;
    }

    /* Hide default hamburger & footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Starter button styling */
    div.stButton > button {
        background: linear-gradient(135deg, #f8f6ff 0%, #ede7f6 100%);
        border: 1px solid #4B0082;
        border-left: 4px solid #FFD700;
        color: #4B0082;
        text-align: left;
        padding: 12px 16px;
        border-radius: 8px;
        width: 100%;
        font-size: 0.9rem;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #ede7f6 0%, #d1c4e9 100%);
        border-color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <h1 style="color:#FFD700 !important; margin-bottom:0;">\U0001f3d2 Victoria Royals</h1>
        <p style="color:#CCCCCC !important; font-size:0.9rem;">Concession Intelligence Platform</p>
    </div>
    <hr style="border-color: #FFD700;">
    """, unsafe_allow_html=True)

    st.markdown("### \U0001f916 Advisor Settings")
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

# --- Title ---
st.title("\U0001f916 Concession Advisor")
st.markdown(
    "Ask me anything about Victoria Royals concession operations. "
    "I can query the database, forecast demand, build prep sheets, and recommend product bundles."
)
st.markdown("---")

# --- Session State ---
if "advisor_messages" not in st.session_state:
    st.session_state.advisor_messages = []  # API message format
if "advisor_display" not in st.session_state:
    st.session_state.advisor_display = []   # Display format: (role, content, tool_calls)

# --- Starter Prompts ---
if not st.session_state.advisor_display:
    st.markdown("#### Try asking:")
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
for role, content, tool_calls in st.session_state.advisor_display:
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


def _run_advisor(user_prompt: str):
    """Send a user message to the advisor and display the response."""
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Please enter your Anthropic API key in the sidebar to use the Advisor.")
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


# --- Handle pending prompt from starter buttons ---
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt
    _run_advisor(prompt)

# --- Chat Input ---
if user_input := st.chat_input("Ask about concessions, game prep, revenue opportunities..."):
    _run_advisor(user_input)
