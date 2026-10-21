"""
Page 1 – Resume Analyzer
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.resume_parser import extract_text, extract_contact_info, extract_sections
from utils.ai_engine import analyze_resume, match_job_description
from utils.scorer import compute_skill_score, compute_resume_completeness, weighted_overall_score
from utils.pdf_report import generate_pdf_report


def render():
    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume for an in-depth AI-powered analysis.")

    # ── Sidebar options ───────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Analysis Settings")
        include_jd = st.checkbox("Include Job Description", value=False)
        show_raw_text = st.checkbox("Show Extracted Text", value=False)

    # ── Upload ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            help="Max file size: 5 MB",
        )

    with col2:
        job_description = ""
        if include_jd:
            job_description = st.text_area(
                "Paste Job Description",
                height=200,
                placeholder="Paste the full job description here…",
            )

    if not uploaded_file:
        _show_placeholder()
        return

    # ── Parse resume ──────────────────────────────────────────────────────────
    with st.spinner("Parsing resume…"):
        resume_text = extract_text(uploaded_file)
        contact_info = extract_contact_info(resume_text)
        sections = extract_sections(resume_text)

    if show_raw_text:
        with st.expander("📝 Extracted Text", expanded=False):
            st.text(resume_text[:3000] + ("…" if len(resume_text) > 3000 else ""))

    # ── AI Analysis ───────────────────────────────────────────────────────────
    analyze_btn = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

    if analyze_btn or st.session_state.get("analysis_done"):
        if analyze_btn:
            with st.spinner("AI is analyzing your resume… This may take a few seconds."):
                analysis = analyze_resume(resume_text, job_description)
                if job_description.strip():
                    jd_match = match_job_description(resume_text, job_description)
                else:
                    jd_match = {}

                skill_data = compute_skill_score(resume_text, job_description)
                completeness = compute_resume_completeness(sections)

                st.session_state["analysis"] = analysis
                st.session_state["jd_match"] = jd_match
                st.session_state["skill_data"] = skill_data
                st.session_state["completeness"] = completeness
                st.session_state["resume_text"] = resume_text
                st.session_state["contact_info"] = contact_info
                st.session_state["analysis_done"] = True

        analysis = st.session_state.get("analysis", {})
        jd_match = st.session_state.get("jd_match", {})
        skill_data = st.session_state.get("skill_data", {})
        completeness = st.session_state.get("completeness", {})
        contact_info = st.session_state.get("contact_info", {})

        if "error" in analysis:
            st.error(f"AI Error: {analysis['error']}")
            return

        _render_contact_card(contact_info)
        _render_score_dashboard(analysis, skill_data, completeness, jd_match)
        _render_detailed_sections(analysis)
        if jd_match:
            _render_jd_match(jd_match)
        _render_skills_chart(analysis)
        _render_download(analysis, contact_info.get("name", "Candidate"))


# ── Sub-renderers ─────────────────────────────────────────────────────────────

def _show_placeholder():
    st.info("👆 Upload a resume above to get started.")
    st.markdown("""
    **What you'll get:**
    - 📊 Comprehensive resume score (Overall + ATS)
    - ✅ Strengths & areas for improvement
    - 🎯 Skills gap analysis
    - 💡 Actionable suggestions
    - 📥 Downloadable PDF report
    """)


def _render_contact_card(info: dict):
    st.markdown("---")
    st.subheader("👤 Candidate Information")
    cols = st.columns(5)
    labels = ["Name", "Email", "Phone", "LinkedIn", "GitHub"]
    keys = ["name", "email", "phone", "linkedin", "github"]
    for col, label, key in zip(cols, labels, keys):
        with col:
            val = info.get(key) or "—"
            st.metric(label, val if len(str(val)) < 25 else str(val)[:22] + "…")


def _render_score_dashboard(analysis: dict, skill_data: dict, completeness: dict, jd_match: dict):
    st.markdown("---")
    st.subheader("📊 Score Dashboard")

    ai_score = analysis.get("overall_score", 0)
    ats_score = analysis.get("ats_score", 0)
    skill_score = skill_data.get("score", 0)
    comp_score = completeness.get("completeness_score", 0)
    overall = weighted_overall_score(ai_score, skill_score, comp_score)

    c1, c2, c3, c4, c5 = st.columns(5)
    _score_metric(c1, "Overall", overall)
    _score_metric(c2, "AI Score", ai_score)
    _score_metric(c3, "ATS Score", ats_score)
    _score_metric(c4, "Skills Match", skill_score)
    _score_metric(c5, "Completeness", comp_score)

    if jd_match:
        st.metric("🎯 JD Match Score", f"{jd_match.get('match_score', 0)}%")

    # Gauge chart for overall score
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall,
        delta={"reference": 70},
        title={"text": "Overall Resume Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": _score_color(overall)},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef9c3"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
            "threshold": {"line": {"color": "black", "width": 4}, "thickness": 0.75, "value": 70},
        },
    ))
    fig.update_layout(height=300, margin=dict(t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Radar chart for section scores
    sections_score = analysis.get("sections_score", {})
    if sections_score:
        cats = [k.replace("_", " ").title() for k in sections_score.keys()]
        vals = list(sections_score.values())
        vals_norm = [v / 10 * 100 for v in vals]  # normalise to 100
        fig2 = go.Figure(go.Scatterpolar(r=vals_norm, theta=cats, fill="toself", name="Score"))
        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Section-by-Section Scores",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)


def _score_metric(col, label: str, value: int):
    color = _score_color(value)
    with col:
        st.metric(label, f"{value}/100")


def _score_color(score: int) -> str:
    if score >= 70:
        return "#22c55e"
    elif score >= 40:
        return "#eab308"
    return "#ef4444"


def _render_detailed_sections(analysis: dict):
    st.markdown("---")
    st.subheader("🔍 Detailed Analysis")

    tab1, tab2, tab3 = st.tabs(["✅ Strengths & Weaknesses", "💡 Suggestions", "📋 Summary Review"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ✅ Strengths")
            for s in analysis.get("strengths", []):
                st.success(f"✔ {s}")
        with col2:
            st.markdown("### ⚠️ Areas for Improvement")
            for w in analysis.get("weaknesses", []):
                st.warning(f"⚠ {w}")

    with tab2:
        st.markdown("### 💡 Actionable Suggestions")
        for i, s in enumerate(analysis.get("suggestions", []), 1):
            st.info(f"**{i}.** {s}")

    with tab3:
        st.markdown("### 📝 Summary Review")
        st.write(analysis.get("summary_review", "N/A"))
        st.markdown("### 🌐 Overall Review")
        st.write(analysis.get("overall_review", "N/A"))

        exp_years = analysis.get("experience_years")
        edu = analysis.get("education_level", "Unknown")
        titles = analysis.get("job_titles", [])

        c1, c2, c3 = st.columns(3)
        c1.metric("Experience", f"{exp_years} yrs" if exp_years else "Unknown")
        c2.metric("Education", edu)
        c3.metric("Roles Detected", len(titles))
        if titles:
            st.markdown("**Job Titles Found:** " + ", ".join(titles))


def _render_jd_match(jd_match: dict):
    st.markdown("---")
    st.subheader("🎯 Job Description Match")

    rec = jd_match.get("recommendation", "")
    color_map = {
        "Strongly Recommend": "🟢",
        "Recommend": "🟡",
        "Neutral": "🟠",
        "Do Not Recommend": "🔴",
    }
    icon = color_map.get(rec, "⚪")
    st.markdown(f"**Recommendation:** {icon} {rec}")
    st.write(jd_match.get("fit_summary", ""))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Experience Match", jd_match.get("experience_match", "—"))
        st.markdown("**Matched Skills:**")
        for s in jd_match.get("matched_skills", []):
            st.success(f"✔ {s}")
    with col2:
        st.metric("Education Match", jd_match.get("education_match", "—"))
        st.markdown("**Missing Skills:**")
        for s in jd_match.get("missing_skills", []):
            st.error(f"✗ {s}")


def _render_skills_chart(analysis: dict):
    st.markdown("---")
    st.subheader("🛠️ Skills Analysis")

    skills_found = analysis.get("skills_found", [])
    missing_skills = analysis.get("missing_skills", [])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Skills Detected in Resume:**")
        if skills_found:
            for skill in skills_found:
                st.markdown(f"<span style='background:#dcfce7;padding:2px 8px;border-radius:12px;margin:2px;display:inline-block'>✅ {skill}</span>", unsafe_allow_html=True)
        else:
            st.info("No specific skills detected.")
    with col2:
        st.markdown("**Skills to Add:**")
        if missing_skills:
            for skill in missing_skills:
                st.markdown(f"<span style='background:#fee2e2;padding:2px 8px;border-radius:12px;margin:2px;display:inline-block'>➕ {skill}</span>", unsafe_allow_html=True)
        else:
            st.success("No critical skills missing!")

    # Keywords chart
    keywords = analysis.get("keywords_found", [])
    missing_kw = analysis.get("keywords_missing", [])
    if keywords or missing_kw:
        kw_df = pd.DataFrame({
            "Keyword": keywords[:15] + missing_kw[:10],
            "Status": ["Found"] * min(len(keywords), 15) + ["Missing"] * min(len(missing_kw), 10),
        })
        if not kw_df.empty:
            fig = px.bar(
                kw_df,
                x="Keyword",
                color="Status",
                color_discrete_map={"Found": "#22c55e", "Missing": "#ef4444"},
                title="ATS Keywords",
                height=350,
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)


def _render_download(analysis: dict, candidate_name: str):
    st.markdown("---")
    st.subheader("📥 Download Report")
    pdf_bytes = generate_pdf_report(analysis, candidate_name)
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name=f"resume_analysis_{candidate_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
