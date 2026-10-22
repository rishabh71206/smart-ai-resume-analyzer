"""
Smart AI Resume Analyzer & Interview Bot
Main Streamlit application entry point.
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, APP_LAYOUT, GEMINI_API_KEY

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# ── Theme toggle ──────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# ── CSS ───────────────────────────────────────────────────────────────────────
dark = st.session_state["dark_mode"]

bg_color     = "#1a1a2e" if dark else "#ffffff"
text_color   = "#ffffff" if dark else "#111111"
card_bg      = "#16213e" if dark else "#f8fafc"
border_color = "#0f3460" if dark else "#e2e8f0"
sub_text     = "#a0aec0" if dark else "#444444"

st.markdown(f"""
<style>
/* Main */
.stApp {{ background-color: {bg_color} !important; }}

/* All text */
.stApp, .stApp p, .stApp div, .stApp span,
.stApp label, .stMarkdown p, .stMarkdown li {{
    color: {text_color} !important;
}}

/* Headings */
h1 {{ color: {'#60a5fa' if dark else '#1e3a5f'} !important; font-weight: 800 !important; }}
h2 {{ color: {'#60a5fa' if dark else '#1e3a5f'} !important; font-weight: 700 !important; }}
h3 {{ color: {'#93c5fd' if dark else '#2563eb'} !important; font-weight: 600 !important; }}

/* Labels */
.stFileUploader label, .stTextInput label,
.stTextArea label, .stSelectbox label,
.stSlider label, .stMultiSelect label,
.stCheckbox label, .stRadio label {{
    color: {text_color} !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}}

/* Input boxes */
.stTextInput input, .stTextArea textarea {{
    background-color: {card_bg} !important;
    color: {text_color} !important;
    border: 1px solid {border_color} !important;
}}

/* Metric cards */
div[data-testid="metric-container"] {{
    background: {card_bg} !important;
    border: 1px solid {border_color} !important;
    border-radius: 10px !important;
    padding: 10px !important;
}}
div[data-testid="metric-container"] label {{
    color: {sub_text} !important;
    font-weight: 600 !important;
}}
div[data-testid="metric-container"] div {{
    color: {text_color} !important;
    font-weight: 700 !important;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {'linear-gradient(180deg, #0f3460 0%, #16213e 100%)' if dark else 'linear-gradient(180deg, #1e3a5f 0%, #2563eb 100%)'} !important;
}}
[data-testid="stSidebar"] * {{ color: white !important; }}

/* Buttons */
.stButton > button[kind="primary"] {{
    background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}}
.stButton > button {{
    color: {text_color} !important;
    background: {card_bg} !important;
    border: 1px solid {border_color} !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: {card_bg} !important;
    border-radius: 8px !important;
    padding: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {text_color} !important;
    font-weight: 600 !important;
}}

/* Alert boxes */
.stAlert p {{ color: #111111 !important; }}

/* Expander */
.streamlit-expanderHeader {{
    color: {text_color} !important;
    font-weight: 700 !important;
    background: {card_bg} !important;
}}

/* Select boxes */
.stSelectbox div[data-baseweb="select"] {{
    background: {card_bg} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Import pages ──────────────────────────────────────────────────────────────
from pages import (resume_analyzer, interview_bot, career_advisor,
                   tips_resources, chatbot, job_recommendations,
                   resume_comparison, resume_builder)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"# {APP_ICON} Smart AI")
    st.markdown("### Resume Analyzer & Bot")
    st.markdown("---")

    # Dark/Light mode toggle
    mode_label = "☀️ Light Mode" if dark else "🌙 Dark Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state["dark_mode"] = not dark
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "📄 Resume Analyzer",
            "🤖 Interview Bot",
            "🚀 Career Advisor",
            "💬 AI Chatbot",
            "🎯 Job Recommendations",
            "👥 Resume Comparison",
            "🎨 Resume Builder",
            "📚 Tips & Resources",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API key status
    if GEMINI_API_KEY:
        st.success("✅ AI Connected")
    else:
        st.error("❌ API Key Missing")
        st.markdown("Add `GEMINI_API_KEY` in Streamlit Secrets!")

    st.markdown("---")
    st.markdown("""
<small>
<b>Smart AI Resume Analyzer</b><br>
Powered by Google Gemini AI<br>
© 2024 – Built with Python
</small>
""", unsafe_allow_html=True)

# ── Render page ───────────────────────────────────────────────────────────────
if page == "📄 Resume Analyzer":
    resume_analyzer.render()
elif page == "🤖 Interview Bot":
    interview_bot.render()
elif page == "🚀 Career Advisor":
    career_advisor.render()
elif page == "💬 AI Chatbot":
    chatbot.render()
elif page == "🎯 Job Recommendations":
    job_recommendations.render()
elif page == "👥 Resume Comparison":
    resume_comparison.render()
elif page == "🎨 Resume Builder":
    resume_builder.render()
elif page == "📚 Tips & Resources":
    tips_resources.render()
