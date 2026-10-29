"""Page 5 - AI Resume Chatbot."""
from __future__ import annotations

import streamlit as st

from utils import cache
from utils.resume_parser import extract_text
from utils.ui import page_header

SUGGESTIONS = [
    "What are my strongest skills?",
    "How can I improve my ATS score?",
    "Which roles fit this resume?",
    "What is missing from my experience section?",
]


def render() -> None:
    page_header(
        "Resume Chatbot",
        "Ask questions about your resume and get answers grounded in the document.",
        "💬",
    )

    resume_text = st.session_state.get("resume_text", "")
    if not resume_text:
        uploaded = st.file_uploader(
            "Upload a resume to start",
            type=["pdf", "docx", "txt"],
            key="chat_upload",
        )
        if uploaded:
            try:
                resume_text = extract_text(uploaded)
                st.session_state["resume_text"] = resume_text
            except Exception as exc:
                st.error(f"Could not read this file: {exc}")
        if not resume_text:
            resume_text = st.text_area(
                "Or paste your resume",
                height=150,
                placeholder="Paste resume content here...",
                key="chat_paste",
            )
            if resume_text.strip():
                st.session_state["resume_text"] = resume_text

    if not resume_text:
        st.info("Upload or paste a resume to begin.")
        return

    st.success("Resume loaded. Ask anything about it.", icon="✅")

    history: list[dict] = st.session_state.setdefault(
        "chat_history",
        [
            {
                "role": "assistant",
                "content": (
                    "Hi. I have your resume. Ask about your score, skills, gaps, "
                    "target roles or how to improve a section."
                ),
            }
        ],
    )

    if st.button("Clear conversation", use_container_width=False):
        st.session_state["chat_history"] = history[:1]
        st.rerun()

    for message in history:
        with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            source = message.get("source")
            if source == "offline":
                st.caption("🧠 Offline answer")

    st.markdown("**Try asking:**")
    columns = st.columns(2)
    for index, suggestion in enumerate(SUGGESTIONS):
        if columns[index % 2].button(suggestion, key=f"chat_suggestion_{index}", use_container_width=True):
            _send(resume_text, suggestion)

    prompt = st.chat_input("Ask about your resume...")
    if prompt:
        _send(resume_text, prompt)


def _send(resume_text: str, question: str) -> None:
    history: list[dict] = st.session_state.setdefault("chat_history", [])
    history.append({"role": "user", "content": question})

    with st.spinner("Thinking..."):
        reply = cache.chat_reply(
            resume_text,
            question,
            tuple((message["role"], message["content"]) for message in history[:-1]),
        )

    history.append(
        {
            "role": "assistant",
            "content": reply.get("answer", "I could not answer that."),
            "source": reply.get("source"),
        }
    )
    st.rerun()
