"""Resume parsing utilities - PDF, DOCX and plain text.

The public API is intentionally small and stable:

``extract_text(uploaded_file)``
    Read a Streamlit ``UploadedFile`` and return plain text.
``extract_contact_info(text)``
    Pull out name, email, phone, LinkedIn and GitHub.
``extract_sections(text)``
    Split the resume into labelled sections.
``is_resume(text)``
    Cheap guard so notes and assignments are rejected early.
"""
from __future__ import annotations

import io
import re
from typing import Any, Optional

try:  # pypdf is the maintained successor to PyPDF2
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - fallback for older environments
    from PyPDF2 import PdfReader  # type: ignore[no-redef]

import docx

from config import SECTION_HEADERS

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,5}\)?[\s\-.]?){2,4}\d{2,4}(?!\d)")
URL_RE = re.compile(r"(?:https?://)?(?:www\.)?(?:linkedin\.com|github\.com)/[\w\-./%?=#]+", re.IGNORECASE)


# ── Public API ────────────────────────────────────────────────────────────────

def extract_text(uploaded_file: Any) -> str:
    """Extract raw text from a Streamlit ``UploadedFile``.

    The file pointer is reset afterwards so the same upload can be reused.
    """
    name = str(getattr(uploaded_file, "name", "")).lower()
    raw_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    return extract_text_from_bytes(raw_bytes, name)


def extract_text_from_bytes(raw_bytes: bytes, filename: str = "resume.txt") -> str:
    """Extract text from raw bytes, dispatching on the file extension."""
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        text = _parse_pdf(raw_bytes)
    elif name.endswith(".docx"):
        text = _parse_docx(raw_bytes)
    elif name.endswith(".doc"):
        # Legacy .doc is not supported by python-docx; try a best-effort decode.
        text = raw_bytes.decode("utf-8", errors="ignore")
    else:
        text = _decode_text(raw_bytes)
    return clean_text(text)


def clean_text(text: str) -> str:
    """Normalise whitespace and bullets without destroying line structure."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate(text: str, limit: int = 6000) -> str:
    """Trim long resumes for prompts without cutting mid-word where possible."""
    text = text or ""
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def extract_contact_info(text: str) -> dict[str, Optional[str]]:
    """Extract email, phone, LinkedIn, GitHub and a best-guess name."""
    return {
        "name": _guess_name(text),
        "email": _find_email(text),
        "phone": _find_phone(text),
        "linkedin": _find_url(text, "linkedin.com"),
        "github": _find_url(text, "github.com"),
    }


def extract_sections(text: str) -> dict[str, str]:
    """Heuristically split resume text into labelled sections.

    Returns ``{section_name: section_text}`` with empty sections removed.
    """
    if not text:
        return {}

    lines = text.split("\n")
    sections: dict[str, str] = {}
    current = "header"
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        matched, inline = _match_section_header(stripped)
        if matched:
            content = "\n".join(buffer).strip()
            if content:
                sections[current] = _merge(sections.get(current, ""), content)
            current = matched
            buffer = [inline] if inline else []
        else:
            buffer.append(line)

    content = "\n".join(buffer).strip()
    if content:
        sections[current] = _merge(sections.get(current, ""), content)

    return {key: value for key, value in sections.items() if value.strip()}


def is_resume(text: str) -> tuple[bool, str]:
    """Check whether *text* looks like a resume.

    Returns ``(is_valid, message)``. The threshold is deliberately low so that
    unusual but legitimate resumes are not rejected.
    """
    if not text or len(text.strip()) < 80:
        return False, "The document is empty or too short to analyse."

    lower = text.lower()
    signals = [
        "experience", "education", "skills", "projects", "summary",
        "objective", "employment", "internship", "certification", "degree",
        "university", "college", "achievements", "work history",
    ]
    found = sum(1 for word in signals if word in lower)
    has_contact = bool(EMAIL_RE.search(text) or PHONE_RE.search(text))

    if found >= 2 or (found >= 1 and has_contact):
        return True, "Resume detected."
    return False, (
        "This does not look like a resume. Upload a PDF, DOCX or TXT file that "
        "includes experience, education or skills."
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _decode_text(raw_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "cp1252", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="ignore")


def _parse_pdf(raw_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw_bytes))
    parts: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            parts.append(text)
    return "\n".join(parts)


def _parse_docx(raw_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(raw_bytes))
    parts: list[str] = [para.text for para in document.paragraphs if para.text.strip()]
    # Resumes often hide content in tables; include them so nothing is lost.
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n".join(parts)


def _find_email(text: str) -> Optional[str]:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def _find_phone(text: str) -> Optional[str]:
    for match in PHONE_RE.finditer(text):
        candidate = match.group(0).strip()
        digits = re.sub(r"\D", "", candidate)
        if 8 <= len(digits) <= 15:
            return candidate
    return None


def _find_url(text: str, domain: str) -> Optional[str]:
    for match in URL_RE.finditer(text):
        value = match.group(0).rstrip(".,;)")
        if domain in value.lower():
            return value if value.lower().startswith("http") else f"https://{value}"
    return None


def _guess_name(text: str) -> str:
    """The first short, human-looking line is usually the candidate name."""
    for line in text.split("\n")[:15]:
        stripped = line.strip(" |,-")
        if not stripped or len(stripped) > 45:
            continue
        if re.search(r"[@:/\\]|\d|http|linkedin|github|resume|curriculum", stripped, re.IGNORECASE):
            continue
        words = stripped.split()
        if 1 <= len(words) <= 4 and all(re.fullmatch(r"[A-Za-z.'\-]+", word) for word in words):
            return stripped.title() if stripped.isupper() else stripped
    return "Unknown"


def _match_section_header(line: str) -> tuple[Optional[str], str]:
    """Return ``(section, inline_content)`` if the line is a section header."""
    if not line or len(line) > 60:
        return None, ""
    clean = re.sub(r"^[\W_]+", "", line).strip()
    lower = clean.lower().strip(": -|")

    inline = ""
    if ":" in lower:
        head, _, tail = lower.partition(":")
        head = head.strip(" -|")
        if head in SECTION_HEADERS:
            return head, line.split(":", 1)[1].strip()

    for header in SECTION_HEADERS:
        if lower == header or lower.startswith(header + " ") or lower.startswith(header + ":"):
            return header, inline
    return None, ""


def _merge(existing: str, new: str) -> str:
    return f"{existing}\n{new}".strip() if existing else new
