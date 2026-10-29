from __future__ import annotations

from utils.scorer import (
    compute_keyword_density,
    compute_resume_completeness,
    compute_skill_score,
    skills_in,
    weighted_overall_score,
)


def test_skills_in_respects_word_boundaries() -> None:
    found = skills_in("Python, C, C++, C#, Java, JavaScript, TypeScript")
    assert "Python" in found
    assert "C" in found
    assert "C++" in found
    assert "C#" in found
    assert "Java" in found
    assert "JavaScript" in found
    assert "TypeScript" in found


def test_skill_score_without_job_description(sample_resume: str) -> None:
    result = compute_skill_score(sample_resume)
    assert 0 <= result["score"] <= 100
    assert result["matched"]
    assert result["missing"] == []


def test_skill_score_with_job_description(sample_resume: str, sample_jd: str) -> None:
    result = compute_skill_score(sample_resume, sample_jd)
    assert result["required_in_jd"]
    assert result["matched"]
    assert result["score"] == int(len(result["matched"]) / len(result["required_in_jd"]) * 100)


def test_completeness_detects_sections(sample_resume: str) -> None:
    from utils.resume_parser import extract_sections

    result = compute_resume_completeness(extract_sections(sample_resume))
    assert result["completeness_score"] >= 80
    assert result["sections_present"]["experience"] is True
    assert result["sections_present"]["education"] is True


def test_keyword_density_removes_stopwords() -> None:
    density = compute_keyword_density("the python python and sql")
    assert density["python"] == 2
    assert "the" not in density
    assert "and" not in density


def test_weighted_overall_score() -> None:
    assert weighted_overall_score(80, 60, 70) == 74
    assert weighted_overall_score(100, 100, 100) == 100
    assert weighted_overall_score(-10, 200, "bad") == 25
