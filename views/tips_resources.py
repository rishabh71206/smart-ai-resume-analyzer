"""Page 4 - Resume Tips and Resources."""
from __future__ import annotations

import html

import streamlit as st

from utils.ui import page_header

TIPS = {
    "Writing a strong summary": [
        "Keep it to 2-4 sentences that state your role, focus and strongest proof point.",
        "Mention years of experience, specialisation and one measurable achievement.",
        "Tailor it to each application; generic summaries are ignored.",
        "Avoid personal pronouns (I, me, my).",
    ],
    "ATS optimisation": [
        "Use keywords directly from the job description.",
        "Avoid tables, headers, footers and text boxes that ATS parsers skip.",
        "Use standard headings: Experience, Education, Skills, Projects.",
        "Spell out acronyms once, e.g. Natural Language Processing (NLP).",
        "Keep a clean, single-column layout.",
    ],
    "Experience section": [
        "Use STAR: Situation, Task, Action, Result.",
        "Start every bullet with a strong action verb.",
        "Quantify outcomes: latency, revenue, users, time saved.",
        "Keep 3-5 bullets per role and show progression.",
    ],
    "Skills section": [
        "List hard skills first: languages, frameworks, databases, cloud.",
        "Group skills by category.",
        "Do not rate yourself with stars; it reads as subjective.",
        "Include the soft skills the role actually asks for.",
    ],
    "Formatting": [
        "One page for under five years of experience; two pages maximum otherwise.",
        "Use a consistent 10-12pt font and 0.5-1 inch margins.",
        "Submit PDF unless the employer asks for another format.",
        "Proofread; spelling mistakes are an instant red flag.",
    ],
    "Interview preparation": [
        "Research the company, product and recent news.",
        "Prepare 3-5 STAR stories that cover common behavioural questions.",
        "Practise with the Interview Bot on this app.",
        "Prepare two thoughtful questions for the interviewer.",
        "Send a short thank-you email within 24 hours.",
    ],
}

RESOURCES = [
    ("LinkedIn Learning", "Courses for technical and business skills", "https://www.linkedin.com/learning/"),
    ("Coursera", "University-level courses and specialisations", "https://www.coursera.org/"),
    ("LeetCode", "Coding interview practice", "https://leetcode.com/"),
    ("HackerRank", "Coding challenges and certifications", "https://www.hackerrank.com/"),
    ("Glassdoor", "Company reviews and salary data", "https://www.glassdoor.com/"),
    ("Levels.fyi", "Tech salary transparency", "https://www.levels.fyi/"),
    ("Resume Worded", "Resume scoring and feedback", "https://resumeworded.com/"),
    ("STAR method guide", "Behavioural interview technique", "https://www.themuse.com/advice/star-interview-method"),
]

CHECKLIST = [
    "Contact information: name, email, phone, LinkedIn",
    "Professional summary or objective",
    "Work experience in reverse chronological order",
    "Quantified achievements with numbers and percentages",
    "Education with relevant coursework or GPA",
    "Technical skills grouped by category",
    "Projects with stack and impact",
    "Certifications and awards",
    "GitHub or portfolio link",
    "No spelling or grammar errors",
]


def render() -> None:
    page_header(
        "Tips and Resources",
        "Practical advice and trusted links to tighten your resume and interviews.",
        "📚",
    )

    tips_tab, resources_tab, checklist_tab = st.tabs(["Tips", "Resources", "Checklist"])

    with tips_tab:
        for section, tips in TIPS.items():
            with st.expander(section):
                for tip in tips:
                    st.markdown(f"- {tip}")

    with resources_tab:
        columns = st.columns(2)
        for index, (name, description, url) in enumerate(RESOURCES):
            with columns[index % 2]:
                st.markdown(
                    f'<div class="rs-card"><strong><a href="{html.escape(url)}" target="_blank" rel="noopener">'
                    f"{html.escape(name)}</a></strong><p>{html.escape(description)}</p></div>",
                    unsafe_allow_html=True,
                )

    with checklist_tab:
        st.markdown("Tick each item before you apply.")
        for item in CHECKLIST:
            st.checkbox(item, key=f"checklist_{item[:24]}")
        completed = sum(1 for item in CHECKLIST if st.session_state.get(f"checklist_{item[:24]}"))
        st.progress(completed / len(CHECKLIST), text=f"{completed}/{len(CHECKLIST)} complete")
