"""Page 2 - Interview Bot."""
from __future__ import annotations

import html

import plotly.graph_objects as go
import streamlit as st

from config import (
    DEFAULT_NUM_QUESTIONS,
    DIFFICULTY_LEVELS,
    MAX_NUM_QUESTIONS,
    QUESTION_TYPES,
)
from utils import cache
from utils.resume_parser import extract_text
from utils.ui import page_header, source_note


def render() -> None:
    page_header(
        "Interview Bot",
        "Practise a mock interview tailored to your resume and target role.",
        "🎙️",
    )

    with st.expander("Interview setup", expanded=True):
        left, middle, right = st.columns([1.6, 1, 1.2])
        with left:
            job_role = st.text_input(
                "Target role",
                placeholder="e.g. Python Developer",
                value=st.session_state.get("interview_role", ""),
                key="interview_role_input",
            )
        with middle:
            difficulty = st.selectbox("Difficulty", DIFFICULTY_LEVELS, index=3, key="interview_difficulty")
        with right:
            num_questions = st.slider(
                "Number of questions",
                1,
                MAX_NUM_QUESTIONS,
                DEFAULT_NUM_QUESTIONS,
                key="interview_count",
            )

        question_types = st.multiselect(
            "Question types",
            QUESTION_TYPES,
            default=["Behavioral", "Technical"],
            key="interview_types",
        )

        resume_text = st.session_state.get("resume_text", "")
        uploaded = st.file_uploader(
            "Upload a resume (optional - the analyzer's resume is reused if present)",
            type=["pdf", "docx", "txt"],
            key="interview_upload",
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
                height=140,
                placeholder="Paste resume content here...",
                key="interview_paste",
            )

    if st.button("Start interview", type="primary", use_container_width=True):
        if not job_role.strip():
            st.warning("Enter a target role first.")
            return
        if not resume_text.strip():
            st.warning("Upload or paste a resume first.")
            return

        with st.spinner("Generating personalised questions..."):
            questions = cache.generate_interview_questions(
                resume_text,
                job_role,
                difficulty,
                num_questions,
                tuple(question_types or ["Behavioral", "Technical"]),
            )

        if not questions:
            st.error("Could not generate questions. Please try again.")
            return

        st.session_state["interview_questions"] = questions
        st.session_state["interview_role"] = job_role
        st.session_state["interview_answers"] = {}
        st.session_state["interview_evaluations"] = {}
        st.session_state["interview_active"] = True
        st.rerun()

    if st.session_state.get("interview_active"):
        _render_interview()


def _render_interview() -> None:
    questions: list[dict] = st.session_state.get("interview_questions", [])
    answers: dict = st.session_state.setdefault("interview_answers", {})
    evaluations: dict = st.session_state.setdefault("interview_evaluations", {})
    job_role: str = st.session_state.get("interview_role", "")

    if not questions:
        st.session_state["interview_active"] = False
        return

    st.markdown("---")
    st.markdown(f"### Mock interview - {html.escape(job_role)}")
    source_note(questions[0].get("source", "offline"))

    answered = sum(1 for value in answers.values() if str(value).strip())
    st.progress(min(answered / len(questions), 1.0), text=f"Progress: {answered}/{len(questions)} answered")

    for question in questions:
        _question_card(question, answers, evaluations, job_role)

    if len(evaluations) == len(questions):
        _final_score(evaluations, questions, job_role, answers)

    st.markdown("---")
    left, right = st.columns(2)
    if left.button("Start a new interview", use_container_width=True):
        for key in (
            "interview_active",
            "interview_questions",
            "interview_answers",
            "interview_evaluations",
            "interview_role",
        ):
            st.session_state.pop(key, None)
        st.rerun()
    with right:
        _download_transcript(questions, answers, evaluations, job_role)


