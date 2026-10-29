from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SAMPLE_RESUME = """Rishabh Srivastava
rishabh@example.com | +91 98765 43210 | linkedin.com/in/rishabh | github.com/rishabh71206

Summary
Python developer with 2 years of experience building AI products and Streamlit dashboards.

Experience
Software Developer, Acme Labs, 2023 - Present
- Built REST APIs with Django and PostgreSQL, reducing response time by 35%
- Automated reporting with pandas, saving 6 hours per week
Data Analyst Intern, Beta Corp, 2022 - 2023
- Analysed 1M+ rows of sales data with SQL and Plotly

Education
B.Tech Computer Science, ABC University, 2018 - 2022, CGPA 8.5

Skills
Python, SQL, Git, Docker, pandas, Plotly, Streamlit, Machine Learning, Communication

Projects
Smart AI Resume Analyzer
- Built an 8-module Streamlit app with Gemini and an offline fallback

Certifications
AWS Cloud Practitioner
"""

SAMPLE_JD = (
    "We need a Python developer with Django, PostgreSQL, Docker, AWS and "
    "3+ years of experience. A bachelor's degree is required."
)


@pytest.fixture
def sample_resume() -> str:
    return SAMPLE_RESUME


@pytest.fixture
def sample_jd() -> str:
    return SAMPLE_JD
