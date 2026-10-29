from __future__ import annotations

from utils.resume_parser import (
    clean_text,
    extract_contact_info,
    extract_sections,
    extract_text_from_bytes,
    is_resume,
    truncate,
)

SAMPLE = """Rishabh Srivastava
rishabh@example.com | +91 98765 43210 | linkedin.com/in/rishabh | github.com/rishabh71206

Summary
Python developer with 2 years of experience building AI products.

Experience
Software Developer, Acme Labs, 2023 - Present
- Built REST APIs with Django and PostgreSQL, reducing response time by 35%

Education
B.Tech Computer Science, ABC University, 2018 - 2022

Skills
Python, SQL, Git, Docker, Streamlit

Projects
Smart AI Resume Analyzer
- Built an 8-module Streamlit app
"""


def test_clean_text_normalises_whitespace() -> None:
    assert clean_text("a  b\t c\r\n\r\n\r\nd") == "a b c\n\nd"
    assert clean_text("") == ""


def test_extract_text_from_bytes_txt() -> None:
    text = extract_text_from_bytes(SAMPLE.encode("utf-8"), "resume.txt")
    assert "Rishabh Srivastava" in text
    assert "\r" not in text


def test_extract_contact_info() -> None:
    info = extract_contact_info(SAMPLE)
    assert info["name"] == "Rishabh Srivastava"
    assert info["email"] == "rishabh@example.com"
    assert info["phone"] is not None
    assert info["linkedin"].startswith("https://")
    assert info["github"].startswith("https://")


def test_extract_sections() -> None:
    sections = extract_sections(SAMPLE)
    assert "summary" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "skills" in sections
    assert "Python, SQL" in sections["skills"]


def test_is_resume_accepts_resume_and_rejects_note() -> None:
    assert is_resume(SAMPLE)[0] is True
    note = "Remember to buy milk and call the plumber tomorrow before the shops close. " * 3
    valid, message = is_resume(note)
    assert valid is False
    assert "does not look like a resume" in message.lower()


def test_truncate_keeps_limit() -> None:
    text = "word " * 100
    result = truncate(text, 50)
    assert len(result) <= 53
    assert result.endswith("...")
