"""Smart AI Resume Analyzer - Streamlit entry point."""
from __future__ import annotations

import streamlit as st

from config import (
    APP_ICON,
    APP_TAGLINE,
    APP_TITLE,
    APP_VERSION,
    PORTFOLIO_URL,
    REPO_URL,
)
from utils import ai_engine, cache
from views import (
    career_advisor,
    chatbot,
    interview_bot,
    job_recommendations,
    resume_analyzer,
    resume_builder,
    resume_comparison,
    tips_resources,
)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

dark = bool(st.session_state["dark_mode"])


def _css(is_dark: bool) -> str:
    bg = "#0f172a" if is_dark else "#f8fafc"
    panel = "#111c31" if is_dark else "#ffffff"
    ink = "#e2e8f0" if is_dark else "#0f172a"
    muted = "#94a3b8" if is_dark else "#64748b"
    border = "#24344d" if is_dark else "#e2e8f0"
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.stApp {{ background: {bg} !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }}

h1, h2, h3, h4 {{ color: {ink} !important; font-weight: 700 !important; letter-spacing: -0.01em; }}
p, li, span, label, .stMarkdown {{ color: {ink}; }}
[data-testid="stCaptionContainer"], .stCaption {{ color: {muted} !important; }}
a {{ color: #2563eb; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0f172a 0%, #1e3a5f 100%) !important;
    border-right: 1px solid #1e293b;
}}
[data-testid="stSidebar"] * {{ color: #e2e8f0 !important; }}
[data-testid="stSidebar"] a {{ color: #d8b36a !important; }}
[data-testid="stSidebar"] .stRadio label {{ font-size: 14px !important; font-weight: 500 !important; }}
[data-testid="stSidebar"] hr {{ border-color: #334155 !important; }}

/* Inputs */
input, textarea, [data-baseweb="select"] > div {{
    background: {panel} !important;
    color: {ink} !important;
    border-color: {border} !important;
    border-radius: 9px !important;
}}
label {{ font-weight: 600 !important; font-size: 14px !important; }}
[data-testid="stFileUploader"] {{
    background: {panel} !important;
    border: 2px dashed #3b82f6 !important;
    border-radius: 12px !important;
    padding: 8px !important;
}}

/* Metrics */
div[data-testid="metric-container"] {{
    background: {panel} !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08) !important;
}}
div[data-testid="metric-container"] label {{ color: {muted} !important; font-size: 12px !important; }}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: {ink} !important; font-weight: 700 !important; }}

/* Buttons */
.stButton > button, .stDownloadButton > button, .stLinkButton > a {{
    border-radius: 9px !important;
    font-weight: 600 !important;
    border: 1px solid {border} !important;
}}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.25) !important;
}}
.stButton > button[kind="primary"]:hover {{ transform: translateY(-1px); }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; background: {panel}; border-radius: 10px; padding: 4px; }}
.stTabs [data-baseweb="tab"] {{ border-radius: 8px; font-weight: 600; }}
.stTabs [aria-selected="true"] {{ background: #2563eb !important; color: #ffffff !important; }}

/* Expander / alerts */
details {{ background: {panel} !important; border: 1px solid {border} !important; border-radius: 10px !important; }}
summary {{ font-weight: 600 !important; }}
.stProgress > div > div > div {{ background: linear-gradient(90deg, #2563eb, #7c3aed) !important; }}
[data-testid="stChatMessage"] {{ background: {panel} !important; border: 1px solid {border} !important; border-radius: 12px !important; }}

/* Custom components */
.rs-chip {{ display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:600; margin:2px 3px 2px 0; }}
.rs-chip--green {{ background:#dcfce7; color:#166534; }}
.rs-chip--amber {{ background:#fef3c7; color:#92400e; }}
.rs-chip--red {{ background:#fee2e2; color:#991b1b; }}
.rs-chip--neutral {{ background:#e2e8f0; color:#334155; }}

.rs-score {{ background:{panel}; border:1px solid {border}; border-radius:12px; padding:12px 14px; height:100%; }}
.rs-score--green {{ border-left:4px solid #22c55e; }}
.rs-score--amber {{ border-left:4px solid #eab308; }}
.rs-score--red {{ border-left:4px solid #ef4444; }}
.rs-score__label {{ display:block; color:{muted}; font-size:11px; letter-spacing:.07em; text-transform:uppercase; font-weight:700; }}
.rs-score__value {{ color:{ink}; font-size:1.35rem; line-height:1.4; }}

.rs-card {{ background:{panel}; border:1px solid {border}; border-radius:12px; padding:14px 16px; margin-bottom:10px; }}
.rs-card p {{ margin:4px 0 0; color:{muted}; font-size:13px; }}
.rs-card__icon {{ font-size:1.6rem; }}

.rs-empty {{ background:{panel}; border:2px dashed #3b82f6; border-radius:16px; padding:26px; text-align:center; margin:12px 0 18px; }}
.rs-empty h3 {{ margin:0 0 4px; }}
.rs-empty p {{ margin:0; color:{muted}; }}

.rs-mini {{ background:{panel}; border:1px solid {border}; border-radius:10px; padding:10px 12px; }}
.rs-mini span {{ display:block; color:{muted}; font-size:11px; text-transform:uppercase; letter-spacing:.06em; font-weight:700; }}
.rs-mini strong {{ color:{ink}; font-size:13px; word-break:break-word; }}

.rs-question {{ background:{panel}; border-left:4px solid #3b82f6; border-radius:8px; padding:12px 14px; margin-bottom:8px; }}
.rs-question__meta {{ color:{muted}; font-size:12px; margin-top:4px; }}

.rs-eval {{ background:{panel}; border:1px solid {border}; border-left-width:5px; border-radius:8px; padding:10px 14px; margin:8px 0; }}

.rs-job {{ background:{panel}; border:1px solid {border}; border-radius:12px; padding:16px 18px; margin:10px 0 6px; }}
.rs-job__head {{ display:flex; justify-content:space-between; gap:12px; align-items:center; }}
.rs-job__head strong {{ font-size:1.05rem; }}
.rs-job__meta {{ color:{muted}; font-size:13px; margin-top:4px; }}
.rs-job p {{ margin:8px 0; }}
.rs-job__skills {{ margin-top:8px; }}

.rs-winner {{ background:linear-gradient(90deg,#16a34a,#22c55e); border-radius:12px; padding:18px; text-align:center; color:#fff; }}
.rs-winner span {{ display:block; font-size:12px; letter-spacing:.12em; text-transform:uppercase; opacity:.85; }}
.rs-winner strong {{ font-size:1.6rem; color:#fff !important; }}

::-webkit-scrollbar {{ width:8px; height:8px; }}
::-webkit-scrollbar-thumb {{ background:#2563eb; border-radius:8px; }}
</style>
"""


st.markdown(_css(dark), unsafe_allow_html=True)

PAGES = {
    "📄 Resume Analyzer": resume_analyzer.render,
    "🎙️ Interview Bot": interview_bot.render,
    "🚀 Career Advisor": career_advisor.render,
    "💬 Resume Chatbot": chatbot.render,
    "🎯 Job Recommendations": job_recommendations.render,
    "👥 Resume Comparison": resume_comparison.render,
    "🎨 Resume Builder": resume_builder.render,
    "📚 Tips & Resources": tips_resources.render,
}

with st.sidebar:
    st.markdown(
        f"""
<div style="text-align:center; padding:6px 0 10px">
  <div style="width:58px;height:58px;border-radius:50%;margin:0 auto 8px;
              background:linear-gradient(135deg,#d8b36a,#8a6d2f);display:flex;
              align-items:center;justify-content:center;font-weight:800;font-size:1.35rem;color:#0b0c0a">
    RS
  </div>
  <div style="font-weight:700;font-size:1rem;color:#ffffff">Smart AI Resume</div>
  <div style="font-size:0.78rem;color:#93c5fd">{APP_TAGLINE}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    page = st.radio("Menu", list(PAGES), label_visibility="collapsed")

    st.markdown("---")
    status = ai_engine.ai_status()
    if status["available"]:
        st.success(f"Gemini connected\n\n`{status['model']}`", icon="⚡")
    else:
        st.info("Offline engine active\n\nEvery feature still works without a key.", icon="🧠")
        if status.get("reason"):
            st.caption(status["reason"])

    st.markdown("---")
    if st.button("☀️ Light mode" if dark else "🌙 Dark mode", use_container_width=True):
        st.session_state["dark_mode"] = not dark
        st.rerun()

    if st.button("Reset session", use_container_width=True):
        for key in list(st.session_state):
            if key != "dark_mode":
                del st.session_state[key]
        cache.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        f"""
<div style="font-size:13px; line-height:1.9">
  <a href="{PORTFOLIO_URL}" target="_blank" rel="noopener">Portfolio</a><br>
  <a href="{REPO_URL}" target="_blank" rel="noopener">Source code</a><br>
  <a href="mailto:rishabhsrivastava712008@gmail.com">Email</a>
</div>
<div style="margin-top:12px; font-size:11px; color:#94a3b8">
  v{APP_VERSION} · Python · Gemini · Streamlit
</div>
""",
        unsafe_allow_html=True,
    )

PAGES[page]()
