"""Deterministic, dependency-free analysis engine.

Every public function mirrors the signature and return shape of the matching
function in :mod:`utils.ai_engine`.  The AI layer falls back to these
implementations whenever Gemini is unavailable, so the application always has a
working answer for the user.
"""
from __future__ import annotations

import re
from typing import Any

from config import COMMON_SKILLS
from utils.resume_parser import extract_contact_info, extract_sections
from utils.scorer import (
    compute_keyword_density,
    compute_resume_completeness,
    compute_skill_score,
)

# ── Skill / role knowledge base ───────────────────────────────────────────────

ROLE_PROFILES: dict[str, dict[str, Any]] = {
    "python developer": {
        "skills": ["Python", "SQL", "Git", "REST API", "Django", "Flask", "Docker", "Testing"],
        "salary": ("$55k - $80k", "$80k - $120k", "$120k - $165k"),
        "certs": ["Python Institute PCEP/PCAP", "AWS Certified Developer - Associate"],
        "industries": ["Software", "Fintech", "SaaS", "E-commerce"],
        "companies": ["Zoho", "Freshworks", "Infosys", "Accenture", "Stripe"],
        "description": "Build and maintain Python services, APIs and automation.",
    },
    "data analyst": {
        "skills": ["SQL", "Excel", "Python", "Pandas", "Tableau", "Power BI", "Statistics", "Data Analysis"],
        "salary": ("$50k - $70k", "$70k - $100k", "$100k - $135k"),
        "certs": ["Google Data Analytics", "Microsoft Power BI Data Analyst"],
        "industries": ["Consulting", "Retail", "Finance", "Healthcare"],
        "companies": ["Deloitte", "EY", "Amazon", "Walmart", "Mu Sigma"],
        "description": "Turn raw data into dashboards and decisions stakeholders trust.",
    },
    "data scientist": {
        "skills": ["Python", "Statistics", "Machine Learning", "Pandas", "NumPy", "SQL", "Scikit-learn", "Plotly"],
        "salary": ("$70k - $95k", "$95k - $140k", "$140k - $190k"),
        "certs": ["Google Advanced Data Analytics", "AWS Certified Machine Learning - Specialty"],
        "industries": ["AI", "Fintech", "Healthcare", "E-commerce"],
        "companies": ["Fractal", "Tiger Analytics", "Amazon", "Microsoft", "Flipkart"],
        "description": "Design experiments, build models and communicate findings.",
    },
    "machine learning engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Docker", "AWS", "MLOps"],
        "salary": ("$80k - $110k", "$110k - $160k", "$160k - $220k"),
        "certs": ["TensorFlow Developer", "AWS Certified Machine Learning - Specialty"],
        "industries": ["AI", "Cloud", "Autonomous Systems", "Healthcare"],
        "companies": ["NVIDIA", "Google", "Microsoft", "Razorpay", "Sprinklr"],
        "description": "Ship models to production and keep them healthy.",
    },
    "frontend developer": {
        "skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Git", "REST API", "Testing"],
        "salary": ("$50k - $75k", "$75k - $110k", "$110k - $150k"),
        "certs": ["Meta Front-End Developer", "JavaScript Algorithms and Data Structures"],
        "industries": ["SaaS", "Media", "E-commerce", "Agencies"],
        "companies": ["Shopify", "Atlassian", "Zomato", "Swiggy", "Adobe"],
        "description": "Build accessible, fast interfaces that feel effortless.",
    },
    "backend developer": {
        "skills": ["Python", "Java", "SQL", "REST API", "Docker", "PostgreSQL", "Redis", "Git"],
        "salary": ("$55k - $80k", "$80k - $120k", "$120k - $165k"),
        "certs": ["AWS Certified Developer - Associate", "Oracle Java SE"],
        "industries": ["Fintech", "SaaS", "Logistics", "Cloud"],
        "companies": ["PayPal", "Razorpay", "Uber", "Oracle", "Zoho"],
        "description": "Own APIs, data models and the reliability of core services.",
    },
    "full stack developer": {
        "skills": ["JavaScript", "React", "Node.js", "Python", "SQL", "REST API", "Docker", "Git"],
        "salary": ("$60k - $85k", "$85k - $125k", "$125k - $170k"),
        "certs": ["Meta Full-Stack Developer", "AWS Certified Developer - Associate"],
        "industries": ["SaaS", "Startups", "E-commerce", "Fintech"],
        "companies": ["Stripe", "Notion", "Freshworks", "Meesho", "Atlassian"],
        "description": "Ship features end to end, from database to interface.",
    },
    "devops engineer": {
        "skills": ["Linux", "Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Bash", "Git"],
        "salary": ("$65k - $90k", "$90k - $135k", "$135k - $180k"),
        "certs": ["AWS Certified Solutions Architect", "Certified Kubernetes Administrator"],
        "industries": ["Cloud", "SaaS", "Fintech", "Enterprise"],
        "companies": ["HashiCorp", "AWS", "Cloudflare", "Infosys", "Wipro"],
        "description": "Automate delivery, observe systems and reduce toil.",
    },
    "business analyst": {
        "skills": ["Excel", "SQL", "Communication", "Data Analysis", "Agile", "Jira", "Problem Solving"],
        "salary": ("$50k - $70k", "$70k - $95k", "$95k - $125k"),
        "certs": ["CBAP", "Google Project Management"],
        "industries": ["Consulting", "Banking", "Insurance", "Retail"],
        "companies": ["McKinsey", "Accenture", "Capgemini", "ICICI", "HDFC"],
        "description": "Translate business needs into clear, testable requirements.",
    },
    "android developer": {
        "skills": ["Kotlin", "Java", "Android", "SQLite", "REST API", "Git", "Firebase"],
        "salary": ("$50k - $75k", "$75k - $110k", "$110k - $145k"),
        "certs": ["Google Associate Android Developer"],
        "industries": ["Mobile", "Consumer Apps", "Fintech", "Health"],
        "companies": ["Google", "Samsung", "Paytm", "PhonePe", "Swiggy"],
        "description": "Build reliable mobile experiences for Android devices.",
    },
    "qa engineer": {
        "skills": ["Testing", "Python", "Selenium", "SQL", "Git", "CI/CD", "Problem Solving"],
        "salary": ("$45k - $65k", "$65k - $95k", "$95k - $125k"),
        "certs": ["ISTQB Foundation", "Certified Selenium Professional"],
        "industries": ["SaaS", "Banking", "Gaming", "Healthcare"],
        "companies": ["TCS", "Infosys", "BrowserStack", "Zoho", "Capgemini"],
        "description": "Protect release quality with automation and sharp test design.",
    },
}

