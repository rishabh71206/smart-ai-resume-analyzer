"""
Page 3 – Career Advisor
"""
import streamlit as st
import plotly.graph_objects as go

from utils.resume_parser import extract_text
from utils.ai_engine import generate_career_advice


def render():
    st.title("🚀 Career Advisor")
    st.markdown("Get a personalised career roadmap based on your resume and target role.")

    # ── Input ─────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx", "txt"],
            key="career_upload",
        )
    with col2:
        target_role = st.text_input(
            "Target Role",
            placeholder="e.g. Machine Learning Engineer",
        )

    resume_text = st.session_state.get("resume_text", "")
    if uploaded:
        resume_text = extract_text(uploaded)
        st.session_state["resume_text"] = resume_text

    if not resume_text:
        resume_text = st.text_area(
            "Or paste resume text",
            height=150,
            placeholder="Paste resume content here…",
        )

    if st.button("🔮 Generate Career Roadmap", type="primary", use_container_width=True):
        if not resume_text.strip():
            st.warning("Please upload or paste your resume.")
            return
        if not target_role.strip():
            st.warning("Please enter your target role.")
            return

        with st.spinner("Building your personalised career roadmap…"):
            advice = generate_career_advice(resume_text, target_role)

        if "error" in advice:
            st.error(f"Error: {advice['error']}")
            return

        st.session_state["career_advice"] = advice
        st.session_state["career_role"] = target_role

    # ── Display ───────────────────────────────────────────────────────────────
    advice = st.session_state.get("career_advice")
    if not advice:
        _show_placeholder()
        return

    target_role = st.session_state.get("career_role", "Target Role")
    _render_overview(advice, target_role)
    _render_skills_roadmap(advice)
    _render_learning_resources(advice)
    _render_action_plan(advice)


def _show_placeholder():
    st.info("👆 Upload your resume and enter your target role to generate a roadmap.")
    st.markdown("""
    **What you'll receive:**
    - 🎯 Current level assessment & fit percentage
    - 📈 Skill gap analysis
    - 🏆 Recommended certifications
    - 📚 Learning resources with links
    - 🗺️ Step-by-step action plan
    - 💰 Estimated salary range
    """)


def _render_overview(advice: dict, target_role: str):
    st.markdown("---")
    st.subheader(f"🗺️ Roadmap to: {target_role}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Level", advice.get("current_level", "—"))
    col2.metric("Role Fit", f"{advice.get('target_role_fit', 0)}%")
    col3.metric("Timeline", advice.get("timeline", "—"))
    col4.metric("Salary Range", advice.get("salary_range", "—"))

    st.markdown("---")
    st.markdown("### 💬 Personalised Advice")
    st.info(advice.get("career_advice", ""))

    # Fit gauge
    fit = advice.get("target_role_fit", 0)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fit,
        title={"text": "Role Fit Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#3b82f6"},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef9c3"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
        },
    ))
    fig.update_layout(height=250, margin=dict(t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)


def _render_skills_roadmap(advice: dict):
    st.markdown("---")
    st.subheader("📈 Skills to Develop")

    skill_gaps = advice.get("skill_gaps", [])
    certs = advice.get("recommended_certifications", [])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top Skill Gaps:**")
        for i, skill in enumerate(skill_gaps, 1):
            priority = "🔴 High" if i <= 2 else "🟡 Medium" if i <= 4 else "🟢 Low"
            st.markdown(f"**{i}.** {skill} — {priority}")

    with col2:
        st.markdown("**Recommended Certifications:**")
        for cert in certs:
            st.markdown(f"🏆 {cert}")


def _render_learning_resources(advice: dict):
    resources = advice.get("learning_resources", [])
    if not resources:
        return

    st.markdown("---")
    st.subheader("📚 Learning Resources")

    for res in resources:
        topic = res.get("topic", "")
        resource = res.get("resource", "")
        url = res.get("url", "")
        link = f"[{resource}]({url})" if url else resource
        st.markdown(f"- **{topic}:** {link}")


def _render_action_plan(advice: dict):
    plan = advice.get("action_plan", [])
    if not plan:
        return

    st.markdown("---")
    st.subheader("✅ Your Action Plan")

    for i, step in enumerate(plan, 1):
        done_key = f"action_done_{i}"
        done = st.checkbox(f"**Step {i}:** {step}", key=done_key)

    completed = sum(
        1 for i in range(1, len(plan) + 1)
        if st.session_state.get(f"action_done_{i}", False)
    )
    st.progress(completed / len(plan), text=f"Progress: {completed}/{len(plan)} steps completed")
