"""
Resume parsing utilities — supports PDF, DOCX, and plain text.
"""
import io
import re
from typing import Optional

import PyPDF2
import docx


# ── Public API ────────────────────────────────────────────────────────────────

def extract_text(uploaded_file) -> str:
    """
    Extract raw text from a Streamlit UploadedFile object.
    Supports .pdf, .docx, and .txt extensions.
    """
    name: str = uploaded_file.name.lower()
    raw_bytes: bytes = uploaded_file.read()
    uploaded_file.seek(0)  # reset for potential re-use

    if name.endswith(".pdf"):
        return _parse_pdf(raw_bytes)
    elif name.endswith(".docx"):
        return _parse_docx(raw_bytes)
    else:
        # plain text / txt
        return raw_bytes.decode("utf-8", errors="ignore")


def extract_contact_info(text: str) -> dict:
    """Extract email, phone, LinkedIn and GitHub URLs from resume text."""
    email = _find_email(text)
    phone = _find_phone(text)
    linkedin = _find_url(text, "linkedin.com")
    github = _find_url(text, "github.com")
    name = _guess_name(text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
    }


def extract_sections(text: str) -> dict:
    """
    Heuristically split resume text into labelled sections.
    Returns a dict: { section_name: section_text }
    """
    section_headers = [
        "summary", "objective", "profile",
        "education", "academic",
        "experience", "work experience", "employment",
        "skills", "technical skills", "core competencies",
        "projects", "personal projects",
        "certifications", "certificates", "awards",
        "publications", "research",
        "volunteer", "activities",
        "languages", "interests", "hobbies",
    ]

    lines = text.split("\n")
    sections: dict = {}
    current_section = "header"
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        matched = _match_section_header(stripped, section_headers)
        if matched:
            sections[current_section] = "\n".join(buffer).strip()
            current_section = matched
            buffer = []
        else:
            buffer.append(line)

    sections[current_section] = "\n".join(buffer).strip()
    return {k: v for k, v in sections.items() if v}


# ── Private helpers ───────────────────────────────────────────────────────────

def _parse_pdf(raw_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _parse_docx(raw_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(raw_bytes))
    parts: list[str] = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    return "\n".join(parts)


def _find_email(text: str) -> Optional[str]:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def _find_phone(text: str) -> Optional[str]:
    match = re.search(
        r"(\+?\d[\d\s\-().]{7,}\d)",
        text,
    )
    return match.group(0).strip() if match else None


def _find_url(text: str, domain: str) -> Optional[str]:
    pattern = rf"https?://(?:www\.)?{re.escape(domain)}/[\w\-/]+"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def _guess_name(text: str) -> str:
    """Very rough heuristic: first non-empty line is often the candidate name."""
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and len(stripped.split()) <= 5 and not re.search(r"[@:/]", stripped):
            return stripped
    return "Unknown"


def _match_section_header(line: str, headers: list[str]) -> Optional[str]:
    """Return normalised header name if line looks like a section header."""
    clean = line.lower().strip(":|-– ")
    # Exact or starts-with match; line must be reasonably short
    if len(clean) > 50:
        return None
    for h in headers:
        if clean == h or clean.startswith(h):
            return h
    return None
