"""Central configuration for the Smart AI Resume Analyzer.

Values are read from (in order): environment variables, Streamlit secrets,
then the defaults below. Nothing here talks to the network.
"""
from __future__ import annotations

import os

try:  # python-dotenv is optional at runtime
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv ships with the app
    pass


def _read(key: str, default: str = "") -> str:
    """Environment first, then Streamlit secrets, then the default."""
    value = os.getenv(key, "").strip()
    if value:
        return value
    try:
        import streamlit as st

        secret = st.secrets.get(key, "")  # type: ignore[union-attr]
        return str(secret).strip() if secret else default
    except Exception:
        return default


# ── Gemini ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = _read("GEMINI_API_KEY")

# Models are tried in order; the first one the key can reach wins.
_DEFAULT_MODELS = "gemini-2.5-flash,gemini-2.0-flash,gemini-1.5-flash"
GEMINI_MODELS: tuple[str, ...] = tuple(
    model.strip()
    for model in _read("GEMINI_MODEL", _DEFAULT_MODELS).split(",")
    if model.strip()
)
GEMINI_MODEL: str = GEMINI_MODELS[0]

AI_TIMEOUT_SECONDS: int = int(_read("AI_TIMEOUT_SECONDS", "60") or 60)
AI_MAX_RETRIES: int = int(_read("AI_MAX_RETRIES", "2") or 2)

# ── App ───────────────────────────────────────────────────────────────────────
APP_TITLE: str = "Smart AI Resume Analyzer"
APP_TAGLINE: str = "Resume analysis, mock interviews and career roadmaps"
APP_ICON: str = "🤖"
APP_LAYOUT: str = "wide"
APP_VERSION: str = "2.0.0"
REPO_URL: str = "https://github.com/rishabh71206/smart-ai-resume-analyzer"
PORTFOLIO_URL: str = "https://rishabh71206.github.io/rishabh-srivastava-portfolio/"

# ── Upload limits ─────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB: int = 5
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS: tuple[str, ...] = ("pdf", "docx", "txt")
MIN_RESUME_CHARS: int = 50

# ── Interview ─────────────────────────────────────────────────────────────────
DEFAULT_NUM_QUESTIONS: int = 5
MAX_NUM_QUESTIONS: int = 10
DIFFICULTY_LEVELS: list[str] = ["Easy", "Medium", "Hard", "Mixed"]
QUESTION_TYPES: list[str] = ["Behavioral", "Technical", "Situational", "HR"]

# ── Scoring ───────────────────────────────────────────────────────────────────
SCORE_WEIGHTS: dict[str, float] = {
    "skills_match": 0.35,
    "experience": 0.25,
    "education": 0.20,
    "keywords": 0.20,
}

# Local blend used for the headline score: AI + skills + completeness.
OVERALL_WEIGHTS: dict[str, float] = {
    "ai": 0.60,
    "skills": 0.25,
    "completeness": 0.15,
}

# ── Skills catalogue (used by the local scorer and offline engine) ────────────
COMMON_SKILLS: list[str] = [
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust",
    "SQL", "NoSQL", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis",
    "HTML", "CSS", "React", "Angular", "Vue", "Node.js", "Django", "Flask",
    "FastAPI", "Streamlit", "REST API", "GraphQL",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "CI/CD",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Plotly",
    "Gemini", "OpenAI", "LLM", "Prompt Engineering",
    "Git", "GitHub", "Linux", "Bash", "Agile", "Scrum", "Jira",
    "Data Analysis", "Data Science", "Statistics", "Tableau", "Power BI",
    "Excel", "Communication", "Leadership", "Problem Solving", "Teamwork",
]

# ── Resume sections we know how to detect ─────────────────────────────────────
SECTION_HEADERS: tuple[str, ...] = (
    "summary", "objective", "profile", "about",
    "education", "academic",
    "experience", "work experience", "employment", "professional experience",
    "skills", "technical skills", "core competencies", "technologies",
    "projects", "personal projects", "selected projects",
    "certifications", "certificates", "awards", "achievements",
    "publications", "research",
    "volunteer", "activities", "leadership",
    "languages", "interests", "hobbies",
)
