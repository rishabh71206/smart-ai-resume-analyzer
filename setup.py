"""
One-time setup script.
Run this after `pip install -r requirements.txt` to verify the environment.
"""
import sys
import os


def check():
    print("=" * 55)
    print("  Smart AI Resume Analyzer & Interview Bot — Setup Check")
    print("=" * 55)

    # Python version
    py = sys.version_info
    ok = py >= (3, 10)
    print(f"\n{'✅' if ok else '❌'} Python {py.major}.{py.minor}.{py.micro}  (requires 3.10+)")

    # Required packages
    packages = [
        ("streamlit", "streamlit"),
        ("google.generativeai", "google-generativeai"),
        ("PyPDF2", "PyPDF2"),
        ("docx", "python-docx"),
        ("pandas", "pandas"),
        ("plotly", "plotly"),
        ("dotenv", "python-dotenv"),
        ("PIL", "Pillow"),
        ("fpdf", "fpdf2"),
        ("requests", "requests"),
    ]

    print("\nPackage checks:")
    all_ok = True
    for module, name in packages:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} — run: pip install {name}")
            all_ok = False

    # .env file
    env_exists = os.path.exists(".env")
    print(f"\n{'✅' if env_exists else '⚠️ '} .env file {'found' if env_exists else 'NOT found — copy .env.example to .env and add your GEMINI_API_KEY'}")

    if env_exists:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("GEMINI_API_KEY", "")
        if key and key != "your_google_gemini_api_key_here":
            print("  ✅ GEMINI_API_KEY is set")
        else:
            print("  ⚠️  GEMINI_API_KEY is missing or still set to placeholder")

    print("\n" + "=" * 55)
    if all_ok:
        print("✅ All good! Run the app with:  streamlit run app.py")
    else:
        print("⚠️  Fix the issues above, then run:  streamlit run app.py")
    print("=" * 55)


if __name__ == "__main__":
    check()
