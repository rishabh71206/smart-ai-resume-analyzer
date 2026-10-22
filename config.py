"""
Central configuration for the AI Resume Analyzer & Interview Bot.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = "gemini-2.0-flash"

# ── App ─────────────────────────────────────────────────────────────────────
APP_TITLE: str = "Smart AI Resume Analyzer & Interview Bot"
APP_ICON: str = "🤖"
APP_LAYOUT: str = "wide"

# ── Upload limits ────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB: int = 5
ALLOWED_EXTENSIONS: list[str] = ["pdf", "docx", "txt"]

# ── Interview ────────────────────────────────────────────────────────────────
DEFAULT_NUM_QUESTIONS: int = 5
MAX_NUM_QUESTIONS: int = 10
DIFFICULTY_LEVELS: list[str] = ["Easy", "Medium", "Hard", "Mixed"]

# ── Scoring ──────────────────────────────────────────────────────────────────
SCORE_WEIGHTS: dict = {
    "skills_match": 0.35,
    "experience": 0.25,
    "education": 0.20,
    "keywords": 0.20,
}

# ── Common tech skills (for keyword matching) ────────────────────────────────
COMMON_SKILLS: list[str] = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
    "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
    "Git", "CI/CD", "Agile", "Scrum", "REST API", "GraphQL",
    "Linux", "Bash", "PowerShell", "Microservices", "DevOps",
    "Data Analysis", "Data Science", "Statistics", "Tableau", "Power BI",
]
