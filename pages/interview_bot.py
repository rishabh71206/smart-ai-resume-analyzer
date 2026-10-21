"""
Page 2 – Interview Bot
"""
import streamlit as st

from utils.resume_parser import extract_text
from utils.ai_engine import generate_interview_questions, evaluate_answer
from config import DEFAULT_NUM_QUESTIONS, MAX_NUM_QUESTIONS, DIFFICULTY_LEVELS


def render():
    st.title("🤖 AI Interview Bot")
    st.markdown("Practice mock interviews tailored to your resume and target role.")

    # ── Setup panel ───────────────────────────────────────────────────────────
    with st.expander("⚙️ Interview Setup", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            job_role = st.text_input(
                "Target Job Role",
                placeholder="e.g. Senior Python Developer",
                value=st.session_state.get("interview_role", ""),
            )
        with col2:
            difficulty = st.selectbox("Difficulty", DIFFICULTY_LEVELS, index=3)
        with col3:
            num_q = st.slider("Number of Questions", 1, MAX_NUM_QUESTIONS, DEFAULT_NUM_QUESTIONS)

        q_types = st.multiselect(
            "Question Types",
            ["Behavioral", "Technical", "Situational", "HR"],
            default=["Behavioral", "Technical"],
        )

        # Resume upload (or reuse from analyzer page)
        resume_text = st.session_state.get("resume_text", "")
        uploaded = st.file_uploader(
            "Upload Resume (optional — uses previously uploaded resume if skipped)",
            type=["pdf", "docx", "txt"],
            key="interview_upload",
        )
        if uploaded:
            resume_text = extract_text(uploaded)
            st.session_state["resume_text"] = resume_text

        if not resume_text:
            resume_text = st.text_area(
                "Or paste your resume text here",
                height=150,
                placeholder="Paste resume content…",
                key="resume_paste",
            )

    start_btn = st.button("🎬 Start Interview", type="primary", use_container_width=True)

    if start_btn:
        if not job_role.strip():
            st.warning("Please enter a target job role.")
            return
        if not resume_text.strip():
            st.warning("Please upload or paste your resume.")
            return

        with st.spinner("Generating personalised interview questions…"):
            questions = generate_interview_questions(
                resume_text=resume_text,
                job_role=job_role,
                difficulty=difficulty,
                num_questions=num_q,
                question_types=q_types if q_types else None,
            )

        if not questions:
            st.error("Could not generate questions. Check your API key and try again.")
            return

        st.session_state["interview_questions"] = questions
        st.session_state["interview_role"] = job_role
        st.session_state["interview_answers"] = {}
        st.session_state["interview_evaluations"] = {}
        st.session_state["interview_active"] = True
        st.rerun()

    # ── Active interview ──────────────────────────────────────────────────────
    if st.session_state.get("interview_active"):
        _render_interview()


def _render_interview():
    questions: list[dict] = st.session_state.get("interview_questions", [])
    answers: dict = st.session_state.get("interview_answers", {})
    evaluations: dict = st.session_state.get("interview_evaluations", {})
    job_role: str = st.session_state.get("interview_role", "")

    st.markdown("---")
    st.subheader(f"🎙️ Mock Interview — {job_role}")

    # Progress bar
    answered = len([a for a in answers.values() if a.strip()])
    st.progress(answered / len(questions), text=f"Progress: {answered}/{len(questions)} answered")

    for q in questions:
        qid = str(q.get("id", q.get("question", "")[:20]))
        _render_question_card(q, qid, answers, evaluations, job_role)

    # ── Final score ───────────────────────────────────────────────────────────
    all_evaluated = len(evaluations) == len(questions) and len(questions) > 0
    if all_evaluated:
        _render_final_score(evaluations, questions)

    # Reset button
    if st.button("🔄 Start New Interview", use_container_width=True):
        for key in ["interview_active", "interview_questions", "interview_answers",
                    "interview_evaluations", "interview_role"]:
            st.session_state.pop(key, None)
        st.rerun()


def _render_question_card(q: dict, qid: str, answers: dict, evaluations: dict, job_role: str):
    diff_color = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴", "Mixed": "⚪"}.get(
        q.get("difficulty", ""), "⚪"
    )
    type_icon = {"Behavioral": "🧠", "Technical": "💻", "Situational": "🎭", "HR": "👥"}.get(
        q.get("type", ""), "❓"
    )

    with st.container():
        st.markdown(f"""
<div style='background:#f8fafc;border-left:4px solid #3b82f6;padding:12px;border-radius:4px;margin-bottom:8px'>
<b>Q{q.get('id','?')}. {q.get('question','')}</b><br>
<small>{type_icon} {q.get('type','')} &nbsp;|&nbsp; {diff_color} {q.get('difficulty','')} &nbsp;|&nbsp; 📌 {q.get('topic','')}</small>
</div>
""", unsafe_allow_html=True)

        # Show hint toggle
        if st.checkbox(f"Show hint for Q{q.get('id','?')}", key=f"hint_{qid}"):
            st.caption(f"💡 Hint: {q.get('hint', 'N/A')}")

        answer = st.text_area(
            f"Your Answer",
            value=answers.get(qid, ""),
            height=120,
            key=f"ans_{qid}",
            placeholder="Type your answer here…",
        )
        answers[qid] = answer
        st.session_state["interview_answers"] = answers

        col1, col2 = st.columns([1, 4])
        with col1:
            eval_btn = st.button("✅ Evaluate", key=f"eval_{qid}", use_container_width=True)

        if eval_btn:
            if not answer.strip():
                st.warning("Please write an answer before evaluating.")
            else:
                with st.spinner("Evaluating your answer…"):
                    ev = evaluate_answer(
                        question=q.get("question", ""),
                        answer=answer,
                        job_role=job_role,
                        expected_hints=q.get("hint", ""),
                    )
                evaluations[qid] = ev
                st.session_state["interview_evaluations"] = evaluations

        # Show evaluation if available
        ev = evaluations.get(qid)
        if ev and "error" not in ev:
            _render_evaluation(ev)

        st.markdown("---")


