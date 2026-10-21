"""
AI Engine — wraps Google Gemini to power resume analysis and interview features.
"""
import json
import re
from typing import Optional

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL


# ── Initialise Gemini ─────────────────────────────────────────────────────────

def _get_model():
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Please add it to your .env file."
        )
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)


# ── Resume Analysis ───────────────────────────────────────────────────────────

def analyze_resume(resume_text: str, job_description: str = "") -> dict:
    """
    Full AI analysis of a resume.
    Returns a structured dict with scores, strengths, weaknesses, suggestions.
    """
    model = _get_model()

    jd_section = (
        f"\n\nJob Description to match against:\n{job_description}"
        if job_description.strip()
        else ""
    )

    prompt = f"""
You are an expert HR professional and resume coach with 15+ years of experience.

Analyze the following resume and return a JSON object (and ONLY JSON, no markdown fences).

Resume:
{resume_text}
{jd_section}

Return this exact JSON structure:
{{
  "overall_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "sections_score": {{
    "contact_info": <0-10>,
    "summary": <0-10>,
    "experience": <0-10>,
    "education": <0-10>,
    "skills": <0-10>,
    "formatting": <0-10>
  }},
  "skills_found": [<list of skills detected>],
  "missing_skills": [<list of important skills missing {"for the JD" if job_description else "in general"}>],
  "strengths": [<3-5 bullet strings>],
  "weaknesses": [<3-5 bullet strings>],
  "suggestions": [<5-7 actionable improvement suggestions>],
  "keywords_found": [<list of industry keywords present>],
  "keywords_missing": [<list of important keywords missing>],
  "experience_years": <estimated total years of experience as integer or null>,
  "education_level": "<highest degree detected, e.g. Bachelor's, Master's, PhD, or Unknown>",
  "job_titles": [<list of job titles found>],
  "summary_review": "<2-3 sentence review of the resume summary/objective section>",
  "overall_review": "<3-4 sentence holistic review>"
}}
"""

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


def match_job_description(resume_text: str, job_description: str) -> dict:
    """Compute a detailed JD-to-resume match report."""
    model = _get_model()

    prompt = f"""
You are an ATS (Applicant Tracking System) expert.

Compare this resume against the job description and return ONLY a JSON object.

Resume:
{resume_text}

Job Description:
{job_description}

Return this exact JSON:
{{
  "match_score": <integer 0-100>,
  "matched_skills": [<skills in both resume and JD>],
  "missing_skills": [<skills in JD but not in resume>],
  "extra_skills": [<skills in resume not required by JD>],
  "matched_keywords": [<keywords matched>],
  "missing_keywords": [<important JD keywords missing>],
  "experience_match": "<Met / Partially Met / Not Met>",
  "education_match": "<Met / Partially Met / Not Met>",
  "recommendation": "<Strongly Recommend / Recommend / Neutral / Do Not Recommend>",
  "fit_summary": "<2-3 sentences explaining the overall fit>"
}}
"""

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


# ── Interview Bot ─────────────────────────────────────────────────────────────

def generate_interview_questions(
    resume_text: str,
    job_role: str,
    difficulty: str = "Mixed",
    num_questions: int = 5,
    question_types: Optional[list[str]] = None,
) -> list[dict]:
    """
    Generate tailored interview questions based on the resume and target role.
    Returns a list of question dicts.
    """
    model = _get_model()

    types_str = (
        ", ".join(question_types)
        if question_types
        else "Behavioral, Technical, Situational"
    )

    prompt = f"""
You are a senior technical interviewer preparing for a {job_role} interview.

Based on the candidate's resume below, generate exactly {num_questions} interview questions.
Difficulty: {difficulty}
Question types to include: {types_str}

Resume:
{resume_text}

Return ONLY a JSON array (no markdown), each element:
{{
  "id": <1-based integer>,
  "question": "<the interview question>",
  "type": "<Behavioral | Technical | Situational | HR>",
  "difficulty": "<Easy | Medium | Hard>",
  "topic": "<what skill/area this tests>",
  "hint": "<what a good answer should include>"
}}
"""

    response = model.generate_content(prompt)
    result = _parse_json_response(response.text)
    # Handle both list and dict-wrapped responses
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("questions", "interview_questions", "data"):
            if key in result and isinstance(result[key], list):
                return result[key]
    return []


def evaluate_answer(
    question: str,
    answer: str,
    job_role: str,
    expected_hints: str = "",
) -> dict:
    """
    Evaluate a candidate's interview answer.
    Returns score, feedback, and a model answer.
    """
    model = _get_model()

    prompt = f"""
You are an expert interviewer evaluating a candidate's response for a {job_role} role.

Question: {question}
Candidate's Answer: {answer}
{"Expected answer hints: " + expected_hints if expected_hints else ""}

Return ONLY a JSON object:
{{
  "score": <integer 0-10>,
  "grade": "<Excellent | Good | Average | Poor>",
  "strengths": [<what the candidate did well>],
  "improvements": [<what could be improved>],
  "model_answer": "<a concise model answer>",
  "feedback": "<2-3 sentence constructive feedback>"
}}
"""

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


def generate_career_advice(resume_text: str, target_role: str) -> dict:
    """Generate personalised career roadmap and advice."""
    model = _get_model()

    prompt = f"""
You are a career counsellor specialising in tech careers.

Based on the resume below and the target role "{target_role}", give personalised advice.

Resume:
{resume_text}

Return ONLY a JSON object:
{{
  "current_level": "<Junior | Mid-level | Senior | Lead | Executive>",
  "target_role_fit": "<percentage as integer>",
  "skill_gaps": [<top 5 skills to develop>],
  "recommended_certifications": [<3-5 certifications with their names>],
  "learning_resources": [
    {{"topic": "<topic>", "resource": "<course/book/platform>", "url": "<url if known or empty string>"}}
  ],
  "timeline": "<realistic timeline to reach target role>",
  "action_plan": [<5 concrete next steps>],
  "salary_range": "<estimated salary range for target role in USD>",
  "career_advice": "<3-4 sentences of personalised advice>"
}}
"""

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


# ── Helper ────────────────────────────────────────────────────────────────────

def _parse_json_response(text: str) -> dict | list:
    """Strip markdown fences and parse JSON from model output."""
    # Remove ```json ... ``` or ``` ... ```
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Attempt to extract the first JSON object/array
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", clean)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {"error": "Could not parse AI response", "raw": text[:500]}
