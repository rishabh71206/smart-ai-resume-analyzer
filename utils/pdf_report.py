"""
Generate a downloadable PDF analysis report using fpdf2.
"""
from fpdf import FPDF
from datetime import datetime


class ResumeReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(37, 99, 235)   # blue
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "AI Resume Analysis Report", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Smart AI Resume Analyzer", align="C")


def generate_pdf_report(analysis: dict, candidate_name: str = "Candidate") -> bytes:
    """
    Build a PDF report from the AI analysis dict and return raw bytes.
    """
    pdf = ResumeReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Candidate header ─────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Candidate: {candidate_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Report Date: {datetime.now().strftime('%B %d, %Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ── Score summary ────────────────────────────────────────────────────────
    _section_title(pdf, "Score Summary")
    overall = analysis.get("overall_score", "N/A")
    ats = analysis.get("ats_score", "N/A")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(95, 10, f"Overall Score: {overall}/100")
    pdf.cell(95, 10, f"ATS Score: {ats}/100", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Section scores
    sections_score = analysis.get("sections_score", {})
    if sections_score:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Section Scores:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for k, v in sections_score.items():
            pdf.cell(0, 7, f"  • {k.replace('_', ' ').title()}: {v}/10", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Overall review ───────────────────────────────────────────────────────
    review = analysis.get("overall_review", "")
    if review:
        _section_title(pdf, "Overall Review")
        _multiline(pdf, review)

    # ── Strengths ────────────────────────────────────────────────────────────
    strengths = analysis.get("strengths", [])
    if strengths:
        _section_title(pdf, "Strengths")
        _bullet_list(pdf, strengths)

    # ── Weaknesses ───────────────────────────────────────────────────────────
    weaknesses = analysis.get("weaknesses", [])
    if weaknesses:
        _section_title(pdf, "Areas for Improvement")
        _bullet_list(pdf, weaknesses)

    # ── Suggestions ──────────────────────────────────────────────────────────
    suggestions = analysis.get("suggestions", [])
    if suggestions:
        _section_title(pdf, "Actionable Suggestions")
        _bullet_list(pdf, suggestions)

    # ── Skills ───────────────────────────────────────────────────────────────
    skills_found = analysis.get("skills_found", [])
    missing_skills = analysis.get("missing_skills", [])
    if skills_found or missing_skills:
        _section_title(pdf, "Skills Analysis")
        if skills_found:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Skills Detected:", new_x="LMARGIN", new_y="NEXT")
            _multiline(pdf, ", ".join(skills_found))
        if missing_skills:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Skills to Add:", new_x="LMARGIN", new_y="NEXT")
            _multiline(pdf, ", ".join(missing_skills))

    return bytes(pdf.output())


# ── Helpers ───────────────────────────────────────────────────────────────────

def _section_title(pdf: FPDF, title: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(235, 245, 255)
    pdf.cell(0, 9, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _bullet_list(pdf: FPDF, items: list):
    pdf.set_font("Helvetica", "", 10)
    for item in items:
        safe = str(item).encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 7, f"  \u2022 {safe}")
    pdf.ln(2)


def _multiline(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "", 10)
    safe = str(text).encode("latin-1", errors="replace").decode("latin-1")
    pdf.multi_cell(0, 7, safe)
    pdf.ln(2)
