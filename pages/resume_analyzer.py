"""
Page 1 – Resume Analyzer
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.resume_parser import extract_text, extract_contact_info, extract_sections, is_resume
from utils.ai_engine import analyze_resume, match_job_description
from utils.scorer import compute_skill_score, compute_resume_completeness, weighted_overall_score
from utils.pdf_report import generate_pdf_report


def render():
    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume for a **comprehensive AI-powered analysis** with ATS score, skills gap, and actionable suggestions.")

    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        include_jd = st.checkbox("Match with Job Description", value=False)
        show_raw = st.checkbox("Show Extracted Text", value=False)

    col1, col2 = st.columns([1, 1] if not include_jd else [1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "📎 Upload Resume (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
        )

    job_description = ""
    if include_jd:
        with col2:
            job_description = st.text_area(
                "📋 Paste Job Description",
                height=200,
                placeholder="Paste the full job description here…",
            )

    if not uploaded_file:
        _show_placeholder()
        return

    with st.spinner("📖 Reading your resume…"):
        resume_text = extract_text(uploaded_file)
        contact_info = extract_contact_info(resume_text)
        sections = extract_sections(resume_text)

    # Validate
    valid, msg = is_resume(resume_text)
    if not valid:
        st.error(f"❌ {msg}")
        st.warning("Please upload your actual resume (PDF/DOCX/TXT). Notes or assignments won't work.")
        return

    if show_raw:
        with st.expander("📝 Extracted Text"):
            st.text(resume_text[:3000])

    if st.button("🚀 Analyze My Resume", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is analyzing your resume… Please wait…"):
            try:
                analysis = analyze_resume(resume_text, job_description)
                jd_match = match_job_description(resume_text, job_description) if job_description.strip() else {}
                skill_data = compute_skill_score(resume_text, job_description)
                completeness = compute_resume_completeness(sections)

                st.session_state["analysis"] = analysis
                st.session_state["jd_match"] = jd_match
                st.session_state["skill_data"] = skill_data
                st.session_state["completeness"] = completeness
                st.session_state["resume_text"] = resume_text
                st.session_state["contact_info"] = contact_info
                st.session_state["analysis_done"] = True
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Please check your Gemini API key in Streamlit Secrets.")
                return

    if not st.session_state.get("analysis_done"):
        return

    analysis = st.session_state.get("analysis", {})
    jd_match = st.session_state.get("jd_match", {})
    skill_data = st.session_state.get("skill_data", {})
    completeness = st.session_state.get("completeness", {})
    contact_info = st.session_state.get("contact_info", {})

    if "error" in analysis:
        st.error(f"AI Error: {analysis['error']}")
        return

    _render_contact(contact_info)
    _render_scores(analysis, skill_data, completeness, jd_match)
    _render_details(analysis)
    if jd_match:
        _render_jd(jd_match)
    _render_skills(analysis)
    _render_download(analysis, contact_info.get("name", "Candidate"))


def _show_placeholder():
    st.markdown("""
