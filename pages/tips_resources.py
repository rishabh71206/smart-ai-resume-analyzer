"""
Page 4 – Resume Tips & Resources
"""
import streamlit as st


TIPS = {
    "📝 Writing a Strong Summary": [
        "Keep it to 2–4 sentences that highlight your key value proposition.",
        "Mention your years of experience, specialisation, and biggest achievement.",
        "Tailor it for each job application.",
        "Avoid personal pronouns (I, me, my).",
    ],
    "🎯 ATS Optimisation": [
        "Use keywords directly from the job description.",
        "Avoid tables, headers/footers, and text boxes — ATS can't parse them.",
        "Use standard section headings: Experience, Education, Skills.",
        "Spell out acronyms at least once (e.g., Natural Language Processing (NLP)).",
        "Use a clean, single-column layout.",
    ],
    "📌 Experience Section": [
        "Use the STAR format: Situation, Task, Action, Result.",
        "Start every bullet with a strong action verb (Led, Built, Reduced, Improved).",
        "Quantify achievements wherever possible (e.g., Reduced API latency by 40%).",
        "Limit to 3–5 bullets per role.",
        "Show progression and growth across roles.",
    ],
    "🛠️ Skills Section": [
        "List hard skills (programming languages, tools, frameworks) prominently.",
        "Group skills by category: Languages, Frameworks, Databases, Cloud, etc.",
        "Don't rate your skills (avoid 'Python ⭐⭐⭐') — it looks subjective.",
        "Include both technical and soft skills.",
    ],
    "📐 Formatting Best Practices": [
        "Keep it to 1 page for <5 years experience; 2 pages max for senior roles.",
        "Use consistent fonts (Calibri, Garamond, or Arial) at 10–12pt.",
        "Maintain uniform margins (0.5–1 inch).",
        "Use PDF format when submitting unless told otherwise.",
        "Proofread — spelling mistakes are an instant red flag.",
    ],
    "🎙️ Interview Preparation": [
        "Research the company: mission, recent news, products, culture.",
        "Prepare 3–5 STAR stories that cover common behavioural questions.",
        "Practise with mock interviews (use the Interview Bot on this app!).",
        "Prepare thoughtful questions for the interviewer.",
        "Follow up with a thank-you email within 24 hours.",
    ],
}

RESOURCES = [
    {"name": "LinkedIn Learning", "desc": "Online courses for tech & business skills", "url": "https://linkedin.com/learning"},
    {"name": "Coursera", "desc": "University-level courses and specialisations", "url": "https://coursera.org"},
    {"name": "LeetCode", "desc": "Coding interview preparation", "url": "https://leetcode.com"},
    {"name": "HackerRank", "desc": "Coding challenges and certifications", "url": "https://hackerrank.com"},
    {"name": "Glassdoor", "desc": "Company reviews and salary data", "url": "https://glassdoor.com"},
    {"name": "Levels.fyi", "desc": "Tech salary transparency", "url": "https://levels.fyi"},
    {"name": "Resume Worded", "desc": "AI-powered resume checker", "url": "https://resumeworded.com"},
    {"name": "STAR Method Guide", "desc": "Behavioural interview technique", "url": "https://www.themuse.com/advice/star-interview-method"},
]


def render():
    st.title("📚 Resume Tips & Resources")
    st.markdown("Expert advice to help you land your dream job.")

    tab1, tab2 = st.tabs(["💡 Tips & Best Practices", "🔗 Useful Resources"])

    with tab1:
        for section, tips in TIPS.items():
            with st.expander(section, expanded=False):
                for tip in tips:
                    st.markdown(f"✅ {tip}")

    with tab2:
        st.markdown("### 🌐 Recommended Platforms & Tools")
        cols = st.columns(2)
        for i, res in enumerate(RESOURCES):
            with cols[i % 2]:
                st.markdown(f"""
<div style='border:1px solid #e2e8f0;border-radius:8px;padding:12px;margin-bottom:8px'>
<b><a href='{res['url']}' target='_blank'>{res['name']}</a></b><br>
<small>{res['desc']}</small>
</div>
""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📖 Resume Template Checklist")
        checklist = [
            "Contact information (name, email, phone, LinkedIn)",
            "Professional summary / objective",
            "Work experience in reverse chronological order",
            "Quantified achievements (numbers, percentages)",
            "Education with relevant coursework / GPA if strong",
            "Technical skills grouped by category",
            "Projects with tech stack and impact",
            "Certifications and awards",
            "GitHub / Portfolio link",
            "No spelling or grammar errors",
        ]
        for item in checklist:
            key = f"checklist_{item[:20]}"
            st.checkbox(item, key=key)
