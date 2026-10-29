"""Gemini-backed AI layer with a deterministic offline fallback.

The public functions mirror :mod:`utils.offline_engine`.  Each call tries
Gemini first (when an API key and the SDK are available) and falls back to the
offline engine on any error, so the UI always receives a usable result.  Every
returned dict carries a ``source`` key (``"ai"`` or ``"offline"``).
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Callable, TypeVar

from config import (
    AI_MAX_RETRIES,
    AI_TIMEOUT_SECONDS,
    GEMINI_API_KEY,
    GEMINI_MODELS,
)
from utils import offline_engine
from utils.resume_parser import truncate

log = logging.getLogger(__name__)

T = TypeVar("T")

_client: Any | None = None
_model_in_use: str = GEMINI_MODELS[0] if GEMINI_MODELS else "gemini-2.5-flash"


class AIError(RuntimeError):
    """Raised when Gemini cannot produce a usable response."""


# ── Client / availability ─────────────────────────────────────────────────────

def _sdk_installed() -> bool:
    try:
        import google.genai  # noqa: F401
    except ImportError:
        return False
    return True


def ai_available() -> bool:
    """True when a key is configured and the SDK can be imported."""
    return bool(GEMINI_API_KEY) and _sdk_installed()


def ai_status() -> dict[str, Any]:
    """Small status dict used by the sidebar."""
    if not GEMINI_API_KEY:
        return {"available": False, "model": None, "reason": "GEMINI_API_KEY is not set."}
    if not _sdk_installed():
        return {"available": False, "model": None, "reason": "google-genai is not installed."}
    return {"available": True, "model": _model_in_use, "reason": ""}


def reset_client() -> None:
    """Drop the cached client (used by tests and after changing the key)."""
    global _client
    _client = None


def _get_client() -> Any:
    global _client
    if _client is not None:
        return _client

    if not GEMINI_API_KEY:
        raise AIError("GEMINI_API_KEY is not configured.")
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover - covered by ai_available
        raise AIError("google-genai is not installed. Run: pip install google-genai") from exc

    try:
        http_options = types.HttpOptions(timeout=AI_TIMEOUT_SECONDS * 1000)
        _client = genai.Client(api_key=GEMINI_API_KEY, http_options=http_options)
    except Exception:
        # Older SDK versions do not accept http_options; the default timeout is fine.
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


# ── Generation helpers ────────────────────────────────────────────────────────

def _generate(
    prompt: str,
    *,
    json_mode: bool = False,
    temperature: float = 0.4,
    max_output_tokens: int = 2048,
) -> str:
    """Call Gemini with model fallback and bounded retries."""
    from google.genai import types

    client = _get_client()
    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_mime_type="application/json" if json_mode else "text/plain",
    )

    errors: list[str] = []
    for model in GEMINI_MODELS:
        for attempt in range(AI_MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                text = (getattr(response, "text", None) or "").strip()
                if not text:
                    raise AIError("Gemini returned an empty response.")
                global _model_in_use
                _model_in_use = model
                return text
            except Exception as exc:  # SDK raises several transport/API types
                message = str(exc)
                errors.append(f"{model}: {message}")
                lowered = message.lower()

                if any(token in lowered for token in ("api key", "unauthenticated", "permission denied", "401", "403")):
                    raise AIError(f"Gemini authentication failed: {message}") from exc
                if any(token in lowered for token in ("not found", "404", "not supported", "does not exist", "invalid model")):
                    break  # try the next model
                if attempt < AI_MAX_RETRIES:
                    time.sleep(min(2 ** attempt, 6))

    raise AIError("Gemini request failed: " + " | ".join(errors[-3:]))


def _parse_json(text: str) -> Any:
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", cleaned) or re.search(r"\[[\s\S]*\]", cleaned)
    if not match:
        raise AIError("Gemini returned text that is not valid JSON.")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise AIError("Gemini returned malformed JSON.") from exc


def _run(
    ai_call: Callable[[], T],
    offline_call: Callable[[], T],
    label: str,
) -> T:
    """Execute *ai_call*, falling back to *offline_call* on any failure."""
    if not ai_available():
        return _mark(offline_call(), "offline", ai_status()["reason"])

    try:
        return _mark(ai_call(), "ai", "")
    except AIError as exc:
        log.warning("%s: falling back to offline engine (%s)", label, exc)
        return _mark(offline_call(), "offline", str(exc))
    except Exception as exc:  # defensive: never break the page
        log.exception("%s: unexpected AI failure", label)
        return _mark(offline_call(), "offline", str(exc))


def _mark(result: T, source: str, reason: str) -> T:
    if isinstance(result, dict):
        result["source"] = source
        if reason:
            result["offline_reason"] = reason
    elif isinstance(result, list):
        for item in result:
            if isinstance(item, dict):
                item["source"] = source
    return result


# ── Normalisers ───────────────────────────────────────────────────────────────

def _as_int(value: Any, default: int = 0, low: int = 0, high: int = 100) -> int:
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def _as_list(value: Any, limit: int = 10) -> list[str]:
    if isinstance(value, str):
        value = [line.strip(" -•") for line in value.splitlines() if line.strip()]
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item).strip() for item in value if str(item).strip()][:limit]


def _normalise_analysis(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise AIError("Analysis response was not an object.")
    sections = data.get("sections_score")
    if not isinstance(sections, dict):
        sections = {}
    normalised_sections = {
        str(key).replace(" ", "_").lower(): _as_int(value, 5, 0, 10)
        for key, value in sections.items()
    } or {key: 5 for key in ("content", "formatting", "keywords", "impact", "clarity")}

    years = data.get("experience_years", 0)
    try:
        years = int(float(str(years).split()[0]))
    except (TypeError, ValueError):
        years = 0

    return {
        "overall_score": _as_int(data.get("overall_score"), 0),
        "ats_score": _as_int(data.get("ats_score"), 0),
        "sections_score": normalised_sections,
        "summary_review": str(data.get("summary_review", "")).strip(),
        "overall_review": str(data.get("overall_review", "")).strip(),
        "strengths": _as_list(data.get("strengths")),
        "weaknesses": _as_list(data.get("weaknesses")),
        "suggestions": _as_list(data.get("suggestions"), 8),
        "skills_found": _as_list(data.get("skills_found"), 20),
        "missing_skills": _as_list(data.get("missing_skills"), 15),
        "keywords_found": _as_list(data.get("keywords_found"), 20),
        "keywords_missing": _as_list(data.get("keywords_missing"), 15),
        "experience_years": max(0, min(50, years)),
        "education_level": str(data.get("education_level", "Not specified")).strip() or "Not specified",
        "job_titles": _as_list(data.get("job_titles"), 6),
    }


def _normalise_match(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise AIError("Match response was not an object.")
    recommendation = str(data.get("recommendation", "Neutral")).strip()
    if recommendation not in {"Strongly Recommend", "Recommend", "Neutral", "Do Not Recommend"}:
        recommendation = "Neutral"
    return {
        "match_score": _as_int(data.get("match_score"), 0),
        "recommendation": recommendation,
        "fit_summary": str(data.get("fit_summary", "")).strip(),
        "matched_skills": _as_list(data.get("matched_skills"), 20),
        "missing_skills": _as_list(data.get("missing_skills"), 20),
        "experience_match": str(data.get("experience_match", "Not specified")).strip(),
        "education_match": str(data.get("education_match", "Not specified")).strip(),
        "keywords_to_add": _as_list(data.get("keywords_to_add"), 12),
    }


def _normalise_questions(data: Any, count: int) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        data = data.get("questions") or data.get("items") or []
    if not isinstance(data, list):
        raise AIError("Question response was not a list.")
    questions: list[dict[str, Any]] = []
    for index, item in enumerate(data[:count], 1):
        if isinstance(item, str):
            item = {"question": item}
        if not isinstance(item, dict) or not str(item.get("question", "")).strip():
            continue
        questions.append(
            {
                "id": index,
                "question": str(item["question"]).strip(),
                "type": str(item.get("type", "Behavioral")).strip().title(),
                "difficulty": str(item.get("difficulty", "Medium")).strip().title(),
                "topic": str(item.get("topic", "")).strip() or "General",
                "hint": str(item.get("hint", "")).strip() or "Use a concrete example and quantify the result.",
            }
        )
    if not questions:
        raise AIError("Gemini returned no usable questions.")
    return questions


def _normalise_evaluation(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise AIError("Evaluation response was not an object.")
    score = _as_int(data.get("score"), 0, 0, 10)
    grade = str(data.get("grade", "")).strip()
    if grade not in {"Excellent", "Good", "Average", "Poor"}:
        grade = "Excellent" if score >= 8 else "Good" if score >= 6 else "Average" if score >= 4 else "Poor"
    return {
        "score": score,
        "grade": grade,
        "strengths": _as_list(data.get("strengths"), 5),
        "improvements": _as_list(data.get("improvements"), 5),
        "feedback": str(data.get("feedback", "")).strip(),
        "model_answer": str(data.get("model_answer", "")).strip(),
    }


def _normalise_career(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise AIError("Career response was not an object.")
    resources = data.get("learning_resources") or []
    normalised_resources = []
    for item in resources[:8]:
        if isinstance(item, dict):
            normalised_resources.append(
                {
                    "topic": str(item.get("topic", "")).strip(),
                    "resource": str(item.get("resource", "")).strip(),
                    "url": str(item.get("url", "")).strip(),
                }
            )
        elif isinstance(item, str):
            normalised_resources.append({"topic": "", "resource": item, "url": ""})
    return {
        "current_level": str(data.get("current_level", "Entry-level")).strip(),
        "target_role_fit": _as_int(data.get("target_role_fit"), 0),
        "timeline": str(data.get("timeline", "")).strip() or "3-6 months",
        "salary_range": str(data.get("salary_range", "")).strip() or "Not specified",
        "career_advice": str(data.get("career_advice", "")).strip(),
        "skill_gaps": _as_list(data.get("skill_gaps"), 8),
        "recommended_certifications": _as_list(data.get("recommended_certifications"), 6),
        "learning_resources": normalised_resources,
        "action_plan": _as_list(data.get("action_plan"), 8),
    }


def _normalise_jobs(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise AIError("Job response was not an object.")
    roles = []
    for item in (data.get("top_roles") or [])[:5]:
        if not isinstance(item, dict):
            continue
        roles.append(
            {
                "title": str(item.get("title", "")).strip() or "Technology Role",
                "match": _as_int(item.get("match"), 0),
                "salary_range": str(item.get("salary_range", "")).strip() or "Not specified",
                "companies": _as_list(item.get("companies"), 6),
                "skills_needed": _as_list(item.get("skills_needed"), 8),
                "description": str(item.get("description", "")).strip(),
            }
        )
    if not roles:
        raise AIError("Gemini returned no job roles.")
    return {
        "top_roles": roles,
        "industries": _as_list(data.get("industries"), 6),
        "career_level": str(data.get("career_level", "Mid-level")).strip(),
        "job_search_tips": _as_list(data.get("job_search_tips"), 6),
    }


def _normalise_comparison(data: Any, name1: str, name2: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise AIError("Comparison response was not an object.")
    scores = data.get("scores") if isinstance(data.get("scores"), dict) else {}
    strengths = data.get("strengths") if isinstance(data.get("strengths"), dict) else {}
    weaknesses = data.get("weaknesses") if isinstance(data.get("weaknesses"), dict) else {}

    def pick(mapping: dict, name: str) -> Any:
        if name in mapping:
            return mapping[name]
        for key, value in mapping.items():
            if str(key).strip().lower() == name.strip().lower():
                return value
        return {}

    normalised_scores = {}
    for name in (name1, name2):
        raw = pick(scores, name)
        if not isinstance(raw, dict):
            raw = {}
        normalised_scores[name] = {
            key: _as_int(raw.get(key), 0)
            for key in ("overall", "skills", "experience", "education", "presentation")
        }

    winner = str(data.get("winner", "")).strip()
    if winner not in (name1, name2):
        winner = name1 if normalised_scores[name1]["overall"] >= normalised_scores[name2]["overall"] else name2

    return {
        "winner": winner,
        "scores": normalised_scores,
        "strengths": {name: _as_list(pick(strengths, name), 4) for name in (name1, name2)},
        "weaknesses": {name: _as_list(pick(weaknesses, name), 4) for name in (name1, name2)},
        "verdict": str(data.get("verdict", "")).strip(),
    }


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_resume(resume_text: str, job_description: str = "") -> dict[str, Any]:
    """Full resume review with scores, strengths, gaps and suggestions."""
    resume = truncate(resume_text, 9000)
    jd_block = f"\nJob description:\n{truncate(job_description, 3500)}\n" if job_description.strip() else ""

    def ai_call() -> dict[str, Any]:
        prompt = f"""You are a senior technical recruiter and ATS specialist.
