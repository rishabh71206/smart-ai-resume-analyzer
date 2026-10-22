"""
Page 7 – Resume Comparison
"""
import streamlit as st
import plotly.graph_objects as go
from utils.resume_parser import extract_text
from utils.ai_engine import _get_model
import json
import re


def compare_resumes(resume1: str, resume2: str, name1: str, name2: str) -> dict:
    model = _get_model()
    prompt = f"""
You are an expert HR professional. Compare these two resumes objectively.

Resume 1 ({name1}):
{resume1[:2000]}

Resume 2 ({name2}):
{resume2[:2000]}

Return ONLY a JSON object:
{{
  "winner": "{name1} or {name2}",
  "scores": {{
    "{name1}": {{
      "overall": 85,
      "skills": 80,
      "experience": 90,
      "education": 85,
      "presentation": 80
    }},
    "{name2}": {{
      "overall": 75,
      "skills": 70,
      "experience": 75,
      "education": 80,
      "presentation": 75
    }}
  }},
  "strengths": {{
    "{name1}": ["strength1", "strength2"],
    "{name2}": ["strength1", "strength2"]
  }},
  "weaknesses": {{
    "{name1}": ["weakness1"],
    "{name2}": ["weakness1"]
  }},
  "verdict": "2-3 sentence comparison summary"
}}
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
    st.title("👥 Resume Comparison")
    st.markdown("2 resumes compare karo — kaun better hai dekho!")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Resume 1")
        name1 = st.text_input("Candidate 1 Name", value="Candidate A", key="name1")
        file1 = st.file_uploader("Resume 1 Upload", type=["pdf", "docx", "txt"], key="comp1")

    with col2:
        st.subheader("📄 Resume 2")
        name2 = st.text_input("Candidate 2 Name", value="Candidate B", key="name2")
        file2 = st.file_uploader("Resume 2 Upload", type=["pdf", "docx", "txt"], key="comp2")

    if not file1 or not file2:
        st.info("👆 Dono resumes upload karo comparison ke liye!")
        return

    resume1 = extract_text(file1)
    resume2 = extract_text(file2)

    if st.button("⚖️ Compare Karo!", type="primary", use_container_width=True):
        with st.spinner("AI dono resumes compare kar raha hai..."):
            result = compare_resumes(resume1, resume2, name1, name2)
            st.session_state["comparison"] = result
            st.session_state["comp_names"] = (name1, name2)

    result = st.session_state.get("comparison")
    if not result:
        return

    names = st.session_state.get("comp_names", (name1, name2))

    # Winner banner
    winner = result.get("winner", "")
    st.markdown(f"""
<div style='background:linear-gradient(90deg,#22c55e,#16a34a);padding:20px;border-radius:10px;text-align:center;margin:10px 0'>
<h2 style='color:white;margin:0'>🏆 Winner: {winner}</h2>
</div>
""", unsafe_allow_html=True)

    # Verdict
    st.info(result.get("verdict", ""))

    # Radar chart comparison
    scores = result.get("scores", {})
    if scores:
        categories = ["overall", "skills", "experience", "education", "presentation"]
        cat_labels = ["Overall", "Skills", "Experience", "Education", "Presentation"]

        fig = go.Figure()
        colors = ["#2563eb", "#ef4444"]
        for i, name in enumerate(names):
            if name in scores:
                vals = [scores[name].get(c, 0) for c in categories]
                fig.add_trace(go.Scatterpolar(
                    r=vals, theta=cat_labels, fill="toself",
                    name=name, line_color=colors[i]
                ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Resume Comparison Radar",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # Score table
    st.markdown("---")
    st.subheader("📊 Score Breakdown")
    col1, col2 = st.columns(2)

    for i, name in enumerate(names):
        col = col1 if i == 0 else col2
        with col:
            st.markdown(f"**{name}**")
            if name in scores:
                for cat, label in zip(categories, cat_labels):
                    val = scores[name].get(cat, 0)
                    color = "#22c55e" if val >= 80 else "#eab308" if val >= 60 else "#ef4444"
                    st.markdown(f"**{label}:** :{val}/100")
                    st.progress(val/100)

    # Strengths & Weaknesses
    st.markdown("---")
    col1, col2 = st.columns(2)
    strengths = result.get("strengths", {})
    weaknesses = result.get("weaknesses", {})

    for i, name in enumerate(names):
        col = col1 if i == 0 else col2
        with col:
            st.markdown(f"### {name}")
            st.markdown("**✅ Strengths:**")
            for s in strengths.get(name, []):
                st.success(f"✔ {s}")
            st.markdown("**⚠️ Weaknesses:**")
            for w in weaknesses.get(name, []):
                st.warning(f"⚠ {w}")
