"""Page 8 - AI Resume Builder."""
from __future__ import annotations

import re

import streamlit as st

from utils import cache
from utils.ui import page_header, source_note


def render() -> None:
    page_header(
        "Resume Builder",
        "Turn your details into a clean, ATS-friendly resume in seconds.",
        "🎨",
    )

    with st.form("resume_builder_form"):
        st.markdown("#### Personal information")
        left, right = st.columns(2)
        with left:
            name = st.text_input("Full name *", placeholder="Rishabh Srivastava")
            email = st.text_input("Email *", placeholder="you@example.com")
            phone = st.text_input("Phone", placeholder="+91 98765 43210")
        with right:
            linkedin = st.text_input("LinkedIn URL", placeholder="linkedin.com/in/you")
            target_role = st.text_input("Target role *", placeholder="Python Developer")
            experience = st.selectbox(
                "Years of experience",
                ["0-1 (Fresher)", "1-3", "3-5", "5-8", "8-10", "10+"],
            )

        st.markdown("#### Education")
        education = st.text_area(
            "Education details",
            placeholder="B.Tech Computer Science, ABC University, 2020-2024, CGPA 8.5",
            height=90,
        )

        st.markdown("#### Skills")
        skills = st.text_area(
            "Technical and soft skills",
            placeholder="Python, Django, React, SQL, Git, Docker, communication",
            height=90,
        )

        st.markdown("#### Experience")
        work_experience = st.text_area(
            "Work experience (company, role, dates, impact)",
            placeholder="XYZ Company, Software Developer, Jan 2022 - Present\nBuilt REST APIs with Django\nReduced page load time by 40%",
            height=180,
        )

        st.markdown("#### Projects")
        projects = st.text_area(
            "Projects (name, stack, impact)",
            placeholder="Smart AI Resume Analyzer\nPython, Streamlit, Gemini AI\nBuilt an analyzer used by 500+ students",
            height=130,
        )

        st.markdown("#### Achievements and certifications")
        left, right = st.columns(2)
        with left:
            achievements = st.text_area("Achievements", placeholder="Won Hackathon 2024", height=90)
        with right:
            certifications = st.text_area("Certifications", placeholder="AWS Cloud Practitioner", height=90)

        submitted = st.form_submit_button("Build my resume", type="primary", use_container_width=True)

    if submitted:
        if not name.strip() or not email.strip() or not target_role.strip():
            st.error("Name, email and target role are required.")
            return
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            st.error("Enter a valid email address.")
            return

        data = {
            "name": name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "linkedin": linkedin.strip(),
            "target_role": target_role.strip(),
            "experience_years": experience,
            "education": education.strip(),
            "skills": skills.strip(),
            "work_exp": work_experience.strip(),
            "projects": projects.strip(),
            "achievements": achievements.strip(),
            "certifications": certifications.strip(),
        }

        with st.spinner("Writing your resume..."):
            result = cache.build_resume(data)
        st.session_state["generated_resume"] = result.get("resume", "")
        st.session_state["generated_resume_source"] = result.get("source", "offline")
        st.session_state["generated_resume_reason"] = result.get("offline_reason", "")
        st.session_state["generated_resume_name"] = name.strip()

    generated = st.session_state.get("generated_resume")
    if not generated:
        return

    st.markdown("---")
    st.markdown("### Your resume")
    source_note(
        st.session_state.get("generated_resume_source", "offline"),
        st.session_state.get("generated_resume_reason", ""),
    )
    st.markdown(generated)

    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", st.session_state.get("generated_resume_name", "resume"))
    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download Markdown",
            data=generated,
            file_name=f"{safe_name}_resume.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with right:
        st.download_button(
            "Download plain text",
            data=generated.replace("**", "").replace("# ", ""),
            file_name=f"{safe_name}_resume.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("Analyze this resume", use_container_width=True):
        st.session_state["resume_text"] = generated
        st.session_state["resume_name"] = st.session_state.get("generated_resume_name", "Candidate")
        st.success("Resume loaded. Open **Resume Analyzer** from the sidebar to score it.")
