from __future__ import annotations

import pytest

from utils import ai_engine


@pytest.fixture
def offline_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_engine, "GEMINI_API_KEY", "")
    ai_engine.reset_client()


def test_ai_status_without_key(offline_mode: None) -> None:
    status = ai_engine.ai_status()
    assert status["available"] is False
    assert "GEMINI_API_KEY" in status["reason"]


def test_analyze_resume_falls_back_offline(offline_mode: None, sample_resume: str) -> None:
    result = ai_engine.analyze_resume(sample_resume)
    assert result["source"] == "offline"
    assert "offline_reason" in result
    assert 0 <= result["overall_score"] <= 100


def test_parse_json_plain() -> None:
    assert ai_engine._parse_json('{"score": 8}') == {"score": 8}


def test_parse_json_fenced() -> None:
    assert ai_engine._parse_json('```json\n{"score": 8}\n```') == {"score": 8}


def test_parse_json_with_prose() -> None:
    assert ai_engine._parse_json('Here is the result: {"score": 8}') == {"score": 8}


def test_parse_json_rejects_garbage() -> None:
    with pytest.raises(ai_engine.AIError):
        ai_engine._parse_json("not json at all")


def test_normalise_analysis_clamps_values() -> None:
    result = ai_engine._normalise_analysis(
        {
            "overall_score": 140,
            "ats_score": -5,
            "sections_score": {"content": 12, "formatting": "7", "impact": 4},
            "experience_years": "3 years",
            "strengths": "one\ntwo",
        }
    )
    assert result["overall_score"] == 100
    assert result["ats_score"] == 0
    assert result["sections_score"]["content"] == 10
    assert result["sections_score"]["formatting"] == 7
    assert result["sections_score"]["impact"] == 4
    assert result["experience_years"] == 3
    assert result["strengths"] == ["one", "two"]


def test_normalise_questions_accepts_strings() -> None:
    result = ai_engine._normalise_questions(["Question one?", "Question two?"], 5)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["question"] == "Question one?"


def test_normalise_evaluation_derives_grade() -> None:
    result = ai_engine._normalise_evaluation({"score": 8})
    assert result["grade"] == "Excellent"
    result = ai_engine._normalise_evaluation({"score": 5})
    assert result["grade"] == "Average"


def test_mark_adds_source() -> None:
    result = ai_engine._mark({"answer": "hi"}, "ai", "")
    assert result["source"] == "ai"
    items = ai_engine._mark([{"answer": "hi"}], "offline", "no key")
    assert items[0]["source"] == "offline"
