from __future__ import annotations

from utils import offline_engine


def test_analyze_resume_schema(sample_resume: str) -> None:
    result = offline_engine.analyze_resume(sample_resume)
    assert result["source"] == "offline"
    assert 0 <= result["overall_score"] <= 100
    assert 0 <= result["ats_score"] <= 100
    assert set(result["sections_score"]) == {"content", "formatting", "keywords", "impact", "clarity"}
    assert result["experience_years"] == 2
    assert result["education_level"] == "Bachelor's"
    assert "Software Developer" in result["job_titles"]
    assert "Data Analyst Intern" in result["job_titles"]
    assert result["strengths"]
    assert result["suggestions"]


def test_analyze_resume_is_calibrated(sample_resume: str) -> None:
    result = offline_engine.analyze_resume(sample_resume)
    # A strong resume should be high, but not a perfect 100.
    assert 70 <= result["overall_score"] < 95
    assert 70 <= result["ats_score"] < 95


def test_match_job_description(sample_resume: str, sample_jd: str) -> None:
    result = offline_engine.match_job_description(sample_resume, sample_jd)
    assert result["source"] == "offline"
    assert 0 <= result["match_score"] <= 100
    assert result["recommendation"] in {"Strongly Recommend", "Recommend", "Neutral", "Do Not Recommend"}
    assert result["matched_skills"]
    assert isinstance(result["missing_skills"], list)


def test_interview_questions(sample_resume: str) -> None:
    questions = offline_engine.generate_interview_questions(
        sample_resume, "Python Developer", "Mixed", 5, ["Behavioral", "Technical"]
    )
    assert len(questions) == 5
    assert [q["id"] for q in questions] == [1, 2, 3, 4, 5]
    assert all(q["question"] for q in questions)
    assert all(q["source"] == "offline" for q in questions)


def test_evaluate_answer(sample_resume: str) -> None:
    result = offline_engine.evaluate_answer(
        "Tell me about a project.",
        (
            "The situation was slow database queries in a Django service. My task was to "
            "cut latency. I added indexes and rewrote the hot query, which reduced response "
            "time by 40% and improved the result for 10,000 users."
        ),
        "Python Developer",
    )
    assert 0 <= result["score"] <= 10
    assert result["grade"] in {"Excellent", "Good", "Average", "Poor"}
    assert result["feedback"]
    assert result["model_answer"]


def test_career_advice(sample_resume: str) -> None:
    result = offline_engine.generate_career_advice(sample_resume, "Machine Learning Engineer")
    assert result["current_level"] == "Junior"
    assert 0 <= result["target_role_fit"] <= 100
    assert result["skill_gaps"]
    assert result["learning_resources"]
    assert len(result["action_plan"]) == 5


def test_job_recommendations(sample_resume: str) -> None:
    result = offline_engine.recommend_jobs(sample_resume)
    assert len(result["top_roles"]) == 5
    matches = [role["match"] for role in result["top_roles"]]
    assert matches == sorted(matches, reverse=True)
    assert all(0 <= match <= 100 for match in matches)


def test_resume_comparison(sample_resume: str) -> None:
    other = sample_resume.replace("Python", "Java").replace("Django", "Spring")
    result = offline_engine.compare_resumes(sample_resume, other, "Alice", "Bob")
    assert result["winner"] in {"Alice", "Bob"}
    assert set(result["scores"]) == {"Alice", "Bob"}
    for scores in result["scores"].values():
        assert set(scores) == {"overall", "skills", "experience", "education", "presentation"}
    assert result["verdict"]


def test_resume_builder() -> None:
    result = offline_engine.build_resume(
        {
            "name": "Rishabh Srivastava",
            "email": "rishabh@example.com",
            "phone": "+91 98765 43210",
            "target_role": "Python Developer",
            "experience_years": "1-3",
            "skills": "Python, SQL, Git",
            "work_exp": "Built APIs at Acme Labs",
            "education": "B.Tech Computer Science",
            "projects": "Smart AI Resume Analyzer",
            "certifications": "AWS Cloud Practitioner",
        }
    )
    resume = result["resume"]
    assert result["source"] == "offline"
    assert "# Rishabh Srivastava" in resume
    assert "## Professional Summary" in resume
    assert "Python, SQL, Git" in resume
    assert "## Certifications" in resume


def test_chat_reply(sample_resume: str) -> None:
    result = offline_engine.chat_reply(sample_resume, "What are my strongest skills?")
    assert result["source"] == "offline"
    assert "skills" in result["answer"].lower()
    assert "Python" in result["answer"]
