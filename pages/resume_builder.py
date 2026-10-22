"""
Page 8 – AI Resume Builder
"""
import streamlit as st
from utils.ai_engine import _get_model
import re


def generate_resume(data: dict) -> str:
    model = _get_model()
    prompt = f"""
You are an expert resume writer. Create a professional resume based on this information.

Candidate Information:
Name: {data.get('name', '')}
Email: {data.get('email', '')}
Phone: {data.get('phone', '')}
LinkedIn: {data.get('linkedin', '')}
Target Role: {data.get('target_role', '')}
Years of Experience: {data.get('experience_years', '')}
Education: {data.get('education', '')}
Skills: {data.get('skills', '')}
Work Experience: {data.get('work_exp', '')}
Projects: {data.get('projects', '')}
Achievements: {data.get('achievements', '')}
Certifications: {data.get('certifications', '')}

Create a professional, ATS-optimized resume with:
1. A strong professional summary
2. Well-formatted work experience with bullet points (use STAR method)
3. Skills section
4. Education section
5. Projects section (if provided)

Make it compelling and use strong action verbs. Format it cleanly with clear sections.
"""
    response = model.generate_content(prompt)
    return response.text


def render():
    st.title("🎨 AI Resume Builder")
    st.markdown("Apni details dalo — AI tumhara professional resume banayega!")

    with st.form("resume_builder_form"):
        st.subheader("👤 Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="Rishabh Srivastava")
            email = st.text_input("Email *", placeholder="rishabh@gmail.com")
            phone = st.text_input("Phone", placeholder="+91 9876543210")
        with col2:
            linkedin = st.text_input("LinkedIn URL", placeholder="linkedin.com/in/rishabh")
            target_role = st.text_input("Target Job Role *", placeholder="Python Developer")
            experience_years = st.selectbox("Years of Experience", ["0-1 (Fresher)", "1-3", "3-5", "5-8", "8-10", "10+"])

        st.subheader("🎓 Education")
        education = st.text_area(
            "Education Details",
            placeholder="B.Tech Computer Science, ABC University, 2020-2024, CGPA: 8.5",
            height=100
        )

        st.subheader("🛠️ Skills")
        skills = st.text_area(
            "Technical & Soft Skills",
            placeholder="Python, Django, React, SQL, Git, Docker, Problem Solving, Team Work",
            height=100
        )

        st.subheader("💼 Work Experience")
        work_exp = st.text_area(
            "Work Experience (Company, Role, Duration, Responsibilities)",
            placeholder="XYZ Company, Software Developer, Jan 2022 - Present\n- Developed REST APIs using Django\n- Reduced load time by 40%",
            height=200
        )

        st.subheader("🚀 Projects")
        projects = st.text_area(
            "Projects (Name, Tech Stack, Description)",
            placeholder="Smart AI Resume Analyzer\nTech: Python, Streamlit, Gemini AI\nBuilt an AI-powered resume analyzer with 95% accuracy",
            height=150
        )

        st.subheader("🏆 Achievements & Certifications")
        col1, col2 = st.columns(2)
        with col1:
            achievements = st.text_area("Achievements", placeholder="Won Hackathon 2023\nTop 5% in batch", height=100)
        with col2:
            certifications = st.text_area("Certifications", placeholder="AWS Cloud Practitioner\nGoogle Data Analytics", height=100)

        submitted = st.form_submit_button("✨ Resume Banao!", type="primary", use_container_width=True)

    if submitted:
        if not name or not email or not target_role:
            st.error("Name, Email aur Target Role zaroori hai!")
            return

        data = {
            "name": name, "email": email, "phone": phone,
            "linkedin": linkedin, "target_role": target_role,
            "experience_years": experience_years, "education": education,
            "skills": skills, "work_exp": work_exp, "projects": projects,
            "achievements": achievements, "certifications": certifications
        }

        with st.spinner("AI tumhara professional resume bana raha hai..."):
            resume_content = generate_resume(data)
            st.session_state["generated_resume"] = resume_content
            st.session_state["resume_text"] = resume_content

    # Display generated resume
    generated = st.session_state.get("generated_resume")
    if generated:
        st.markdown("---")
        st.subheader("✅ Tumhara AI-Generated Resume!")
        st.markdown(generated)

        # Download as text
        st.download_button(
            label="⬇️ Resume Download Karo (.txt)",
            data=generated,
            file_name=f"resume_{name if 'name' in dir() else 'candidate'}.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.success("✅ Resume ban gaya! Ab Resume Analyzer mein analyze bhi kar sakte ho!")