def _question_card(question: dict, answers: dict, evaluations: dict, job_role: str) -> None:
    qid = str(question.get("id", question.get("question", "")[:20]))
    difficulty = str(question.get("difficulty", ""))
    qtype = str(question.get("type", ""))
    icons = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
    type_icons = {"Behavioral": "🧠", "Technical": "💻", "Situational": "🎭", "HR": "👥"}
    number = question.get("id", "?")
    question_text = html.escape(str(question.get("question", "")))
    topic = html.escape(str(question.get("topic", "")))

    st.markdown(
        f'<div class="rs-question"><strong>Q{number}. {question_text}</strong>'
        f'<div class="rs-question__meta">{type_icons.get(qtype, "❓")} {html.escape(qtype)}'
        f" &nbsp;|&nbsp; {icons.get(difficulty, '⚪')} {html.escape(difficulty)}"
        f" &nbsp;|&nbsp; {topic}</div></div>",
        unsafe_allow_html=True,
    )

    if st.checkbox(f"Show hint for Q{number}", key=f"hint_{qid}"):
        st.caption(f"Hint: {question.get('hint', 'Use a concrete example and quantify the result.')}")

    answer = st.text_area(
        "Your answer",
        value=answers.get(qid, ""),
        height=120,
        key=f"answer_{qid}",
        placeholder="Type your answer here...",
    )
    answers[qid] = answer
    st.session_state["interview_answers"] = answers

    if st.button("Evaluate answer", key=f"evaluate_{qid}"):
        if not answer.strip():
            st.warning("Write an answer before evaluating.")
        else:
            with st.spinner("Evaluating..."):
                evaluation = cache.evaluate_answer(
                    str(question.get("question", "")),
                    answer,
                    job_role,
                    str(question.get("hint", "")),
                )
            evaluations[qid] = evaluation
            st.session_state["interview_evaluations"] = evaluations
            st.rerun()

    evaluation = evaluations.get(qid)
    if evaluation:
        _render_evaluation(evaluation)
    st.markdown("---")


def _render_evaluation(evaluation: dict) -> None:
    score = int(evaluation.get("score", 0) or 0)
    grade = str(evaluation.get("grade", "Average"))
    color = {"Excellent": "#22c55e", "Good": "#84cc16", "Average": "#eab308", "Poor": "#ef4444"}.get(grade, "#64748b")
    st.markdown(
        f'<div class="rs-eval" style="border-color:{color}">'
        f"<strong>Score: {score}/10</strong> &nbsp;|&nbsp; <strong>{html.escape(grade)}</strong></div>",
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.markdown("**What worked**")
        for item in evaluation.get("strengths", []):
            st.success(str(item), icon="✅")
    with right:
        st.markdown("**What to improve**")
        for item in evaluation.get("improvements", []):
            st.warning(str(item), icon="⚠️")
    st.markdown(f"**Feedback:** {evaluation.get('feedback', '')}")
    with st.expander("Model answer"):
        st.info(evaluation.get("model_answer", ""))


def _final_score(evaluations: dict, questions: list, job_role: str, answers: dict) -> None:
    scores = [int(item.get("score", 0) or 0) for item in evaluations.values()]
    if not scores:
        return
    average = sum(scores) / len(scores)
    percentage = int(average * 10)
    grade = "Excellent" if percentage >= 80 else "Good" if percentage >= 60 else "Average" if percentage >= 40 else "Needs work"

    st.markdown("---")
    st.markdown("### Interview complete")
    columns = st.columns(3)
    columns[0].metric("Average score", f"{average:.1f}/10")
    columns[1].metric("Percentage", f"{percentage}%")
    columns[2].metric("Overall grade", grade)

    labels = [f"Q{question.get('id', '?')}" for question in questions]
    values = [
        int(evaluations.get(str(question.get("id", question.get("question", "")[:20])), {}).get("score", 0) or 0)
        for question in questions
    ]
    figure = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color=["#22c55e" if value >= 7 else "#eab308" if value >= 4 else "#ef4444" for value in values],
        )
    )
    figure.update_layout(title="Score per question", yaxis_range=[0, 10], height=300)
    st.plotly_chart(figure, use_container_width=True)

    if percentage >= 80:
        st.balloons()
        st.success("Outstanding. You are close to interview-ready.")
    elif percentage >= 60:
        st.success("Good work. Review the model answers and repeat the weak questions.")
    else:
        st.info("Keep practising. Focus on structure and one measurable result per answer.")


def _download_transcript(questions: list, answers: dict, evaluations: dict, job_role: str) -> None:
    if not evaluations:
        st.button("Download transcript", disabled=True, use_container_width=True)
        return

    lines = [f"# Mock interview - {job_role}", ""]
    for question in questions:
        qid = str(question.get("id", question.get("question", "")[:20]))
        lines.append(f"## Q{question.get('id', '?')}. {question.get('question', '')}")
        lines.append(f"*{question.get('type', '')} | {question.get('difficulty', '')}*")
        lines.append("")
        lines.append(f"**Answer:** {answers.get(qid, 'Not answered.')}")
        evaluation = evaluations.get(qid)
        if evaluation:
            lines.append("")
            lines.append(f"**Score:** {evaluation.get('score', 0)}/10 ({evaluation.get('grade', '')})")
            lines.append(f"**Feedback:** {evaluation.get('feedback', '')}")
        lines.append("")
    transcript = "\n".join(lines)
    st.download_button(
        "Download transcript",
        data=transcript,
        file_name="mock_interview_transcript.md",
        mime="text/markdown",
        use_container_width=True,
    )
