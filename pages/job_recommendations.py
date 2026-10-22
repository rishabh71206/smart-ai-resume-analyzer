"""
Page 6 – Job Recommendations
"""
import streamlit as st
from utils.resume_parser import extract_text
from utils.ai_engine import _get_model
import json
import re


def get_job_recommendations(resume_text: str) -> dict:
    model = _get_model()
    prompt = f"""
You are a job placement expert. Based on this resume, suggest relevant jobs.

Resume:
{resume_text[:3000]}

Return ONLY a JSON object:
{{
  "top_roles": [
    {{
      "title": "Job Title",
      "match": 95,
      "salary_range": "$80,000 - $120,000",
      "companies": ["Company1", "Company2", "Company3"],
      "skills_needed": ["skill1", "skill2"],
      "description": "Brief job description"
    }}
  ],
  "industries": ["Industry1", "Industry2", "Industry3"],
  "career_level": "Mid-level",
  "job_search_tips": ["tip1", "tip2", "tip3"]
}}
Give exactly 5 job roles.
"""
    response = model.generate_content(prompt)
    clean = re.sub(r"```(?:json)?", "", response.text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except:
        match = re.search(r"\{[\s\S]*\}", clean)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return {}


def render():
    st.title("🎯 Job Recommendations")
    st.markdown("Resume ke hisaab se best job matches AI dhundega!")

    resume_text = st.session_state.get("resume_text", "")
    if not resume_text:
        uploaded = st.file_uploader("Resume upload karo", type=["pdf", "docx", "txt"], key="job_upload")
        if uploaded:
            resume_text = extract_text(uploaded)
            st.session_state["resume_text"] = resume_text

    if not resume_text:
        st.info("👆 Pehle resume upload karo!")
        return

    if st.button("🔍 Jobs Dhundo", type="primary", use_container_width=True):
        with st.spinner("AI best jobs dhundh raha hai..."):
            recs = get_job_recommendations(resume_text)
            st.session_state["job_recs"] = recs

    recs = st.session_state.get("job_recs")
    if not recs:
        return

    # Career level & Industries
    col1, col2 = st.columns(2)
    col1.metric("Career Level", recs.get("career_level", "—"))
    industries = recs.get("industries", [])
    col2.metric("Best Industries", ", ".join(industries[:2]) if industries else "—")

    st.markdown("---")

    # Job cards
    st.subheader("🏆 Top Job Matches")
    for job in recs.get("top_roles", []):
        match = job.get("match", 0)
        color = "#22c55e" if match >= 80 else "#eab308" if match >= 60 else "#ef4444"

        with st.container():
            st.markdown(f"""
<div style='border:1px solid {color};border-radius:10px;padding:15px;margin-bottom:10px;background:white'>
<h3 style='color:{color};margin:0'>{job.get('title','')} — {match}% Match</h3>
<p style='color:#666;margin:5px 0'>💰 {job.get('salary_range','')}</p>
<p style='color:#333'>{job.get('description','')}</p>
<b>Top Companies:</b> {', '.join(job.get('companies', []))}<br>
<b>Skills Needed:</b> {', '.join(job.get('skills_needed', []))}
</div>
""", unsafe_allow_html=True)

    # Job search tips
    tips = recs.get("job_search_tips", [])
    if tips:
        st.markdown("---")
        st.subheader("💡 Job Search Tips")
        for tip in tips:
            st.info(f"✅ {tip}")

    # Job portals
    st.markdown("---")
    st.subheader("🌐 Job Search Karo")
    col1, col2, col3, col4 = st.columns(4)
    col1.link_button("LinkedIn Jobs", "https://linkedin.com/jobs")
    col2.link_button("Naukri.com", "https://naukri.com")
    col3.link_button("Indeed", "https://indeed.com")
    col4.link_button("Glassdoor", "https://glassdoor.com")
