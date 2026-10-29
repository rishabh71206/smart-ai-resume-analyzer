"""Generate a downloadable PDF analysis report using fpdf2."""
from __future__ import annotations

import unicodedata
from datetime import datetime
from typing import Any

from fpdf import FPDF

ACCENT = (37, 99, 235)
INK = (15, 23, 42)
MUTED = (100, 116, 139)
PANEL = (241, 245, 249)


class ResumeReport(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(*ACCENT)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "AI Resume Analysis Report", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.cell(
            0,
            10,
            f"Page {self.page_no()} | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} | Smart AI Resume Analyzer",
            align="C",
        )


def generate_pdf_report(
    analysis: dict[str, Any],
    candidate_name: str = "Candidate",
    jd_match: dict[str, Any] | None = None,
) -> bytes:
    """Build a PDF report from an analysis dict and return raw bytes."""
    pdf = ResumeReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    _candidate_header(pdf, analysis, candidate_name)
    _score_summary(pdf, analysis, jd_match)
    _text_block(pdf, "Summary", analysis.get("summary_review", ""))
    _text_block(pdf, "Overall Review", analysis.get("overall_review", ""))
    _bullets(pdf, "Strengths", analysis.get("strengths", []))
    _bullets(pdf, "Areas for Improvement", analysis.get("weaknesses", []))
    _bullets(pdf, "Actionable Suggestions", analysis.get("suggestions", []))
    _skills(pdf, analysis)
    _jd_section(pdf, jd_match)
    _bullets(pdf, "Next Steps", analysis.get("next_steps", []))
    return bytes(pdf.output())


# ── Sections ──────────────────────────────────────────────────────────────────

def _candidate_header(pdf: FPDF, analysis: dict[str, Any], candidate_name: str) -> None:
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INK)
    pdf.cell(0, 10, _safe(f"Candidate: {candidate_name}"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MUTED)
    bits = []
    if analysis.get("experience_years") not in (None, ""):
        bits.append(f"Experience: {analysis['experience_years']} year(s)")
    if analysis.get("education_level"):
        bits.append(f"Education: {analysis['education_level']}")
    bits.append(f"Report date: {datetime.now().strftime('%B %d, %Y')}")
    pdf.cell(0, 6, _safe(" | ".join(bits)), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*INK)
    pdf.ln(4)


def _score_summary(pdf: FPDF, analysis: dict[str, Any], jd_match: dict[str, Any] | None) -> None:
    _section_title(pdf, "Score Summary")
    overall = analysis.get("overall_score", 0)
    ats = analysis.get("ats_score", 0)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(60, 10, _safe(f"Overall: {overall}/100"))
    pdf.cell(60, 10, _safe(f"ATS: {ats}/100"))
    if jd_match:
        pdf.cell(60, 10, _safe(f"JD match: {jd_match.get('match_score', 0)}%"))
    pdf.ln(12)

    sections = analysis.get("sections_score") or {}
    if sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Section scores", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for key, value in sections.items():
            label = str(key).replace("_", " ").title()
            pdf.cell(0, 7, _safe(f"  - {label}: {value}/10"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)


def _skills(pdf: FPDF, analysis: dict[str, Any]) -> None:
    found = analysis.get("skills_found") or []
    missing = analysis.get("missing_skills") or []
    keywords_found = analysis.get("keywords_found") or []
    keywords_missing = analysis.get("keywords_missing") or []
    if not (found or missing or keywords_found or keywords_missing):
        return

    _section_title(pdf, "Skills and Keywords")
    if found:
        _labelled(pdf, "Skills detected", ", ".join(map(str, found)))
    if missing:
        _labelled(pdf, "Skills to add", ", ".join(map(str, missing)))
    if keywords_found:
        _labelled(pdf, "Keywords present", ", ".join(map(str, keywords_found[:15])))
    if keywords_missing:
        _labelled(pdf, "Keywords missing", ", ".join(map(str, keywords_missing[:15])))


def _jd_section(pdf: FPDF, jd_match: dict[str, Any] | None) -> None:
    if not jd_match:
        return
    _section_title(pdf, "Job Description Match")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, _safe(f"Recommendation: {jd_match.get('recommendation', 'Neutral')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _multiline(pdf, jd_match.get("fit_summary", ""))
    if jd_match.get("matched_skills"):
        _labelled(pdf, "Matched", ", ".join(map(str, jd_match["matched_skills"])))
    if jd_match.get("missing_skills"):
        _labelled(pdf, "Missing", ", ".join(map(str, jd_match["missing_skills"])))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _section_title(pdf: FPDF, title: str) -> None:
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(*PANEL)
    pdf.set_text_color(*INK)
    pdf.cell(0, 9, _safe(f"  {title}"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _text_block(pdf: FPDF, title: str, text: Any) -> None:
    if not text:
        return
    _section_title(pdf, title)
    _multiline(pdf, str(text))


def _bullets(pdf: FPDF, title: str, items: Any) -> None:
    if not items:
        return
    _section_title(pdf, title)
    pdf.set_font("Helvetica", "", 10)
    for item in items:
        _multiline(pdf, f"- {item}")
    pdf.ln(2)


def _labelled(pdf: FPDF, label: str, value: str) -> None:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, _safe(f"{label}:"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _multiline(pdf, value)


def _multiline(pdf: FPDF, text: str) -> None:
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _safe(text))
    pdf.ln(1)


def _safe(text: str) -> str:
    """Normalise text to latin-1 so fpdf's core fonts never crash."""
    text = str(text).replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2022", "-").replace("\u00a0", " ")
    normalised = unicodedata.normalize("NFKD", text)
    return normalised.encode("latin-1", errors="replace").decode("latin-1")