def _render_evaluation(ev: dict):
    score = ev.get("score", 0)
    grade = ev.get("grade", "")
    grade_color = {
        "Excellent": "#22c55e",
        "Good": "#84cc16",
        "Average": "#eab308",
        "Poor": "#ef4444",
    }.get(grade, "#6b7280")

    st.markdown(
        f"<div style='background:{grade_color}20;border:1px solid {grade_color};padding:10px;border-radius:6px'>"
        f"<b>Score: {score}/10</b> &nbsp;|&nbsp; <b>Grade: {grade}</b></div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**What you did well:**")
        for s in ev.get("strengths", []):
            st.success(f"✔ {s}")
    with col2:
        st.markdown("**Improvements:**")
        for imp in ev.get("improvements", []):
            st.warning(f"⚠ {imp}")

    st.markdown(f"**Feedback:** {ev.get('feedback', '')}")

    with st.expander("💡 Model Answer"):
        st.info(ev.get("model_answer", ""))


def _render_final_score(evaluations: dict, questions: list):
    st.markdown("---")
    st.subheader("🏆 Interview Complete!")

    scores = [ev.get("score", 0) for ev in evaluations.values() if "error" not in ev]
    if scores:
        avg = sum(scores) / len(scores)
        pct = int(avg * 10)

        col1, col2, col3 = st.columns(3)
        col1.metric("Average Score", f"{avg:.1f}/10")
        col2.metric("Percentage", f"{pct}%")
        grade = "Excellent" if pct >= 80 else "Good" if pct >= 60 else "Average" if pct >= 40 else "Needs Work"
        col3.metric("Overall Grade", grade)

        # Per-question bar chart
        import plotly.graph_objects as go
        q_labels = [f"Q{q.get('id','?')}" for q in questions]
        q_scores = [evaluations.get(str(q.get("id", q.get("question", "")[:20])), {}).get("score", 0) for q in questions]

        fig = go.Figure(go.Bar(
            x=q_labels, y=q_scores,
            marker_color=["#22c55e" if s >= 7 else "#eab308" if s >= 4 else "#ef4444" for s in q_scores],
        ))
        fig.update_layout(title="Score per Question", yaxis_range=[0, 10], height=300)
        st.plotly_chart(fig, use_container_width=True)

        if pct >= 80:
            st.balloons()
            st.success("🎉 Outstanding performance! You're ready for the real interview.")
        elif pct >= 60:
            st.success("👍 Good job! Review the model answers and keep practising.")
        else:
            st.info("📚 Keep practising — focus on the improvement areas highlighted above.")
