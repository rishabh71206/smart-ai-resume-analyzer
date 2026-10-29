"""Local (non-AI) scoring utilities.

These functions are deterministic and are used both by the UI and by the
offline engine, so they are covered by unit tests.
"""
from __future__ import annotations

import re

from config import COMMON_SKILLS, OVERALL_WEIGHTS

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "that", "this", "these",
    "those", "i", "we", "you", "he", "she", "it", "they", "my", "our",
    "your", "his", "her", "its", "their", "as", "if", "then", "than",
    "so", "yet", "both", "either", "not", "no", "nor", "just", "also",
    "using", "used", "work", "worked", "working", "role", "team",
}


def _skill_pattern(skill: str) -> re.Pattern[str]:
    # Lookarounds stop "C" matching "C++"/"C#", and "Java" matching "JavaScript".
    return re.compile(rf"(?<![\w+#]){re.escape(skill)}(?![\w+#])", re.IGNORECASE)


def skills_in(text: str) -> list[str]:
    """Return the canonical skills mentioned in *text*."""
    if not text:
        return []
    found = [skill for skill in COMMON_SKILLS if _skill_pattern(skill).search(text)]
    return sorted(dict.fromkeys(found), key=lambda value: (-len(value), value))


def compute_skill_score(resume_text: str, job_description: str = "") -> dict:
    """Return a skills-match breakdown using keyword matching.

    When a job description is supplied the score is the share of required
    skills present in the resume; otherwise it is a coverage heuristic.
    """
    resume_lower = (resume_text or "").lower()
    jd_lower = (job_description or "").lower()

    found_in_resume = skills_in(resume_text)
    required_in_jd = skills_in(job_description) if jd_lower else []

    if required_in_jd:
        matched = [skill for skill in required_in_jd if skill.lower() in resume_lower]
        missing = [skill for skill in required_in_jd if skill.lower() not in resume_lower]
        score = int(round(len(matched) / len(required_in_jd) * 100))
        coverage = score
    else:
        matched = found_in_resume
        missing = []
        score = min(len(found_in_resume) * 5, 100)
        coverage = score

    return {
        "score": score,
        "coverage": coverage,
        "found_in_resume": found_in_resume,
        "required_in_jd": required_in_jd,
        "matched": matched,
        "missing": missing,
    }


def compute_keyword_density(text: str, top_n: int = 30) -> dict[str, int]:
    """Return word frequency of meaningful tokens (no stopwords)."""
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#.]{2,}\b", (text or "").lower())
    frequency: dict[str, int] = {}
    for word in words:
        if word in STOPWORDS or len(word) < 3:
            continue
        frequency[word] = frequency.get(word, 0) + 1
    ranked = sorted(frequency.items(), key=lambda item: (-item[1], item[0]))
    return dict(ranked[:top_n])


def compute_resume_completeness(sections: dict) -> dict:
    """Score resume completeness based on which sections are present."""
    keys = {key.lower() for key in sections}
    important = {
        "contact / header": bool(keys & {"header", "contact"}),
        "summary / objective": bool(keys & {"summary", "objective", "profile", "about"}),
        "experience": bool(keys & {"experience", "work experience", "employment", "professional experience"}),
        "education": bool(keys & {"education", "academic"}),
        "skills": bool(keys & {"skills", "technical skills", "core competencies", "technologies"}),
        "projects": bool(keys & {"projects", "personal projects", "selected projects"}),
        "certifications": bool(keys & {"certifications", "certificates", "awards", "achievements"}),
    }

    present = sum(important.values())
    score = int(round(present / len(important) * 100))
    return {
        "sections_present": important,
        "completeness_score": score,
        "missing_sections": [name for name, found in important.items() if not found],
    }


def weighted_overall_score(ai_score: int, skill_score: int, completeness: int) -> int:
    """Combine multiple signals into a single weighted overall score."""
    ai = _as_score(ai_score)
    skills = _as_score(skill_score)
    complete = _as_score(completeness)
    combined = (
        ai * OVERALL_WEIGHTS["ai"]
        + skills * OVERALL_WEIGHTS["skills"]
        + complete * OVERALL_WEIGHTS["completeness"]
    )
    return min(int(round(combined)), 100)


def _as_score(value: object) -> int:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, int(number)))
