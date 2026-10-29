from __future__ import annotations

from utils.pdf_report import _safe, generate_pdf_report

ANALYSIS = {
    "overall_score": 84,
    "ats_score": 83,
    "sections_score": {
        "content": 10,
        "formatting": 9,
        "keywords": 10,
        "impact": 9,
        "clarity": 9,
    },
    "summary_review": "A strong Python resume with clear impact - ready for tailoring.",
    "overall_review": "The structure is clean and the projects are relevant.",
    "strengths": ["Clear skills section", "Quantified impact"],
    "weaknesses": ["No portfolio link"],
    "suggestions": ["Add a GitHub link", "Tailor the summary per role"],
    "skills_found": ["Python", "SQL", "Docker"],
    "missing_skills": ["AWS"],
    "keywords_found": ["Python", "REST API"],
    "keywords_missing": ["Kubernetes"],
    "experience_years": 2,
    "education_level": "Bachelor's",
}

JD_MATCH = {
    "match_score": 78,
    "recommendation": "Recommend",
    "fit_summary": "Good overlap on Python and SQL.",
    "matched_skills": ["Python", "SQL"],
    "missing_skills": ["AWS"],
}


def test_generate_pdf_report() -> None:
    pdf = generate_pdf_report(ANALYSIS, "Rishabh Srivastava", JD_MATCH)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_generate_pdf_report_without_jd() -> None:
    pdf = generate_pdf_report(ANALYSIS, "Rishabh Srivastava")
    assert pdf.startswith(b"%PDF")


def test_generate_pdf_report_handles_empty_analysis() -> None:
    pdf = generate_pdf_report({}, "Candidate")
    assert pdf.startswith(b"%PDF")


def test_safe_normalises_unicode() -> None:
    value = _safe("Rishabh \u2014 Srivastava \u2022 Python \U0001f600")
    assert "\u2014" not in value
    assert "\u2022" not in value
    assert value.isascii() or all(ord(char) < 256 for char in value)
    assert "Rishabh" in value
