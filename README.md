# 🤖 Smart AI Resume Analyzer & Interview Bot

A full-featured Python + Streamlit application that uses **Google Gemini AI** to analyze resumes, simulate mock interviews, and provide personalized career advice.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Resume Analyzer** | Deep AI analysis — scores, strengths, weaknesses, ATS check |
| 🎯 **JD Matching** | Compare your resume against a job description |
| 🤖 **Interview Bot** | AI-generated interview questions + answer evaluation |
| 🚀 **Career Advisor** | Personalized roadmap, skill gaps, certifications |
| 📥 **PDF Report** | Downloadable analysis report |
| 📚 **Tips & Resources** | Expert resume writing advice and resources |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — web UI
- **Google Gemini AI** — AI analysis engine
- **PyPDF2 / python-docx** — resume parsing
- **Plotly** — interactive charts
- **fpdf2** — PDF report generation
- **python-dotenv** — environment management

---

## 🚀 Quick Start

### 1. Clone / Open the project
```bash
cd "PROJECT   Smart AI Resume Analyzer & Interview Bot"
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
```bash
# Copy the example env file
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux

# Edit .env and add your key:
# GEMINI_API_KEY=your_google_gemini_api_key_here
```

> **Get a free Gemini API key:** https://aistudio.google.com/

### 5. Run the app
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 📁 Project Structure

```
├── app.py                    # Main Streamlit entry point
├── config.py                 # Central configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── pages/
│   ├── resume_analyzer.py    # Resume analysis page
│   ├── interview_bot.py      # Mock interview page
│   ├── career_advisor.py     # Career roadmap page
│   └── tips_resources.py     # Tips & resources page
└── utils/
    ├── resume_parser.py      # PDF/DOCX/TXT parser
    ├── ai_engine.py          # Gemini AI wrapper
    ├── scorer.py             # Local scoring utilities
    └── pdf_report.py         # PDF report generator
```

---

## 📸 Pages Overview

### 📄 Resume Analyzer
- Upload PDF, DOCX, or TXT resume
- Optionally paste a Job Description for targeted analysis
- Get an **Overall Score**, **ATS Score**, section breakdown radar chart, skills gap analysis, actionable suggestions, and a downloadable PDF report

### 🤖 Interview Bot
- Select job role, difficulty (Easy/Medium/Hard/Mixed), and number of questions
- Choose question types: Behavioral, Technical, Situational, HR
- Answer questions and get AI evaluation with score, grade, feedback, and model answers
- Final performance dashboard with per-question scores

### 🚀 Career Advisor
- Get your current level assessed (Junior → Executive)
- See your fit percentage for the target role
- Prioritized skill gap list with learning resources
- Recommended certifications and an interactive action plan checklist

### 📚 Tips & Resources
- Expandable expert tips for each resume section
- Curated platform and tool links
- Interactive resume checklist

---

## ⚙️ Configuration

Edit `config.py` to customize:
- Gemini model (`gemini-1.5-flash` by default)
- Number of interview questions
- Score weights
- Common skills list for keyword matching

---

## 📄 License

MIT License — free to use and modify.
