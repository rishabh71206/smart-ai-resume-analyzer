"""
Scoring utilities — compute local (non-AI) skill match and keyword scores.
"""
import re
from config import COMMON_SKILLS, SCORE_WEIGHTS


def compute_skill_score(resume_text: str, job_description: str = "") -> dict:
    """
    Return a skills-match breakdown using simple keyword matching.
    Used as a quick local score alongside the AI score.
    """
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    found_in_resume = [s for s in COMMON_SKILLS if s.lower() in resume_lower]

    if jd_lower:
        required_in_jd = [s for s in COMMON_SKILLS if s.lower() in jd_lower]
        matched = [s for s in required_in_jd if s.lower() in resume_lower]
        missing = [s for s in required_in_jd if s.lower() not in resume_lower]
        score = int((len(matched) / len(required_in_jd)) * 100) if required_in_jd else 0
    else:
        required_in_jd = []
        matched = found_in_resume
        missing = []
        score = min(len(found_in_resume) * 5, 100)  # rough heuristic

    return {
        "score": score,
        "found_in_resume": found_in_resume,
        "required_in_jd": required_in_jd,
        "matched": matched,
        "missing": missing,
    }


def compute_keyword_density(text: str) -> dict:
    """Return word frequency of meaningful tokens (no stopwords)."""
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "that", "this", "these",
        "those", "i", "we", "you", "he", "she", "it", "they", "my", "our",
        "your", "his", "her", "its", "their", "as", "if", "then", "than",
        "so", "yet", "both", "either", "not", "no", "nor", "just", "also",
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    # Sort by frequency descending, return top 30
    sorted_freq = dict(sorted(freq.items(), key=lambda x: x[1], reverse=True)[:30])
    return sorted_freq


def compute_resume_completeness(sections: dict) -> dict:
    """
    Score resume completeness based on which sections are present.
    Returns a dict with section flags and a total completeness score (0-100).
    """
    important_sections = {
        "contact / header": any(k in sections for k in ["header", "contact"]),
        "summary / objective": any(k in sections for k in ["summary", "objective", "profile"]),
        "experience": any(k in sections for k in ["experience", "work experience", "employment"]),
        "education": any(k in sections for k in ["education", "academic"]),
        "skills": any(k in sections for k in ["skills", "technical skills", "core competencies"]),
        "projects": "projects" in sections or "personal projects" in sections,
        "certifications": any(k in sections for k in ["certifications", "certificates"]),
    }

    present_count = sum(important_sections.values())
    completeness_score = int((present_count / len(important_sections)) * 100)

    return {
        "sections_present": important_sections,
        "completeness_score": completeness_score,
        "missing_sections": [s for s, present in important_sections.items() if not present],
    }


def weighted_overall_score(ai_score: int, skill_score: int, completeness: int) -> int:
    """Combine multiple signals into a single weighted overall score."""
    combined = (
        ai_score * 0.60
        + skill_score * 0.25
        + completeness * 0.15
    )
    return min(int(combined), 100)
