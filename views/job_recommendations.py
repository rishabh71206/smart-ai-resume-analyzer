"""Page 6 - Job Recommendations."""
from __future__ import annotations

import html

import streamlit as st

from utils import cache
from utils.resume_parser import extract_text
from utils.ui import chip, page_header, source_note


def render() -> None:
    page_header(
        "Job Recommendations",
        "Match your resume to realistic roles, salary bands and the skills to add next.",
        "🎯",
    )

    resume_text = st.session_state.get("resume_text", "")
    if not resume_text:
        uploaded = st.file_uploader(
            "Upload a resume (optional - the analyzer's resume is reused)",
            type=["pdf", "docx", "txt"],
            key="jobs_upload",
        )
        if uploaded:
            try:
                resume_text = extract_text(uploaded)
                st.session_state["resume_text"] = resume_text
            except Exception as exc:
                st.error(f"Could not read this file: {exc}")

    if not resume_text:
        resume_text = st.text_area(
            "Or paste your resume",
            height=150,
            placeholder="Paste resume content here...",
            key="jobs_paste",
        )

    if not resume_text.strip():
        st.info("Upload or paste a resume to see job matches.")
        return

    if st.button("Find my job matches", type="primary", use_container_width=True):
        with st.spinner("Matching roles..."):
            recommendations = cache.recommend_jobs(resume_text)
        st.session_state["job_recommendations"] = recommendations

    recommendations = st.session_state.get("job_recommendations")
    if not recommendations:
        return

    source_note(recommendations.get("source", "offline"), recommendations.get("offline_reason", ""))

    columns = st.columns(2)
    columns[0].metric("Career level", str(recommendations.get("career_level", "—")))
    industries = recommendations.get("industries") or []
    columns[1].metric("Strongest industries", ", ".join(map(str, industries[:3])) or "—")

    st.markdown("### Top matches")
    for job in recommendations.get("top_roles", []):
        _job_card(job)

    tips = recommendations.get("job_search_tips") or []
    if tips:
        st.markdown("### Search strategy")
        for tip in tips:
            st.info(str(tip), icon="💡")

    st.markdown("### Job boards")
    columns = st.columns(4)
    columns[0].link_button("LinkedIn Jobs", "https://www.linkedin.com/jobs/", use_container_width=True)
    columns[1].link_button("Naukri", "https://www.naukri.com/", use_container_width=True)
    columns[2].link_button("Indeed", "https://www.indeed.com/", use_container_width=True)
    columns[3].link_button("Glassdoor", "https://www.glassdoor.com/", use_container_width=True)


def _job_card(job: dict) -> None:
    match = int(job.get("match", 0) or 0)
    tone = "green" if match >= 80 else "amber" if match >= 60 else "red"
    title = html.escape(str(job.get("title", "Role")))
    salary = html.escape(str(job.get("salary_range", "Not specified")))
    description = html.escape(str(job.get("description", "")))
    companies = ", ".join(map(str, job.get("companies") or []))
    skills = job.get("skills_needed") or []
    match_chip = chip(f"{match}% match", tone)
    skills_html = "".join(chip(str(skill), "neutral") for skill in skills)
    companies_text = html.escape(companies or "—")

    st.markdown(
        f'<div class="rs-job"><div class="rs-job__head"><strong>{title}</strong>'
        f"<span>{match_chip}</span></div>"
        f'<div class="rs-job__meta">{salary}</div>'
        f"<p>{description}</p>"
        f'<div class="rs-job__meta"><strong>Companies:</strong> {companies_text}</div>'
        f'<div class="rs-job__skills">{skills_html}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    st.progress(match / 100)
