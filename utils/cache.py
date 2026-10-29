"""Streamlit-cached wrappers around the AI engine.

Caching keeps Gemini quota (and page latency) under control: identical inputs
return the previous result for an hour.  Tests import ``utils.ai_engine``
directly, so this module is only used by the UI.
"""
from __future__ import annotations

from typing import Any

import streamlit as st

from utils import ai_engine


@st.cache_data(show_spinner=False, ttl=3600)
def analyze_resume(resume_text: str, job_description: str = "") -> dict[str, Any]:
    return ai_engine.analyze_resume(resume_text, job_description)


@st.cache_data(show_spinner=False, ttl=3600)
def match_job_description(resume_text: str, job_description: str) -> dict[str, Any]:
    return ai_engine.match_job_description(resume_text, job_description)


@st.cache_data(show_spinner=False, ttl=3600)
def generate_interview_questions(
    resume_text: str,
    job_role: str,
    difficulty: str,
    num_questions: int,
    question_types: tuple[str, ...],
) -> list[dict[str, Any]]:
    return ai_engine.generate_interview_questions(
        resume_text,
        job_role,
        difficulty,
        num_questions,
        list(question_types),
    )


@st.cache_data(show_spinner=False, ttl=3600)
def evaluate_answer(question: str, answer: str, job_role: str, expected_hints: str) -> dict[str, Any]:
    return ai_engine.evaluate_answer(question, answer, job_role, expected_hints)


@st.cache_data(show_spinner=False, ttl=3600)
def generate_career_advice(resume_text: str, target_role: str) -> dict[str, Any]:
    return ai_engine.generate_career_advice(resume_text, target_role)


@st.cache_data(show_spinner=False, ttl=3600)
def recommend_jobs(resume_text: str) -> dict[str, Any]:
    return ai_engine.recommend_jobs(resume_text)


@st.cache_data(show_spinner=False, ttl=3600)
def compare_resumes(resume1: str, resume2: str, name1: str, name2: str) -> dict[str, Any]:
    return ai_engine.compare_resumes(resume1, resume2, name1, name2)


@st.cache_data(show_spinner=False, ttl=3600)
def build_resume(data: dict[str, Any]) -> dict[str, Any]:
    return ai_engine.build_resume(data)


@st.cache_data(show_spinner=False, ttl=3600)
def chat_reply(resume_text: str, question: str, history: tuple[tuple[str, str], ...]) -> dict[str, Any]:
    messages = [{"role": role, "content": content} for role, content in history]
    return ai_engine.chat_reply(resume_text, question, messages)


@st.cache_data(show_spinner=False, ttl=3600)
def pdf_report(analysis: dict[str, Any], candidate_name: str, jd_match: dict[str, Any] | None = None) -> bytes:
    from utils.pdf_report import generate_pdf_report

    return generate_pdf_report(analysis, candidate_name, jd_match)


def clear() -> None:
    """Clear every cached AI result (used by the sidebar reset button)."""
    for func in (
        analyze_resume,
        match_job_description,
        generate_interview_questions,
        evaluate_answer,
        generate_career_advice,
        recommend_jobs,
        compare_resumes,
        build_resume,
        chat_reply,
        pdf_report,
    ):
        func.clear()
