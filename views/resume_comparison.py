"""Page 7 - Resume Comparison."""
from __future__ import annotations

import html

import plotly.graph_objects as go
import streamlit as st

from utils import cache
from utils.resume_parser import extract_text
from utils.ui import page_header, source_note


def render() -> None:
    page_header(
        "Resume Comparison",
        "Compare two resumes on the same rubric and see which one is stronger.",
        "👥",
    )

    left, right = st.columns(2)
    with left:
        st.markdown("#### Resume 1")
        name1 = st.text_input("Candidate 1 name", value="Candidate A", key="comparison_name1")
        file1 = st.file_uploader("Resume 1", type=["pdf", "docx", "txt"], key="comparison_file1")
    with right:
        st.markdown("#### Resume 2")
        name2 = st.text_input("Candidate 2 name", value="Candidate B", key="comparison_name2")
        file2 = st.file_uploader("Resume 2", type=["pdf", "docx", "txt"], key="comparison_file2")

    if not file1 or not file2:
        st.info("Upload both resumes to compare them.")
        return

    try:
        resume1 = extract_text(file1)
        resume2 = extract_text(file2)
    except Exception as exc:
        st.error(f"Could not read one of the files: {exc}")
        return

    if not resume1.strip() or not resume2.strip():
        st.error("One of the files has no readable text.")
        return

    comparison_key = f"{name1}|{name2}|{len(resume1)}|{len(resume2)}"
    if st.button("Compare resumes", type="primary", use_container_width=True):
        with st.spinner("Comparing..."):
            result = cache.compare_resumes(resume1, resume2, name1, name2)
        st.session_state["comparison"] = result
        st.session_state["comparison_names"] = (name1, name2)
        st.session_state["comparison_key"] = comparison_key

    result = st.session_state.get("comparison")
    if not result or st.session_state.get("comparison_key") != comparison_key:
        st.info("Click **Compare resumes** to see the result.")
        return

    names = st.session_state.get("comparison_names", (name1, name2))
    source_note(result.get("source", "offline"), result.get("offline_reason", ""))

    winner = str(result.get("winner", ""))
    st.markdown(
        f'<div class="rs-winner"><span>Winner</span><strong>{html.escape(winner)}</strong></div>',
        unsafe_allow_html=True,
    )
    st.info(result.get("verdict", ""))

    _radar(result.get("scores") or {}, names)
    _breakdown(result, names)
    _strengths(result, names)
    _download(result, names)


def _radar(scores: dict, names: tuple[str, str]) -> None:
    if not scores:
        return
    categories = ["overall", "skills", "experience", "education", "presentation"]
    labels = ["Overall", "Skills", "Experience", "Education", "Presentation"]
    figure = go.Figure()
    colors = ["#2563eb", "#ef4444"]
    for index, name in enumerate(names):
        values = [int(scores.get(name, {}).get(category, 0) or 0) for category in categories]
        figure.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels,
                fill="toself",
                name=name,
                line_color=colors[index % len(colors)],
            )
        )
    figure.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Comparison radar",
        height=400,
    )
    st.plotly_chart(figure, use_container_width=True)


def _breakdown(result: dict, names: tuple[str, str]) -> None:
    scores = result.get("scores") or {}
    categories = ["overall", "skills", "experience", "education", "presentation"]
    st.markdown("### Score breakdown")
    columns = st.columns(2)
    for index, name in enumerate(names):
        with columns[index]:
            st.markdown(f"**{html.escape(name)}**")
            person = scores.get(name) or {}
            for category in categories:
                value = int(person.get(category, 0) or 0)
                st.markdown(f"{category.title()}: **{value}/100**")
                st.progress(value / 100)


def _strengths(result: dict, names: tuple[str, str]) -> None:
    strengths = result.get("strengths") or {}
    weaknesses = result.get("weaknesses") or {}
    st.markdown("### Strengths and gaps")
    columns = st.columns(2)
    for index, name in enumerate(names):
        with columns[index]:
            st.markdown(f"**{html.escape(name)}**")
            for item in strengths.get(name, []):
                st.success(str(item), icon="✅")
            for item in weaknesses.get(name, []):
                st.warning(str(item), icon="⚠️")


def _download(result: dict, names: tuple[str, str]) -> None:
    scores = result.get("scores") or {}
    lines = [f"# Resume comparison: {names[0]} vs {names[1]}", ""]
    lines.append(f"**Winner:** {result.get('winner', '')}")
    lines.append("")
    lines.append(result.get("verdict", ""))
    lines.append("")
    for name in names:
        person = scores.get(name) or {}
        lines.append(f"## {name}")
        for category, value in person.items():
            lines.append(f"- {category.title()}: {value}/100")
        lines.append("")
    st.download_button(
        "Download comparison (.md)",
        data="\n".join(lines) + "\n",
        file_name="resume_comparison.md",
        mime="text/markdown",
        use_container_width=True,
    )
