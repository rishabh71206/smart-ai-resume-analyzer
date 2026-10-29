"""Small presentation helpers shared by the pages."""
from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


def page_header(title: str, subtitle: str, icon: str = "") -> None:
    heading = f"{icon} {title}".strip()
    st.markdown(f"## {heading}")
    st.caption(subtitle)


def source_note(source: str, reason: str = "") -> None:
    """Tell the user whether Gemini or the offline engine produced a result."""
    if source == "ai":
        st.caption("⚡ Generated with Gemini")
        return
    text = "🧠 Offline analysis (deterministic engine)"
    if reason:
        short = reason if len(reason) <= 180 else reason[:177] + "..."
        text += f" - {short}"
    st.caption(text)


def score_tone(score: float) -> str:
    if score >= 75:
        return "green"
    if score >= 50:
        return "amber"
    return "red"


def chip(text: str, tone: str = "neutral") -> str:
    safe = html.escape(str(text))
    return f'<span class="rs-chip rs-chip--{tone}">{safe}</span>'


def chips(items: Iterable[str], tone: str = "neutral") -> str:
    return "".join(chip(item, tone) for item in items)


def score_cards(items: list[tuple[str, str, str]]) -> None:
    """Render a row of compact score cards: (label, value, tone)."""
    columns = st.columns(len(items))
    for column, (label, value, tone) in zip(columns, items):
        column.markdown(
            f'<div class="rs-score rs-score--{tone}">'
            f'<span class="rs-score__label">{html.escape(label)}</span>'
            f'<strong class="rs-score__value">{html.escape(value)}</strong>'
            f"</div>",
            unsafe_allow_html=True,
        )
