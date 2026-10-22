"""
Smart AI Resume Analyzer & Interview Bot
Main Streamlit application entry point.
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, GEMINI_API_KEY

st.set_page_config(
    page_title="Smart AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

dark = st.session_state["dark_mode"]

# ── Full Professional CSS ─────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif !important; }}

.stApp {{
    background: {'#0f172a' if dark else '#f8fafc'} !important;
}}

/* All text */
.stApp p, .stApp div, .stApp span, .stApp li,
.stMarkdown p, .stMarkdown li {{
    color: {'#e2e8f0' if dark else '#1e293b'} !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}}

/* Headings */
h1 {{
    color: {'#60a5fa' if dark else '#1e40af'} !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
}}
h2 {{
    color: {'#93c5fd' if dark else '#1e40af'} !important;
    font-weight: 700 !important;
}}
h3 {{
    color: {'#bfdbfe' if dark else '#2563eb'} !important;
    font-weight: 600 !important;
}}

/* Labels */
label, .stTextInput label, .stTextArea label,
.stSelectbox label, .stFileUploader label,
.stSlider label, .stMultiSelect label,
.stCheckbox label, .stRadio label {{
    color: {'#e2e8f0' if dark else '#1e293b'} !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}}

/* Input fields */
input, textarea {{
    background: {'#1e293b' if dark else '#ffffff'} !important;
    color: {'#e2e8f0' if dark else '#1e293b'} !important;
    border: 1.5px solid {'#334155' if dark else '#cbd5e1'} !important;
    border-radius: 8px !important;
}}

/* Metrics */
div[data-testid="metric-container"] {{
    background: {'#1e293b' if dark else '#ffffff'} !important;
    border: 1px solid {'#334155' if dark else '#e2e8f0'} !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,{'0.3' if dark else '0.06'}) !important;
}}
div[data-testid="metric-container"] label {{
    color: {'#94a3b8' if dark else '#64748b'} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
    color: {'#f1f5f9' if dark else '#0f172a'} !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {'linear-gradient(180deg, #0f172a 0%, #1e3a5f 100%)' if dark else 'linear-gradient(180deg, #1e3a5f 0%, #1d4ed8 100%)'} !important;
    border-right: 1px solid {'#1e293b' if dark else '#1e40af'} !important;
}}
[data-testid="stSidebar"] * {{
    color: #f1f5f9 !important;
}}
[data-testid="stSidebar"] .stRadio label {{
    color: #f1f5f9 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}}

/* Primary button */
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4) !important;
    transition: all 0.3s !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.5) !important;
}}

/* Secondary buttons */
.stButton > button {{
    color: {'#e2e8f0' if dark else '#1e293b'} !important;
    background: {'#1e293b' if dark else '#ffffff'} !important;
    border: 1.5px solid {'#334155' if dark else '#cbd5e1'} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}}

/* File uploader */
[data-testid="stFileUploader"] {{
    background: {'#1e293b' if dark else '#f1f5f9'} !important;
    border: 2px dashed {'#3b82f6' if dark else '#3b82f6'} !important;
    border-radius: 12px !important;
    padding: 10px !important;
}}
[data-testid="stFileUploader"] * {{
    color: {'#e2e8f0' if dark else '#1e293b'} !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: {'#1e293b' if dark else '#f1f5f9'} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {'#94a3b8' if dark else '#64748b'} !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}}
.stTabs [aria-selected="true"] {{
    background: {'#2563eb' if dark else '#2563eb'} !important;
    color: white !important;
}}

/* Expander */
details {{
    background: {'#1e293b' if dark else '#ffffff'} !important;
    border: 1px solid {'#334155' if dark else '#e2e8f0'} !important;
    border-radius: 10px !important;
    padding: 4px !important;
}}
summary {{
    color: {'#e2e8f0' if dark else '#1e293b'} !important;
    font-weight: 600 !important;
}}

/* Alert boxes */
.stSuccess, .stInfo, .stWarning, .stError {{
    border-radius: 10px !important;
    font-weight: 500 !important;
}}

/* Selectbox */
.stSelectbox > div > div {{
    background: {'#1e293b' if dark else '#ffffff'} !important;
    color: {'#e2e8f0' if dark else '#1e293b'} !important;
    border: 1.5px solid {'#334155' if dark else '#cbd5e1'} !important;
}}

/* Progress bar */
.stProgress > div > div {{
    background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
    border-radius: 10px !important;
}}

/* Divider */
hr {{
    border-color: {'#334155' if dark else '#e2e8f0'} !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {'#0f172a' if dark else '#f1f5f9'}; }}
::-webkit-scrollbar-thumb {{ background: #2563eb; border-radius: 10px; }}

/* Chat messages */
[data-testid="stChatMessage"] {{
    background: {'#1e293b' if dark else '#f8fafc'} !important;
    border-radius: 12px !important;
    padding: 12px !important;
    margin: 4px 0 !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Import pages ──────────────────────────────────────────────────────────────
from pages import (resume_analyzer, interview_bot, career_advisor,
                   tips_resources, chatbot, job_recommendations,
                   resume_comparison, resume_builder)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style='text-align:center;padding:10px 0'>
<span style='font-size:2.5rem'>🤖</span>
<h2 style='margin:5px 0;color:white!important;font-size:1.1rem'>Smart AI Resume</h2>
<p style='margin:0;color:#93c5fd!important;font-size:0.85rem'>Analyzer & Interview Bot</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # Dark/Light toggle
    mode_icon = "☀️ Light Mode" if dark else "🌙 Dark Mode"
    if st.button(mode_icon, use_container_width=True):
        st.session_state["dark_mode"] = not dark
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "Menu",
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

    if GEMINI_API_KEY:
        st.markdown("""
<div style='background:rgba(34,197,94,0.2);border:1px solid #22c55e;border-radius:8px;padding:8px;text-align:center'>
<span style='color:#22c55e;font-size:13px;font-weight:600'>✅ AI Connected</span>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style='background:rgba(239,68,68,0.2);border:1px solid #ef4444;border-radius:8px;padding:8px;text-align:center'>
<span style='color:#ef4444;font-size:13px;font-weight:600'>❌ API Key Missing</span>
</div>
""", unsafe_allow_html=True)
        st.caption("Add GEMINI_API_KEY in Streamlit Secrets!")

    st.markdown("---")
    st.markdown("""
<div style='text-align:center;opacity:0.7'>
<small style='color:#94a3b8!important'>Powered by Google Gemini AI<br>Built with Python & Streamlit<br>© 2024</small>
</div>
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
