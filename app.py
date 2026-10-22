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
.stApp { background-color: #ffffff; }

/* All text dark */
.stApp, .stApp p, .stApp div, .stApp span, .stApp label {
    color: #111111 !important;
}

/* Headings */
h1 { color: #1e3a5f !important; font-weight: 800 !important; }
h2 { color: #1e3a5f !important; font-weight: 700 !important; }
h3 { color: #2563eb !important; font-weight: 600 !important; }

/* Paragraph text */
p, li, span {
    color: #111111 !important;
    font-size: 15px !important;
}

/* File uploader text */
.stFileUploader label, .stTextInput label,
.stTextArea label, .stSelectbox label,
.stSlider label, .stMultiSelect label,
.stCheckbox label, .stRadio label {
    color: #111111 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* Info/success/warning/error boxes */
.stAlert p { color: #111111 !important; }

/* Metric labels and values */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] label {
    color: #444444 !important;
    font-weight: 600 !important;
}
[data-testid="metric-container"] div {
    color: #111111 !important;
    font-weight: 700 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a5f 0%, #2563eb 100%);
}
[data-testid="stSidebar"] * { color: white !important; }

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 16px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f0f4f8;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    font-weight: 600 !important;
    color: #111111 !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 700 !important;
    color: #111111 !important;
}

/* Markdown text */
.stMarkdown p { color: #111111 !important; }
.stMarkdown li { color: #111111 !important; }
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
