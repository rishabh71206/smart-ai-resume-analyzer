# 🤖 Smart AI Resume Analyzer & Interview Bot

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38-red)
![Gemini AI](https://img.shields.io/badge/Google-Gemini%20AI-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌐 Live Demo
### 👉 [Click Here to Use the App](https://smart-ai-resume-analyzer-nfdlpabrwsiiuvghfphuzv.streamlit.app/)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Analyzer** | AI-powered resume scoring with ATS check |
| 🤖 **Interview Bot** | Mock interview with AI question generation & evaluation |
| 🚀 **Career Advisor** | Personalized career roadmap & skill gap analysis |
| 💬 **AI Chatbot** | Ask anything about your resume |
| 🎯 **Job Recommendations** | AI suggests best job matches |
| 👥 **Resume Comparison** | Compare 2 resumes side by side |
| 🎨 **Resume Builder** | Build a professional resume with AI |
| 📚 **Tips & Resources** | Expert resume writing tips |
| 🌙 **Dark/Light Mode** | Toggle between themes |
| 📥 **PDF Report** | Download your analysis as PDF |

---

## 🚀 How to Use (Online)

1. Go to → **[Live App](https://smart-ai-resume-analyzer-nfdlpabrwsiiuvghfphuzv.streamlit.app/)**
2. Upload your resume (PDF, DOCX, or TXT)
3. Click **"Analyze Resume"**
4. Get instant AI-powered feedback!

---

## 💻 Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/rishabh71206/smart-ai-resume-analyzer.git
cd smart-ai-resume-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a FREE Gemini API Key
- Go to → **https://aistudio.google.com/app/apikey**
- Click **"Create API Key"**
- Copy the key

### 4. Create .env file
```bash
cp .env.example .env
```
Add your key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the app
```bash
streamlit run app.py
```

App opens at → **http://localhost:8501**

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11 | Core language |
| Streamlit | Web UI |
| Google Gemini AI | AI analysis engine |
| PyPDF2 | PDF parsing |
| python-docx | DOCX parsing |
| Plotly | Interactive charts |
| fpdf2 | PDF report generation |
| pandas | Data handling |

---

## 📁 Project Structure

```
├── app.py                      # Main entry point
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── pages/
│   ├── resume_analyzer.py      # Resume analysis
│   ├── interview_bot.py        # Mock interview
│   ├── career_advisor.py       # Career roadmap
│   ├── chatbot.py              # AI chatbot
│   ├── job_recommendations.py  # Job matching
│   ├── resume_comparison.py    # Resume comparison
│   ├── resume_builder.py       # Resume builder
│   └── tips_resources.py       # Tips & resources
└── utils/
    ├── resume_parser.py        # Document parser
    ├── ai_engine.py            # Gemini AI wrapper
    ├── scorer.py               # Scoring logic
    └── pdf_report.py           # PDF generator
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make changes and commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## ⭐ Support

If you found this helpful, please **star ⭐ this repository!**

---

## 👨‍💻 Developer

**Rishabh Srivastava**
- GitHub: [@rishabh71206](https://github.com/rishabh71206)

---

## 📄 License

MIT License — free to use and modify.