DEFAULT_PROFILE: dict[str, Any] = {
    "skills": ["Python", "SQL", "Git", "Communication", "Problem Solving", "Docker"],
    "salary": ("$50k - $70k", "$70k - $100k", "$100k - $140k"),
    "certs": ["Google Career Certificate", "AWS Cloud Practitioner"],
    "industries": ["Technology", "Consulting", "Finance"],
    "companies": ["Infosys", "Accenture", "TCS", "Wipro", "Deloitte"],
    "description": "Apply your strengths to measurable business problems.",
}

CORE_SKILLS = ["Python", "SQL", "Git", "Docker", "Communication", "Problem Solving"]

ACTION_VERBS = (
    "built", "led", "designed", "shipped", "reduced", "improved", "automated",
    "launched", "migrated", "optimised", "optimized", "delivered", "owned",
    "scaled", "mentored", "created", "implemented", "increased", "cut",
)

DEGREE_LEVELS = {
    "phd": 4, "doctorate": 4, "master": 3, "m.tech": 3, "mba": 3, "m.sc": 3,
    "bachelor": 2, "b.tech": 2, "b.e": 2, "b.sc": 2, "bca": 2, "b.com": 2,
    "diploma": 1, "high school": 0, "12th": 0, "10th": 0,
}
DEGREE_LABELS = {4: "PhD", 3: "Master's", 2: "Bachelor's", 1: "Diploma", 0: "High school"}

SKILL_RESOURCES = {
    "Python": ("Python for Everybody", "https://www.py4e.com/"),
    "SQL": ("SQLBolt", "https://sqlbolt.com/"),
    "Machine Learning": ("Machine Learning Specialization", "https://www.coursera.org/specializations/machine-learning-introduction"),
    "Deep Learning": ("Deep Learning Specialization", "https://www.coursera.org/specializations/deep-learning"),
    "Docker": ("Docker Getting Started", "https://docs.docker.com/get-started/"),
    "Kubernetes": ("Kubernetes Basics", "https://kubernetes.io/docs/tutorials/"),
    "AWS": ("AWS Skill Builder", "https://skillbuilder.aws/"),
    "React": ("React Learn", "https://react.dev/learn"),
    "JavaScript": ("JavaScript.info", "https://javascript.info/"),
    "Django": ("Django Tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/"),
    "Flask": ("Flask Quickstart", "https://flask.palletsprojects.com/quickstart/"),
    "Git": ("Pro Git", "https://git-scm.com/book/en/v2"),
    "Data Analysis": ("Data Analysis with Python", "https://www.freecodecamp.org/learn/data-analysis-with-python/"),
    "Statistics": ("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability"),
    "Communication": ("Toastmasters", "https://www.toastmasters.org/"),
    "Problem Solving": ("LeetCode", "https://leetcode.com/"),
}