Analyse the resume and return ONLY a JSON object with exactly these keys:
{{
  "overall_score": 0-100,
  "ats_score": 0-100,
  "sections_score": {{"content": 0-10, "formatting": 0-10, "keywords": 0-10, "impact": 0-10, "clarity": 0-10}},
  "summary_review": "two specific sentences",
  "overall_review": "three or four specific sentences",
  "strengths": ["3-5 items"],
  "weaknesses": ["3-5 items"],
  "suggestions": ["3-6 actionable items"],
  "skills_found": ["skills actually present"],
  "missing_skills": ["skills expected for the target role but absent"],
  "keywords_found": ["ATS keywords present"],
  "keywords_missing": ["ATS keywords missing"],
  "experience_years": 0,
  "education_level": "e.g. Bachelor's",
  "job_titles": ["titles held"]
}}
Be specific, quote the resume where useful, and do not invent experience.
{jd_block}
Resume:
{resume}
"""
        return _normalise_analysis(_parse_json(_generate(prompt, json_mode=True, temperature=0.3)))

    return _run(ai_call, lambda: offline_engine.analyze_resume(resume_text, job_description), "analyze_resume")


def match_job_description(resume_text: str, job_description: str) -> dict[str, Any]:
    """Score a resume against a specific job description."""
    resume = truncate(resume_text, 7000)
    jd = truncate(job_description, 5000)

    def ai_call() -> dict[str, Any]:
        prompt = f"""Compare this resume with the job description like an experienced hiring manager.
