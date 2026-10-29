"""Page 1 - Resume Analyzer."""
from __future__ import annotations

import html

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from utils import cache
from utils.resume_parser import (
    extract_contact_info,
    extract_sections,
    extract_text,
    is_resume,
)
from utils.scorer import (
    compute_resume_completeness,
    compute_skill_score,
    weighted_overall_score,
)
from utils.ui import chip, chips, page_header, score_cards, score_tone, source_note


def render() -> None:
    page_header(
        "Resume Analyzer",
        "Upload a resume for an ATS score, skills gap analysis and concrete next steps.",
        "📄",
    )

    with st.sidebar:
        st.markdown("### Analyzer settings")
        include_jd = st.checkbox("Match against a job description", value=False, key="analyzer_include_jd")
        show_raw = st.checkbox("Show extracted text", value=False, key="analyzer_show_raw")

    if include_jd:
        left, right = st.columns(2)
    else:
        left = st.container()
        right = None

    pasted = ""
    with left:
        uploaded = st.file_uploader(
            "Upload resume (PDF, DOCX or TXT)",
            type=["pdf", "docx", "txt"],
            key="analyzer_upload",
        )
        if not uploaded:
            pasted = st.text_area(
                "Or paste resume text",
                value=st.session_state.get("resume_text", ""),
                height=170,
                placeholder="Paste your resume text here...",
                key="analyzer_paste",
            )
    job_description = ""
    if include_jd and right is not None:
        with right:
            job_description = st.text_area(
                "Paste the job description",
                height=190,
                placeholder="Paste the full job description here...",
                key="analyzer_jd",
            )

    if not uploaded and not pasted.strip():
        _placeholder()
        return

    if uploaded and getattr(uploaded, "size", 0) > MAX_FILE_SIZE_BYTES:
        st.error(f"This file is larger than {MAX_FILE_SIZE_MB} MB. Please upload a smaller resume.")
        return

    try:
        resume_text = extract_text(uploaded) if uploaded else pasted
    except Exception as exc:  # corrupted PDFs, password-protected files, ...
        st.error(f"Could not read this file: {exc}")
        return

    valid, message = is_resume(resume_text)
    if not valid:
        st.error(message)
        return

    contact = extract_contact_info(resume_text)
    sections = extract_sections(resume_text)
    completeness = compute_resume_completeness(sections)
    skill_data = compute_skill_score(resume_text, job_description)
    if uploaded:
        file_id = f"{getattr(uploaded, 'name', 'resume')}:{getattr(uploaded, 'size', len(resume_text))}"
    else:
        file_id = f"pasted:{len(resume_text)}:{resume_text[:80]}"

    # A new upload must never show the previous resume's report.
    if st.session_state.get("analyzer_file_id") != file_id:
        for key in ("analysis", "jd_match", "analysis_file_id"):
            st.session_state.pop(key, None)
        st.session_state["analyzer_file_id"] = file_id

    if show_raw:
        with st.expander("Extracted text", expanded=False):
            st.text(resume_text[:6000])

    if st.button("Analyze my resume", type="primary", use_container_width=True):
        with st.spinner("Analyzing your resume..."):
            analysis = cache.analyze_resume(resume_text, job_description)
            jd_match = (
                cache.match_job_description(resume_text, job_description)
                if job_description.strip()
                else {}
            )
        st.session_state["analysis"] = analysis
        st.session_state["jd_match"] = jd_match
        st.session_state["analysis_file_id"] = file_id
        st.session_state["resume_text"] = resume_text
        st.session_state["resume_name"] = contact.get("name") or "Candidate"

    if st.session_state.get("analysis_file_id") != file_id:
        st.info("Click **Analyze my resume** to generate the report.")
        return

    analysis = st.session_state.get("analysis") or {}
    jd_match = st.session_state.get("jd_match") or {}

    source_note(analysis.get("source", "offline"), analysis.get("offline_reason", ""))
    _render_contact(contact)
    _render_scores(analysis, skill_data, completeness, jd_match)
    _render_details(analysis)
    if jd_match:
        _render_jd(jd_match)
    _render_skills(analysis)
    _render_download(analysis, jd_match, contact.get("name") or "Candidate")