QUESTION_BANK: dict[str, list[str]] = {
    "Behavioral": [
        "Tell me about a time you disagreed with a teammate. How did you resolve it?",
        "Describe a project you delivered under a tight deadline. What did you cut?",
        "Tell me about a failure and what you changed afterwards.",
        "How do you prioritise when everything feels urgent?",
        "Describe a time you had to learn a new technology quickly.",
        "Tell me about a moment you took ownership beyond your job description.",
    ],
    "Technical": [
        "Walk me through a {skill} project you built and the trade-offs you made.",
        "How would you debug a production issue in a {skill} service?",
        "Explain how {skill} works under the hood, and when you would avoid it.",
        "Describe a performance problem you solved using {skill}.",
        "How do you test and validate {skill} work before shipping?",
        "What is the most common mistake you see people make with {skill}?",
    ],
    "Situational": [
        "You join a team with no tests and a release in two weeks. What do you do first?",
        "A stakeholder changes requirements mid-sprint. How do you respond?",
        "Your model's accuracy drops after deployment. Walk me through your response.",
        "You have two high-priority tasks and one engineer. How do you decide?",
        "A teammate's code repeatedly breaks the build. How do you handle it?",
        "You inherit a service nobody understands. How do you make it safe to change?",
    ],
    "HR": [
        "Why do you want this {role} role?",
        "Where do you see yourself in three years?",
        "What kind of team environment helps you do your best work?",
        "What are your salary expectations for this role?",
        "Why are you leaving your current position?",
        "What would your last manager say is your biggest growth area?",
    ],
}

