"""Page 3 - Career Advisor."""
from __future__ import annotations

import html

import plotly.graph_objects as go
import streamlit as st

from utils import cache
from utils.resume_parser import extract_text
from utils.ui import page_header, source_note


def render() -> None:
    page_header(
        "Career Advisor",
        "Turn your resume into a prioritised roadmap for the role you want next.",
        "🚀",
    )

    left, right = st.columns([2, 1])
    with left:
        uploaded = st.file_uploader(
            "Upload a resume (optional - the analyzer's resume is reused)",
            type=["pdf", "docx", "txt"],
            key="career_upload",
        )
    with right:
        target_role = st.text_input(
            "Target role",
            placeholder="e.g. Machine Learning Engineer",
            key="career_target",
        )

    resume_text = st.session_state.get("resume_text", "")
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
            key="career_paste",
        )

    if st.button("Generate roadmap", type="primary", use_container_width=True):
        if not resume_text.strip():
            st.warning("Upload or paste a resume first.")
            return
        if not target_role.strip():
            st.warning("Enter a target role first.")
            return

        with st.spinner("Building your roadmap..."):
            advice = cache.generate_career_advice(resume_text, target_role)
        st.session_state["career_advice"] = advice
        st.session_state["career_role"] = target_role

    advice = st.session_state.get("career_advice")
    if not advice:
        _placeholder()
        return

    role = st.session_state.get("career_role", "Target role")
    source_note(advice.get("source", "offline"), advice.get("offline_reason", ""))
    _overview(advice, role)
    _skills(advice)
    _resources(advice)
    _plan(advice, role)


def _placeholder() -> None:
    st.info("Upload a resume and name a target role to generate a roadmap.")
    st.markdown(
        """
- Current level and role fit
- Skill gaps ordered by impact
- Certifications worth the time
- Learning resources with links
- A five-step action plan
- A realistic salary range
"""
    )


def _overview(advice: dict, role: str) -> None:
    st.markdown(f"### Roadmap to {html.escape(role)}")
    columns = st.columns(4)
    columns[0].metric("Current level", str(advice.get("current_level", "—")))
    columns[1].metric("Role fit", f"{advice.get('target_role_fit', 0)}%")
    columns[2].metric("Timeline", str(advice.get("timeline", "—")))
    columns[3].metric("Salary range", str(advice.get("salary_range", "—")))

    st.info(advice.get("career_advice", ""))

    fit = int(advice.get("target_role_fit", 0) or 0)
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=fit,
            title={"text": "Role fit"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2563eb"},
                "steps": [
                    {"range": [0, 40], "color": "#fee2e2"},
                    {"range": [40, 70], "color": "#fef9c3"},
                    {"range": [70, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    figure.update_layout(height=250, margin=dict(t=30, b=0))
    st.plotly_chart(figure, use_container_width=True)


def _skills(advice: dict) -> None:
    st.markdown("### Skills to develop")
    gaps = advice.get("skill_gaps") or []
    certifications = advice.get("recommended_certifications") or []

    left, right = st.columns(2)
    with left:
        st.markdown("**Priority gaps**")
        if not gaps:
            st.success("No major gaps found. Focus on proof of impact.")
        for index, skill in enumerate(gaps, 1):
            priority = "High" if index <= 2 else "Medium" if index <= 4 else "Low"
            st.markdown(f"**{index}. {html.escape(str(skill))}** — {priority}")
    with right:
        st.markdown("**Certifications worth considering**")
        for certification in certifications:
            st.markdown(f"- {html.escape(str(certification))}")


def _resources(advice: dict) -> None:
    resources = advice.get("learning_resources") or []
    if not resources:
        return
    st.markdown("### Learning resources")
    for resource in resources:
        topic = html.escape(str(resource.get("topic", "")))
        name = html.escape(str(resource.get("resource", "")))
        url = str(resource.get("url", "")).strip()
        if url.startswith(("http://", "https://")):
            st.markdown(f"- **{topic}:** [{name}]({url})" if topic else f"- [{name}]({url})")
        else:
            st.markdown(f"- **{topic}:** {name}" if topic else f"- {name}")


def _plan(advice: dict, role: str) -> None:
    plan = advice.get("action_plan") or []
    if not plan:
        return

    st.markdown("### Action plan")
    for index, step in enumerate(plan, 1):
        st.checkbox(f"**Step {index}.** {step}", key=f"career_step_{index}")

    completed = sum(1 for index in range(1, len(plan) + 1) if st.session_state.get(f"career_step_{index}"))
    st.progress(completed / len(plan), text=f"Progress: {completed}/{len(plan)} steps completed")

    lines = [f"# Career roadmap - {role}", "", advice.get("career_advice", ""), "", "## Action plan"]
    lines += [f"{index}. {step}" for index, step in enumerate(plan, 1)]
    st.download_button(
        "Download roadmap (.md)",
        data="\n".join(lines) + "\n",
        file_name="career_roadmap.md",
        mime="text/markdown",
        use_container_width=True,
    )
