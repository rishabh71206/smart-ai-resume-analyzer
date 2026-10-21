"""
Smart AI Resume Analyzer & Interview Bot
Main Streamlit application entry point.
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, APP_LAYOUT, GEMINI_API_KEY

# ── Page config — MUST be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Main background */
.stApp { background-color: #f0f4f8; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a5f 0%, #2563eb 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stCheckbox label { color: white !important; }

/* Cards */
div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: white;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    font-weight: 500;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600;
    background: white;
    border-radius: 8px;
}

h1 { color: #1e3a5f; }
h2, h3 { color: #2563eb; }
</style>
""", unsafe_allow_html=True)

# ── Import pages ──────────────────────────────────────────────────────────────
from pages import resume_analyzer, interview_bot, career_advisor, tips_resources

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"# {APP_ICON} {APP_TITLE}")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "📄 Resume Analyzer",
            "🤖 Interview Bot",
            "🚀 Career Advisor",
            "📚 Tips & Resources",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API key status
    if GEMINI_API_KEY:
        st.success("✅ Gemini API Connected")
    else:
        st.error("❌ Gemini API Key Missing")
        st.markdown("""
**To set up:**
1. Get a free key at [Google AI Studio](https://aistudio.google.com/)
2. Create a `.env` file in the project root
3. Add: `GEMINI_API_KEY=your_key_here`
4. Restart the app
""")

    st.markdown("---")
    st.markdown("""
<small>
<b>Smart AI Resume Analyzer</b><br>
Powered by Google Gemini AI<br><br>
© 2024 – Built with Streamlit & Python
</small>
""", unsafe_allow_html=True)

# ── Render selected page ──────────────────────────────────────────────────────
if page == "📄 Resume Analyzer":
    resume_analyzer.render()
elif page == "🤖 Interview Bot":
    interview_bot.render()
elif page == "🚀 Career Advisor":
    career_advisor.render()
elif page == "📚 Tips & Resources":
    tips_resources.render()