HINTS = {
    "Behavioral": "Use STAR: Situation, Task, Action, Result. End with a measurable result.",
    "Technical": "Name the tool, explain the trade-off, then give a concrete example from your work.",
    "Situational": "State your first move, how you communicate, and how you measure success.",
    "HR": "Keep it honest and specific to this company and role.",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clamp(value: float, low: float = 0, high: float = 100) -> int:
    return int(max(low, min(high, round(value))))


def _pattern(skill: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![\w+#]){re.escape(skill)}(?![\w+#])", re.IGNORECASE)


def skills_in(text: str) -> list[str]:
    """Return canonical skills mentioned in *text*, longest names first."""
    if not text:
        return []
    found = [skill for skill in COMMON_SKILLS if _pattern(skill).search(text)]
    return sorted(dict.fromkeys(found), key=lambda s: (-len(s), s))


def _estimate_years(text: str, sections: dict[str, str] | None = None) -> int:
    # A stated total ("2 years of experience") is more trustworthy than dates,
    # which often include education and overlapping internships.
    explicit = [int(n) for n in re.findall(r"(\d{1,2})\+?\s*(?:years?|yrs?)", text, re.I)]
    if explicit:
        return max(0, min(max(explicit), 40))

    scope = ""
    if sections:
        scope = " ".join(
            value for key, value in sections.items()
            if any(word in key for word in ("experience", "employment", "work"))
        )
    scope = scope or text
    total = 0
    for start, end in re.findall(r"((?:19|20)\d{2})\s*(?:-|–|—|to)\s*((?:19|20)\d{2}|present|current)", scope, re.I):
        end_year = 2026 if end.lower() in {"present", "current"} else int(end)
        total += max(0, end_year - int(start))
    return max(0, min(total, 40))


def _education(text: str) -> tuple[int, str]:
    lower = text.lower()
    for token, level in sorted(DEGREE_LEVELS.items(), key=lambda kv: -kv[1]):
        if token in lower:
            return level, DEGREE_LABELS[level]
    return 0, "Not specified"


def _job_titles(text: str, sections: dict[str, str] | None = None) -> list[str]:
    scope = ""
    if sections:
        scope = " ".join(
            value for key, value in sections.items()
            if any(word in key for word in ("experience", "employment", "work"))
        )
    scope = scope or text
    titles: list[str] = []
    keywords = ("engineer", "developer", "analyst", "scientist", "manager", "intern",
                "designer", "consultant", "architect", "lead", "specialist")

    for line in scope.splitlines():
        clean = line.strip(" -•\t|")
        if not clean or len(clean) > 120:
            continue
        # Remove date ranges before looking for a title so "Role, Company, 2022 - 2024"
        # is still recognised.
        candidate = re.sub(
            r"\(?\b(?:19|20)\d{2}\b\s*(?:-|–|—|to)\s*(?:(?:19|20)\d{2}|present|current)\)?",
            "",
            clean,
            flags=re.IGNORECASE,
        )
        candidate = re.sub(r"\b(?:19|20)\d{2}\b", "", candidate)
        candidate = re.sub(r"\s{2,}", " ", candidate).strip(" ,|-–—")
        if not candidate or not any(word in candidate.lower() for word in keywords):
            continue
        # Keep the title, not the company: "Role, Company" / "Role at Company".
        title = re.split(r"\s+[|@]\s+|,\s+|\s+at\s+", candidate)[0].strip(" ,-")
        if 1 <= len(title.split()) <= 6:
            titles.append(title[:80])

    return list(dict.fromkeys(titles))[:5]


def _role_key(role: str) -> str:
    role = (role or "").lower().strip()
    for key in ROLE_PROFILES:
        if key in role or all(word in role for word in key.split()):
            return key
    tokens = [token for token in re.findall(r"[a-z]+", role) if len(token) > 2]
    for key in ROLE_PROFILES:
        if any(token in key for token in tokens):
            return key
    return ""


def _profile(role: str) -> dict[str, Any]:
    return ROLE_PROFILES.get(_role_key(role), DEFAULT_PROFILE)


def _career_level(years: int) -> str:
    if years >= 8:
        return "Senior"
    if years >= 4:
        return "Mid-level"
    if years >= 1:
        return "Junior"
    return "Entry-level"


def _top_keywords(text: str, limit: int = 12) -> list[str]:
    density = compute_keyword_density(text)
    return [word.title() for word in list(density)[:limit]]


def _sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1].upper() + text[1:] if text else text


# ── Resume analysis ───────────────────────────────────────────────────────────

def analyze_resume(resume_text: str, job_description: str = "") -> dict[str, Any]:
    """Heuristic resume review with the same schema as the AI version."""
    text = resume_text or ""
    sections = extract_sections(text)
    contact = extract_contact_info(text)
    found = skills_in(text)
    completeness = compute_resume_completeness(sections)
    years = _estimate_years(text, sections)
    _, education = _education(text)

    jd_skills = skills_in(job_description) if job_description else []
    required = jd_skills or [skill for skill in CORE_SKILLS if skill in COMMON_SKILLS]
    missing = [skill for skill in required if skill not in found]

    words = len(re.findall(r"\b\w+\b", text))
    bullets = len(re.findall(r"^\s*[-•*]", text, re.MULTILINE))
    numbers = len(re.findall(r"\d+\s*%|\$\s?\d+|\b\d{2,}\b", text))
    verbs = sum(1 for verb in ACTION_VERBS if re.search(rf"\b{verb}\b", text, re.I))
    has_contact = bool(contact["email"] and contact["phone"])

    content = _clamp(completeness["completeness_score"] / 10, 1, 10)
    formatting = _clamp(
        4
        + (2 if has_contact else 0)
        + (2 if bullets >= 4 else 1 if bullets else 0)
        + (1 if 300 <= words <= 900 else 0),
        1, 10,
    )
    keyword_score = _clamp(3 + len(found) * 0.7 + (2 if job_description and not missing else 0), 1, 10)
    impact = _clamp(3 + min(numbers, 6) + min(verbs, 4) * 0.5, 1, 10)
    clarity = _clamp(
        4
        + (2 if any(key in sections for key in ("summary", "objective", "profile")) else 0)
        + (2 if len(sections) >= 4 else 1 if len(sections) >= 2 else 0)
        + (1 if words >= 200 else 0),
        1, 10,
    )

    sections_score = {
        "content": content,
        "formatting": formatting,
        "keywords": keyword_score,
        "impact": impact,
        "clarity": clarity,
    }
    # Calibration: the raw weighted total is generous for a complete resume, so
    # scale it down. A well-structured resume lands in the mid-80s, not the 90s.
    raw_overall = content * 3.0 + formatting * 2.0 + keyword_score * 2.5 + impact * 2.5
    overall = _clamp(raw_overall * 0.88)
    ats = _clamp((keyword_score * 4.0 + formatting * 3.0 + content * 3.0) * 0.88)

    strengths: list[str] = []
    if found:
        strengths.append(f"Detected {len(found)} relevant skills, including {', '.join(found[:4])}.")
    if has_contact:
        strengths.append("Contact details are complete and easy to find.")
    if bullets >= 4:
        strengths.append(f"Experience is written as {bullets} scannable bullet points.")
    if numbers:
        strengths.append(f"Uses {numbers} quantified detail(s) such as percentages or figures.")
    if years:
        strengths.append(f"Shows roughly {years} year(s) of relevant experience.")
    if not strengths:
        strengths.append("The document is readable and can be improved with structure.")

    weaknesses: list[str] = []
    if not has_contact:
        weaknesses.append("Missing a complete email or phone number in the header.")
    if completeness["missing_sections"]:
        weaknesses.append(
            "Missing sections: " + ", ".join(completeness["missing_sections"]) + "."
        )
    if not numbers:
        weaknesses.append("No quantified achievements - add numbers, %, or scale.")
    if not bullets:
        weaknesses.append("Experience is not broken into bullet points, which hurts ATS parsing.")
    if len(found) < 5:
        weaknesses.append("The skills section is thin for most technical roles.")
    if words > 1100:
        weaknesses.append("The resume is long; trim it to the most relevant evidence.")
    if not weaknesses:
        weaknesses.append("No structural blockers found - focus on tailoring per role.")

    suggestions: list[str] = []
    if missing:
        suggestions.append("Add evidence for: " + ", ".join(missing[:5]) + ".")
    suggestions.append("Start every experience bullet with a strong action verb and end with a result.")
    suggestions.append("Mirror the exact keywords from the job description in your skills and summary.")
    if not numbers:
        suggestions.append("Quantify at least three achievements (latency, revenue, users, time saved).")
    if not any(key in sections for key in ("summary", "objective", "profile")):
        suggestions.append("Add a 2-3 line summary naming your target role and strongest proof point.")
    if not contact["linkedin"]:
        suggestions.append("Add a LinkedIn URL so recruiters can verify your profile.")
    if not contact["github"]:
        suggestions.append("Add a GitHub or portfolio link with work they can inspect.")

    summary_review = (
        f"{contact['name']} presents as a {_career_level(years).lower()} candidate"
        f"{' targeting ' + job_description.splitlines()[0][:60] if job_description else ''}. "
        f"The resume scores {overall}/100 overall with {len(found)} recognised skills."
    )
    overall_review = (
        f"Overall the resume is {'strong' if overall >= 75 else 'solid' if overall >= 55 else 'a work in progress'}. "
        f"Structure scores {content}/10 and ATS readability {ats}/100. "
        f"Focus next on {'quantified impact' if not numbers else 'role-specific keyword tailoring'}"
        f"{' and missing sections' if completeness['missing_sections'] else ''}."
    )

    return {
        "overall_score": overall,
        "ats_score": ats,
        "sections_score": sections_score,
        "summary_review": summary_review,
        "overall_review": overall_review,
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:5],
        "suggestions": suggestions[:6],
        "skills_found": found,
        "missing_skills": missing[:8],
        "keywords_found": found[:12] + [k for k in _top_keywords(text) if k not in found][:6],
        "keywords_missing": [k for k in _top_keywords(job_description) if k.lower() not in text.lower()][:8]
        if job_description else [],
        "experience_years": years,
        "education_level": education,
        "job_titles": _job_titles(text, sections),
        "source": "offline",
    }


# ── Job description match ─────────────────────────────────────────────────────

def match_job_description(resume_text: str, job_description: str) -> dict[str, Any]:
    """Compare a resume with a job description using local signals."""
    text = resume_text or ""
    jd = job_description or ""
    required = skills_in(jd)
    found = skills_in(text)
    matched = [skill for skill in required if skill in found]
    missing = [skill for skill in required if skill not in found]

    coverage = (len(matched) / len(required) * 100) if required else 0
    jd_tokens = set(compute_keyword_density(jd))
    resume_tokens = set(compute_keyword_density(text))
    keyword_overlap = (len(jd_tokens & resume_tokens) / len(jd_tokens) * 100) if jd_tokens else 0
    base = coverage if required else keyword_overlap

    candidate_years = _estimate_years(text, extract_sections(text))
    required_years = [int(n) for n in re.findall(r"(\d{1,2})\+?\s*(?:years?|yrs?)", jd, re.I)]
    need = max(required_years) if required_years else 0
    if not need:
        experience_match = "Not specified"
        experience_points = 60
    elif candidate_years >= need:
        experience_match = f"Strong ({candidate_years}+ vs {need}+ years)"
        experience_points = 100
    elif candidate_years + 1 >= need:
        experience_match = f"Close ({candidate_years} vs {need}+ years)"
        experience_points = 70
    else:
        experience_match = f"Below requirement ({candidate_years} vs {need}+ years)"
        experience_points = 35

    jd_level = max((level for token, level in DEGREE_LEVELS.items() if token in jd.lower()), default=0)
    resume_level, _ = _education(text)
    if not jd_level:
        education_match = "Not specified"
        education_points = 60
    elif resume_level >= jd_level:
        education_match = "Meets requirement"
        education_points = 100
    else:
        education_match = "Below requirement"
        education_points = 45

    score = _clamp(base * 0.7 + experience_points * 0.2 + education_points * 0.1)
    if score >= 80:
        recommendation = "Strongly Recommend"
    elif score >= 65:
        recommendation = "Recommend"
    elif score >= 45:
        recommendation = "Neutral"
    else:
        recommendation = "Do Not Recommend"

    fit_summary = (
        f"Matched {len(matched)} of {len(required)} required skills"
        f"{' (' + ', '.join(matched[:5]) + ')' if matched else ''}. "
        f"Experience: {experience_match.lower()}. Education: {education_match.lower()}."
    )

    return {
        "match_score": score,
        "recommendation": recommendation,
        "fit_summary": fit_summary,
        "matched_skills": matched,
        "missing_skills": missing,
        "experience_match": experience_match,
        "education_match": education_match,
        "keywords_to_add": [k for k in _top_keywords(jd) if k.lower() not in text.lower()][:8],
        "source": "offline",
    }


# ── Interview practice ────────────────────────────────────────────────────────

def generate_interview_questions(
    resume_text: str,
    job_role: str,
    difficulty: str = "Mixed",
    num_questions: int = 5,
    question_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Build a personalised question set from templates and resume skills."""
    role = (job_role or "Software Engineer").strip()
    types = [t for t in (question_types or ["Behavioral", "Technical"]) if t in QUESTION_BANK]
    if not types:
        types = ["Behavioral", "Technical"]

    skills = skills_in(resume_text) or _profile(role)["skills"]
    levels = ["Easy", "Medium", "Hard"] if difficulty == "Mixed" else [difficulty]
    questions: list[dict[str, Any]] = []

    for index in range(max(1, min(int(num_questions), 10))):
        qtype = types[index % len(types)]
        bank = QUESTION_BANK[qtype]
        template = bank[(index // len(types)) % len(bank)]
        skill = skills[index % len(skills)]
        text = template.format(skill=skill, role=role)
        questions.append(
            {
                "id": index + 1,
                "question": text,
                "type": qtype,
                "difficulty": levels[index % len(levels)],
                "topic": skill if "{skill}" in template else role,
                "hint": HINTS.get(qtype, "Be specific and quantify the outcome."),
                "source": "offline",
            }
        )
    return questions


def evaluate_answer(
    question: str,
    answer: str,
    job_role: str = "",
    expected_hints: str = "",
) -> dict[str, Any]:
    """Score an interview answer on structure, evidence and specificity."""
    text = (answer or "").strip()
    lower = text.lower()
    words = len(re.findall(r"\b\w+\b", text))
    star = sum(1 for word in ("situation", "task", "action", "result", "impact", "because") if word in lower)
    numbers = len(re.findall(r"\d+", text))
    skills = skills_in(text)

    score = 2
    score += 2 if words >= 40 else 1 if words >= 15 else 0
    score += 1 if words >= 80 else 0
    score += 2 if star >= 2 else 1 if star >= 1 else 0
    score += 1 if numbers else 0
    score += 1 if skills else 0
    score += 1 if 30 <= words <= 260 else 0
    score = _clamp(score, 0, 10)

    grade = "Excellent" if score >= 8 else "Good" if score >= 6 else "Average" if score >= 4 else "Poor"

    strengths: list[str] = []
    if words >= 40:
        strengths.append("Answer has enough detail to show your reasoning.")
    if star >= 1:
        strengths.append("Uses a narrative structure rather than a list of claims.")
    if numbers:
        strengths.append("Includes concrete numbers or evidence.")
    if skills:
        strengths.append(f"References relevant tools: {', '.join(skills[:3])}.")
    if not strengths:
        strengths.append("You made a start - now add a specific example.")

    improvements: list[str] = []
    if words < 40:
        improvements.append("Expand to 4-6 sentences with one concrete example.")
    if not star:
        improvements.append("Use STAR: Situation, Task, Action, Result.")
    if not numbers:
        improvements.append("Add a measurable result (%, time saved, users, revenue).")
    if words > 300:
        improvements.append("Tighten the answer; aim for under two minutes of speech.")
    if not improvements:
        improvements.append("Polish delivery: lead with the result, then explain how you got there.")

    feedback = (
        f"This answer scores {score}/10. It is {grade.lower()} for a {job_role or 'technical'} interview. "
        f"{'Structure and evidence are working.' if score >= 6 else 'The core idea is there but needs evidence and structure.'}"
    )
    model_answer = (
        "A strong answer would: (1) set the situation in one sentence, "
        "(2) state the task and your specific responsibility, "
        "(3) describe the action you took and the trade-off you chose, "
        "(4) close with a measurable result and what you would repeat. "
        f"Anchor it to this question: {question[:140]}"
    )

    return {
        "score": score,
        "grade": grade,
        "strengths": strengths,
        "improvements": improvements,
        "feedback": feedback,
        "model_answer": model_answer,
        "source": "offline",
    }


# ── Career advice ─────────────────────────────────────────────────────────────

def generate_career_advice(resume_text: str, target_role: str) -> dict[str, Any]:
    """Produce a practical roadmap from local skill-gap analysis."""
    role = (target_role or "").strip()
    profile = _profile(role)
    found = skills_in(resume_text)
    required = profile["skills"]
    matched = [skill for skill in required if skill in found]
    gaps = [skill for skill in required if skill not in found]

    fit = _clamp((len(matched) / len(required) * 100) if required else 50)
    years = _estimate_years(resume_text, extract_sections(resume_text))
    level = _career_level(years)
    salary_index = 2 if level == "Senior" else 1 if level == "Mid-level" else 0

    resources = []
    for skill in gaps[:5]:
        name, url = SKILL_RESOURCES.get(skill, (f"{skill} fundamentals", "https://roadmap.sh/"))
        resources.append({"topic": skill, "resource": name, "url": url})

    timeline = (
        "3-4 months" if len(gaps) <= 3
        else "5-7 months" if len(gaps) <= 5
        else "8-12 months"
    )

    plan = [
        f"Close the highest-impact gap first: {gaps[0]}." if gaps else "Deepen your strongest skill with a production-grade project.",
        f"Build one portfolio project that demonstrates {role or 'your target role'} end to end.",
        "Rewrite your resume around outcomes, not responsibilities, and tailor it per application.",
        "Practise 3 mock interviews per week using the Interview Bot.",
        "Apply to 5 targeted roles per week and track responses in a simple sheet.",
    ]

    advice = (
        f"You are a {level.lower()} candidate with about {years} year(s) of experience. "
        f"You already match {len(matched)} of {len(required)} core skills for a {role or 'target role'}. "
        f"{'Your fastest win is ' + gaps[0] + '.' if gaps else 'Your skills already cover the core requirements; focus on proof of impact.'}"
    )

    return {
        "current_level": level,
        "target_role_fit": fit,
        "timeline": timeline,
        "salary_range": profile["salary"][salary_index],
        "career_advice": advice,
        "skill_gaps": gaps[:6],
        "recommended_certifications": profile["certs"][:3],
        "learning_resources": resources,
        "action_plan": plan,
        "source": "offline",
    }


# ── Job recommendations ───────────────────────────────────────────────────────

def recommend_jobs(resume_text: str) -> dict[str, Any]:
    """Rank role profiles against the skills found in the resume."""
    found = set(skills_in(resume_text))
    years = _estimate_years(resume_text, extract_sections(resume_text))
    level = _career_level(years)

    ranked: list[tuple[float, dict[str, Any]]] = []
    for profile in ROLE_PROFILES.values():
        required = set(profile["skills"])
        overlap = len(found & required) / len(required) if required else 0
        ranked.append((overlap, profile))
    ranked.sort(key=lambda item: item[0], reverse=True)

    roles = []
    for overlap, profile in ranked[:5]:
        match = _clamp(55 + overlap * 45)
        salary = profile["salary"][2 if level == "Senior" else 1 if level == "Mid-level" else 0]
        roles.append(
            {
                "title": next(
                    (key.title() for key, value in ROLE_PROFILES.items() if value is profile),
                    "Technology Role",
                ),
                "match": match,
                "salary_range": salary,
                "companies": profile["companies"][:4],
                "skills_needed": profile["skills"][:6],
                "description": profile["description"],
            }
        )

    industries: list[str] = []
    for _, profile in ranked[:3]:
        for industry in profile["industries"]:
            if industry not in industries:
                industries.append(industry)

    return {
        "top_roles": roles,
        "industries": industries[:5],
        "career_level": level,
        "job_search_tips": [
            "Tailor the top third of your resume to each posting - that is what gets read first.",
            "Ask for referrals before applying cold; referral rates are several times higher.",
            "Keep a tracker with date, company, role, source and next follow-up.",
            "Prepare two STAR stories per core skill you list.",
        ],
        "source": "offline",
    }


# ── Resume comparison ─────────────────────────────────────────────────────────

def compare_resumes(resume1: str, resume2: str, name1: str, name2: str) -> dict[str, Any]:
    """Score two resumes locally on the same rubric."""
    analyses = {
        name1: analyze_resume(resume1),
        name2: analyze_resume(resume2),
    }
    scores: dict[str, dict[str, int]] = {}
    for name, text in ((name1, resume1), (name2, resume2)):
        analysis = analyses[name]
        years = int(analysis.get("experience_years") or 0)
        education = str(analysis.get("education_level", ""))
        edu_map = {"PhD": 95, "Master's": 85, "Bachelor's": 75, "Diploma": 65, "High school": 55}
        scores[name] = {
            "overall": int(analysis["overall_score"]),
            "skills": compute_skill_score(text)["score"],
            "experience": _clamp(45 + years * 8),
            "education": edu_map.get(education, 60),
            "presentation": int(analysis["sections_score"]["formatting"]) * 10,
        }

    winner = name1 if scores[name1]["overall"] >= scores[name2]["overall"] else name2
    loser = name2 if winner == name1 else name1
    diff = scores[winner]["overall"] - scores[loser]["overall"]
    verdict = (
        f"{winner} is the stronger resume by {diff} point(s) overall. "
        f"The gap comes mainly from {'skills coverage' if scores[winner]['skills'] > scores[loser]['skills'] else 'presentation and impact'}. "
        f"{loser} can close it by adding quantified achievements and role-specific keywords."
    )

    return {
        "winner": winner,
        "scores": scores,
        "strengths": {
            name1: analyses[name1]["strengths"][:3],
            name2: analyses[name2]["strengths"][:3],
        },
        "weaknesses": {
            name1: analyses[name1]["weaknesses"][:3],
            name2: analyses[name2]["weaknesses"][:3],
        },
        "verdict": verdict,
        "source": "offline",
    }


# ── Resume builder ────────────────────────────────────────────────────────────

def build_resume(data: dict[str, Any]) -> dict[str, Any]:
    """Assemble an ATS-friendly markdown resume from form data."""
    name = (data.get("name") or "Your Name").strip()
    role = (data.get("target_role") or "Software Engineer").strip()
    skills = [s.strip() for s in re.split(r"[,\n]", data.get("skills", "")) if s.strip()]
    years = (data.get("experience_years") or "0-1 (Fresher)").strip()

    contact = " | ".join(
        part for part in (
            data.get("email", "").strip(),
            data.get("phone", "").strip(),
            data.get("linkedin", "").strip(),
        ) if part
    )

    summary = (
        f"{role} with {years} of experience, focused on shipping reliable work and measurable outcomes. "
        f"Strongest in {', '.join(skills[:3]) if skills else 'problem solving and delivery'}."
    )

    lines = [f"# {name}", "", contact, "", "## Professional Summary", summary, ""]

    if skills:
        lines += ["## Skills", ", ".join(skills), ""]

    experience = (data.get("work_exp") or "").strip()
    if experience:
        lines.append("## Experience")
        for line in experience.splitlines():
            clean = line.strip()
            if not clean:
                continue
            lines.append(clean if clean.startswith(("-", "•", "*")) else f"- {clean}")
        lines.append("")

    education = (data.get("education") or "").strip()
    if education:
        lines += ["## Education", education, ""]

    projects = (data.get("projects") or "").strip()
    if projects:
        lines.append("## Projects")
        for line in projects.splitlines():
            clean = line.strip()
            if not clean:
                continue
            lines.append(clean if clean.startswith(("-", "•", "*")) else f"- {clean}")
        lines.append("")

    for heading, key in (("Achievements", "achievements"), ("Certifications", "certifications")):
        value = (data.get(key) or "").strip()
        if value:
            lines.append(f"## {heading}")
            for line in value.splitlines():
                clean = line.strip()
                if clean:
                    lines.append(clean if clean.startswith(("-", "•", "*")) else f"- {clean}")
            lines.append("")

    return {"resume": "\n".join(lines).strip() + "\n", "source": "offline"}


# ── Chatbot ───────────────────────────────────────────────────────────────────

def chat_reply(
    resume_text: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Answer common resume questions without a language model."""
    text = resume_text or ""
    q = (question or "").lower().strip()
    analysis = analyze_resume(text)
    contact = extract_contact_info(text)
    found = analysis["skills_found"]

    if not q:
        answer = "Ask me about your resume score, skills, experience, or how to improve it."
    elif any(word in q for word in ("hello", "hi", "hey", "namaste")):
        answer = (
            f"Hi! I have your resume loaded. It currently scores {analysis['overall_score']}/100. "
            "Ask me about skills, gaps, ATS score, or next steps."
        )
    elif any(word in q for word in ("skill", "technology", "stack", "tool")):
        answer = (
            f"I found {len(found)} skills: {', '.join(found[:12])}."
            if found
            else "I could not detect a clear skills section. Add one with the tools you actually use."
        )
    elif any(word in q for word in ("score", "ats", "rating", "how good", "evaluate")):
        answer = (
            f"Overall score: {analysis['overall_score']}/100. ATS score: {analysis['ats_score']}/100. "
            f"Biggest levers: {analysis['suggestions'][0]} {analysis['suggestions'][1]}"
        )
    elif any(word in q for word in ("improve", "better", "fix", "suggest", "weakness")):
        answer = "Top improvements:\n\n" + "\n".join(
            f"{i}. {item}" for i, item in enumerate(analysis["suggestions"][:4], 1)
        )
    elif any(word in q for word in ("experience", "years", "worked")):
        answer = (
            f"Estimated experience: about {analysis['experience_years']} year(s). "
            f"Roles detected: {', '.join(analysis['job_titles']) or 'none - add clear job titles.'}"
        )
    elif any(word in q for word in ("education", "degree", "college", "university")):
        answer = f"Highest education detected: {analysis['education_level']}."
    elif any(word in q for word in ("contact", "email", "phone", "linkedin", "github")):
        answer = (
            f"Email: {contact['email'] or 'missing'}; phone: {contact['phone'] or 'missing'}; "
            f"LinkedIn: {contact['linkedin'] or 'missing'}; GitHub: {contact['github'] or 'missing'}."
        )
    elif any(word in q for word in ("job", "role", "career", "apply")):
        jobs = recommend_jobs(text)
        answer = (
            "Best-fit roles: "
            + ", ".join(f"{job['title']} ({job['match']}%)" for job in jobs["top_roles"][:3])
            + ". " + jobs["job_search_tips"][0]
        )
    elif any(word in q for word in ("salary", "pay", "package", "ctc")):
        jobs = recommend_jobs(text)
        answer = (
            f"For a {jobs['career_level'].lower()} profile, a realistic range is "
            f"{jobs['top_roles'][0]['salary_range']} for {jobs['top_roles'][0]['title']}."
        )
    elif any(word in q for word in ("interview", "question", "prepare")):
        answer = (
            "Prepare two STAR stories per core skill, one failure story, and one conflict story. "
            "Then run a mock interview from the Interview Bot page."
        )
    else:
        answer = (
            f"Here is the short version: {analysis['summary_review']} "
            f"Overall {analysis['overall_score']}/100, ATS {analysis['ats_score']}/100. "
            f"Next step: {analysis['suggestions'][0]}"
        )

    return {"answer": answer, "source": "offline"}