<div style='background:linear-gradient(135deg,#eff6ff,#f0fdf4);border:2px dashed #3b82f6;border-radius:16px;padding:30px;text-align:center;margin:20px 0'>
<h3 style='color:#1e40af'>👆 Upload your resume to get started!</h3>
<p style='color:#475569'>Supports PDF, DOCX, and TXT formats</p>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
<div style='background:white;border-radius:12px;padding:16px;border:1px solid #e2e8f0;text-align:center'>
<div style='font-size:2rem'>📊</div>
<b>Resume Score</b><br>
<small>Overall + ATS score</small>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
<div style='background:white;border-radius:12px;padding:16px;border:1px solid #e2e8f0;text-align:center'>
<div style='font-size:2rem'>🎯</div>
<b>Skills Analysis</b><br>
<small>Found + missing skills</small>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
<div style='background:white;border-radius:12px;padding:16px;border:1px solid #e2e8f0;text-align:center'>
<div style='font-size:2rem'>💡</div>
<b>AI Suggestions</b><br>
<small>Actionable improvements</small>
</div>""", unsafe_allow_html=True)


def _render_contact(info: dict):
    st.markdown("---")
    st.subheader("👤 Candidate Information")
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, key in zip(
        [c1, c2, c3, c4, c5],
        ["Name", "Email", "Phone", "LinkedIn", "GitHub"],
        ["name", "email", "phone", "linkedin", "github"]
    ):
        val = info.get(key) or "—"
        col.metric(label, str(val)[:20] + "…" if len(str(val)) > 20 else val)


def _render_scores(analysis, skill_data, completeness, jd_match):
    st.markdown("---")
    st.subheader("📊 Score Dashboard")

    ai  = analysis.get("overall_score", 0)
    ats = analysis.get("ats_score", 0)
    sk  = skill_data.get("score", 0)
    cp  = completeness.get("completeness_score", 0)
    ov  = weighted_overall_score(ai, sk, cp)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏆 Overall", f"{ov}/100")
    c2.metric("🤖 AI Score", f"{ai}/100")
    c3.metric("✅ ATS Score", f"{ats}/100")
    c4.metric("🛠️ Skills", f"{sk}/100")
    c5.metric("📋 Complete", f"{cp}/100")

    if jd_match:
        st.metric("🎯 JD Match", f"{jd_match.get('match_score', 0)}%")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ov,
            delta={"reference": 70},
            title={"text": "Overall Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2563eb"},
                "steps": [
                    {"range": [0, 40], "color": "#fee2e2"},
                    {"range": [40, 70], "color": "#fef9c3"},
                    {"range": [70, 100], "color": "#dcfce7"},
                ],
                "threshold": {"line": {"color": "#1e293b", "width": 4}, "thickness": 0.75, "value": 70},
            },
        ))
        fig.update_layout(height=280, margin=dict(t=30, b=0, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sc = analysis.get("sections_score", {})
        if sc:
            cats = [k.replace("_", " ").title() for k in sc.keys()]
            vals = [v / 10 * 100 for v in sc.values()]
            fig2 = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill="toself",
                line_color="#2563eb", fillcolor="rgba(37,99,235,0.2)"))
            fig2.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title="Section Scores", height=280,
                margin=dict(t=40, b=10, l=10, r=10)
            )
            st.plotly_chart(fig2, use_container_width=True)


def _render_details(analysis):
    st.markdown("---")
    st.subheader("🔍 Detailed Analysis")

    tab1, tab2, tab3 = st.tabs(["✅ Strengths & Weaknesses", "💡 Suggestions", "📋 Summary"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### ✅ Strengths")
            for s in analysis.get("strengths", []):
                st.success(f"✔ {s}")
        with c2:
            st.markdown("### ⚠️ Weaknesses")
            for w in analysis.get("weaknesses", []):
                st.warning(f"⚠ {w}")

    with tab2:
        for i, s in enumerate(analysis.get("suggestions", []), 1):
            st.info(f"**{i}.** {s}")

    with tab3:
        st.write("**Summary Review:**", analysis.get("summary_review", "N/A"))
        st.write("**Overall Review:**", analysis.get("overall_review", "N/A"))
        c1, c2, c3 = st.columns(3)
        c1.metric("Experience", f"{analysis.get('experience_years', '?')} yrs")
        c2.metric("Education", analysis.get("education_level", "Unknown"))
        titles = analysis.get("job_titles", [])
        c3.metric("Roles Found", len(titles))
        if titles:
            st.markdown("**Roles:** " + ", ".join(titles))


def _render_jd(jd_match):
    st.markdown("---")
    st.subheader("🎯 Job Description Match")
    rec = jd_match.get("recommendation", "")
    icons = {"Strongly Recommend": "🟢", "Recommend": "🟡", "Neutral": "🟠", "Do Not Recommend": "🔴"}
    st.markdown(f"**Recommendation:** {icons.get(rec,'⚪')} {rec}")
    st.write(jd_match.get("fit_summary", ""))
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Experience Match", jd_match.get("experience_match", "—"))
        for s in jd_match.get("matched_skills", []):
            st.success(f"✔ {s}")
    with c2:
        st.metric("Education Match", jd_match.get("education_match", "—"))
        for s in jd_match.get("missing_skills", []):
            st.error(f"✗ {s}")


def _render_skills(analysis):
    st.markdown("---")
    st.subheader("🛠️ Skills Analysis")
    found = analysis.get("skills_found", [])
    missing = analysis.get("missing_skills", [])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**✅ Skills Found:**")
        if found:
            html = "".join([f"<span style='background:#dcfce7;color:#166534;padding:3px 10px;border-radius:20px;margin:3px;display:inline-block;font-size:13px'>✅ {s}</span>" for s in found])
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("No skills detected.")
    with c2:
        st.markdown("**➕ Skills to Add:**")
        if missing:
            html = "".join([f"<span style='background:#fee2e2;color:#991b1b;padding:3px 10px;border-radius:20px;margin:3px;display:inline-block;font-size:13px'>➕ {s}</span>" for s in missing])
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.success("No critical skills missing!")

    kw = analysis.get("keywords_found", [])
    mkw = analysis.get("keywords_missing", [])
    if kw or mkw:
        df = pd.DataFrame({
            "Keyword": kw[:15] + mkw[:10],
            "Status": ["Found"] * min(len(kw), 15) + ["Missing"] * min(len(mkw), 10),
        })
        if not df.empty:
            fig = px.bar(df, x="Keyword", color="Status",
                color_discrete_map={"Found": "#22c55e", "Missing": "#ef4444"},
                title="ATS Keywords", height=320)
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)


def _render_download(analysis, name):
    st.markdown("---")
    pdf = generate_pdf_report(analysis, name)
    st.download_button(
        "⬇️ Download PDF Report",
        data=pdf,
        file_name=f"resume_analysis_{name.replace(' ','_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