Return ONLY a JSON object with exactly these keys:
{{
  "match_score": 0-100,
  "recommendation": "Strongly Recommend" | "Recommend" | "Neutral" | "Do Not Recommend",
  "fit_summary": "two or three sentences",
  "matched_skills": ["required skills present in the resume"],
  "missing_skills": ["required skills absent from the resume"],
  "experience_match": "short phrase",
  "education_match": "short phrase",
  "keywords_to_add": ["keywords the candidate should add"]
}}
Only count skills that are explicitly evidenced.

Job description:
{jd}

Resume:
{resume}
"""
        return _normalise_match(_parse_json(_generate(prompt, json_mode=True, temperature=0.2)))

    return _run(
        ai_call,
        lambda: offline_engine.match_job_description(resume_text, job_description),
        "match_job_description",
    )


def generate_interview_questions(
    resume_text: str,
    job_role: str,
    difficulty: str = "Mixed",
    num_questions: int = 5,
    question_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Generate personalised interview questions."""
    count = max(1, min(int(num_questions), 10))
    types = ", ".join(question_types or ["Behavioral", "Technical"])

    def ai_call() -> list[dict[str, Any]]:
        prompt = f"""Create exactly {count} interview questions for a {job_role} role.
Difficulty: {difficulty}. Question types: {types}.
Use the resume to make at least half the questions specific to the candidate's projects and skills.
Return ONLY a JSON array:
[{{"question": "...", "type": "Behavioral|Technical|Situational|HR", "difficulty": "Easy|Medium|Hard", "topic": "...", "hint": "one sentence"}}]

Resume:
{truncate(resume_text, 6000)}
"""
        return _normalise_questions(
            _parse_json(_generate(prompt, json_mode=True, temperature=0.7, max_output_tokens=3000)),
            count,
        )

    return _run(
        ai_call,
        lambda: offline_engine.generate_interview_questions(
            resume_text, job_role, difficulty, count, question_types
        ),
        "generate_interview_questions",
    )