# ── Placeholder ───────────────────────────────────────────────────────────────

def _placeholder() -> None:
    st.markdown(
        """
<div class="rs-empty">
  <h3>Upload a resume to get started</h3>
  <p>PDF, DOCX and TXT are supported. Your file stays in this session.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    cards = [
        ("📊", "Score dashboard", "Overall, ATS, skills and completeness."),
        ("🎯", "Job match", "See exactly which required skills are missing."),
        ("💡", "Next steps", "Prioritised, specific edits you can make today."),
    ]
    for column, (icon, title, text) in zip(columns, cards):
        column.markdown(
            f'<div class="rs-card"><div class="rs-card__icon">{icon}</div>'
            f"<strong>{html.escape(title)}</strong><p>{html.escape(text)}</p></div>",
            unsafe_allow_html=True,
        )


# ── Sections ──────────────────────────────────────────────────────────────────

def _render_contact(info: dict) -> None:
    st.markdown("### Candidate")
    columns = st.columns(5)
    values = [
        ("Name", info.get("name") or "Not found"),
        ("Email", info.get("email") or "Not found"),
        ("Phone", info.get("phone") or "Not found"),
        ("LinkedIn", info.get("linkedin") or "Not found"),
        ("GitHub", info.get("github") or "Not found"),
    ]
    for column, (label, value) in zip(columns, values):
        display = value if len(value) <= 26 else value[:23] + "..."
        column.markdown(
            f'<div class="rs-mini"><span>{html.escape(label)}</span>'
            f"<strong>{html.escape(display)}</strong></div>",
            unsafe_allow_html=True,
        )


def _render_scores(analysis: dict, skill_data: dict, completeness: dict, jd_match: dict) -> None:
    st.markdown("### Score dashboard")
    ai_score = int(analysis.get("overall_score", 0) or 0)
    ats = int(analysis.get("ats_score", 0) or 0)
    skills = int(skill_data.get("score", 0) or 0)
    complete = int(completeness.get("completeness_score", 0) or 0)
    overall = weighted_overall_score(ai_score, skills, complete)

    score_cards(
        [
            ("Overall", f"{overall}/100", score_tone(overall)),
            ("AI review", f"{ai_score}/100", score_tone(ai_score)),
            ("ATS", f"{ats}/100", score_tone(ats)),
            ("Skills", f"{skills}/100", score_tone(skills)),
            ("Completeness", f"{complete}/100", score_tone(complete)),
        ]
    )
    if jd_match:
        st.metric("Job description match", f"{jd_match.get('match_score', 0)}%")

    left, right = st.columns(2)
    with left:
        figure = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=overall,
                title={"text": "Overall score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2563eb"},
                    "steps": [
                        {"range": [0, 40], "color": "#fee2e2"},
                        {"range": [40, 70], "color": "#fef9c3"},
                        {"range": [70, 100], "color": "#dcfce7"},
                    ],
                    "threshold": {"line": {"color": "#0f172a", "width": 3}, "thickness": 0.75, "value": 70},
                },
            )
        )
        figure.update_layout(height=260, margin=dict(t=30, b=0, l=10, r=10))
        st.plotly_chart(figure, use_container_width=True)

    with right:
        sections = analysis.get("sections_score") or {}
        if sections:
            labels = [str(key).replace("_", " ").title() for key in sections]
            values = [min(float(value), 10) / 10 * 100 for value in sections.values()]
            figure = go.Figure(
                go.Scatterpolar(r=values, theta=labels, fill="toself", line_color="#2563eb")
            )
            figure.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title="Section scores",
                height=260,
                margin=dict(t=40, b=10, l=10, r=10),
            )
            st.plotly_chart(figure, use_container_width=True)


def _render_details(analysis: dict) -> None:
    st.markdown("### Detailed review")
    strengths_tab, suggestions_tab, summary_tab = st.tabs(
        ["Strengths and weaknesses", "Suggestions", "Summary"]
    )

    with strengths_tab:
        left, right = st.columns(2)
        with left:
            st.markdown("**Strengths**")
            for item in analysis.get("strengths", []) or ["No strengths detected yet."]:
                st.success(str(item), icon="✅")
        with right:
            st.markdown("**Areas to improve**")
            for item in analysis.get("weaknesses", []) or ["No major issues detected."]:
                st.warning(str(item), icon="⚠️")

    with suggestions_tab:
        suggestions = analysis.get("suggestions") or []
        if not suggestions:
            st.info("No suggestions returned.")
        for index, suggestion in enumerate(suggestions, 1):
            st.markdown(f"**{index}.** {suggestion}")

    with summary_tab:
        st.markdown("**Summary**")
        st.write(analysis.get("summary_review") or "Not available.")
        st.markdown("**Overall review**")
        st.write(analysis.get("overall_review") or "Not available.")
        columns = st.columns(3)
        columns[0].metric("Experience", f"{analysis.get('experience_years', 0)} yrs")
        columns[1].metric("Education", str(analysis.get("education_level", "Unknown"))[:24])
        titles = analysis.get("job_titles") or []
        columns[2].metric("Roles found", len(titles))
        if titles:
            st.caption("Roles: " + ", ".join(map(str, titles)))


def _render_jd(jd_match: dict) -> None:
    st.markdown("### Job description match")
    recommendation = str(jd_match.get("recommendation", "Neutral"))
    tone = {"Strongly Recommend": "green", "Recommend": "green", "Neutral": "amber"}.get(recommendation, "red")
    st.markdown(
        f"**Recommendation:** {chip(recommendation, tone)}",
        unsafe_allow_html=True,
    )
    st.write(jd_match.get("fit_summary") or "")

    left, right = st.columns(2)
    with left:
        st.markdown("**Matched skills**")
        matched = jd_match.get("matched_skills") or []
        st.markdown(chips(matched, "green") if matched else "None detected.", unsafe_allow_html=True)
    with right:
        st.markdown("**Missing skills**")
        missing = jd_match.get("missing_skills") or []
        st.markdown(chips(missing, "red") if missing else "Nothing critical missing.", unsafe_allow_html=True)

    columns = st.columns(2)
    columns[0].metric("Experience match", str(jd_match.get("experience_match", "Not specified"))[:30])
    columns[1].metric("Education match", str(jd_match.get("education_match", "Not specified"))[:30])


def _render_skills(analysis: dict) -> None:
    st.markdown("### Skills and keywords")
    found = analysis.get("skills_found") or []
    missing = analysis.get("missing_skills") or []

    left, right = st.columns(2)
    with left:
        st.markdown("**Skills detected**")
        st.markdown(chips(found, "green") if found else "No skills detected.", unsafe_allow_html=True)
    with right:
        st.markdown("**Skills to add**")
        st.markdown(chips(missing, "red") if missing else "No critical gaps found.", unsafe_allow_html=True)

    keywords_found = [str(item) for item in (analysis.get("keywords_found") or [])][:15]
    keywords_missing = [str(item) for item in (analysis.get("keywords_missing") or [])][:10]
    rows = [{"Keyword": item, "Status": "Found"} for item in keywords_found]
    rows += [{"Keyword": item, "Status": "Missing"} for item in keywords_missing if item not in keywords_found]
    if rows:
        frame = pd.DataFrame(rows)
        figure = px.bar(
            frame,
            x="Keyword",
            color="Status",
            color_discrete_map={"Found": "#22c55e", "Missing": "#ef4444"},
            title="ATS keywords",
            height=320,
        )
        figure.update_layout(xaxis_tickangle=-40, margin=dict(t=50, b=80))
        st.plotly_chart(figure, use_container_width=True)


def _render_download(analysis: dict, jd_match: dict, name: str) -> None:
    st.markdown("---")
    try:
        pdf_bytes = cache.pdf_report(analysis, name, jd_match or None)
    except Exception as exc:
        st.warning(f"Could not build the PDF report: {exc}")
        return
    safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in name)
    st.download_button(
        "Download PDF report",
        data=pdf_bytes,
        file_name=f"resume_analysis_{safe_name}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
