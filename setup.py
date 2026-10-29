"""Packaging metadata for the Smart AI Resume Analyzer.

The app is normally run with ``streamlit run app.py``. This file keeps the
project installable as a package and documents its runtime dependencies in one
place: ``requirements.txt``.
"""
from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


requirements = [
    line.strip()
    for line in _read("requirements.txt").splitlines()
    if line.strip() and not line.strip().startswith("#")
]

setup(
    name="smart-ai-resume-analyzer",
    version="2.0.0",
    description=(
        "AI resume analyzer, mock interview bot and career advisor built with "
        "Streamlit and Google Gemini."
    ),
    long_description=_read("README.md"),
    long_description_content_type="text/markdown",
    author="Rishabh Srivastava",
    author_email="rishabhsrivastava712008@gmail.com",
    url="https://github.com/rishabh71206/smart-ai-resume-analyzer",
    project_urls={
        "Live Demo": "https://smart-ai-resume-analyzer-nfdlpabrwsiiuvghfphuzv.streamlit.app/",
        "Portfolio": "https://rishabh71206.github.io/rishabh-srivastava-portfolio/",
        "Source": "https://github.com/rishabh71206/smart-ai-resume-analyzer",
    },
    license="MIT",
    python_requires=">=3.11",
    packages=find_packages(exclude=("tests", "tests.*")),
    py_modules=["config"],
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Office/Business",
    ],
)