def evaluate_answer(
    question: str,
    answer: str,
    job_role: str = "",
    expected_hints: str = "",
) -> dict[str, Any]:
    """Evaluate a practice interview answer."""

    def ai_call() -> dict[str, Any]:
        prompt = f"""You are a supportive but demanding interview coach.
Evaluate the candidate's answer for a {job_role or 'technical'} interview.
Return ONLY a JSON object:
{{
  "score": 0-10,
  "grade": "Excellent" | "Good" | "Average" | "Poor",
  "strengths": ["2-3 specific things done well"],
  "improvements": ["2-3 specific fixes"],
  "feedback": "2-3 sentences",
  "model_answer": "a strong example answer in 4-6 sentences"
}}

Question: {question}
Hint: {expected_hints}
Answer:
{answer}
"""
        return _normalise_evaluation(_parse_json(_generate(prompt, json_mode=True, temperature=0.4)))

    return _run(
        ai_call,
        lambda: offline_engine.evaluate_answer(question, answer, job_role, expected_hints),
        "evaluate_answer",
    )


def generate_career_advice(resume_text: str, target_role: str) -> dict[str, Any]:
    """Build a skill-gap roadmap for a target role."""

    def ai_call() -> dict[str, Any]:
        prompt = f"""Act as a career coach for a candidate targeting "{target_role}".
Return ONLY a JSON object:
{{
  "current_level": "Entry-level | Junior | Mid-level | Senior",
  "target_role_fit": 0-100,
  "timeline": "realistic time to become interview-ready",
  "salary_range": "realistic range for this level",
  "career_advice": "3-4 sentences",
  "skill_gaps": ["ordered by priority"],
  "recommended_certifications": ["3 specific certificates"],
  "learning_resources": [{{"topic": "...", "resource": "...", "url": "https://..."}}],
  "action_plan": ["5 concrete steps"]
}}
Base the gaps on the resume, not generic advice.

Resume:
{truncate(resume_text, 7000)}
"""
        return _normalise_career(_parse_json(_generate(prompt, json_mode=True, temperature=0.5)))

    return _run(
        ai_call,
        lambda: offline_engine.generate_career_advice(resume_text, target_role),
        "generate_career_advice",
    )


def recommend_jobs(resume_text: str) -> dict[str, Any]:
    """Recommend five realistic job matches."""

    def ai_call() -> dict[str, Any]:
        prompt = f"""You are a job placement specialist.
Based on this resume, recommend exactly 5 realistic roles.
Return ONLY a JSON object:
{{
  "top_roles": [
    {{"title": "...", "match": 0-100, "salary_range": "...", "companies": ["4 examples"], "skills_needed": ["6 skills"], "description": "one sentence"}}
  ],
  "industries": ["4 industries"],
  "career_level": "Entry-level | Junior | Mid-level | Senior",
  "job_search_tips": ["4 specific tips"]
}}

Resume:
{truncate(resume_text, 7000)}
"""
        return _normalise_jobs(_parse_json(_generate(prompt, json_mode=True, temperature=0.5)))

    return _run(ai_call, lambda: offline_engine.recommend_jobs(resume_text), "recommend_jobs")


def compare_resumes(resume1: str, resume2: str, name1: str, name2: str) -> dict[str, Any]:
    """Compare two resumes on a consistent rubric."""

    def ai_call() -> dict[str, Any]:
        prompt = f"""Compare these two resumes objectively for a hiring manager.
Return ONLY a JSON object:
{{
  "winner": "{name1}" or "{name2}",
  "scores": {{
    "{name1}": {{"overall": 0-100, "skills": 0-100, "experience": 0-100, "education": 0-100, "presentation": 0-100}},
    "{name2}": {{"overall": 0-100, "skills": 0-100, "experience": 0-100, "education": 0-100, "presentation": 0-100}}
  }},
  "strengths": {{"{name1}": ["3 items"], "{name2}": ["3 items"]}},
  "weaknesses": {{"{name1}": ["3 items"], "{name2}": ["3 items"]}},
  "verdict": "3 sentences explaining the decision"
}}

{name1}:
{truncate(resume1, 5000)}

{name2}:
{truncate(resume2, 5000)}
"""
        return _normalise_comparison(
            _parse_json(_generate(prompt, json_mode=True, temperature=0.3)),
            name1,
            name2,
        )

    return _run(
        ai_call,
        lambda: offline_engine.compare_resumes(resume1, resume2, name1, name2),
        "compare_resumes",
    )


def build_resume(data: dict[str, Any]) -> dict[str, Any]:
    """Generate an ATS-friendly resume in Markdown."""

    def ai_call() -> dict[str, Any]:
        details = "\n".join(f"{key}: {value}" for key, value in data.items() if str(value).strip())
        prompt = f"""Write a complete, ATS-friendly resume in Markdown for this candidate.
Use strong action verbs, quantify achievements where the input allows it, and keep it honest.
Include: summary, skills, experience, education, projects, achievements and certifications
(omit a section only when the input has nothing for it).
Return ONLY the resume text, no code fences and no commentary.

Candidate details:
{details}
"""
        text = _generate(prompt, temperature=0.6, max_output_tokens=2500).strip()
        text = re.sub(r"^```(?:markdown)?|```$", "", text).strip()
        if not text:
            raise AIError("Gemini returned an empty resume.")
        return {"resume": text + "\n"}

    return _run(ai_call, lambda: offline_engine.build_resume(data), "build_resume")


def chat_reply(
    resume_text: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Answer a free-form question about the resume."""
    transcript = ""
    for message in (history or [])[-8:]:
        role = "User" if message.get("role") == "user" else "Assistant"
        transcript += f"{role}: {message.get('content', '')}\n"

    def ai_call() -> dict[str, Any]:
        prompt = f"""You are a concise, honest career coach embedded in a resume analyzer.
Answer the user's question using only the resume and conversation below.
If the resume does not contain the answer, say so and suggest what to add.
Keep the answer under 180 words. Use short paragraphs or bullets.

Resume:
{truncate(resume_text, 7000)}

Conversation:
{transcript}
User: {question}
"""
        answer = _generate(prompt, temperature=0.5, max_output_tokens=800).strip()
        if not answer:
            raise AIError("Gemini returned an empty answer.")
        return {"answer": answer}

    return _run(
        ai_call,
        lambda: offline_engine.chat_reply(resume_text, question, history),
        "chat_reply",
    )
